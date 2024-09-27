# -*- encoding: utf-8 -*-
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

from vision import obstacle_avoidance
import captureUnityData
from util import tools

# ################################################
ip = str("127.0.0.1")
port = str(8311)
distance_min = 0.12
Vis = True
play_Sound = True
rectangle_color = (0, 0, 0)
txt_color = (0, 0, 0)
# ###############################################################
depth_scale = 0.0010000000474974513
source_700 = oalOpen("../../../materials/700.wav")
source_water = oalOpen("../../../materials/water.wav")
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

                direction_togo, walkable_7, dist_7 = obstacle_avoidance.get_direction_by_depth(_depth_image_matrix)
                if Vis:
                    pass  # visualization not provided
                if direction_togo == -1:
                    tools.speak_str("do walkable direction found.")
                tools.play_by_7_blocks_direction(_listener, direction_togo, source_water, source_water, source_water)
        except RuntimeError:
            raise ValueError


class myThread2(threading.Thread):
    def __init__(self, threadID, name, qq1):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.qq1 = qq1

    def run(self):
        print('consumer thread start ......')
        run_obstacle_avoidance(self.name, self.qq1)


@app.route('/local_nav', methods=["POST"])
def detect():
    r = request
    depth_frame_str = r.form["depth_frame"]
    depth_frame_ndarray = captureUnityData.upsample(depth_frame_str, 1280, 720, 5, 5, 2.8)
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
