import math
import time
import platform
import numpy as np
from openal import *
import pyttsx3

np.random.seed(123)

if platform.system() == "Windows":
    audio_sleep_time = 0.1  # windows CPU speed is fast so slow down the audio feedback to avoid high perceived load
else:
    audio_sleep_time = 0  #


def speak_str(context_str, speed=170, lang="en"):
    voice_engine = pyttsx3.init()
    voice_engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')  # en zh
    voice_engine.setProperty('rate', speed)
    voice_engine.say(context_str)
    voice_engine.runAndWait()


def compute_mean_min(array_in, min_v=0.12, N=4):
    if array_in.size == 0:
        return None
    filtered_values = array_in[array_in > min_v]
    if filtered_values.size == 0:
        return None
    mean_value = np.mean(filtered_values)
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


def vis_Unity_OA(direction_togo, distance_min, raw_depth_colormap, raw_depth_image_matrix, walkable_7=None, target_dist=None):
    pass


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


if __name__ == "__main__":
    print("==========================================")
    print("==========================================")
