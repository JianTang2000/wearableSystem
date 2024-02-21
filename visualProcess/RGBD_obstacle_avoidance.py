# -*- encoding: utf-8 -*-
import numpy as np
from util import tools

distance_min = 0.12


def get_direction_by_depth(depth_matrix):
    walkable_7, dist_7, dist_diff_7 = check_block_walkable(depth_matrix)
    direction_togo = get_direction(walkable_7, dist_7, dist_diff_7)
    return direction_togo, walkable_7, dist_7


def check_block_walkable(depth_matrix):
    walkable_7 = [None for i in range(7)]
    dist_7 = [None for i in range(7)]
    dist_diff_7 = [None for i in range(7)]
    # raw = [1.56 for i in range(7)]
    raw = [2.5 for i in range(7)]
    block_distance_predefine = [i for i in raw]
    diff_thrd = 0.05
    current_x_start = 20
    end_ = 10
    w_gap = 5
    w = int((640 - w_gap * 8 - current_x_start - end_) / 7)
    h = 10 * 2
    y = 345
    for i in range(7):
        current_x_start += w_gap
        x_min = int(current_x_start)
        x_max = int(x_min + w)
        current_x_start = x_max
        y_min = int(y - 1 / 2 * h)
        y_max = int(y + 1 / 2 * h)
        object_box = depth_matrix[y_min:y_max, x_min:x_max].astype(float)
        no_depth_area = round(np.count_nonzero(object_box < distance_min) / object_box.size, 4)
        close_area = round(np.count_nonzero(object_box < block_distance_predefine[i]) / object_box.size - no_depth_area, 4)
        distance = tools.compute_mean_min(object_box)
        dist_7[i] = distance
        dist_diff_7[i] = round(abs(distance - block_distance_predefine[i]) / block_distance_predefine[i], 6)
        if (abs(distance - block_distance_predefine[i]) <= diff_thrd or distance - block_distance_predefine[i] >= diff_thrd) \
                and no_depth_area < 0.3 and close_area < 0.5:
            walkable_7[i] = True
        else:
            walkable_7[i] = False
    return walkable_7, dist_7, dist_diff_7


def get_direction(walkable_7, dist_7, dist_diff_7):
    good_blocks = [False for i in range(7)]
    for i in range(7):
        if i != 0 and i != 6:
            if walkable_7[i] and walkable_7[i + 1] and walkable_7[i - 1]:
                good_blocks[i] = True
    best_blocks = [False for i in range(7)]
    for i in range(7):
        if 1 < i < 5:
            if walkable_7[i] and walkable_7[i + 1] and walkable_7[i - 1] and walkable_7[i + 2] and walkable_7[i - 2]:
                best_blocks[i] = True
    if walkable_7[3] and walkable_7[4] and walkable_7[2]:
        return 3
    if best_blocks.__contains__(True):
        if best_blocks[3]:
            return 3
        if best_blocks[4]:
            return 4
        if best_blocks[2]:
            return 2
    if good_blocks.__contains__(True):
        if good_blocks[3]:
            return 3
        if good_blocks[4]:
            return 4
        if good_blocks[2]:
            return 2
        if good_blocks[5]:
            return 5
        if good_blocks[1]:
            return 1
    if walkable_7[3]:
        return 3
    if walkable_7[4]:
        return 4
    if walkable_7[2]:
        return 2
    if walkable_7[5]:
        return 5
    if walkable_7[1]:
        return 1
    if walkable_7[6]:
        return 6
    if walkable_7[0]:
        return 0
    return -1


if __name__ == "__main__":
    print("===")
