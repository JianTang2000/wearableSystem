"""
object detection, usage example provided in main
"""

import cv2
import time
import numpy as np
from ultralytics import YOLO

from util.tools import compute_mean_min

print("============loading model .....================")
model = YOLO(r'../materials/best.onnx', task='detect')  # speed UP in Pi
# model = YOLO(r'../materials/best.pt', task='detect')
print("============loading model done ================")

detection_classes = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light',
                     10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow',
                     20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee',
                     30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle',
                     40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange',
                     50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed',
                     60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven',
                     70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush',
                     80: 'door', 81: 'stair'}
RGB_w = 640
RGB_h = 360
az_max = 70
el_max = 43
pred_imgsz = (224, 384)
conf_thrd = 0.5


def post_process_angle(xywh):
    # xywh is a list like : [x y w h]
    x, y = (RGB_w / 2 - xywh[0]) / RGB_w, (RGB_h / 2 - xywh[1]) / RGB_h
    az, el = round(-az_max * x, 2), round(el_max * y, 2)
    return f"{abs(az)} {'left' if az <= 0 else 'right'}"  # "10.8 right"


def post_process_distance(depth_image_npy, xywh, distance_min=0.12, box_w=5):
    x = int(xywh[0])
    y = int(xywh[1])
    object_box = depth_image_npy[y - box_w:y + box_w, x - box_w:x + box_w].astype(float)
    no_depth_area = round(np.count_nonzero(object_box < distance_min) / object_box.size, 2)  # e.g. 0.05
    distance = compute_mean_min(object_box)
    return distance, no_depth_area


def detect(img_cv2, classes=None, max_det=10):
    results = model.predict(img_cv2, imgsz=pred_imgsz, conf=conf_thrd, classes=classes, max_det=max_det, device='cpu', show=True)

    # # Extract bounding boxes, classes, names, and confidences
    # boxes = results[0].boxes.xywh.tolist()  #
    # classes = results[0].boxes.cls.tolist()  #
    # names = results[0].names
    # confidences = results[0].boxes.conf.tolist()  #
    #
    # # Iterate through the results
    # for box, cls, conf in zip(boxes, classes, confidences):
    #     x1, y1, x2, y2 = box
    #     confidence = conf
    #     detected_class = cls
    #     name = names[int(cls)]

    return results


def detect_target_obj(img_cv2, classes=80, max_det=1, show=False):
    results = model.predict(img_cv2, imgsz=pred_imgsz, conf=conf_thrd, classes=[classes], max_det=max_det, device='cpu', show=show)
    xywh = results[0].boxes.xywh.tolist()  # [[193.43765258789062, 180.96485900878906, 290.7906494140625, 358.0702819824219]]
    # classes = results[0].boxes.cls.tolist()  # [80.0]
    # names = results[0].names  # all name dict
    # confidences = results[0].boxes.conf.tolist()  # [0.9656597375869751]
    return xywh if len(xywh) > 0 else None


def demo():
    img_cv2 = cv2.imread(r'../materials/0-rgb-scene1-.jpg')
    model.predict(img_cv2, imgsz=pred_imgsz, conf=conf_thrd, device='cpu', show=True)
    time.sleep(100)


def usage_example():
    target = 80
    # target = 60
    # target = 56
    rgb = r"../materials/0-rgb-scene1-.jpg"
    npy = rgb.replace("0-rgb", "2-depth").replace(".jpg", ".npy")
    img_cv2 = cv2.imread(rgb)
    depth_image_npy = np.load(npy)
    xywh = detect_target_obj(img_cv2, classes=target, show=True)
    if xywh is not None:
        angle = post_process_angle(xywh[0])
        distance, invalid_p = post_process_distance(depth_image_npy, xywh[0])  # =======> NOTE
        # print(f"angle (degree left/right) : {angle}")
        # print(f"distance (meter) : {distance}")
        # print(f"invalid depth area in the box (0~1) : {invalid_p}")
    else:
        print(f' no {detection_classes.get(target)} detected ')

    time.sleep(100)


if __name__ == "__main__":
    print("==")
    # demo()
    usage_example()
