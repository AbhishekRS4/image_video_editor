import os
import sys
import cv2
import streamlit as st

from video_utils_opencv import VideoToImageWriter, ImageToVideoWriter

def images_to_video_opencv():
    st.title("Video creator from images - opencv")
    st.write(f"Current working directory - {os.getcwd()}")
    fps = st.sidebar.selectbox("FPS", [10, 15, 30, 60], index=0)
    width = st.sidebar.number_input("Image width", value=640)
    height = st.sidebar.number_input("Image height", value=480)
    file_video = st.sidebar.text_input("Video file to be created", "sample.mp4")
    dir_images = st.sidebar.text_input("Directory to read images", "images")
    img_format = st.sidebar.selectbox("Image file format to be used", [".png", ".jpg"], index=0)
    video_encoder = st.sidebar.selectbox("Video encoder to use", ["mp4v", "xvid"], index=0)
    video_writer = ImageToVideoWriter(
        fps=fps,
        width=width,
        height=height,
        file_video=file_video,
        dir_images=dir_images,
        img_format=img_format,
        video_encoder=video_encoder
    )
    start_button = st.sidebar.button("Start video encoding")
    if start_button:
        st.write(video_writer.params)
        video_writer.generate_video_from_images()

def video_to_images_opencv():
    st.title("Image extractor from video - opencv")
    st.write(f"Current working directory - {os.getcwd()}")
    file_video = st.sidebar.text_input("Video file to load", "sample.mp4")
    dir_images = st.sidebar.text_input("Directory to save images", "images")
    img_prefix = st.sidebar.text_input("Prefix to use for image files", "image-")
    img_format = st.sidebar.selectbox("Image file format for saving", [".png", ".jpg"], index=0)
    img_id_start = st.sidebar.selectbox("Image start id to use", [10000, 100000, 1000000], index=0)
    image_writer = VideoToImageWriter(
        file_video=file_video,
        dir_images=dir_images,
        img_prefix=img_prefix,
        img_format=img_format,
        img_id_start=img_id_start
    )
    start_button = st.sidebar.button("Start image extraction")
    if start_button:
        st.write(image_writer.params)
        image_writer.generate_images_from_video()

def image_viewer():
    st.title("Image viewer")
    st.write(f"Current working directory - {os.getcwd()}")
    dir_images = st.sidebar.text_input("Directory to load images", "images")
    img_format = st.sidebar.selectbox("Image file format for saving", [".png", ".jpg"], index=0)
    try:
        st.header(f"Image directory - {dir_images}")
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
        st.error(f"Images directory {dir_images} does not contain images")
        return

def video_player():
    st.title("Video player")
    st.write(f"Current working directory - {os.getcwd()}")
    file_video = st.sidebar.text_input("Video file", "sample.mp4")
    try:
        st.header(f"Playing video file - {file_video}")
        video_file_des = open(file_video, "rb")
        video_bytes = video_file_des.read()
        st.video(video_bytes)
    except:
        st.error(f"Error in loading the video file - {file_video}")
        return


video_editor_modes = {
    "Images to video opencv" : images_to_video_opencv,
    "Video to images opencv" : video_to_images_opencv,
    "Image viewer" : image_viewer,
    "Video player" : video_player,
}

def main():
    mode = st.sidebar.selectbox("Video editor modes" , list(video_editor_modes.keys()))
    video_editor_modes[mode]()

if __name__ == "__main__" :
    main()
