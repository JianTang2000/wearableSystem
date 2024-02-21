import os
import shutil
import tools
import shutil
import os
import random
from lxml import etree
import numpy as np
import json
from PIL import Image

dic = {'apple': 0,
       'chair': 1}


def get_xml_text(root, pattern):
    return list(map(lambda x: x.text, root.xpath(pattern)))


def random_true(prob):
    p = ([prob, 1 - prob])
    return np.random.choice([True, False], p=p)


def xml_to_txt(path, pic_name, save_dir, abs=True):
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)
    tree = etree.parse(path)
    root = tree.getroot()
    infos = {}
    for _pattern in ('width', 'height', 'name', 'xmin', 'ymin', 'xmax', 'ymax'):
        pattern = f'//{_pattern}'
        infos[_pattern] = get_xml_text(root, pattern)

    names = infos['name']
    width, height = int(infos['width'][0]), int(infos['height'][0])
    if abs:
        xmins = np.array(list(map(int, infos['xmin']))) / width
        ymins = np.array(list(map(int, infos['ymin']))) / height
        xmaxs = np.array(list(map(int, infos['xmax']))) / width
        ymaxs = np.array(list(map(int, infos['ymax']))) / height
    else:
        xmins = np.array(list(map(int, infos['xmin'])))
        ymins = np.array(list(map(int, infos['ymin'])))
        xmaxs = np.array(list(map(int, infos['xmax'])))
        ymaxs = np.array(list(map(int, infos['ymax'])))

    xs = list(map(lambda x: '%.6f' % x, ((xmaxs + xmins) / 2).tolist()))
    ys = list(map(lambda x: '%.6f' % x, ((ymaxs + ymins) / 2).tolist()))

    ws = list(map(lambda x: '%.6f' % x, ((xmaxs - xmins).tolist())))
    hs = list(map(lambda x: '%.6f' % x, ((ymaxs - ymins).tolist())))

    _names, _xs, _ys, _ws, _hs = [[] for _ in range(5)]
    for i, name in enumerate(names):
        if name in dic:
            _names.append(dic[name])
            _xs.append(xs[i])
            _ys.append(ys[i])
            _ws.append(ws[i])
            _hs.append(hs[i])

    if _names:
        res = np.column_stack((_names, _xs, _ys, _ws, _hs)).tolist()
        res = [' '.join(_res) + '\n' for _res in res]
    else:
        res = ['\n']

    # Discard the blank txt at a certain percentage
    if res == ['\n']:
        if random_true(1):
            with open(os.path.join(save_dir, '{pic_name}.txt'.format(pic_name=pic_name)), 'w') as f:
                f.writelines(res)
        else:
            print('drop')
    else:
        with open(os.path.join(save_dir, '{pic_name}.txt'.format(pic_name=pic_name)), 'w') as f:
            f.writelines(res)
    return res


def split_train_test(Test=False):
    todo_path = r"00-OD-dataset\81C\2.7K-all"
    save_path = r'00-OD-dataset\81C\2.7K-all-totrain'
    if not os.path.isdir(os.path.join(save_path, r'images\train')):
        os.makedirs(os.path.join(save_path, r'images\train'))
    if not os.path.isdir(os.path.join(save_path, r'images\val')):
        os.makedirs(os.path.join(save_path, r'images\val'))
    if not os.path.isdir(os.path.join(save_path, r'labels\train')):
        os.makedirs(os.path.join(save_path, r'labels\train'))
    if not os.path.isdir(os.path.join(save_path, r'labels\val')):
        os.makedirs(os.path.join(save_path, r'labels\val'))
    if Test:
        if not os.path.isdir(os.path.join(save_path, r'images\test')):
            os.makedirs(os.path.join(save_path, r'images\test'))
        if not os.path.isdir(os.path.join(save_path, r'labels\test')):
            os.makedirs(os.path.join(save_path, r'labels\test'))
    shutil.rmtree(os.path.join(save_path, r'images\train'))
    os.mkdir(os.path.join(save_path, r'images\train'))
    shutil.rmtree(os.path.join(save_path, r'images\val'))
    os.mkdir(os.path.join(save_path, r'images\val'))
    shutil.rmtree(os.path.join(save_path, r'labels\train'))
    os.mkdir(os.path.join(save_path, r'labels\train'))
    shutil.rmtree(os.path.join(save_path, r'labels\val'))
    os.mkdir(os.path.join(save_path, r'labels\val'))
    if Test:
        shutil.rmtree(os.path.join(save_path, r'images\test'))
        os.mkdir(os.path.join(save_path, r'images\test'))
        shutil.rmtree(os.path.join(save_path, r'labels\test'))
        os.mkdir(os.path.join(save_path, r'labels\test'))

    files_all = os.listdir(todo_path)
    files = [i for i in files_all if i.endswith('.jpg') or i.endswith(".JPEG")]
    txts = [i for i in files_all if i.endswith('.txt')]
    jpg_format = [i for i in files if i.replace(".jpg", ".txt") in txts]
    other_format = [i for i in files if i.replace(".JPEG", ".txt") in txts]
    files = list(set(jpg_format).union(set(other_format)))
    if not Test:
        for file in files:
            if tools.random_true(0.7):
                img_path = os.path.join(todo_path, file)
                img_path_new = os.path.join(os.path.join(save_path, r'images\train'), file)
                if file.endswith("jpg"):
                    label_path = os.path.join(todo_path, file.replace('.jpg', '.txt'))
                    label_path_new = os.path.join(os.path.join(save_path, r'labels\train'), file.replace('.jpg', '.txt'))
                    shutil.copy(img_path, img_path_new)
                    shutil.copy(label_path, label_path_new)
                else:
                    label_path = os.path.join(todo_path, file.replace('.JPEG', '.txt'))
                    label_path_new = os.path.join(os.path.join(save_path, r'labels\train'), file.replace('.JPEG', '.txt'))
                    shutil.copy(img_path, img_path_new)
                    shutil.copy(label_path, label_path_new)
            else:
                img_path = os.path.join(todo_path, file)
                img_path_new = os.path.join(os.path.join(save_path, r'images\val'), file)
                if file.endswith("jpg"):
                    label_path = os.path.join(todo_path, file.replace('.jpg', '.txt'))
                    label_path_new = os.path.join(os.path.join(save_path, r'labels\val'), file.replace('.jpg', '.txt'))
                    shutil.copy(img_path, img_path_new)
                    shutil.copy(label_path, label_path_new)
                else:
                    label_path = os.path.join(todo_path, file.replace('.JPEG', '.txt'))
                    label_path_new = os.path.join(os.path.join(save_path, r'labels\val'), file.replace('.JPEG', '.txt'))
                    shutil.copy(img_path, img_path_new)
                    shutil.copy(label_path, label_path_new)
    else:
        for file in files:
            if tools.random_true(0.6):
                img_path = os.path.join(todo_path, file)
                img_path_new = os.path.join(os.path.join(save_path, r'images\train'), file)
                if file.endswith("jpg"):
                    label_path = os.path.join(todo_path, file.replace('.jpg', '.txt'))
                    label_path_new = os.path.join(os.path.join(save_path, r'labels\train'), file.replace('.jpg', '.txt'))
                    shutil.copy(img_path, img_path_new)
                    shutil.copy(label_path, label_path_new)
                else:
                    label_path = os.path.join(todo_path, file.replace('.JPEG', '.txt'))
                    label_path_new = os.path.join(os.path.join(save_path, r'labels\train'), file.replace('.JPEG', '.txt'))
                    shutil.copy(img_path, img_path_new)
                    shutil.copy(label_path, label_path_new)
            else:
                if tools.random_true(0.5):
                    img_path = os.path.join(todo_path, file)
                    img_path_new = os.path.join(os.path.join(save_path, r'images\val'), file)
                    if file.endswith("jpg"):
                        label_path = os.path.join(todo_path, file.replace('.jpg', '.txt'))
                        label_path_new = os.path.join(os.path.join(save_path, r'labels\val'), file.replace('.jpg', '.txt'))
                        shutil.copy(img_path, img_path_new)
                        shutil.copy(label_path, label_path_new)
                    else:
                        label_path = os.path.join(todo_path, file.replace('.JPEG', '.txt'))
                        label_path_new = os.path.join(os.path.join(save_path, r'labels\val'), file.replace('.JPEG', '.txt'))
                        shutil.copy(img_path, img_path_new)
                        shutil.copy(label_path, label_path_new)
                else:
                    img_path = os.path.join(todo_path, file)
                    img_path_new = os.path.join(os.path.join(save_path, r'images\test'), file)
                    if file.endswith("jpg"):
                        label_path = os.path.join(todo_path, file.replace('.jpg', '.txt'))
                        label_path_new = os.path.join(os.path.join(save_path, r'labels\test'), file.replace('.jpg', '.txt'))
                        shutil.copy(img_path, img_path_new)
                        shutil.copy(label_path, label_path_new)
                    else:
                        label_path = os.path.join(todo_path, file.replace('.JPEG', '.txt'))
                        label_path_new = os.path.join(os.path.join(save_path, r'labels\test'), file.replace('.JPEG', '.txt'))
                        shutil.copy(img_path, img_path_new)
                        shutil.copy(label_path, label_path_new)


if __name__ == "__main__":
    print("================================")
    split_train_test(Test=False)
    print("================================")
