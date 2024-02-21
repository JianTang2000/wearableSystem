# -*- encoding: utf-8 -*-
import math
import threading
import time
from queue import Queue

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
play_Sound = True
rectangle_color = (0, 0, 0)
txt_color = (0, 0, 0)
depth_scale = 0.0010000000474974513
source300 = oalOpen("../materials/300.wav")
source700 = oalOpen("../materials/water2.wav")
_listener = oalGetListener()
qq = Queue(1)

app = Flask(__name__)
CORS(app, resources=r'/*')


def run_obstacle_avoidance(threadName, qq1):
    while True:
        try:
            if not qq1.empty():
                context_1 = qq1.get()
                depth_frame_ndarray = context_1[0]
                _depth_image_matrix = depth_frame_ndarray
                _depth_colormap = depth_frame_ndarray
                direction_togo, walkable_7, dist_7 = Unity_obstacle_avoidance.get_direction_by_depth(_depth_image_matrix)
                if direction_togo == -1:
                    pass
                if direction_togo == 0:
                    tools.play_by_direction(-25, _listener, source700, sleep_time=tools.audio_sleep_time)
                if direction_togo == 1:
                    tools.play_by_direction(-25, _listener, source700, sleep_time=tools.audio_sleep_time)
                if direction_togo == 2:
                    tools.play_by_direction(-25, _listener, source700, sleep_time=tools.audio_sleep_time)
                if direction_togo == 3:
                    tools.play_by_direction(0, _listener, source300, sleep_time=tools.audio_sleep_time)
                if direction_togo == 4:
                    tools.play_by_direction(25, _listener, source700, sleep_time=tools.audio_sleep_time)
                if direction_togo == 5:
                    tools.play_by_direction(25, _listener, source700, sleep_time=tools.audio_sleep_time)
                if direction_togo == 6:
                    tools.play_by_direction(25, _listener, source700)
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
    depth_frame_ndarray = upsample(depth_frame_str, 1920, 1080, 10, 10, 2.8)
    context_1 = [depth_frame_ndarray, None]
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
