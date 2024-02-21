# -*- encoding: utf-8 -*-
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
    block_distance_predefine = [2.53, 2.27, 2.11, 2.04, 2.09, 2.25, 2.5]  # when fov=-86.9 pitch=20 depth_factor=10  height=1.7m -- HMI training
    y = 345
    diff_thrd = 0.1
    w_gap = 5
    w = int((640 - w_gap * 8) / 7)
    h = 10 * 2
    current_x_start = 0
    for i in range(7):
        current_x_start += w_gap
        x_min = int(current_x_start)
        x_max = int(x_min + w)
        current_x_start = x_max
        y_min = int(y - 1 / 2 * h)
        y_max = int(y + 1 / 2 * h)
        object_box = depth_matrix[y_min:y_max, x_min:x_max].astype(float)
        distance = tools.compute_mean_min(object_box)
        dist_7[i] = distance
        dist_diff_7[i] = round(abs(distance - block_distance_predefine[i]) / block_distance_predefine[i], 6)
        if abs(distance - block_distance_predefine[i]) <= diff_thrd:
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

    if walkable_7[2] & walkable_7[3] & walkable_7[4]:
        return 3
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
    index = None
    dist_max = -1
    for i in range(7):
        if dist_7[i] > dist_max:
            index = i
            dist_max = dist_7[i]
    print(" no direction to go, go to max depth block.. ")
    return index


if __name__ == "__main__":
    print("==")
