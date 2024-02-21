import argparse
import json
import os

import fiftyone as fo
import fiftyone.zoo as foz
from tqdm import tqdm


def download_coco():
    dataset = foz.load_zoo_dataset(
        "coco-2017",
        split="train",
        label_types=["detections"],
    )
    session = fo.launch_app(dataset)
    session.dataset = dataset


parser = argparse.ArgumentParser()
parser.add_argument('--json_path', default=r'coco\annotations\instances_train2017.json', type=str, help="input: coco format(json)")
parser.add_argument('--save_path', default=r'coco\annotations\train-cocoYOLOtxt', type=str, help="specify where to save the output dir of labels")
arg = parser.parse_args()


def convert(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = box[0] + box[2] / 2.0
    y = box[1] + box[3] / 2.0
    w = box[2]
    h = box[3]

    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def extract_coco():
    json_file = arg.json_path
    ana_txt_save_path = arg.save_path

    data = json.load(open(json_file, 'r'))
    if not os.path.exists(ana_txt_save_path):
        os.makedirs(ana_txt_save_path)

    id_map = {}  # The id of the coco dataset is discontinuous! Re-map and output again!
    for i, category in enumerate(data['categories']):
        id_map[category['id']] = i

    # Reduce time complexity by building tables in advance
    max_id = 0
    for img in data['images']:
        max_id = max(max_id, img['id'])
    img_ann_dict = [[] for i in range(max_id + 1)]
    for i, ann in enumerate(data['annotations']):
        img_ann_dict[ann['image_id']].append(i)

    for img in tqdm(data['images']):
        filename = img["file_name"]
        img_width = img["width"]
        img_height = img["height"]
        img_id = img["id"]
        head, tail = os.path.splitext(filename)
        ana_txt_name = head + ".txt"
        f_txt = open(os.path.join(ana_txt_save_path, ana_txt_name), 'w')
        # look up the table directly without having to iterate
        for ann_id in img_ann_dict[img_id]:
            ann = data['annotations'][ann_id]
            box = convert((img_width, img_height), ann["bbox"])
            f_txt.write("%s %s %s %s %s\n" % (id_map[ann["category_id"]], box[0], box[1], box[2], box[3]))
        f_txt.close()


if __name__ == '__main__':
    download_coco()
    # extract_coco()  # jason labels to txt labels
