# -*- coding: utf-8 -*-
"""
Class definition of YOLO_v3 style detection model on image and video
"""

import colorsys
from timeit import default_timer as timer
import time

import numpy as np
from keras import backend as K
from keras.models import load_model
from keras.layers import Input
from PIL import Image, ImageFont, ImageDraw

from yolo3.model import yolo_eval, yolo_body, tiny_yolo_body
from yolo3.utils import letterbox_image
import os
from keras.utils import multi_gpu_model

#ep047-loss11.355-val_loss11.966.h5    第一版

class YOLO(object):
    _defaults = {
        "model_path": 'logs/ep069-loss11.013-val_loss11.563.h5',
        "anchors_path": 'model_data/yolo_anchors.txt',
        "classes_path": 'model_data/voc_classes.txt',
        "score" : 0.35,
        "iou" : 0.45,
        "model_image_size" : (416, 416),
        "gpu_num" : 1,
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    def __init__(self, **kwargs):
        self.__dict__.update(self._defaults) # set up default values
        self.__dict__.update(kwargs) # and update with user overrides
        self.class_names = self._get_class()
        self.anchors = self._get_anchors()
        self.sess = K.get_session()
        self.boxes, self.scores, self.classes = self.generate()

    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    def _get_anchors(self):
        anchors_path = os.path.expanduser(self.anchors_path)
        with open(anchors_path) as f:
            anchors = f.readline()
        anchors = [float(x) for x in anchors.split(',')]
        return np.array(anchors).reshape(-1, 2)

    def generate(self):  #加载模型调用model/yolo_eval函数产生boxes,scores,classes
        model_path = os.path.expanduser(self.model_path)  #获取model 路径
        assert model_path.endswith('.h5'), 'Keras model or weights must be a .h5 file.'

        # 加载模型、结构、权重
        num_anchors = len(self.anchors)
        num_classes = len(self.class_names)
        is_tiny_version = num_anchors==6 # default setting
        try:
            self.yolo_model = load_model(model_path, compile=False)
        except:
            self.yolo_model = tiny_yolo_body(Input(shape=(None,None,3)), num_anchors//2, num_classes) \
                if is_tiny_version else yolo_body(Input(shape=(None,None,3)), num_anchors//3, num_classes)
            self.yolo_model.load_weights(self.model_path) # make sure model, anchors and classes match
        else:
            assert self.yolo_model.layers[-1].output_shape[-1] == \
                num_anchors/len(self.yolo_model.output) * (num_classes + 5), \
                'Mismatch between model and given anchor and class sizes'

        # 78行 model.layer[-1]:网络最后一层输出。 output_shape[-1]:输出维度的最后一维。 -> (?,13,13,21)  3anchorbox*(5+2类别)
        print('{} model, anchors, and classes loaded.'.format(model_path))

        # Generate colors for drawing bounding boxes.
        # 不同的框，用不同的颜色
        hsv_tuples = [(x / len(self.class_names), 1., 1.)
                      for x in range(len(self.class_names))]
        self.colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples)) #hsv转换为rgb
        self.colors = list(
            map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
                self.colors))
        # hsv取值范围在[0,1]，而RBG取值范围在[0,255]，所以乘上255
        np.random.seed(10101)  # np.random.seed():产生随机种子。固定种子为一致的颜色
        np.random.shuffle(self.colors)  # 调整颜色来装饰相邻的类
        np.random.seed(None)  # 重置种子为默认.

        # 为过滤的边界框生成输出张量目标Generate output tensor targets for filtered bounding boxes.
        self.input_image_shape = K.placeholder(shape=(2, ))  #K.placeholder:keras中的占位符 实际是原始图片的尺寸
        if self.gpu_num>=2:
            self.yolo_model = multi_gpu_model(self.yolo_model, gpus=self.gpu_num)

        # 加载模型调用model/yolo_eval函数产生boxes,scores,classes  NMS
        boxes, scores, classes = yolo_eval(self.yolo_model.output, self.anchors,
                len(self.class_names), self.input_image_shape,
                score_threshold=self.score, iou_threshold=self.iou)   #yolo_eval():yolo评估函数
        return boxes, scores, classes

    def detect_image(self, image):
        start = timer()

        #将图片等比例转换为检测尺寸，检测尺寸是32的倍数，
        if self.model_image_size != (None, None):  #判断图片是否存在
            assert self.model_image_size[0]%32 == 0, 'Multiples of 32 required'
            assert self.model_image_size[1]%32 == 0, 'Multiples of 32 required'
            #model_image_size[0][1] 指图像的w和h，且必须是32的整数倍
            boxed_image = letterbox_image(image, tuple(reversed(self.model_image_size)))
        else:
            # letterbox_image()定义见附录中的yolo3.utils。输入参数（图像 ,(w=416,h=416)),
            # 输出一张使用填充来调整图像的纵横比不变的新图。
            new_image_size = (image.width - (image.width % 32),
                              image.height - (image.height % 32))
            boxed_image = letterbox_image(image, new_image_size)
        image_data = np.array(boxed_image, dtype='float32')

        #print(image_data.shape)
        image_data /= 255.      #转换为0-1  归一化
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.添加批次维度，将图片增加一维
        # 添加批量维度为 (1,416,416,3)，使输入网络的张量满足(bitch, w, h, c)的格式

        #feed数据 图像 图像尺寸
        out_boxes, out_scores, out_classes = self.sess.run(
            [self.boxes, self.scores, self.classes],  #目的为了求boxes,scores,classes，具体计算方式定义在generate（）函数内。在yolo.py中
            feed_dict={
                self.yolo_model.input: image_data,    #图像数据
                self.input_image_shape: [image.size[1], image.size[0]], #图像尺寸
                K.learning_phase(): 0   #学习模式 0：测试模型。1：训练模式
            })

        #print('Found {} boxes for {}'.format(len(out_boxes), 'img'))
        #绘制边框，自动设置边框宽度，绘制边框和类别文字，使用pillow绘图库。
        font = ImageFont.truetype(font='font/FiraMono-Medium.otf',
                    size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32')) #设置字体
        thickness = (image.size[0] + image.size[1]) // 300    #设置厚度

        result=[]
        for i, c in reversed(list(enumerate(out_classes))): #enumerate 列举
            predicted_class = self.class_names[c]   #类别
            box = out_boxes[i]   #框
            score = out_scores[i]   #置信度

            label = '{} {:.2f}'.format(predicted_class, score) #标签
            draw = ImageDraw.Draw(image)  #画图
            label_size = draw.textsize(label, font)  #标签文字

            top, left, bottom, right = box
            top = max(0, np.floor(top + 0.5).astype('int32'))    # np.floor向下取整
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
            #print(label, (left, top), (right, bottom))   #bounding box
            res=[label,left,top,right,bottom]
            result.append(res)
            if top - label_size[1] >= 0:  #标签文字
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            # My kingdom for a good redistributable image drawing library.
            for i in range(thickness):   #画边框
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=self.colors[c])
            draw.rectangle(   #文字背景
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=self.colors[c])
            draw.text(text_origin, label, fill=(0, 0, 0), font=font)
            del draw

        end = timer()
        #print(end - start)
        return image,result

    def close_session(self):
        self.sess.close()

def detect_video(yolo, video_path, output_path=""):
    import cv2
    vid = cv2.VideoCapture(0)
    if not vid.isOpened():
        raise IOError("Couldn't open webcam or video")
    video_FourCC    = int(vid.get(cv2.CAP_PROP_FOURCC))
    video_fps       = vid.get(cv2.CAP_PROP_FPS)
    video_size      = (int(vid.get(cv2.CAP_PROP_FRAME_WIDTH)),
                        int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    isOutput = True if output_path != "" else False
    if isOutput:
        print("!!! TYPE:", type(output_path), type(video_FourCC), type(video_fps), type(video_size))
        out = cv2.VideoWriter(output_path, video_FourCC, video_fps, video_size)
    accum_time = 0
    curr_fps = 0
    fps = "FPS: ??"
    prev_time = timer()
    while True:
        return_value, frame = vid.read()
        #time.sleep(10)    #暂停10秒再继续  需要修改
        image = Image.fromarray(frame)
        image,res = yolo.detect_image(image)   #对一帧图片进行判断
        result = np.asarray(image)
        curr_time = timer()
        exec_time = curr_time - prev_time
        prev_time = curr_time
        accum_time = accum_time + exec_time
        curr_fps = curr_fps + 1
        if accum_time > 1:
            accum_time = accum_time - 1
            fps = "FPS: " + str(curr_fps)
            curr_fps = 0
        #cv2.putText(result, text=fps, org=(3, 15), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        #            fontScale=0.50, color=(255, 0, 0), thickness=2)
        cv2.namedWindow("result", cv2.WINDOW_NORMAL)
        cv2.imshow("result", result)
        if isOutput:
            out.write(result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    yolo.close_session()
