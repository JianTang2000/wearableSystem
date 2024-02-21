import cv2
import detect
import numpy as np


def compute_mean_min(array_in, min_v=0.12, N=4):
    exist = (array_in >= min_v)
    _a = array_in[exist].sum()
    _b = exist.sum()
    mean_value = _a / _b
    return round(mean_value, N)


def compute_depth(depth_matrix, xywh):
    factor = 1
    y = int(xywh[1] * factor)
    x = int(xywh[0] * factor)
    distance_value = compute_mean_min(depth_matrix[y - 5:y + 5, x - 5:x + 5])
    distance_value = distance_value
    return distance_value


def distance_estimation():
    _model = detect.model_init()
    img_path_d = r"../materials/imgs/chair-2m-R.jpg"
    depth_path_d = r"../materials/imgs/chair-2m-R.npy"
    img = cv2.imread(img_path_d)
    im_BGR = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    r1, r2 = detect.detect_Real(_model, im_BGR, wanted_id=56)
    depth = np.load(depth_path_d)
    print(f"==========> distance to object center is {compute_depth(depth, r2)}")


def angle_estimation():
    _model = detect.model_init()
    img_path_d = r"../materials/imgs/chair-2m-R.jpg"
    img = cv2.imread(img_path_d)
    im_BGR = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    r1, r2 = detect.detect_Real(_model, im_BGR, wanted_id=56)
    print(f"==========> angle is {r1}")


if __name__ == "__main__":
    distance_estimation()
    # angle_estimation()
