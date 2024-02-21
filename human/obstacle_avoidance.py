# -*- encoding: utf-8 -*-
import time
from openal import *
from openal.al import *
import platform

sys.path.append(r"../..")
sys.path.append(r"..")

from util import tools
from rgbdSensor import alignedRGBD640
from visualProcess import RGBD_obstacle_avoidance


def run_obstacle_avoidance():
    source300 = oalOpen("../materials/300.wav")
    source1100 = oalOpen("../materials/water2.wav")
    _listener = oalGetListener()
    if platform.system() == "Windows":
        print("==================> Running on Windows")
    else:
        print("==================> Running on Pi")
    while True:
        color_image, depth_colormap, depth_image_matrix, raw_depth_colormap, raw_depth_image_matrix = alignedRGBD640.get_RGBD()
        direction_togo, walkable_7, dist_7 = RGBD_obstacle_avoidance.get_direction_by_depth(raw_depth_image_matrix)
        tools.play_by_7_blocks_direction(_listener, direction_togo, source1100, source300, source1100, feedback_mode=0)


if __name__ == '__main__':
    print('=========================================================================')
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print('=================================================================================')
    print('========= start running at: ', now, '=========')
    run_obstacle_avoidance()
