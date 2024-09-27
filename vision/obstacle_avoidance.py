import numpy as np
import os
import cv2
import copy

from util.tools import compute_mean_min

depth_scale = 0.0010000000474974513
dist_min = 0.12
height, width = 640, 360
lane_num = 7
rect_w = 80
bottom_start = 1
rect_gap = 5
rect_h = int((height - (lane_num + 1) * rect_gap) / lane_num)
row_max, row_min = width - bottom_start, width - (bottom_start + rect_w)
col_start_list = []
current_col_p = 2
for m in range(lane_num):
    current_col_p += rect_gap
    col_start_list.append(current_col_p)
    current_col_p += rect_h


def get_direction_by_depth(depth_image_npy, global_thrd=1.5, ground_interval=0.18):
    output_image, _ = segment_ground_from_depth(depth_image_npy, ground_interval=ground_interval)
    w7_planes = lane_selection_planes(output_image)
    w7_dist, dist_7 = lane_selection_depth(depth_image_npy, global_thrd=global_thrd)
    W7 = [a and b for a, b in zip(w7_planes, w7_dist)]
    direction_togo = get_direction(W7)
    return direction_togo, W7, dist_7


def lane_selection_depth(depth_matrix2, global_thrd=1.5):
    walkable_7 = [False for i in range(lane_num)]
    dist_7 = [0 for i in range(lane_num)]
    for i in range(lane_num):
        value_rect = depth_matrix2[0:row_max, col_start_list[i]:col_start_list[i] + rect_h].astype(float)
        # percent_below_threshold = np.mean(dist_min < value_rect < global_thrd)
        condition = (value_rect > dist_min) & (value_rect < global_thrd)
        percent_below_threshold = np.mean(condition)
        if percent_below_threshold < 0.05:  # smaller than 1% (could be noise)
            walkable_7[i] = True

        # for debug
        value_rect_bottom = depth_matrix2[row_min + 60:row_max, col_start_list[i]:col_start_list[i] + rect_h].astype(float)
        dist_7[i] = compute_mean_min(value_rect_bottom)
    return walkable_7, dist_7


def lane_selection_planes(output_image2):
    walkable_7 = [False for i in range(lane_num)]
    for i in range(lane_num):
        value_rect = output_image2[row_min:row_max, col_start_list[i]:col_start_list[i] + rect_h, 0].astype(int)
        no_ground_area = round(np.count_nonzero(value_rect > 1) / value_rect.size, 4)  # 0 Ground  128 non-Ground
        if no_ground_area <= 0.1:
            walkable_7[i] = True
    return walkable_7


def get_direction(walkable_7):
    # return 0/1/2/3/4/5/6/-1
    good_blocks = [i != 0 and i != 6 and walkable_7[i - 1] and walkable_7[i] and walkable_7[i + 1] for i in range(7)]
    best_blocks = [1 < i < 5 and walkable_7[i - 2] and walkable_7[i - 1] and walkable_7[i] and walkable_7[i + 1] and walkable_7[i + 2] for i in range(7)]

    if walkable_7[3] and walkable_7[4] and walkable_7[2]: return 3
    if any(best_blocks): return [3, 4, 2][best_blocks[3:5].index(True) if True in best_blocks[3:5] else best_blocks[2]]
    if any(good_blocks): return [3, 4, 2, 5, 1][good_blocks[3:6].index(True) if True in good_blocks[3:6] else good_blocks[1]]
    return next((i for i in [3, 4, 2, 5, 1, 6, 0] if walkable_7[i]), -1)


def vis_7_lanes(color_image, direction_togo_pred, walkable_7):
    for i in range(lane_num):
        x_min = col_start_list[i]
        x_max = col_start_list[i] + rect_h
        y_min = row_min
        y_max = row_max
        txt = str(i)
        if walkable_7[i]:
            cv2.putText(color_image, txt, (x_min + 35, y_min - 30), 0, 0.68, (50, 200, 50), 2, 4)
            cv2.rectangle(color_image, (x_min, y_min), (x_max, y_max), (50, 200, 50), 2)
        else:
            cv2.putText(color_image, txt, (x_min + 35, y_min - 30), 0, 0.68, (100, 100, 100), 2, 4)
            cv2.rectangle(color_image, (x_min, y_min), (x_max, y_max), (100, 100, 100), 2)
        # 加上 预测方向的箭头
        if i == int(direction_togo_pred):
            start_point = (int(x_min + rect_h / 2), y_min - 80)
            end_point = (int(x_min + rect_h / 2), y_min - 125)
            color = (50, 200, 50)
            thickness = 5
            line_type = cv2.LINE_AA
            tip_length = 0.3
            cv2.arrowedLine(color_image, start_point, end_point, color, thickness, line_type, tipLength=tip_length)
    cv2.imshow('0', color_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def segment_ground_from_depth(depth_image_npy, bottom_rows, ground_interval=0.3):
    depth_image = copy.deepcopy(depth_image_npy)
    bottom_part = depth_image[-bottom_rows:]
    # Determine the column index by finding the column with the maximum sum of values
    col_sums = np.sum(bottom_part, axis=0)
    col_index = np.argmax(col_sums)
    # fit ground curve
    x = np.arange(bottom_rows)
    y = bottom_part[:, col_index]
    coeffs = np.polyfit(x, y, 2)
    poly = np.poly1d(coeffs)

    ground_mask = np.zeros_like(depth_image, dtype=np.uint8)
    # Evaluate the ground across all columns using the fitted model
    for i in range(depth_image.shape[1]):
        column_depths = depth_image[-bottom_rows:, i]
        estimated_ground_depths = poly(x)
        diff = np.abs(column_depths - estimated_ground_depths)
        ground_pixels = diff < ground_interval
        ground_mask[-bottom_rows:, i][ground_pixels] = 255
    # vis results
    output_image = np.full((depth_image_npy.shape[0], depth_image_npy.shape[1], 3), (128, 128, 128), dtype=np.uint8)
    output_image[np.where(ground_mask == 255)] = (0, 255, 0)
    return output_image, depth_image_npy


def demo_img():
    root = r"../"
    rgb = "materials/0-rgb-scene1-.jpg"
    # rgb = "materials/0-rgb-scene2-.jpg"
    # rgb = "materials/0-rgb-scene3-.jpg"
    npy = rgb.replace("0-rgb", "2-depth").replace(".jpg", ".npy")
    color_image = cv2.imread(os.path.join(root, rgb))
    # get ground seg by ground interval method
    depth_image_npy = np.load(os.path.join(root, npy))
    output_image, _ = segment_ground_from_depth(depth_image_npy, bottom_rows=80)
    # 7 blocks walkable check
    w7_planes = lane_selection_planes(output_image)
    # global thrd filter
    w7_dist, _ = lane_selection_depth(depth_image_npy)
    # double check walkable blocks
    W7 = [a and b for a, b in zip(w7_planes, w7_dist)]
    direction_togo = get_direction(W7)
    # display results
    color_image = cv2.addWeighted(color_image, 0.9, output_image, 0.3, 1)
    vis_7_lanes(color_image, direction_togo, W7)


if __name__ == "__main__":
    demo_img()
