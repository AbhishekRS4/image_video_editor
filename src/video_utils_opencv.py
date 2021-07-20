import os
import sys
import cv2
import numpy as np
import streamlit as st
from dataclasses import dataclass

def create_directory(directory_path):
    """
    Parameters
    ----------
    directory_path (str) : full path of directory
    """
    if not os.path.isdir(directory_path):
        os.makedirs(directory_path)
        st.write(f"Directory created: {directory_path}")
    else:
        st.write(f"Directory {directory_path} already exists")

class VideoToImageWriter:
    def __init__(self, file_video, dir_images, img_prefix, img_format, img_id_start):
        self.params = self.ImageParams(file_video=file_video, dir_images=dir_images,
            img_prefix=img_prefix, img_format=img_format, img_id_start=img_id_start)

    @dataclass
    class ImageParams:
        file_video : str
        dir_images : str
        img_prefix : str
        img_format : str
        img_id_start : int

    def generate_images_from_video(self):
        if not os.path.isfile(self.params.file_video):
            st.error(f"Video file: {self.params.file_video} does not exist")
            return

        create_directory(self.params.dir_images)

        try:
            video_reader = cv2.VideoCapture(self.params.file_video)
        except:
            st.error(f"failed to load the video: {self.params.file_video}")
            return

        num_images = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
        success = True
        image_id = self.params.img_id_start
        image_count = 0
        st.write(f"Extracting {num_images} images from {self.params.file_video}")
        progress_bar = st.progress(0.0)
        while success:
            success, image_frame = video_reader.read()

            if not success:
                break

            cv2.imwrite(os.path.join(self.params.dir_images, self.params.img_prefix +\
                str(image_id) + self.params.img_format), image_frame
            )
            image_id += 1
            image_count += 1
            progress_bar.progress(image_count / num_images)
        st.write(f"Extraction of {image_id - self.params.img_id_start} images completed, images are in : {self.params.dir_images} \n")
        st.success("Image extraction from the video completed")

class ImageToVideoWriter:
    def __init__(self, fps, width, height, file_video, dir_images, img_format, video_encoder):
        self.params = self.VideoParams(fps=fps, width=width, height=height, file_video=file_video,
            dir_images=dir_images, img_format=img_format, video_encoder=video_encoder)

    @dataclass
    class VideoParams:
        fps : int
        width : int
        height : int
        file_video : str
        dir_images : str
        img_format : str
        video_encoder : str

    def generate_video_from_images(self):
        if not os.path.isdir(self.params.dir_images):
            st.error(f"Images directory {self.params.dir_images} does not exist")
            return

        dir_out = os.path.dirname(self.params.file_video)
        if not dir_out == "":
            create_directory(dir_out)
        else:
            dir_out = os.getcwd()

        if os.path.isfile(self.params.file_video):
            st.write(f"Deleteing already present {self.params.file_video}")
            os.unlink(self.params.file_video)

        list_images = sorted(
            [f for f in os.listdir(self.params.dir_images)\
            if f.endswith(self.params.img_format)]
        )
        num_images = len(list_images)
        st.write(f"Number of images to be converted into a video : {num_images}")
        st.write(f"Video creation params - fps : {self.params.fps}, video_resolution : {self.params.width}x{self.params.height}")
        img = cv2.imread(os.path.join(self.params.dir_images, list_images[0]))
        if (img.shape[0] != self.params.height or \
            img.shape[1] != self.params.width):
            st.error(f"Image dimensions {img.shape[1]}x{img.shape[0]} mismatch with video dimensions {self.params.width}x{self.params.height}")
            return

        video_writer = cv2.VideoWriter(self.params.file_video,
            cv2.VideoWriter_fourcc(*self.params.video_encoder),
            self.params.fps, (self.params.width, self.params.height)
        )

        st.write("Video generation started")
        progress_bar = st.progress(0.0)
        for i in range(num_images):
            try:
                img = cv2.imread(os.path.join(self.params.dir_images, list_images[i]))
                video_writer.write(img)
                progress_bar.progress((i + 1)/ num_images)
            except IOError:
                st.error("Unknown error in image or video file handling")
                return
        video_writer.release()
        st.write(f"{self.params.file_video} has been successfully created in : {dir_out}")
        st.success("Video encoding from images completed")
