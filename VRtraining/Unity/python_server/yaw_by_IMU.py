# -*- encoding: utf-8 -*-

import serial
from threading import Thread
from statistics import mean
import time
from openal import *

sys.path.append(r"../..")
sys.path.append(r"..")

from util import UdpComms as U, IMU as imu

# ################################################
_IP = "192.168.137.1"
IMU_port = "/dev/ttyUSB0"

# _IP = "127.0.0.1"
# IMU_port = "COM7"  # windows

sock = U.UdpComms(udpIP=_IP, portTX=8000, portRX=8001, enableRX=True, suppressWarnings=True)  # 发送到Unity, IP写Unity 所在主机IP
IMU_baudrate = 921600


# ###############################################################


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

                if time.time() - t1 < 1:
                    continue
                if time.time() - t1 < 2:
                    yaw_init_list.append(yaw)
                    continue
                else:
                    if not self.init_yaw:
                        self.yaw_start_value = mean(yaw_init_list)
                        self.init_yaw = True
                        continue
                    else:
                        print("==================================================")
                        spin_msg = "yaw_" + str(round(yaw - self.yaw_start_value, 2))
                        sen_msg(spin_msg)
                        time.sleep(0.05)  # slow down


if __name__ == "__main__":
    print("server IP is :", _IP)
    imu_thread = ImuThread("imu_thread")
    imu_thread.setDaemon(True)
    imu_thread.start()
    while True:
        time.sleep(100)
