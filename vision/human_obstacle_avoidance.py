from openal import *
from vision import obstacle_avoidance
from util.RGBD import alignedRGBD640
from util import tools

source_700 = oalOpen("../../../materials/700.wav")
source_water = oalOpen("../../../materials/water.wav")
_listener = oalGetListener()


def run():
    while True:
        color_image, raw_depth_colormap, raw_depth_image_matrix = alignedRGBD640.get_RGBD_raw()
        direction_togo, walkable_7, dist_7 = obstacle_avoidance.get_direction_by_depth(raw_depth_image_matrix)
        if direction_togo == -1:
            tools.speak_str("do walkable direction found.")
        tools.play_by_7_blocks_direction(_listener, direction_togo, source_water, source_water, source_water)
        print("============")


if __name__ == "__main__":
    run()
