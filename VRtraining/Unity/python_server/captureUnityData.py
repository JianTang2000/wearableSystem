# -*- encoding: utf-8 -*-
"""
receive the simulated data from Unity
"""
import os
import threading
import time
from queue import Queue

import cv2
import jsonpickle
import numpy as np
from flask import Flask, request, Response
from flask_cors import CORS
from gevent import pywsgi

from util import tools

ip = str("127.0.0.1")
port = str(8311)
distance_min = 0.12
Vis = True
rectangle_color = (0, 0, 0)  # black (0, 0, 0)
txt_color = (0, 255, 127)
depth_scale = 0.0010000000474974513
qq = Queue(1)

app = Flask(__name__)
CORS(app, resources=r'/*')


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
    depth_frame_ndarray = upsample(depth_frame_str, 1920, 1080, 5, 5, 2.8)  # 0.35625 = 100cm
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


def vis_RGB_D(threadName, qq1):
    save_RGBD = True
    Vis_blocks = False
    save_dir = r"data\Unity_RGBD"
    count_current = 0
    while True:
        try:
            if not qq1.empty():
                context_1 = qq1.get()
                _depth_image_matrix = context_1[0]
                rgb_str = context_1[1]
                np_img = np.fromstring(rgb_str, np.uint8)
                cv2_rgb = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                depth_img = _depth_image_matrix / depth_scale  # mimic realsense's deep visualization method for visualization
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_img, alpha=0.03), cv2.COLORMAP_JET)
                # save the simulated data for analysis
                if save_RGBD:
                    date = time.strftime("%Y-%m-%d-%H-%M-%S")
                    depth_name = "object-" + str(date) + "-" + str(count_current) + ".npy"
                    rgb_name = "object-" + str(date) + "-" + str(count_current) + ".jpg"
                    cv2.imwrite(os.path.join(save_dir, rgb_name), cv2_rgb)
                    count_current += 1
                    np.save(os.path.join(save_dir, depth_name), _depth_image_matrix)
                # vis the simulated data with blocks
                if Vis_blocks:
                    tools.vis_Unity_OA(3, 0.12, depth_colormap, _depth_image_matrix)
                else:
                    if Vis:
                        cv2.namedWindow('RGB')
                        cv2.namedWindow('Depth')
                        cv2.imshow('RGB', cv2_rgb)
                        cv2.imshow('Depth', depth_colormap)
                        key = cv2.waitKey(1)
        except RuntimeError:
            print(threadName, "queue1 error occurs and skip for next frame!")
            raise NotImplementedError


class myThread2(threading.Thread):
    def __init__(self, threadID, name, qq1):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.qq1 = qq1

    def run(self):
        vis_RGB_D(self.name, self.qq1)


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
