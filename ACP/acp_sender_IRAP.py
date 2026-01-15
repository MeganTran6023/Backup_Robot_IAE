#!/usr/bin/env python3
# encoding:utf-8
import sys
sys.path.append('/home/megan/MasterPi/')
import cv2
import time
import threading
import numpy as np
from CameraCalibration.CalibrationConfig import *

if sys.version_info.major == 2:
    print('Please run this program with python3!')
    sys.exit(0)

class Camera:
    def __init__(self, resolution=(640, 480)):
        self.cap = None
        self.width = resolution[0]
        self.height = resolution[1]
        self.frame = None
        self.opened = False
        #加载参数
        self.param_data = np.load(calibration_param_path + '.npz')
        
        #获取参数
        self.mtx = self.param_data['mtx_array']
        self.dist = self.param_data['dist_array']
        self.newcameramtx, roi = cv2.getOptimalNewCameraMatrix(
            self.mtx, self.dist,
            (self.width, self.height), 0,
            (self.width, self.height)
        )
        self.mapx, self.mapy = cv2.initUndistortRectifyMap(
            self.mtx, self.dist, None,
            self.newcameramtx,
            (self.width, self.height), 5
        )

        # ---------- ADD: HSV color ranges ----------
        self.color_ranges = {
            'red': [
                ((0, 120, 70), (10, 255, 255)),
                ((170, 120, 70), (180, 255, 255))
            ],
            'green': [((36, 50, 70), (89, 255, 255))],
            'blue': [((90, 50, 70), (128, 255, 255))]
        }

        self.color_draw = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0)
        }
        # -----------------------------------------

        self.th = threading.Thread(target=self.camera_task, args=(), daemon=True)
        self.th.start()

    def camera_open(self):
        try:
            self.cap = cv2.VideoCapture(-1)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            self.cap.set(cv2.CAP_PROP_SATURATION, 40)
            self.opened = True
        except Exception as e:
            print('打开摄像头失败:', e)

    def camera_close(self):
        try:
            self.opened = False
            time.sleep(0.2)
            if self.cap is not None:
                self.cap.release()
                time.sleep(0.05)
            self.cap = None
        except Exception as e:
            print('关闭摄像头失败:', e)

    def camera_task(self):
        while True:
            try:
                if self.opened and self.cap.isOpened():
                    ret, frame_tmp = self.cap.read()
                    if ret:
                        frame_resize = cv2.resize(
                            frame_tmp,
                            (self.width, self.height),
                            interpolation=cv2.INTER_NEAREST
                        )
                        frame = cv2.remap(
                            frame_resize,
                            self.mapx, self.mapy,
                            cv2.INTER_LINEAR
                        )

                        # ---------- ADD: COLOR DETECTION ----------
                        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

                        for color_name, ranges in self.color_ranges.items():
                            mask = None
                            for lower, upper in ranges:
                                m = cv2.inRange(
                                    hsv,
                                    np.array(lower),
                                    np.array(upper)
                                )
                                mask = m if mask is None else cv2.bitwise_or(mask, m)

                            mask = cv2.morphologyEx(
                                mask, cv2.MORPH_OPEN,
                                np.ones((5, 5), np.uint8)
                            )

                            contours, _ = cv2.findContours(
                                mask,
                                cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE
                            )

                            if contours:
                                c = max(contours, key=cv2.contourArea)
                                if cv2.contourArea(c) > 1500:
                                    x, y, w, h = cv2.boundingRect(c)
                                    cv2.rectangle(
                                        frame,
                                        (x, y),
                                        (x + w, y + h),
                                        self.color_draw[color_name],
                                        2
                                    )
                                    cv2.putText(
                                        frame,
                                        color_name,
                                        (x, y - 5),
                                        cv2.FONT_HERSHEY_SIMPLEX,
                                        0.6,
                                        self.color_draw[color_name],
                                        2
                                    )
                        # ----------------------------------------

                        self.frame = frame
                    else:
                        print(1)
                        self.frame = None
                        cap = cv2.VideoCapture(-1)
                        ret, _ = cap.read()
                        if ret:
                            self.cap = cap
                elif self.opened:
                    print(2)
                    cap = cv2.VideoCapture(-1)
                    ret, _ = cap.read()
                    if ret:
                        self.cap = cap              
                else:
                    time.sleep(0.01)
            except Exception as e:
                print('获取摄像头画面出错:', e)
                time.sleep(0.01)

if __name__ == '__main__':
    my_camera = Camera()
    my_camera.camera_open()
    while True:
        img = my_camera.frame
        if img is not None:
            cv2.imshow('img', img)
            key = cv2.waitKey(1)
            if key == 27:
                break
    my_camera.camera_close()
    cv2.destroyAllWindows()
