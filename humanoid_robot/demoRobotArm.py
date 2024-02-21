#!/usr/bin/python

# custom usage of the humanoid robot and VL53L0 sensor

import time
import VL53L0X
import hiwonder.ActionGroupControl as AGC

tof = VL53L0X.VL53L0X(i2c_bus=1, i2c_address=0x29)
tof.open()
tof.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BETTER)

AGC.runActionGroup('01_init', times=1)
distance = tof.get_distance()  # in mm
if distance <= 160:
    tof.stop_ranging()
    tof.close()
else:
    AGC.runActionGroup('02_fast', times=1)
    distance = tof.get_distance()
    if distance <= 160:
        AGC.runActionGroup('03_slow_4', times=1)
    else:
        AGC.runActionGroup('03_fast', times=1)
    tof.stop_ranging()
    tof.close()
