# -*- encoding: utf-8 -*-
import math
import threading
import time
from queue import Queue
import torch

import cv2
import jsonpickle
import numpy as np
from flask import Flask, request, Response
from flask_cors import CORS
from gevent import pywsgi
from openal import *
from openal.al import *

from visualProcess import Unity_obstacle_avoidance
from util import tools

ip = str("127.0.0.1")
port = str(8311)
distance_min = 0.12
Vis = True
play_Sound = True
rectangle_color = (0, 0, 0)
txt_color = (0, 0, 0)
depth_scale = 0.0010000000474974513
source300 = oalOpen("../materials/300.wav")  # 对应 direction 3
source700 = oalOpen("../materials/water2.wav")  # 对应 left right
_listener = oalGetListener()
qq = Queue(1)

app = Flask(__name__)
CORS(app, resources=r'/*')

model = torch.hub.load(r'path2yoloV5', 'custom',
                       path=r'../materials/weights/best.onnx',
                       source='local',
                       force_reload=True,
                       device='cpu')


def run_obstacle_avoidance(threadName, qq1):
    direction_all = ["left", "right"]
    model.conf = 0.4
    min_angle_error = 5
    close_distance = 1
    current_target_index = 0
    landmarks = [60, 56]
    landmark_dist_threshold = [2, 2]  # distance in m
    landmark_names = ["table", "chair"]
    landmark_desc = ["table", "chair"]
    running_OA = False
    start_OA_time = -1
    oa_time = 5
    while True:
        try:
            if not qq1.empty():
                context_1 = qq1.get()
                depth_frame_ndarray = context_1[0]
                rgb_str = context_1[1]
                np_img = np.fromstring(rgb_str, np.uint8)
                cv2_rgb = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                _color_image = cv2_rgb
                _depth_image_matrix = depth_frame_ndarray
                _depth_colormap = depth_frame_ndarray
                direction_togo, walkable_7, dist_7 = Unity_obstacle_avoidance.get_direction_by_depth(_depth_image_matrix)
                results = model(_color_image, size=512)
                angle_info, xywh = tools.post_process_angle_unity(results, obj_id=landmarks[current_target_index])
                distance, no_depth_area = tools.post_process_distance_unity(xywh, _depth_image_matrix)
                if distance is not None:
                    angle_float = float(angle_info.split(" ")[0])  # "10.8 right" "10.8 left"
                    direction = str(angle_info.split(" ")[1])
                    if landmark_dist_threshold[current_target_index] < distance <= close_distance:
                        angle_err_accept = min_angle_error
                        if angle_float <= angle_err_accept:
                            tools.play_by_direction(0, _listener, source300, sleep_time=tools.audio_sleep_time)
                        else:
                            if direction == "left":
                                tools.play_by_direction(-90, _listener, source700, sleep_time=tools.audio_sleep_time)
                            elif direction == "right":
                                tools.play_by_direction(90, _listener, source700, sleep_time=tools.audio_sleep_time)
                        continue
                    if distance <= landmark_dist_threshold[current_target_index]:
                        tools.speak_str(landmark_desc[current_target_index] + f" on the {direction}, go {direction_all[1] if direction_all[0] == direction else direction_all[0]}")
                        if current_target_index != len(landmarks) - 1:
                            current_target_index += 1
                        continue

                if running_OA:
                    tools.play_by_7_blocks_direction(_listener, direction_togo, source700, source300, source700)
                    print(f"=====> doing OA at {time.time() - start_OA_time}/{oa_time} <=====")
                    if time.time() - start_OA_time > oa_time:
                        running_OA = False
                    continue
                if direction_togo not in [2, 3, 4]:
                    running_OA = True
                    start_OA_time = time.time()
                    tools.play_by_7_blocks_direction(_listener, direction_togo, source700, source300, source700)
                    continue
                else:
                    if distance is None:
                        tools.play_by_7_blocks_direction(_listener, direction_togo, source700, source300, source700)
                        continue
                    else:
                        direction_togo, angle_float, direction = tools.OD_with_OA(angle_info, distance, direction_togo, walkable_7, dist_7)
                        tools.play_by_7_blocks_direction(_listener, direction_togo, source700, source300, source700)
                        continue

        except RuntimeError:
            raise ValueError


class myThread2(threading.Thread):
    def __init__(self, threadID, name, qq1):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.qq1 = qq1

    def run(self):
        run_obstacle_avoidance(self.name, self.qq1)


def upsample(distance, des_res_width, des_res_height, factor_width, factor_height, scale_factor):
    distance = readDistance(distance, des_res_height, factor_height, scale_factor)
    distance = cv2.resize(distance, dsize=(640, 360))
    return distance


def readDistance(distance, des_res_height, factor_height, scale_factor):
    data = np.array(distance.split(","), dtype=np.float)
    if des_res_height / factor_height != des_res_height // factor_height:
        raise ValueError
    data = data.reshape(-1, des_res_height // factor_height)
    distance = np.zeros((data.shape[1], data.shape[0]))
    shape = distance.shape
    for indx in range(shape[0]):
        for indy in range(shape[1]):
            distance[indx][indy] = data[indy][shape[0] - 1 - indx]
    distance = np.sqrt(distance) * scale_factor
    return distance


@app.route('/local_nav', methods=["POST"])
def detect():
    r = request
    depth_frame_str = r.form["depth_frame"]
    depth_frame_ndarray = upsample(depth_frame_str, 1280, 720, 10, 10, 2.8)
    rgb_str = request.files['rgb'].read()
    context_1 = [depth_frame_ndarray, rgb_str]
    if qq.full():
        qq.get()
        qq.put(context_1)
    else:
        qq.put(context_1)
    response = {'message': 'data received'}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


if __name__ == '__main__':
    thread11 = myThread2(11, "thread_get_queue_cam", qq)
    thread11.start()
    print('=========================================================================')
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('=================================================================================')
    print('=========server start running at: ', now, '=========')
    print('=========IP + Port    =   ', ip, ':', port, '=========')
    print('=========================== ready to fly ========================================')
    server = pywsgi.WSGIServer((ip, int(port)), app)
    server.serve_forever()
