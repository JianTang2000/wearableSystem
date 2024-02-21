import math
import time
import cv2
import platform
import numpy as np
from openal import *
import pyttsx3

np.random.seed(123)


def random_true(prob):
    p = ([prob, 1 - prob])
    return np.random.choice([True, False], p=p)


def compute_mean(array_in, N=4):
    exist = (array_in != 0)
    mean_value = array_in.sum() / exist.sum()
    return round(mean_value, N)


def compute_mean_min(array_in, min_v=0.12, N=4):
    exist = (array_in >= min_v)
    _a = array_in[exist].sum()
    _b = exist.sum()
    mean_value = _a / _b
    return round(mean_value, N)


def pi_format(degree: float):
    return math.radians(degree)


def get_obj_direction_index(angle_float, direction):
    angle_float = angle_float if direction == "right" else 0 - angle_float
    if angle_float < -25:
        direction_object_index = 0
    elif angle_float < -15:
        direction_object_index = 1
    elif angle_float < -5:
        direction_object_index = 2
    elif angle_float < 5:
        direction_object_index = 3
    elif angle_float < 15:
        direction_object_index = 4
    elif angle_float < 25:
        direction_object_index = 5
    else:
        direction_object_index = 6
    return direction_object_index


def OD_with_OA(angle_info, distance, direction_togo, walkable_7, dist_7):
    if distance is None:
        print("========= no detection")
        return direction_togo, None, None
    angle_float = float(angle_info.split(" ")[0])  # "10.8 right" "10.8 left"
    direction = str(angle_info.split(" ")[1])
    direction_object_index = get_obj_direction_index(angle_float, direction)
    if abs(direction_object_index - direction_togo) <= 1:
        return direction_togo, angle_float, direction
    if walkable_7[direction_object_index]:
        return direction_object_index, angle_float, direction
    else:
        return direction_togo, angle_float, direction


def vis_oa_od(color_image, direction_togo, distance, distance_min, raw_depth_image_matrix, xywh, txt_sp="",
              _vis=False, class_name=None):
    pass


def vis_OA(direction_togo, distance_min, raw_depth_colormap, raw_depth_image_matrix):
    pass


def vis_Unity_OA(direction_togo, distance_min, raw_depth_colormap, raw_depth_image_matrix, walkable_7=None, target_dist=None):
    pass


if platform.system() == "Windows":
    audio_sleep_time = 0.1  # windows CPU speed is fast so slow down the audio feedback to keep the same output frequency
else:
    audio_sleep_time = 0  #


def play_by_direction(lr_direction, listener, source1, sleep_time=0.25, feedback_mode=0, angle=5):
    if feedback_mode == 1:
        if lr_direction == 0:
            speak_str("ahead")
        if lr_direction < 0:
            speak_str("left " + str(int(angle)))
        else:
            speak_str("right " + str(int(angle)))
        return
    _el = 0
    _distance = 1
    _az = - lr_direction  # In pyopenal, x is negative on the right, and xyz2AZEL is negative on the left, so switch the symbol #_az>0 to the left
    # play by pyOpenAL
    openal_z = _distance * math.cos(pi_format(_el)) * math.cos(pi_format(_az))
    openal_y = _distance * math.sin(pi_format(_el))
    openal_x = _distance * math.cos(pi_format(_el)) * math.sin(pi_format(_az))
    listener.move_to((openal_x, openal_y, openal_z))
    source1.play()
    while source1.get_state() == AL_PLAYING:
        if sleep_time == 0:
            pass
        else:
            time.sleep(sleep_time)


def play_by_7_blocks_direction(_listener, direction_togo, source1100, source300, source700,
                               feedback_mode=0):
    if feedback_mode == 1:
        if direction_togo == -1:
            print("no direction togo...")
        if direction_togo == 0:
            speak_str("left")
        if direction_togo == 1:
            speak_str("left")
        if direction_togo == 2:
            speak_str("left")
        if direction_togo == 3:
            speak_str("ahead")
        if direction_togo == 4:
            speak_str("right")
        if direction_togo == 5:
            speak_str("right")
        if direction_togo == 6:
            speak_str("right")
        return

    if direction_togo == -1:
        print("no direction togo...")
    if direction_togo == 0:
        play_by_direction(-90, _listener, source1100, sleep_time=audio_sleep_time)
    if direction_togo == 1:
        play_by_direction(-90, _listener, source700, sleep_time=audio_sleep_time)
    if direction_togo == 2:
        play_by_direction(-90, _listener, source700, sleep_time=audio_sleep_time)
    if direction_togo == 3:
        play_by_direction(0, _listener, source300, sleep_time=audio_sleep_time)
    if direction_togo == 4:
        play_by_direction(90, _listener, source700, sleep_time=audio_sleep_time)
    if direction_togo == 5:
        play_by_direction(90, _listener, source700, sleep_time=audio_sleep_time)
    if direction_togo == 6:
        play_by_direction(90, _listener, source1100, sleep_time=audio_sleep_time)


def speak_str(context_str, speed=170, lang="en"):
    voice_engine = pyttsx3.init()
    voice_engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')  # en zh
    voice_engine.setProperty('rate', speed)
    voice_engine.say(context_str)
    voice_engine.runAndWait()


def post_process_angle(results, obj_id=0, img_w=640, calibration=False):
    xywh = [None for i in range(5)]
    found = False
    ret_tensor = results.xywh
    ret_numpy = ret_tensor[0].numpy()
    best_conf = 0
    for pred in ret_numpy:
        conf = float(pred[4])
        class_id = int(pred[5])
        if class_id == int(obj_id) and conf > best_conf:
            xywh[0] = pred[0]
            xywh[1] = pred[1]
            xywh[2] = pred[2]
            xywh[3] = pred[3]
            xywh[4] = conf
            found = True
            best_conf = conf
    if not found:
        return None, None
    w_max = img_w
    h_max = 360 if img_w == 640 else 1080
    az_max = 69.46  # 70
    el_max = 42.63  # 42
    x = (w_max / 2 - xywh[0]) / w_max
    y = (h_max / 2 - xywh[1]) / h_max
    az = round(-az_max * 1 / 2 * 2 * x, 2)
    el = round(el_max * 1 / 2 * 2 * y, 2)
    part_2 = " "
    angle_value = abs(az)
    if calibration:
        pass
    part_3 = str(angle_value)
    part_1 = "left" if az <= 0 else "right"
    ret = part_3 + part_2 + part_1
    return ret, xywh  # "10.8 right"


def post_process_angle_unity(results, obj_id=0, img_w=1280, calibration=False):
    xywh = [None for i in range(5)]
    found = False
    ret_tensor = results.xywh
    ret_numpy = ret_tensor[0].numpy()
    best_conf = 0
    for pred in ret_numpy:
        conf = float(pred[4])
        class_id = int(pred[5])
        if class_id == int(obj_id) and conf > best_conf:
            xywh[0] = pred[0]
            xywh[1] = pred[1]
            xywh[2] = pred[2]
            xywh[3] = pred[3]
            xywh[4] = conf
            found = True
            best_conf = conf
    if not found:
        return None, None
    w_max = img_w
    h_max = 720
    az_max = 86
    el_max = 57.8
    x = (w_max / 2 - xywh[0]) / w_max
    y = (h_max / 2 - xywh[1]) / h_max
    az = round(-az_max * 1 / 2 * 2 * x, 2)
    el = round(el_max * 1 / 2 * 2 * y, 2)
    part_2 = " "
    angle_value = abs(az)
    if calibration:
        pass
    part_3 = str(angle_value)
    part_1 = "left" if az <= 0 else "right"
    ret = part_3 + part_2 + part_1
    return ret, xywh  # "10.8 right"


def post_process_distance(xywh, depth_matrix, distance_min=0.12, box_w=5):
    if xywh is not None:
        x = int(xywh[0])
        y = int(xywh[1])
        object_box = depth_matrix[y - box_w:y + box_w, x - box_w:x + box_w].astype(float)
        no_depth_area = round(np.count_nonzero(object_box < distance_min) / object_box.size, 2)
        distance = compute_mean_min(object_box)
        return distance, no_depth_area
    else:
        return None, None


def post_process_distance_unity(xywh, depth_matrix, distance_min=0.12, box_w=5):
    if xywh is not None:
        x = int(xywh[0] * 0.5)
        y = int(xywh[1] * 0.5)
        object_box = depth_matrix[y - box_w:y + box_w, x - box_w:x + box_w].astype(float)
        no_depth_area = round(np.count_nonzero(object_box < distance_min) / object_box.size, 2)
        distance = compute_mean_min(object_box)
        return distance, no_depth_area
    else:
        return None, None


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


if __name__ == "__main__":
    print("==========================================")
    print("==========================================")
