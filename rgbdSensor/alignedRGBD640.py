# -*- encoding: utf-8 -*-
import time

import cv2
import numpy as np
import pyrealsense2 as rs

open_dot = 1
img_size_W = 640
img_size_H = 360

pipeline = rs.pipeline()
config = rs.config()

pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

depth_sensor = device.query_sensors()[0]
if depth_sensor.supports(rs.option.emitter_enabled):
    depth_sensor.set_option(rs.option.emitter_enabled, open_dot)

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, img_size_W, img_size_H, rs.format.z16, 30)

config.enable_stream(rs.stream.color, img_size_W, img_size_H, rs.format.bgr8, 30)
config.enable_stream(rs.stream.infrared)  # 启动IR支持

# Start streaming
profile = pipeline.start(config)
# Getting the depth sensor's depth scale (see rs-align example for explanation)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()

align_to = rs.stream.color
align = rs.align(align_to)


def compute_mean_min(array_in, min_v=0.12, N=4):
    exist = (array_in >= min_v)
    _a = array_in[exist].sum()
    _b = exist.sum()
    mean_value = _a / _b
    return round(mean_value, N)


def get_RGBD():
    frames = pipeline.wait_for_frames()
    raw_depth = frames.get_depth_frame()
    raw_depth_image = np.asanyarray(raw_depth.get_data())
    raw_depth_image_matrix = raw_depth_image * depth_scale
    raw_depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(raw_depth_image, alpha=0.03), cv2.COLORMAP_JET)
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    if not aligned_depth_frame or not color_frame:
        print("depth or RGB input not found!")
    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    depth_image_matrix = depth_image * depth_scale
    color_image = np.asanyarray(color_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    return color_image, depth_colormap, depth_image_matrix, raw_depth_colormap, raw_depth_image_matrix


def get_img_depth():
    frames = pipeline.wait_for_frames()
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    if not aligned_depth_frame or not color_frame:
        print("depth or RGB input not found!")
    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    depth_image_matrix = depth_image * depth_scale
    color_image = np.asanyarray(color_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    return color_image, depth_colormap, depth_image_matrix


def get_img_depth_ir(align_ir=False):
    frames = pipeline.wait_for_frames()
    ir_frame = frames.first(rs.stream.infrared)
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    if not aligned_depth_frame or not color_frame or not ir_frame:
        print("depth or RGB or IR input not found!")
    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    depth_image_matrix = depth_image * depth_scale
    color_image = np.asanyarray(color_frame.get_data())
    ir_image = np.asanyarray(ir_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    aligned_ir = None
    if align_ir:
        aligned_ir, color_image = align_ir_rgb(ir_image, color_image)
    return color_image, depth_colormap, depth_image_matrix, ir_image, aligned_ir


def align_ir_rgb(ir_input, rgb_input):
    _height = rgb_input.shape[0]
    _width = rgb_input.shape[1]
    assert _height == 360 or _height == 720
    if _height == 360:
        cut_lef_right = ir_input[:, 80:(640 - 99)]
        cut_up_down = cut_lef_right[53:(360 - 55), :]
        ret_ir = cv2.resize(cut_up_down, dsize=(_width, _height))
    else:
        cut_lef_right = ir_input[:, 172:(1280 - 199)]
        cut_up_down = cut_lef_right[105:(780 - 170), :]
        ret_ir = cv2.resize(cut_up_down, dsize=(_width, _height))
    return ret_ir, rgb_input


def show_real_time_rgbd():
    while True:
        c, d, dm = get_img_depth()
        cv2.namedWindow('RGB')
        cv2.namedWindow('Depth')
        cv2.imshow('RGB', c)
        cv2.imshow('Depth', d)
        key = cv2.waitKey(1)


if __name__ == "__main__":
    print("start running...")
    print("========================================================")
    show_real_time_rgbd()
