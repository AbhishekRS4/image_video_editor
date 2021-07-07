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

@dataclass
class ImageWriterParams:
    file_video : str
    dir_images : str
    img_prefix : str
    img_format : str
    img_id_start : int

def extract_images_from_video(image_writer_params):
    """
    Paramaters
    ----------
    image_writer_params (ImageWriterParams) : object of dataclass ImageWriterParams
    """
    if not os.path.isfile(image_writer_params.file_video):
        st.error(f"Video file: {image_writer_params.file_video} does not exist")
        return

    create_directory(image_writer_params.dir_images)

    try:
        video_reader = cv2.VideoCapture(image_writer_params.file_video)
    except:
        st.error(f"failed to load the video: {image_writer_params.file_video}")
        return

    num_images = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))
    success = True
    image_id = image_writer_params.img_id_start
    image_count = 0
    st.write(f"Extracting {num_images} images from {image_writer_params.file_video}")
    progress_bar = st.progress(0.0)
    while success:
        success, image_frame = video_reader.read()

        if not success:
            break

        cv2.imwrite(os.path.join(image_writer_params.dir_images, image_writer_params.img_prefix +\
            str(image_id) + image_writer_params.img_format), image_frame
        )
        image_id += 1
        image_count += 1
        progress_bar.progress(image_count / num_images)
    st.write(f"Extraction of {image_id - image_writer_params.img_id_start} images completed, images are in : {image_writer_params.dir_images} \n")
    st.success("Image extraction from the video completed")

@dataclass
class VideoWriterParams:
    fps : int
    width : int
    height : int
    file_video : str
    dir_images : str
    img_format : str
    video_encoder : str

def create_video_from_images(video_writer_params):
    """
    Parameters
    ----------
    video_writer_params (VideoWriterParams) : object of dataclass VideoWriterParams
    """
    if not os.path.isdir(video_writer_params.dir_images):
        st.error(f"Images directory {video_writer_params.dir_images} does not exist")
        return

    dir_out = os.path.dirname(video_writer_params.file_video)
    if not dir_out == "":
        create_directory(dir_out)
    else:
        dir_out = os.getcwd()

    if os.path.isfile(video_writer_params.file_video):
        st.write(f"Deleteing already present {video_writer_params.file_video}")
        os.unlink(video_writer_params.file_video)

    list_images = sorted(
        [f for f in os.listdir(video_writer_params.dir_images)\
        if f.endswith(video_writer_params.img_format)]
    )
    num_images = len(list_images)
    st.write(f"Number of images to be converted into a video : {num_images}")
    st.write(f"Video creation params - fps : {video_writer_params.fps}, video_resolution : {video_writer_params.width}x{video_writer_params.height}")
    img = cv2.imread(os.path.join(video_writer_params.dir_images, list_images[0]))
    if (img.shape[0] != video_writer_params.height or \
        img.shape[1] != video_writer_params.width):
        st.error(f"Image dimensions {img.shape[1]}x{img.shape[0]} mismatch with video dimensions {video_writer_params.width}x{video_writer_params.height}")
        return

    video_writer = cv2.VideoWriter(video_writer_params.file_video,
        cv2.VideoWriter_fourcc(*video_writer_params.video_encoder),
        video_writer_params.fps, (video_writer_params.width, video_writer_params.height)
    )

    st.write("Video generation started")
    progress_bar = st.progress(0.0)
    for i in range(num_images):
        try:
            img = cv2.imread(os.path.join(video_writer_params.dir_images, list_images[i]))
            video_writer.write(img)
            progress_bar.progress((i + 1)/ num_images)
        except IOError:
            st.error("Unknown error in image or video file handling")
            return
    video_writer.release()
    st.write(f"{video_writer_params.file_video} has been successfully created in : {dir_out}")
    st.success("Video encoding from images completed")
