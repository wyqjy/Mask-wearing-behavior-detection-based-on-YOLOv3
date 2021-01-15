# -*- coding: utf-8 -*-
# @Time : 2020/4/12 10:28
# @Author : Wangyuqi
# @FileName: people_counting.py
# @Email : www2048g@126.com

#统计时间段人数  目标跟踪

from __future__ import division, print_function, absolute_import

import os
from timeit import time
import warnings
import sys
import cv2
import numpy as np
from PIL import Image
from yolo import YOLO
import pymysql
import datetime

from deep_sort import preprocessing
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tools import generate_detections as gdet
from deep_sort.detection import Detection as ddet

warnings.filterwarnings('ignore')

conn = pymysql.connect(host='127.0.0.1',user='root',passwd='123456',db='mask',port=3306,charset='utf8')
cur = conn.cursor()

def main(yolo, videopath):
    # Definition of the parameters
    max_cosine_distance = 0.3
    nn_budget = None
    nms_max_overlap = 1.0

    # deep_sort
    model_filename = 'model_data/mars-small128.pb'
    encoder = gdet.create_box_encoder(model_filename, batch_size=1)

    metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)  #余弦度量距离
    tracker = Tracker(metric)

    writeVideo_flag = True  # 是否保存处理后的视频

    video_capture = cv2.VideoCapture(videopath)  # 读取视频路径

    if writeVideo_flag:
        # Define the codec and create VideoWriter object
        w = int(video_capture.get(3))  # 读取宽
        h = int(video_capture.get(4))  # 读取高
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # 用于设置保存视频的格式
        out = cv2.VideoWriter('output.avi', fourcc, 15, (w, h))
        #list_file = open('detection.txt', 'w')

    fps = 0.0
    st1 = int(time.time())
    time_flag = 0
    people=0
    last_people=0
    while True:

        flag_nomask = False
        havema = 0
        ret, frame = video_capture.read()  # frame shape 640*480*3    ret是否成功读取视频帧
        if ret != True:
            break

        t1 = time.time()

        #image = Image.fromarray(frame)
        image = Image.fromarray(frame[..., ::-1])  # bgr to rgb
        r_image,result = yolo.detect_image(image)  # 按帧检测图片
        boxs=[]
        label=''
        #print(len(result))
        if len(result) == 0:
            time.sleep(1)
            print('当前窗口内无人，暂停一秒检测')
        for box in result:
            label = box[0].split(' ')[0]
            x = int(box[1])
            y = int(box[2])
            w = int(box[3] - box[1])
            h = int(box[4] - box[2])
            print(box[0].split(' ')[0])
            if label == 'no_mask':
                flag_nomask = True
                boxs.append([x,y,w,h])
            if label == 'have_mask':
                havema = havema + 1
                cv2.rectangle(frame, (int(box[1]), int(box[2])), (int(box[3]), int(box[4])), (0, 255, 0), 2)
                cv2.putText(frame, label, (int(box[3]), int(box[4])), 0, 5e-3 * 200, (255, 0, 0), 2)


        # print("box_num",len(boxs))
        #print(label)
        features = encoder(frame, boxs)

        # score to 1.0 here).
        detections = [Detection(bbox, 1.0, feature) for bbox, feature in zip(boxs, features)]

        # Run non-maxima suppression.  NMS非极大值抑制
        boxes = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        indices = preprocessing.non_max_suppression(boxes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices]

        # Call the tracker
        tracker.predict()
        tracker.update(detections)


        for track in tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue
            bbox = track.to_tlbr()
            people=max(people,track.track_id)
            #cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (255, 255, 255), 2)
            #print('--------======-------  ', str(track.track_id))
            cv2.putText(frame, str(track.track_id), (int(bbox[0]), int(bbox[1])), 0, 5e-3 * 200, (0, 255, 0), 2)  # 在左上角标记上绿色的人数
            cv2.putText(frame, label , (int(bbox[2]), int(bbox[3])), 0, 5e-3 * 200, (255, 0, 0), 2)

        # 计算时间
        now_time = datetime.datetime.now()
        date_time = datetime.datetime.strftime(now_time, '%Y-%m-%d')
        time2= datetime.datetime.strftime(now_time, '%H:%M:%S')
        file = datetime.datetime.strftime(now_time, '%H_%M_%S')

        #print('---------',time2,' ',time_flag)
        if time2 == '00:00:01' and time_flag==0:
            time_flag=1
            sql="insert into day_statistics(date1,people)values('"+date_time+"','"+str(people)+"')"
            #print(sql)
            cur.execute(sql)
            conn.commit()
            last_people = people
        if time2 == '00:00:02' and time_flag==1:
            time_flag=0

        for det in detections:
            bbox = det.to_tlbr()
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), (0, 0, 255), 2)
            st2=int(time.time())
            #print('------------',st2,'  ',st1)
            if st2>st1:
                st1=st2
                sql="insert into no_mask(date1,time1,left1,top,right1,bottom)values('" + date_time +"','"+ time2+ "','"+ str(bbox[0])+ "','"+ str(bbox[1])+"','"+str(bbox[2])+"','"+str(bbox[3])+"')"
                #print(sql)
                cur.execute(sql)
                conn.commit()

        tip_people = "current have_mask:"+str(havema)+", no_mask:"+str(len(boxs))+"    Today no_mask:"+str(people-last_people)
        print(tip_people)
        cv2.putText(frame, tip_people, org=(3, 15),fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.50, color=(255, 0, 0), thickness=2)

        cv2.namedWindow("MASK Detection", cv2.WINDOW_NORMAL)
        cv2.imshow('MASK Detection', frame)


        path='Result-video/'+date_time
        if not os.path.exists(path):
            os.mkdir(path)
        if (flag_nomask == True) :
            filename=path+'/no_mask_'+file+'.jpg'
            cv2.imwrite(filename, frame)

        if writeVideo_flag:
            # save a frame
            out.write(frame)  # 保存处理后的视频


        fps = (fps + (1. / (time.time() - t1))) / 2
        print("fps= %f" % (fps))

        # Press Q to stop!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    if writeVideo_flag:
        out.release()
    cv2.destroyAllWindows()

def Main():
    videopath = 0
    yolo = YOLO()
    main(yolo, videopath)

if __name__ == '__main__':
    videopath = 0  # test001.mp4
    yolo=YOLO()
    main(yolo, videopath)

