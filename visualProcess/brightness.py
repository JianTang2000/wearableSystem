import cv2
import numpy as np
import os


def show_brightness_reduction():
    # Load the image
    img = cv2.imread(r"../materials/imgs/chair-2m-R.jpg")
    brightness_reduction = np.arange(0.1, 1.1, 0.1)
    for i in brightness_reduction:
        print(f"current brightness is : {i}")
        new_brightness_reduction = round(i, 1)
        # Create a new image with the reduced brightness
        dst = cv2.convertScaleAbs(img, alpha=new_brightness_reduction, beta=0)
        noise = np.random.normal(loc=0, scale=0.1 * 255, size=img.shape)
        dst = cv2.add(dst, noise.astype(np.int16), dtype=cv2.CV_8UC3)
        cv2.imshow('image', dst)
        if cv2.waitKey(0) == 27:
            break
    cv2.destroyAllWindows()


def save_brightness_reduction_2():
    todo_path = r"brightness_reduction\to-test-RGB\images\val"
    save_path = r"brightness_reduction"
    brightness_reduction = np.arange(1, 10, 1)
    for i in brightness_reduction:
        print("processing..", i)
        alpha = 1 - i / 9
        beta = (1 - alpha) * 30
        noise_level = i * 0.015
        imgs = os.listdir(todo_path)
        for img_name in imgs:
            img = cv2.imread(os.path.join(todo_path, img_name))
            noise = np.random.normal(loc=0, scale=noise_level * 255, size=img.shape)
            new_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
            new_img = cv2.add(new_img, noise.astype(np.int16), dtype=cv2.CV_8UC3)
            save_path_full = os.path.join(os.path.join(save_path, str(i)), r"images\val")
            cv2.imwrite(os.path.join(save_path_full, img_name), new_img)


if __name__ == "__main__":
    show_brightness_reduction()
    # save_brightness_reduction_2()
    print("Done")
