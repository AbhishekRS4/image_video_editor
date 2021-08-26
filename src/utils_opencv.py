import os
import sys
import cv2
import numpy as np
from dataclasses import dataclass

class VideoReader:
    def __init__(self, file_video):
        """
        Parameters
        ----------
        file_video (str) : full path of valid video file
        """
        self.num_images = None
        self.video_reader = None
        self.file_video = file_video

    def init_video_reader(self):
        if self.video_reader is None:
            self.video_reader = cv2.VideoCapture(self.file_video)
            self.num_images = int(self.video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
        return

    def get_num_images_in_video(self):
        return self.num_images

    def get_next_image(self):
        ret_val, img = self.video_reader.read()
        return ret_val, img

    def get_nth_image(self, n):
        self.video_reader.set(cv2.CAP_PROP_POS_FRAMES, n)
        return self.get_next_image()

class VideoWriter:
    def __init__(self, fps, width, height, file_video, video_encoder):
        """
        Parameters
        ----------
        fps (int) : fps of video
        width (int) : width of the video
        height (int) : height of the video
        file_video (str) : full path of video file
        video_encoder (str) : video encoder to be used
        """
        self.params = self.VideoParams(fps=fps, width=width, height=height, file_video=file_video,
            video_encoder=video_encoder)
        self.video_writer = None

    @dataclass
    class VideoParams:
        fps : int
        width : int
        height : int
        file_video : str
        video_encoder : str

    def init_video_writer(self):
        self.video_writer = cv2.VideoWriter(self.params.file_video,
            cv2.VideoWriter_fourcc(*self.params.video_encoder), self.params.fps,
            (self.params.width, self.params.height))
        return

    def close_video_writer(self):
        if self.video_writer is not None:
            self.video_writer.release()
        return

    def write_image_to_video(self, image_array):
        self.video_writer.write(image_array)

def write_text_to_image(img, text, text_position, font, font_scale, color_rgb):
    img = cv2.putText(img, text, text_position, fontFace=font, fontScale=font_scale, color=color_rgb)
    return img

def get_font_list():
    list_fonts = [
        cv2.FONT_HERSHEY_PLAIN, cv2.FONT_HERSHEY_SIMPLEX,
        cv2.FONT_HERSHEY_DUPLEX, cv2.FONT_HERSHEY_COMPLEX,
        cv2.FONT_HERSHEY_TRIPLEX, cv2.FONT_HERSHEY_COMPLEX_SMALL,
        cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, cv2.FONT_HERSHEY_SCRIPT_COMPLEX,
    ]

    list_font_names = [
        "PLAIN", "SIMPLEX", "DUPLEX", "COMPLEX", "TRIPLEX", "COMPLEX_SMALL",
        "SCRIPT_SIMPLEX", "SCRIPT_COMPLEX",
    ]

    return list_fonts, list_font_names

def get_font_dict():
    list_fonts, list_font_names = get_font_list()
    dict_fonts = {}
    num_fonts = len(list_fonts)

    for i in range(num_fonts):
        dict_fonts[list_font_names[i]] = list_fonts[i]

    return dict_fonts

def get_font_preview_image():
    list_fonts, list_font_names = get_font_list()
    num_fonts = len(list_fonts)
    pos_x = 40
    pos_y = 40
    font_preview_img = np.zeros((360, 360, 3), dtype=np.uint8)

    for i in range(num_fonts):
        font_preview_img = write_text_to_image(font_preview_img, list_font_names[i],
            (pos_x, pos_y * (i+1)), list_fonts[i], 1, (255, 255, 255))
    return font_preview_img

def get_preview_image_with_text(font, text, image_height, image_width, text_position, color_background="black", color_text="white", font_scale=2):
    preview_image = None
    color_rgb = None

    if color_background == "black":
        preview_image = np.zeros((image_height, image_width, 3), dtype=np.uint8)
    else:
        preview_image = 255 * np.ones((image_height, image_width, 3), dtype=np.uint8)

    if color_text == "white":
        color_rgb = (255, 255, 255)
    else:
        color_rgb = (0, 0, 0)

    preview_image = write_text_to_image(preview_image, text, text_position, font, font_scale, color_rgb)
    return preview_image
