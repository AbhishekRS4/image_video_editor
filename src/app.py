import os
import sys
import cv2
import streamlit as st

from video_utils_opencv import VideoWriter, VideoReader
from file_utils import get_list_images, get_abs_path, delete_file, create_directory
from video_utils_ffmpeg import FFMPEGImageToVideoWriter, FFMPEGSavedImageToVideoWriter

def saved_images_to_video_ffmpeg():
    st.title("FFMPEG - Video generator from saved images")
    st.write(f"Current working dir - {os.getcwd()}")
    fps = st.sidebar.selectbox("FPS", [10, 15, 30, 60], index=0)
    crf = st.sidebar.number_input("CRF (0-51)", value=23, min_value=0, max_value=51)
    file_video = st.sidebar.text_input("Video file to be created", "sample.mp4")
    dir_images = st.sidebar.text_input("dir to read images", "images")
    img_format = st.sidebar.selectbox("Image file format to be used", [".png", ".jpg"], index=0)
    video_encoder = st.sidebar.selectbox("Video encoder to use", ["libx264", "libx265"], index=0)
    start_button = st.sidebar.button("Start video encoding")

    file_video = get_abs_path(file_video)
    dir_images = get_abs_path(dir_images)

    if start_button:
        num_images = 0
        ffmpeg_video_writer = FFMPEGSavedImageToVideoWriter(fps=fps, crf=crf,
            file_video=file_video, dir_images=dir_images, img_format=img_format,
            video_encoder=video_encoder)
        st.write(ffmpeg_video_writer.ffmpeg_params)

        if os.path.isdir(dir_images):
            list_images = get_list_images(dir_images, img_format)
            num_images = len(list_images)
        else:
            st.error(f"not found, images dir : {dir_images}")
            return

        if os.path.isfile(file_video):
            delete_file(file_video)
            st.write(f"Deleting existing video : {file_video}")

        if num_images > fps:
            st.write(f"Images dir : {dir_images}")
            st.write(f"Starting video generation with {num_images} images")
            try:
                ffmpeg_video_writer.generate_video_from_saved_images()
                st.success(f"Video successfully created, saved in {file_video}")
            except:
                st.error("unknown ffmpeg error")
        else:
            st.error(f"Num images : {num_images}, not enough")

def streaming_images_to_video_ffmpeg():
    st.title("FFMPEG - Video generator from streaming images")
    st.write(f"Current working dir - {os.getcwd()}")
    fps = st.sidebar.selectbox("FPS", [10, 15, 30, 60], index=0)
    width = st.sidebar.number_input("Image width", value=640)
    height = st.sidebar.number_input("Image height", value=480)
    file_video = st.sidebar.text_input("Video file to be created", "sample.mp4")
    dir_images = st.sidebar.text_input("dir to read images", "images")
    img_format = st.sidebar.selectbox("Image file format to be used", [".png", ".jpg"], index=0)
    video_encoder = st.sidebar.selectbox("Video encoder to use", ["libx264", "libx265"], index=0)
    start_button = st.sidebar.button("Start video encoding")

    file_video = get_abs_path(file_video)
    dir_images = get_abs_path(dir_images)

    if start_button:
        num_images = 0
        ffmpeg_video_writer = FFMPEGImageToVideoWriter(fps=fps, width=width,
            height=height, file_video=file_video, video_encoder=video_encoder)
        st.write(ffmpeg_video_writer.ffmpeg_params)

        if os.path.isdir(dir_images):
            list_images = get_list_images(dir_images, img_format)
            num_images = len(list_images)
        else:
            st.error(f"not found, images dir : {dir_images}")
            return

        if os.path.isfile(file_video):
            delete_file(file_video)
            st.write(f"Deleting existing video : {file_video}")

        if num_images > fps:
            st.write(f"Images dir : {dir_images}")
            st.write(f"Starting video generation with {num_images} images")

            img = cv2.imread(os.path.join(dir_images, list_images[0]))
            if (img.shape[0] != height) or (img.shape[1] != width):
                st.error(f"Image dimensions {img.shape[1]}x{img.shape[0]} mismatch with video encoding dimensions {width}x{height}")
                return

            ffmpeg_video_writer.open_ffmpeg_process()
            progress_bar = st.progress(0.0)
            for i in range(num_images):
                img = cv2.imread(os.path.join(dir_images, list_images[i]))
                ffmpeg_video_writer.write_image_to_video(img)
                progress_bar.progress((i+1)/num_images)
            ffmpeg_video_writer.close_ffmpeg_process()
            st.success(f"Video successfully created, saved in {file_video}")
        else:
            st.error(f"Num images : {num_images}, not enough")

def images_to_video_opencv():
    st.title("OpenCV - Video generator from images")
    st.write(f"Current working dir - {os.getcwd()}")
    fps = st.sidebar.selectbox("FPS", [10, 15, 30, 60], index=0)
    width = st.sidebar.number_input("Image width", value=640)
    height = st.sidebar.number_input("Image height", value=480)
    file_video = st.sidebar.text_input("Video file to be created", "sample.mp4")
    dir_images = st.sidebar.text_input("Directory to read images", "images")
    img_format = st.sidebar.selectbox("Image file format to be used", [".png", ".jpg"], index=0)
    video_encoder = st.sidebar.selectbox("Video encoder to use", ["mp4v", "xvid"], index=0)
    start_button = st.sidebar.button("Start video encoding")

    file_video = get_abs_path(file_video)
    dir_images = get_abs_path(dir_images)

    if start_button:
        num_images = 0
        opencv_video_writer = VideoWriter(fps=fps, width=width, height=height,
            file_video=file_video, video_encoder=video_encoder)
        st.write(opencv_video_writer.params)

        if not os.path.isdir(dir_images):
            st.error(f"not found, images dir : {dir_images}")
            return

        dir_out = os.path.dirname(file_video)
        if not os.path.isdir(dir_out):
            _ = create_directory(dir_out)
            st.write(f"Created directory : {dir_out}")

        if os.path.isfile(file_video):
            delete_file(file_video)
            st.write(f"Deleting existing video : {file_video}")

        list_images = sorted([f for f in os.listdir(dir_images) if f.endswith(img_format)])
        num_images = len(list_images)

        if num_images > fps:
            st.write(f"Images dir : {dir_images}")
            st.write(f"Starting video generation with {num_images} images")

            img = cv2.imread(os.path.join(dir_images, list_images[0]))
            if (img.shape[0] != height or img.shape[1] != width):
                st.error(f"Image dimensions {img.shape[1]}x{img.shape[0]} mismatch with video dimensions {width}x{height}")
                return

            opencv_video_writer.init_video_writer()
            progress_bar = st.progress(0.0)
            for i in range(num_images):
                img = cv2.imread(os.path.join(dir_images, list_images[i]))
                opencv_video_writer.write_image_to_video(img)
                progress_bar.progress((i+1)/num_images)
            opencv_video_writer.close_video_writer()
            st.success(f"Video successfully created, saved in {file_video}")
        else:
            st.error(f"Num images : {num_images}, not enough")

def video_to_images_opencv():
    st.title("OpenCV - Image extractor from video")
    st.write(f"Current working dir - {os.getcwd()}")
    file_video = st.sidebar.text_input("Video file to load", "sample.mp4")
    dir_images = st.sidebar.text_input("Directory to save images", "images")
    img_prefix = st.sidebar.text_input("Prefix to use for image files", "image-")
    img_format = st.sidebar.selectbox("Image file format for saving", [".png", ".jpg"], index=0)
    img_id_start = st.sidebar.selectbox("Image start id to use", [10000, 100000, 1000000], index=0)
    start_button = st.sidebar.button("Start image extraction")

    file_video = get_abs_path(file_video)
    dir_images = get_abs_path(dir_images)

    if start_button:
        if not os.path.isfile(file_video):
            st.error(f"not found, video file: {file_video}")
            return

        opencv_video_reader = VideoReader(file_video)

        try:
            opencv_video_reader.init_video_reader()
        except:
            st.error(f"failed to load the video: {file_video}")
            return

        if not os.path.isdir(dir_images):
            _ = create_directory(dir_images)
            st.write(f"Created directory : {dir_images}")

        num_images = opencv_video_reader.get_num_images_in_video()
        st.write(f"Video file : {file_video}")
        st.write(f"Extracting {num_images} images from {file_video}")
        progress_bar = st.progress(0.0)
        for i in range(num_images):
            success, image_frame = opencv_video_reader.get_nth_image(i)
            if not success:
                break
            file_name = os.path.join(dir_images, img_prefix + str(img_id_start+i) + img_format)
            cv2.imwrite(file_name, image_frame)
            progress_bar.progress((i+1)/num_images)
        st.success(f"Extraction of {num_images} images completed, images are saved in : {dir_images}")

def image_viewer():
    st.title("Image viewer")
    st.write(f"Current working dir - {os.getcwd()}")
    dir_images = st.sidebar.text_input("Directory to load images", "images")
    img_format = st.sidebar.selectbox("Image file format for saving", [".png", ".jpg"], index=0)
    dir_images = get_abs_path(dir_images)
    try:
        st.header(f"Image dir - {dir_images}")
        list_images = sorted([f for f in os.listdir(dir_images) if f.endswith(img_format)])
        num_images = len(list_images)
        image_id = st.sidebar.slider(
            f"Select image_id ({0}-{num_images-1})", min_value=0, max_value=num_images-1,
            value=0, step=1,
        )
        img = cv2.imread(os.path.join(dir_images, list_images[image_id]))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        st.image(img, caption=list_images[image_id])
    except:
        st.error(f"not found, images dir : {dir_images}")
        return

def video_player():
    st.title("Video player")
    st.write(f"Current working dir - {os.getcwd()}")
    file_video = st.sidebar.text_input("Video file", "sample.mp4")
    file_video = get_abs_path(file_video)
    try:
        st.header(f"Playing video file - {file_video}")
        video_file_des = open(file_video, "rb")
        video_bytes = video_file_des.read()
        st.video(video_bytes)
    except:
        st.error(f"Error in loading the video file - {file_video}")
        return

video_editor_modes = {
    "FFMPEG - streaming images to video" : streaming_images_to_video_ffmpeg,
    "FFMPEG - saved images to video" : saved_images_to_video_ffmpeg,
    "OpenCV - images to video" : images_to_video_opencv,
    "OpenCV - video to images" : video_to_images_opencv,
    "Image viewer" : image_viewer,
    "Video player" : video_player,
}

def main():
    mode = st.sidebar.selectbox("Video editor modes" , list(video_editor_modes.keys()))
    video_editor_modes[mode]()

if __name__ == "__main__" :
    main()
