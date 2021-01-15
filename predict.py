#不用命令 python yolo_video.py --image
# 可单独使用，不从GUI界面进入
import os
from yolo import YOLO,detect_video
from PIL import Image
from os import getcwd

yolo = YOLO()
def predict_imag(imgpath,imgname):

    #img = input('Input image filename:')
    try:
        image = Image.open(imgpath)    # 用pillow打开
    except:
        print('Open Error! Try again!')
    else:              #有异常时else不执行
        r_image,result= yolo.detect_image(image)  #返回PIL类型，没有用到cv2
        #print(type(r_image))
        print('----',result)
        r_image.show()
        #print(imgname+'保存')
        r_image.save('Result/'+imgname+'.jpg')
        print(imgname+'保存成功')



def generate(txt_name, dir, prefix, folder, label):
    files = os.listdir(dir)  # 里面的图片.jpg
    files.sort()

    listText = open(txt_name, 'w+')
    for file in files:
        name = prefix + folder + '/' + file + ' ' + str(int(label)) + '\n'
        listText.write(name)
    listText.close()


def gen_text_list(test_path):
    #test_path = "img/"  # 这里是你的图片的目录
    txt_name = 'test_imglist.txt'
    print('开始生成测试图片路径文件')
    img_list = os.listdir(test_path)
    img_list.sort()
    list_Text = open(txt_name, 'w+')
    wd = getcwd()
    for img in img_list:
        name = wd + '/test/'  + img + '\n'
        list_Text.write(name)
    list_Text.close()
    print('列表文件已生成')



def video(yolo,video_path):
    try:
        detect_video(yolo,video_path)
    except:
        print('Open Error! Try again!')

def detect_images():
    test_file = "test_imglist.txt"
    img_file = "./test/"
    gen_text_list(img_file)  # 获取
    with open(test_file) as f:
        lines = f.readlines()
        n_test = len(lines)
        print("num of test images:", n_test)  # 输出测试文件夹中有几张图片
        for line in lines:
            img_path = line.strip()
            img_name = line.strip().split("/")[2].split(".")[0]  # 第一个里是6 在云端上
            #print(img_name)
            #print(img_path)
            predict_imag(img_path, img_name)
        yolo.close_session()

if __name__ == '__main__':

    #detect_images()

    video_path=0
    video(yolo,video_path)
    yolo.close_session()
