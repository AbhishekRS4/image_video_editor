import os
import sys

def get_list_images(dir_images, img_format):
    list_images = os.listdir(dir_images)
    list_images = sorted([f for f in list_images if f.endswith(img_format)])
    return list_images

def create_directory(dir_path):
    dir_status = False
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
        dir_status = True
    return dir_status

def get_abs_path(file_path):
    abs_path = os.path.abspath(file_path)
    return abs_path

def delete_file(file_path):
    os.unlink(file_path)
    return
