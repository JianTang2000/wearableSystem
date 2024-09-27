"""
upload this demo code to the robot and run.
"""

from openal import *

sys.path.append(r"../../..")
sys.path.append(r"../..")
sys.path.append(r"..")
import cv2
import numpy as np
from datetime import datetime
import hiwonder.ActionGroupControl as AGC
from util.RGBD import alignedRGBD640
from object_detection import detect_target_obj, post_process_angle, post_process_distance, detection_classes
from obstacle_avoidance import get_direction_by_depth


def get_formatted_timestamp():
    # Get the current time and format it as 'month_day_hour_min_sec_millisecond'
    now = datetime.now()
    return now.strftime("%m_%d_%H_%M_%S_%f")[:-3]


def reaching_with_OA(target=47, success_dist=0.5, min_angle_error=8):
    # Initialize storage for images and timestamps
    image_data = []

    print("start doing to reaching object (apple) demo...")
    print("warm-up .. ")
    for i in range(3):
        _, _, _ = alignedRGBD640.get_RGBD_align()
    color_image, depth_colormap, depth_image_npy = alignedRGBD640.get_RGBD_align()
    color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)  # to  RGB
    xywh = detect_target_obj(color_image, classes=target)
    if xywh is not None:
        angle = post_process_angle(xywh[0])
        distance, invalid_p = post_process_distance(depth_image_npy, xywh[0])
        print(f"==== angle (degree left/right) : {angle}")
        print(f"==== distance (meter) : {distance}")
        # print(f"invalid depth area in the box (0~1) : {invalid_p}")
    else:
        print(f'==== no {detection_classes.get(target)} detected!')
    direction_togo, W7, dist_7 = get_direction_by_depth(depth_image_npy, global_thrd=0.3, ground_interval=0.03)
    print("========= OA result : ", direction_togo)
    print("========= OA 7 walkable : ", W7)
    print("========= OA 7 distance (meter) : ", dist_7)
    print("warm-up finished. ")

    print('===========  demo start  ==============')

    while True:
        color_image, depth_colormap, depth_image_npy = alignedRGBD640.get_RGBD_align()
        image_data.append((get_formatted_timestamp(), color_image, depth_image_npy))  # Store timestamp, RGB, and depth
        color_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2RGB)  # to  RGB
        xywh = detect_target_obj(color_image, classes=target)
        if xywh is None:
            print("==== no detection! search from right side")
            AGC.runActionGroup('turn_right', times=2, with_stand=True)
            continue
        else:
            angle = post_process_angle(xywh[0])
            distance, invalid_p = post_process_distance(depth_image_npy, xywh[0])
            print(f"==== angle (degree left/right) : {angle}")
            print(f"==== distance (meter) : {distance}")
            # print(f"invalid depth area in the box (0~1) : {invalid_p}")
            angle_float = float(angle.split(" ")[0])  # "10.8 right"
            direction = str(angle.split(" ")[1])

            # check OA
            direction_togo, W7, dist_7 = get_direction_by_depth(depth_image_npy, global_thrd=0.3, ground_interval=0.03)
            print("========= OA result is ", direction_togo)
            if distance >= success_dist:  # 距离较远
                if direction_togo != 3 and distance < 1:
                    print("obstacle detected, doing OA on the right side")
                    # AGC.runActionGroup('go_forward', times=5, with_stand=True)
                    AGC.runActionGroup('turn_right', times=4, with_stand=True)
                    AGC.runActionGroup('go_forward', times=4, with_stand=False)
                    AGC.runActionGroup('turn_left', times=4, with_stand=True)
                    AGC.runActionGroup('go_forward', times=4, with_stand=False)
                    continue
                if angle_float <= min_angle_error:
                    AGC.runActionGroup('go_forward', times=2, with_stand=False)
                else:
                    if angle_float <= 15:
                        if direction == "left":
                            AGC.runActionGroup('turn_left', times=1, with_stand=True)
                        elif direction == "right":
                            AGC.runActionGroup('turn_right', times=1, with_stand=True)
                        else:
                            raise ValueError
                    else:
                        if direction == "left":
                            AGC.runActionGroup('turn_left', times=2, with_stand=True)
                        elif direction == "right":
                            AGC.runActionGroup('turn_right', times=2, with_stand=True)
                        else:
                            raise ValueError
            else:
                if angle_float <= min_angle_error:
                    print("========= object reached! =========")
                    AGC.runActionGroup('go_forward', times=5, with_stand=True)  # 再往前几步，然后站立，然后挥手致意
                    AGC.runActionGroup('04_pickup_apple', times=1)
                    # AGC.runActionGroup('stand')
                    # return
                    break
                else:
                    if angle_float <= 15:
                        if direction == "left":
                            AGC.runActionGroup('turn_left', times=1, with_stand=True)
                        elif direction == "right":
                            AGC.runActionGroup('turn_right', times=1, with_stand=True)
                        else:
                            raise ValueError
                    else:
                        if direction == "left":
                            AGC.runActionGroup('turn_left', times=2, with_stand=True)
                        elif direction == "right":
                            AGC.runActionGroup('turn_right', times=2, with_stand=True)
                        else:
                            raise ValueError
            print("-------------------------------------------------")

    # Save captured data
    if len(image_data) > 0:
        save_path = "captured_data"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        for timestamp_ms, color_img, depth_img in image_data:
            rgb_filename = os.path.join(save_path, f"{timestamp_ms}_rgb.jpg")
            depth_filename = os.path.join(save_path, f"{timestamp_ms}_depth.npy")
            cv2.imwrite(rgb_filename, color_img)
            np.save(depth_filename, depth_img)
        print(f"========= {len(image_data)} images saved in {save_path} =========")


if __name__ == "__main__":
    reaching_with_OA()
