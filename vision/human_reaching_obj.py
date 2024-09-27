import time
from openal import *
from vision import obstacle_avoidance, object_detection
from util.RGBD import alignedRGBD640
from util import tools

source_700 = oalOpen("../../../materials/700.wav")
source_water = oalOpen("../../../materials/water.wav")
_listener = oalGetListener()


def run():
    Vis = False
    close_distance = 3.5
    current_target_index = 0
    landmarks = [56]
    landmark_dist_threshold = [2]  # distance in meter
    landmark_names = ["chair"]
    landmark_desc = ["chair ahead, success and stop"]
    running_OA = False
    start_OA_time = -1
    oa_time = 3
    while True:
        color_image, depth_colormap, depth_image_matrix = alignedRGBD640.get_RGBD_align()

        direction_togo, walkable_7, dist_7 = obstacle_avoidance.get_direction_by_depth(depth_image_matrix)
        xywh = object_detection.detect_target_obj(color_image, classes=landmarks[current_target_index], show=False)
        angle_info, distance, no_depth_area = None, None, None
        if xywh is not None:
            angle_info = object_detection.post_process_angle(xywh[0])
            distance, no_depth_area = object_detection.post_process_distance(depth_image_matrix, xywh[0])
        else:
            print(f' no {object_detection.detection_classes.get(landmarks[current_target_index])} detected ')
        if Vis:
            pass  # visualization not provided

        if distance is not None:
            angle_float = float(angle_info.split(" ")[0])  # e.g.  "10.8 right" "10.8 left"
            direction = str(angle_info.split(" ")[1])
            if landmark_dist_threshold[current_target_index] < distance <= close_distance:
                angle_err_accept = 5
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

    if direction_togo == -1:
        tools.speak_str("do walkable direction found.")
    tools.play_by_7_blocks_direction(_listener, direction_togo, source_water, source_water, source_water)
    print("============")


if __name__ == "__main__":
    run()
