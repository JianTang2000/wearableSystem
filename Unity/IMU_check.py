# -*- encoding: utf-8 -*-

import serial
from threading import Thread
import time
from openal import *

sys.path.append(r"../..")
sys.path.append(r"..")

from util import UdpComms as U
import IMU.core as imu

sock = U.UdpComms(udpIP="127.0.0.1", portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)  # 发送到Unity, IP写Unity 所在主机IP
IMU_port = "COM7"  # windows
# IMU_port = "/dev/ttyUSB0" # in raspberryPi
IMU_baudrate = 921600


def sen_msg(msg):
    print(f"sending msg {msg}......")
    sock.SendData(str(msg))


class ImuThread(Thread):
    def __init__(self, thread_name):
        super(ImuThread, self).__init__(name=thread_name)
        self.previous_yaw = None
        self.init_yaw = False
        self.yaw_start_value = None

    def run(self) -> None:
        print("IMU start...")
        port = IMU_port
        baudrate = IMU_baudrate
        try:
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
            print("waiting for init...")
            yaw_init_list = []
            t1 = time.time()
            while True:
                _tmp_imu_data = imu.get_one_data(_hf_imu)
                yaw = round(float(_tmp_imu_data[8]), 4)
                print(yaw)
                time.sleep(0.2)


if __name__ == "__main__":
    imu_thread = ImuThread("imu_thread")
    imu_thread.setDaemon(True)
    imu_thread.start()
    while True:
        time.sleep(100)
