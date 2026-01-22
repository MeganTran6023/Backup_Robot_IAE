#!/usr/bin/env python3
# encoding:utf-8

import sys
import time
import zlib
import threading
import cv2
import numpy as np
from bson import BSON
from CameraCalibration.CalibrationConfig import *

# === IMPORT STREAMER ===
from acpcomms.streamer import Streamer  # adjust import path as needed

# ================= CAMERA CLASS =================
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
        self.detected_colors = set()

        self.param_data = np.load(calibration_param_path + '.npz')
        self.mtx = self.param_data['mtx_array']
        self.dist = self.param_data['dist_array']

        self.newcameramtx, _ = cv2.getOptimalNewCameraMatrix(
            self.mtx, self.dist,
            (self.width, self.height), 0,
            (self.width, self.height)
        )

        self.mapx, self.mapy = cv2.initUndistortRectifyMap(
            self.mtx, self.dist, None,
            self.newcameramtx,
            (self.width, self.height), 5
        )

        self.color_ranges = {
            'red': [((0, 120, 70), (10, 255, 255)),
                    ((170, 120, 70), (180, 255, 255))],
            'green': [((36, 50, 70), (89, 255, 255))],
            'blue': [((90, 50, 70), (128, 255, 255))]
        }

        self.color_draw = {
            'red': (0, 0, 255),
            'green': (0, 255, 0),
            'blue': (255, 0, 0)
        }

        self.th = threading.Thread(target=self.camera_task, daemon=True)
        self.th.start()

    def camera_open(self):
        self.cap = cv2.VideoCapture(-1)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('Y', 'U', 'Y', 'V'))
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_SATURATION, 40)
        self.opened = True

    def camera_close(self):
        self.opened = False
        time.sleep(0.2)
        if self.cap:
            self.cap.release()
        self.cap = None

    def camera_task(self):
        while True:
            if self.opened and self.cap and self.cap.isOpened():
                ret, frame_tmp = self.cap.read()
                if not ret:
                    continue

                frame_resize = cv2.resize(
                    frame_tmp, (self.width, self.height),
                    interpolation=cv2.INTER_NEAREST
                )

                frame = cv2.remap(
                    frame_resize, self.mapx, self.mapy,
                    cv2.INTER_LINEAR
                )

                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                self.detected_colors.clear()

                for color_name, ranges in self.color_ranges.items():
                    mask = None
                    for lower, upper in ranges:
                        m = cv2.inRange(hsv, np.array(lower), np.array(upper))
                        mask = m if mask is None else cv2.bitwise_or(mask, m)

                    mask = cv2.morphologyEx(
                        mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)
                    )

                    contours, _ = cv2.findContours(
                        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                    )

                    if contours:
                        c = max(contours, key=cv2.contourArea)
                        if cv2.contourArea(c) > 1500:
                            self.detected_colors.add(color_name)
                            x, y, w, h = cv2.boundingRect(c)
                            cv2.rectangle(frame, (x, y), (x + w, y + h),
                                          self.color_draw[color_name], 2)
                            cv2.putText(frame, color_name, (x, y - 5),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                                        self.color_draw[color_name], 2)
                self.frame = frame
            else:
                time.sleep(0.01)

# ================= STREAMER CONFIG =================
CHUNK_SIZE = 65000 - 4

# Video streamer on port 9998
video_streamer = Streamer()
video_streamer.configure({
    "host": "192.168.1.209",
    "port": 9998,  # Changed from 9999
    "bufferSize": 65535
})
video_streamer.connect()

# Metadata streamer on port 9999
metadata_streamer = Streamer()
metadata_streamer.configure({
    "host": "192.168.1.209",
    "port": 9999,  # Metadata only
    "bufferSize": 65535
})
metadata_streamer.connect()

# ================= HELPERS =================
def get_color_status(camera: Camera):
    if not camera.detected_colors:
        return "none"
    return sorted(camera.detected_colors)

# ================= METADATA THREAD =================
def metadata_loop(camera: Camera):
    while True:
        payload = {
            "sensor_id": "PiCam_001",
            "timestamp": time.time(),
            "status": "active",
            "colors_detected": get_color_status(camera)
        }
        metadata_streamer.sendBson(payload)  # Keep original method
        time.sleep(5)

# ================= STREAM THREAD =================
def stream_loop(camera: Camera):
    JPEG_QUALITY = 70

    while True:
        frame = camera.frame
        if frame is None:
            time.sleep(0.01)
            continue

        ok, jpeg = cv2.imencode(
            ".jpg", frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY]
        )
        if not ok:
            continue

        data = jpeg.tobytes()
        for i in range(0, len(data), CHUNK_SIZE):
            video_streamer.sendChunkWithChecksum(data[i:i + CHUNK_SIZE])

        time.sleep(0.03)

# ================= MAIN =================
if __name__ == "__main__":
    my_camera = Camera()
    my_camera.camera_open()

    threading.Thread(target=metadata_loop, args=(my_camera,), daemon=True).start()
    threading.Thread(target=stream_loop, args=(my_camera,), daemon=True).start()

    # === DEBUG DISPLAY LOOP ===
    while True:
        frame = my_camera.frame
        if frame is not None:
            cv2.imshow("Camera Stream", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

    my_camera.camera_close()
    video_streamer.disconnect()
    metadata_streamer.disconnect()
    cv2.destroyAllWindows()
