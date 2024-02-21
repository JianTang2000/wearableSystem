import copy

import torch
import math
import threading
import time
from queue import Queue
import platform

import cv2
import jsonpickle
import numpy as np
import pyttsx3
from flask import Flask, request, Response
from flask_cors import CORS
from gevent import pywsgi
from openal import *
from openal.al import *

from visualProcess import Unity_obstacle_avoidance
from util import UdpComms as U
from util import tools

ip = str("127.0.0.1")
port = str(8311)
depth_scale = 0.0010000000474974513
app = Flask(__name__)
CORS(app, resources=r'/*')
qq = Queue(2)
sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)


def sen_msg(msg):
    sock.SendData(msg)  # Send this string to other application


def reachingObj(data_q, target_id=4, close_distance=3, success_dist=1.8):
    source300 = oalOpen("../materials/300.wav")
    source1100 = oalOpen("../materials/water2.wav")
    _listener = oalGetListener()
    if platform.system() == "Windows":
        print("==================> Running on Windows")
        model = torch.hub.load(r'yolov5', 'custom',
                               path='../materials/weights/best.pt',
                               source='local',
                               force_reload=True,
                               device='cpu')
        vis = True
    else:
        raise NotImplementedError
    model.conf = 0.4
    min_angle_error = 5
    running_OA = False
    start_OA_time = -1
    distance_min = 0.12
    oa_time = 8
    arrived = False
    feedback_mode = 0

    while True:
        if data_q.empty() or arrived:
            time.sleep(0.01)
            continue

        context_1 = data_q.get()
        rgb_str = context_1[1]
        np_img = np.fromstring(rgb_str, np.uint8)
        cv2_rgb = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
        _depth_image_matrix = context_1[0]
        raw_depth_image_matrix = copy.deepcopy(_depth_image_matrix)
        depth_image_matrix = copy.deepcopy(_depth_image_matrix)
        color_image = cv2_rgb
        _color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        _color_image = cv2.resize(_color_image, dsize=(640, 360))
        color_image = cv2.resize(color_image, dsize=(640, 360))
        results = model(_color_image, size=512)
        angle_info, xywh = tools.post_process_angle(results, obj_id=target_id)
        distance, no_depth_area = tools.post_process_distance(xywh, depth_image_matrix)
        direction_togo, walkable_7, dist_7 = Unity_obstacle_avoidance.get_direction_by_depth(raw_depth_image_matrix)
        if distance is not None:
            angle_float = float(angle_info.split(" ")[0])  # "10.8 right"
            direction = str(angle_info.split(" ")[1])
            if success_dist < distance <= close_distance:
                if angle_float <= min_angle_error * 1:
                    tools.play_by_direction(0, _listener, source300, feedback_mode=feedback_mode)
                    sen_msg("forward")
                    # tools.vis_oa_od(color_image, 3, distance, distance_min, raw_depth_image_matrix, xywh,
                    #                 txt_sp="close", _vis=vis)
                else:
                    if direction == "left":
                        tools.play_by_direction(-90, _listener, source1100, feedback_mode=feedback_mode)
                        sen_msg("left")
                        # tools.vis_oa_od(color_image, 2, distance, distance_min, raw_depth_image_matrix, xywh,
                        #                 txt_sp="close", _vis=vis)
                    elif direction == "right":
                        tools.play_by_direction(90, _listener, source1100, feedback_mode=feedback_mode)
                        sen_msg("right")
                        # tools.vis_oa_od(color_image, 4, distance, distance_min, raw_depth_image_matrix, xywh,
                        #                 txt_sp="close, no OA", _vis=vis)
                continue
            if distance <= success_dist:
                sen_msg("forward")
                time.sleep(0.3)
                sen_msg("stop")
                tools.speak_str("arrived")
                # tools.vis_oa_od(color_image, 3, distance, distance_min, raw_depth_image_matrix, xywh,
                #                 txt_sp="arrived!", _vis=vis)
                arrived = True
                continue
        if running_OA:
            if direction_togo == -1:
                print("no direction togo...")
                sen_msg("left_m")
            if direction_togo == 0:
                tools.play_by_direction(-90, _listener, source1100)
                sen_msg("left_m")
            if direction_togo == 1:
                tools.play_by_direction(-90, _listener, source1100)
                sen_msg("left")
            if direction_togo == 2:
                tools.play_by_direction(-90, _listener, source1100)
                sen_msg("left")
            if direction_togo == 3:
                tools.play_by_direction(0, _listener, source300)
                sen_msg("forward")
            if direction_togo == 4:
                tools.play_by_direction(90, _listener, source1100)
                sen_msg("right")
            if direction_togo == 5:
                tools.play_by_direction(90, _listener, source1100)
                sen_msg("right_m")
            if direction_togo == 6:
                tools.play_by_direction(90, _listener, source1100)
                sen_msg("right_m")
            if time.time() - start_OA_time > oa_time:
                running_OA = False
            # tools.vis_oa_od(color_image, direction_togo, distance, distance_min, raw_depth_image_matrix, xywh,
            #                 txt_sp="OA", _vis=vis)
            continue

        if direction_togo not in [2, 3, 4]:
            running_OA = True
            start_OA_time = time.time()
            continue
        else:
            if distance is None:
                tools.speak_str("searching")
                sen_msg("left_m")
                # tools.vis_oa_od(color_image, direction_togo, distance, distance_min, raw_depth_image_matrix, xywh,
                #                 txt_sp="Searching", _vis=vis)
                continue
            else:
                direction_togo, angle_float, direction = tools.OD_with_OA(angle_info, distance, direction_togo, walkable_7, dist_7)
                if direction_togo == -1:
                    print("no direction togo...")
                    sen_msg("left_m")
                if direction_togo == 0:
                    tools.play_by_direction(-90, _listener, source1100)
                    sen_msg("left_m")
                if direction_togo == 1:
                    tools.play_by_direction(-90, _listener, source1100)
                    sen_msg("left")
                if direction_togo == 2:
                    tools.play_by_direction(-90, _listener, source1100)
                    sen_msg("left")
                if direction_togo == 3:
                    tools.play_by_direction(0, _listener, source300)
                    sen_msg("forward")
                if direction_togo == 4:
                    tools.play_by_direction(90, _listener, source1100)
                    sen_msg("right")
                if direction_togo == 5:
                    tools.play_by_direction(90, _listener, source1100)
                    sen_msg("right")
                if direction_togo == 6:
                    tools.play_by_direction(90, _listener, source1100)
                    sen_msg("right_m")
                # tools.vis_oa_od(color_image, direction_togo, distance, distance_min, raw_depth_image_matrix, xywh,
                #                 txt_sp="", _vis=vis)
                continue


@app.route('/local_nav', methods=["POST"])
def func_name():
    r = request
    depth_frame_str = r.form["depth_frame"]
    depth_frame_ndarray = tools.upsample(depth_frame_str, 1920, 1080, 10, 10, 2.8)
    rgb_str = request.files['rgb'].read()
    context_1 = [depth_frame_ndarray, rgb_str]
    print("receiving and put to queue...")
    if qq.full():
        qq.get()
        qq.put(context_1)
    else:
        qq.put(context_1)
    response = {'message': 'data received'}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


class ConsumerThread(threading.Thread):
    def __init__(self, threadID, name, qq1):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.qq1 = qq1

    def run(self):
        reachingObj(self.qq1)


if __name__ == "__main__":
    thread11 = ConsumerThread(11, "thread_get_queue_cam", qq)
    thread11.start()
    print('=========================================================================')
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('=================================================================================')
    print('=========server start running at: ', now, '=========')
    print('=========IP + Port    =   ', ip, ':', port, '=========')
    print('=========================== ready to fly ========================================')
    server = pywsgi.WSGIServer((ip, int(port)), app)
    server.serve_forever()
