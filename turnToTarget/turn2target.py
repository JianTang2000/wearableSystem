import serial
import time
from openal import *
import statistics
import pandas as pd
from threading import Thread
from multiprocessing import Queue

from util import tools
from IMU import core

port = "COM3"  # windows
baudrate = 921600

min_angle_error = 5  # +- min_angle_error for "ahead"
audio_sleep = tools.audio_sleep_time
audio_mode = ["SP-cue", "verbal", "3D-cue"]

sourceWater = oalOpen("../materials/water2.wav")
_listener = oalGetListener()

IMU_data_Q = Queue(1)
global_start_recode = False


class ImuThread(Thread):
    def __init__(self, thread_name, value, file_name):
        super(ImuThread, self).__init__(name=thread_name)
        self.value = value
        self.file_name = file_name

    def run(self) -> None:
        try:
            print("...ImuThread start...please wait about 5 seconds...")
            _hf_imu = serial.Serial(port=port, baudrate=baudrate, timeout=0.5)
            if _hf_imu.isOpen():
                print("serial open success...")
            else:
                _hf_imu.open()
                print("serial open success...")
        except Exception as e:
            print("Exception:" + str(e))
            print("serial open fail")
            exit(0)
        else:
            # IMU check
            IMU_test(_hf_imu)

            # init stage
            init_list = []
            for i in range(100):
                _tmp_imu_data = core.get_one_data(_hf_imu)
                init_list.append(round(float(_tmp_imu_data[8]), 6))
                time.sleep(0.02)
            print("time-yaw results saving as : ", self.file_name)
            print("=========================================")
            print("current target angle is ", self.value)
            print("=========================================")

            init_mean = round(statistics.mean(init_list), 6)

            list_yaw = []
            list_time = []
            while True:
                _tmp_imu_data = core.get_one_data(_hf_imu)
                current_yaw = float(_tmp_imu_data[8])
                current_yaw = round(current_yaw - init_mean, 6)
                list_yaw.append(current_yaw)
                list_time.append(time.time())
                if IMU_data_Q.full():
                    IMU_data_Q.get()
                    IMU_data_Q.put(current_yaw)
                else:
                    IMU_data_Q.put(current_yaw)
                if not global_start_recode:
                    list_yaw = []
                    list_time = []
                else:
                    df = pd.DataFrame({"time_" + str(self.value): list_time, "yaw_" + str(self.value): list_yaw})
                    df.to_csv(os.path.join(r"data\turn2target", self.file_name))
                time.sleep(0.01)


def run_test(value=50, subject_name="XXX", audio_index=1):
    global global_start_recode
    input("Press Enter to continue... ")
    done_feedback = False
    while True:
        if not done_feedback:
            if IMU_data_Q.empty():
                print("Queue empty, do nothing...")
            else:
                current_yaw = IMU_data_Q.get()
                print(current_yaw)
                diff = current_yaw - value
                angle_abs = abs(round(diff, 6))
                global_start_recode = True
                status_done_feedback = audio_feedback(angle_abs, current_yaw, value, audio_index)
                done_feedback = status_done_feedback
        else:
            time.sleep(0.2)


def audio_feedback(angle_abs, current_yaw, value, audio_index=0):
    """
    audio_mode = [ "SP-cue","verbal","3D-cue"]
    """
    angle_abs = int(angle_abs)
    if audio_index == 0:
        if angle_abs <= min_angle_error:
            tools.play_by_direction(0, _listener, sourceWater, audio_sleep)
        else:
            if current_yaw > value:
                tools.play_by_direction(-25, _listener, sourceWater, audio_sleep)
            elif current_yaw < value:
                tools.play_by_direction(25, _listener, sourceWater, audio_sleep)
            else:
                raise ValueError
    elif audio_index == 1:
        if angle_abs <= min_angle_error:
            tools.speak_str("ahead", speed=450)
        else:
            if current_yaw > value:
                tools.speak_str("left " + str(int(angle_abs)), speed=450)
            elif current_yaw < value:
                tools.speak_str("right " + str(int(angle_abs)), speed=450)
            else:
                raise ValueError
    elif audio_index == 2:
        if angle_abs <= min_angle_error:
            tools.play_by_direction(0, _listener, sourceWater, audio_sleep)
        else:
            if current_yaw > value:
                tools.play_by_direction(0 - angle_abs, _listener, sourceWater, audio_sleep)
            elif current_yaw < value:
                tools.play_by_direction(angle_abs, _listener, sourceWater, audio_sleep)
            else:
                raise ValueError
    return False


def IMU_test(_hf_imu):
    print("please check IMU status")
    time.sleep(0.3)
    time.sleep(1)
    t1 = time.time()
    while time.time() - t1 < 3:
        _tmp_imu_data = core.get_one_data(_hf_imu)
        print(f"yaw is ---- {_tmp_imu_data[8]} -----", )
        time.sleep(0.2)


if __name__ == "__main__":
    # values = [60, 30, -60, -10, -30, 80, -70, 70, 90, -40, 50, -80, 20, -90, 10, -50, -20, 40]
    # values = [-50, 30, 90, 40, -80, -70, 20, 50, -30, -10, -40, -60, -20, 80, 60, -90, 70, 10]
    # values = [30, -30, 70, -50, -70, 40, -10, 10, -60, -20, -90, 80, -40, 20, 50, 90, 60, -80]
    # values = [-90, 50, -40, -30, -50, -20, -70, -80, 10, 80, -60, 60, 40, -10, 20, 70, 30, 90]
    # values = [40, -60, 90, 20, -90, -80, 50, -70, -40, 70, -50, 80, -10, -30, -20, 10, 30, 60]
    # values = [-30, 20, 60, 30, -20, 80, 70, -80, 90, 50, -60, 40, -70, -90, -50, -40, 10, -10]
    # values = [20, 70, 10, -90, -60, 40, -50, -80, -30, -70, -40, 80, 30, 90, 60, -10, -20, 50]
    # values = [60, 20, 30, -80, -30, -20, 40, 90, -10, -70, 10, -60, -90, 80, -50, -40, 70, 50]
    # values = [-10, 70, 80, -30, -90, 20, -80, 50, 40, -20, 10, 60, -60, -70, 90, 30, -50, -40]
    # values = [50, 10, 70, -80, 20, -10, -70, 90, -90, 60, 30, -40, -60, -50, 80, 40, -30, -20]
    # values = [50, -80, -50, 70, -30, -90, -60, -70, 40, 10, -10, -20, 20, 90, 80, 30, 60, -40]
    # values = [90, -50, -10, 80, -90, -20, -30, 60, -40, -80, -60, 10, 50, 40, 20, 30, -70, 70]
    # values = [80, 10, 70, -20, -90, 20, -80, 50, -10, -60, 40, 90, -30, -50, 30, 60, -70, -40]
    _value = 50
    _subject_name = "XX"
    # audio_mode = [ "SP-cue","verbal","3D-cue"]
    _audio_index = 0
    _file_name = _subject_name + "_" + str(audio_mode[_audio_index]) + "_" + str(_value) + ".csv"

    imu_thread = ImuThread("imu_thread", value=_value, file_name=_file_name)
    imu_thread.start()
    run_test(value=_value, subject_name=_subject_name, audio_index=_audio_index)
