import cv2
import torch


def model_init(device="PC", onnx=False, min_conf=0.05):
    model = None
    if device == 'PC':
        if onnx:
            model = torch.hub.load(r'yolov5',
                                   'custom',
                                   path=r'../materials/weights/best.onnx',
                                   source='local',
                                   force_reload=True,
                                   device='cpu')
        else:
            model = torch.hub.load(r'C:\Users\jiant\OneDrive\SJTU\6code\yolov51106\yolov5-local-hub',
                                   'custom',
                                   path=r'../materials/weights/best.pt',
                                   source='local',
                                   force_reload=True,
                                   device='cpu')
    else:
        if onnx:
            model = torch.hub.load(r'/home/pi/yolov5', 'custom',
                                   path=r'../materials/weights/best.onnx',
                                   source='local',
                                   force_reload=True,
                                   device='cpu')
        else:
            model = torch.hub.load(r'/home/pi/yolov5', 'custom',
                                   path=r'../materials//weights/best.pt',
                                   source='local',
                                   force_reload=True,
                                   device='cpu')
    assert model is not None
    model.conf = min_conf
    return model


def detect_RGB(model_ins, cv2_rgb, cv2_raw, img_size=[288, 512], wanted_id=56):
    rectangle_color = (0, 0, 50)
    results = model_ins(cv2_rgb, size=img_size)
    # results.print()  # print time cost and prediction in txt
    ret_tensor = results.xywh
    ret_numpy = ret_tensor[0].cpu().numpy()
    best_conf = 0
    xywh_1920 = [None for i in range(4)]
    found = False
    for pred in ret_numpy:
        conf = float(pred[4])
        class_id = int(pred[5])
        if class_id == int(wanted_id) and conf > best_conf:
            xywh_1920[0] = pred[0]
            xywh_1920[1] = pred[1]
            xywh_1920[2] = pred[2]
            xywh_1920[3] = pred[3]
            best_conf = conf
            found = True
    if not found:
        print("...nothing found")
        return None, None
    x_min = int(xywh_1920[0] - 1 / 2 * xywh_1920[2])
    x_max = int(xywh_1920[0] + 1 / 2 * xywh_1920[2])
    y_min = int(xywh_1920[1] - 1 / 2 * xywh_1920[3])
    y_max = int(xywh_1920[1] + 1 / 2 * xywh_1920[3])

    cv2.rectangle(cv2_raw, (x_min, y_min), (x_max, y_max), rectangle_color, 2)
    txt = str(wanted_id) + " " + str(round(best_conf, 2))
    cv2.putText(cv2_raw, txt, (x_min - 5, y_min - 15), 0, 0.75, rectangle_color, 2, 4)  # txt_color 前面那个是字体大小
    cv2.namedWindow('RGB')
    cv2.imshow('RGB', cv2_raw)
    key = cv2.waitKey(-1)


def detect_Real(model_ins, cv2_rgb, img_size=[288, 512], wanted_id=56):
    # w_max = 1280  # 1280  # img width
    # h_max = 720  # 720  # img height
    h_max, w_max = cv2_rgb.shape[:2]
    az_max = 70  # 70
    el_max = 42  # 42
    xywh_1920 = [None for i in range(4)]
    found = False
    results = model_ins(cv2_rgb, size=img_size)
    results.print()  # print time cost and prediction in txt
    ret_tensor = results.xywh
    ret_numpy = ret_tensor[0].cpu().numpy()
    best_conf = 0
    for pred in ret_numpy:
        conf = float(pred[4])  # 0.98
        class_id = int(pred[5])  # 0,1,2,3
        if class_id == int(wanted_id) and conf > best_conf:
            xywh_1920[0] = pred[0]
            xywh_1920[1] = pred[1]
            xywh_1920[2] = pred[2]
            xywh_1920[3] = pred[3]
            best_conf = conf
            found = True
    if not found:
        print("...nothing found")
        return None, None
    x = (w_max / 2 - xywh_1920[0]) / w_max
    y = (h_max / 2 - xywh_1920[1]) / h_max
    az = round(-az_max * 1 / 2 * 2 * x, 2)
    el = round(el_max * 1 / 2 * 2 * y, 2)
    part_2 = " "
    angle_value = abs(az)
    part_3 = str(angle_value)
    part_1 = "left" if az <= 0 else "right"
    ret = part_3 + part_2 + part_1
    return ret, xywh_1920  # "10.8 right"


if __name__ == "__main__":
    _model = model_init()
    img_path = r"../materials/imgs/chair-2m-R.jpg"
    im_raw = cv2.imread(img_path)
    im = cv2.cvtColor(im_raw, cv2.COLOR_BGR2RGB)
    detect_RGB(_model, im, im_raw)
