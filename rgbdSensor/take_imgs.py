"""
running and collect data for building the dataset
"""
import os
import time

import cv2
import numpy as np


def save_img(img_size=1280):
    save_dir = r"./"
    count_current = 0
    if img_size == 640:
        import alignedRGBD640
        while True:
            count_current += 1
            _color_image, _depth_colormap, _depth_image_matrix, ir_image, aligned_ir_image = alignedRGBD640.get_img_depth_ir(align_ir=True)
            date = time.strftime("%Y-%m-%d-%H-%M-%S")
            rgb_name = "0-rgb-" + str(date) + "-" + str(count_current) + ".jpg"
            depth_rgb_name = "1-depthRGB-" + str(date) + "-" + str(count_current) + ".jpg"
            depth_name = "2-depth-" + str(date) + "-" + str(count_current) + ".npy"
            # ir_name = "3-ir-" + str(date) + "-" + str(count_current) + ".npy"
            # AlignedIR_name = "4-AlignedIR-" + str(date) + "-" + str(count_current) + ".npy"
            ir_name_rgb = "5-ir-" + str(date) + "-" + str(count_current) + ".jpg"
            cv2.imwrite(os.path.join(save_dir, rgb_name), _color_image)
            cv2.imwrite(os.path.join(save_dir, depth_rgb_name), _depth_colormap)
            # cv2.imwrite(os.path.join(save_dir, ir_name_rgb), aligned_ir_image)
            np.save(os.path.join(save_dir, depth_name), _depth_image_matrix)
            print("current at ", count_current)
            # cv2.namedWindow('ir_image')
            # cv2.imshow('ir_image', aligned_ir_image)
            # key = cv2.waitKey(1)
            time.sleep(0.3)
    else:
        import alignedRGBD1280
        while True:
            count_current += 1
            _color_image, _depth_colormap, _depth_image_matrix, ir_image, aligned_ir_image = alignedRGBD1280.get_img_depth_ir(align_ir=True)
            date = time.strftime("%Y-%m-%d-%H-%M-%S")
            rgb_name = "0-rgb-" + str(date) + "-" + str(count_current) + ".jpg"
            depth_rgb_name = "1-depthRGB-" + str(date) + "-" + str(count_current) + ".jpg"
            depth_name = "2-depth-" + str(date) + "-" + str(count_current) + ".npy"
            # ir_name = "3-ir-" + str(date) + "-" + str(count_current) + ".npy"
            # AlignedIR_name = "4-AlignedIR-" + str(date) + "-" + str(count_current) + ".npy"
            ir_name_rgb = "5-ir-" + str(date) + "-" + str(count_current) + ".jpg"
            cv2.imwrite(os.path.join(save_dir, rgb_name), _color_image)
            cv2.imwrite(os.path.join(save_dir, depth_rgb_name), _depth_colormap)
            # cv2.imwrite(os.path.join(save_dir, ir_name_rgb), aligned_ir_image)
            np.save(os.path.join(save_dir, depth_name), _depth_image_matrix)
            print("current at ", count_current)
            # cv2.namedWindow('ir_image')
            # cv2.imshow('ir_image', aligned_ir_image)
            # key = cv2.waitKey(1)
            time.sleep(0.3)


if __name__ == "__main__":
    # img_w_size = 640
    img_w_size = 1280
    save_img(img_w_size)
