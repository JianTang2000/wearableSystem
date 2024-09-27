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

from vision import object_detection, obstacle_avoidance
import captureUnityData
from util import tools

# ################################################
ip = str("127.0.0.1")
port = str(8311)
distance_min = 0.12  # min depth value in meter
Vis = True
play_Sound = True  #
rectangle_color = (0, 0, 0)  #
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
    close_distance = 3.5
    current_target_index = 0
    landmarks = [60, 56]
    landmark_dist_threshold = [2.5, 2]  # distance in meter
    landmark_names = ["table", "chair"]
    landmark_desc = ["table on AXX. turn to the opposite direction",
                     "chair ahead, success and stop"]
    running_OA = False
    start_OA_time = -1
    oa_time = 3
    while True:
        try:
            if not qq1.empty():
                # get data
                context_1 = qq1.get()
                depth_frame_ndarray = context_1[0]
                rgb_str = context_1[1]
                np_img = np.fromstring(rgb_str, np.uint8)
                cv2_rgb = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                _color_image = cv2_rgb
                _depth_image_matrix = depth_frame_ndarray  # 640*360 in meter
                _depth_colormap = depth_frame_ndarray

                # run algorithms
                angle_info, distance, no_depth_area = None, None, None
                direction_togo, walkable_7, dist_7 = obstacle_avoidance.get_direction_by_depth(_depth_image_matrix)
                xywh = object_detection.detect_target_obj(cv2_rgb, classes=landmarks[current_target_index], show=False)
                if xywh is not None:
                    angle_info = object_detection.post_process_angle(xywh[0])
                    distance, no_depth_area = object_detection.post_process_distance(_depth_image_matrix, xywh[0])
                    # print(f"angle (degree left/right) : {angle}")
                    # print(f"distance (meter) : {distance}")
                    # print(f"invalid depth area in the box (0~1) : {invalid_p}")
                else:
                    print(f' no {object_detection.detection_classes.get(landmarks[current_target_index])} detected ')
                if Vis:
                    pass  # visualization not provided

                # feedbacks
                if distance is not None:
                    angle_float = float(angle_info.split(" ")[0])  # e.g.  "10.8 right" "10.8 left"
                    direction = str(angle_info.split(" ")[1])
                    if landmark_dist_threshold[current_target_index] < distance <= close_distance:
                        angle_err_accept = 10 if current_target_index == 0 else 5
                        if angle_float <= angle_err_accept:
                            tools.play_by_direction(0, _listener, source_700, sleep_time=0.2)  # slow the frequency coz VIP requires so
                        else:
                            if direction == "left":
                                tools.play_by_direction(-90, _listener, source_water, sleep_time=0.1)  # slow and differ the frequency coz VIP requires so
                            elif direction == "right":
                                tools.play_by_direction(90, _listener, source_water, sleep_time=0.1)
                        continue
                    if distance <= landmark_dist_threshold[current_target_index]:
                        if current_target_index == 0:
                            tools.speak_str(landmark_desc[current_target_index].replace("AXX", direction))
                            time.sleep(0.1)
                            tools.speak_str(landmark_desc[current_target_index].replace("AXX", direction))
                            time.sleep(0.1)
                            tools.speak_str(landmark_desc[current_target_index].replace("AXX", direction))
                        else:
                            tools.speak_str(landmark_desc[current_target_index])
                            time.sleep(0.1)
                            tools.speak_str(landmark_desc[current_target_index])
                            time.sleep(0.1)
                            tools.speak_str(landmark_desc[current_target_index])
                            print(f"--success reach {landmark_names[current_target_index]}--")
                        if current_target_index != len(landmarks) - 1:
                            current_target_index += 1
                        continue

                if running_OA:
                    tools.play_by_7_blocks_direction(_listener, direction_togo, source_water, source_water, source_water)
                    print(f"== obstacle avoidance ==")
                    if time.time() - start_OA_time > oa_time:
                        running_OA = False
                    continue

                if direction_togo not in [2, 3, 4]:
                    running_OA = True
                    start_OA_time = time.time()
                    tools.play_by_7_blocks_direction(_listener, direction_togo, source_water, source_water, source_water)
                    continue
                else:
                    if distance is None:
                        tools.play_by_7_blocks_direction(_listener, direction_togo, source_water, source_water, source_water)
                        continue
                    else:
                        direction_togo, angle_float, direction = tools.OD_with_OA(angle_info, distance, direction_togo, walkable_7, dist_7)
                        tools.play_by_7_blocks_direction(_listener, direction_togo, source_water, source_water, source_water)
                        continue
        except RuntimeError:
            print(f" .. RuntimeError ..")
            pass


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
