import cv2
from openal import *
from openal.al import *
import torch
import platform
import time

sys.path.append(r"../..")
sys.path.append(r"..")

from rgbdSensor import alignedRGBD640
from visualProcess import RGBD_obstacle_avoidance
from util import tools


def maze_run():
    source300 = oalOpen("../materials/300.wav")
    source1100 = oalOpen("../materials/1100.wav")
    _listener = oalGetListener()
    if platform.system() == "Windows":
        print("==================> Running on Windows")
        model = torch.hub.load(r'path2yolov5', 'custom',
                               path=r'../materials/weights/best.onnx',
                               source='local',
                               force_reload=True,
                               device='cpu')
    else:
        print("==================> Running on Pi")
        model = torch.hub.load('/home/pi/yolov5', 'custom',
                               path=r'../materials/weights/best.onnx',
                               source='local',
                               force_reload=True,
                               device='cpu')
    direction_all = ["left", "right"]
    model.conf = 0.4
    min_angle_error = 5
    distance_min = 0.12
    current_target_index = 0
    close_distance = 1
    landmarks = [60, 56]
    landmark_dist_threshold = [2, 2]  # distance in m
    landmark_names = ["table", "chair"]
    landmark_desc = ["table", "chair"]
    running_OA = False
    start_OA_time = -1
    oa_time = 5
    while True:
        color_image, depth_colormap, depth_image_matrix, raw_depth_colormap, raw_depth_image_matrix = alignedRGBD640.get_RGBD()
        _color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)
        results = model(_color_image, size=512)
        angle_info, xywh = tools.post_process_angle(results, obj_id=landmarks[current_target_index])
        distance, no_depth_area = tools.post_process_distance(xywh, depth_image_matrix)
        direction_togo, walkable_7, dist_7 = RGBD_obstacle_avoidance.get_direction_by_depth(raw_depth_image_matrix)
        if distance is not None:
            angle_float = float(angle_info.split(" ")[0])
            direction = str(angle_info.split(" ")[1])
            if landmark_dist_threshold[current_target_index] < distance <= close_distance:
                if angle_float <= min_angle_error * 1:
                    tools.play_by_direction(0, _listener, source300, sleep_time=0.3)
                else:
                    if direction == "left":
                        tools.play_by_direction(-90, _listener, source1100, sleep_time=0.15)
                    elif direction == "right":
                        tools.play_by_direction(90, _listener, source1100, sleep_time=0.15)
                continue
            if distance <= landmark_dist_threshold[current_target_index]:
                tools.speak_str(landmark_desc[current_target_index] + f" on the {direction}, go {direction_all[1] if direction_all[0] == direction else direction_all[0]}")
                if current_target_index != len(landmarks) - 1:
                    current_target_index += 1
                continue
        if running_OA:
            tools.play_by_7_blocks_direction(_listener, direction_togo, source1100, source300, source1100)
            if time.time() - start_OA_time > oa_time:
                running_OA = False
            continue
        if direction_togo not in [2, 3, 4]:
            running_OA = True
            start_OA_time = time.time()
            tools.play_by_7_blocks_direction(_listener, direction_togo, source1100, source300, source1100)
            continue
        else:
            tools.play_by_7_blocks_direction(_listener, direction_togo, source1100, source300, source1100)
            continue


if __name__ == "__main__":
    maze_run()
