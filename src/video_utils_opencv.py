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
