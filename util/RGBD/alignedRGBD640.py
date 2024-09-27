"""
core function of the RGB-D camera, usage example provided in main
"""

import time
import cv2
import numpy as np
import pyrealsense2 as rs

open_dot = 1  # Infrared circular projection.  0 off 1 on
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

# config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
config.enable_stream(rs.stream.color, img_size_W, img_size_H, rs.format.bgr8, 30)
config.enable_stream(rs.stream.infrared)

profile = pipeline.start(config)
depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()
print("Depth Scale is: ", depth_scale)

# Create an align object
align_to = rs.stream.color
align = rs.align(align_to)


# align
def get_RGBD_align():
    frames = pipeline.wait_for_frames()
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    if not aligned_depth_frame or not color_frame:
        print("depth or RGB input not found!")
    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    depth_image_matrix = depth_image * depth_scale  # in meter
    color_image = np.asanyarray(color_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    return color_image, depth_colormap, depth_image_matrix


# non-align
def get_RGBD_raw():
    frames = pipeline.wait_for_frames()
    raw_depth = frames.get_depth_frame()
    raw_depth_image = np.asanyarray(raw_depth.get_data())
    raw_depth_image_matrix = raw_depth_image * depth_scale  # in meter
    raw_depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(raw_depth_image, alpha=0.03), cv2.COLORMAP_JET)
    color_frame = frames.get_color_frame()
    color_image = np.asanyarray(color_frame.get_data())
    return color_image, raw_depth_colormap, raw_depth_image_matrix


# non-align & align
def get_RGBD_all():
    frames = pipeline.wait_for_frames()

    raw_depth = frames.get_depth_frame()
    raw_depth_image = np.asanyarray(raw_depth.get_data())
    raw_depth_image_matrix = raw_depth_image * depth_scale  # in meter
    raw_depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(raw_depth_image, alpha=0.03), cv2.COLORMAP_JET)
    aligned_frames = align.process(frames)
    aligned_depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    if not aligned_depth_frame or not color_frame:
        print("depth or RGB input not found!")
    depth_image = np.asanyarray(aligned_depth_frame.get_data())
    depth_image_matrix = depth_image * depth_scale  # in meter
    color_image = np.asanyarray(color_frame.get_data())
    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
    return color_image, depth_colormap, depth_image_matrix, raw_depth_colormap, raw_depth_image_matrix


def demo_show_real_time_RGBD():
    while True:
        color_image, depth_colormap, depth_image_matrix, raw_depth_colormap, raw_depth_image_matrix = get_RGBD_all()
        cv2.namedWindow('RGB')
        cv2.namedWindow('Depth')
        cv2.imshow('RGB', color_image)
        cv2.imshow('Depth', depth_colormap)
        key = cv2.waitKey(1)

    # while True:
    #     color_image, depth_colormap, depth_image_matrix = get_RGBD_align()
    #     cv2.namedWindow('RGB')
    #     cv2.namedWindow('Depth')
    #     cv2.imshow('RGB', color_image)
    #     cv2.imshow('Depth', depth_colormap)
    #     key = cv2.waitKey(1)

    # while True:
    #     color_image, depth_colormap, depth_image_matrix = get_RGBD_raw()
    #     cv2.namedWindow('RGB')
    #     cv2.namedWindow('Depth')
    #     cv2.imshow('RGB', color_image)
    #     cv2.imshow('Depth', depth_colormap)
    #     key = cv2.waitKey(1)


if __name__ == "__main__":
    print("==")
    demo_show_real_time_RGBD()
