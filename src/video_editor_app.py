import os
import sys
import streamlit as st
from video_utils_opencv import ImageWriterParams, VideoWriterParams, extract_images_from_video, create_video_from_images

def imgs_to_vid_opencv():
    st.title("Video creator from images - opencv")
    st.write(f"Current working directory - {os.getcwd()}")
    fps = st.sidebar.selectbox("FPS", [10, 15, 30, 60], index=0)
    width = st.sidebar.number_input("Image width", value=640)
    height = st.sidebar.number_input("Image height", value=480)
    file_video = st.sidebar.text_input("Video file to be created", "sample.mp4")
    dir_images = st.sidebar.text_input("Directory to read images", "images")
    img_format = st.sidebar.selectbox("Image file format to be used", [".png", ".jpg"], index=0)
    video_encoder = st.sidebar.selectbox("Video encoder to use", ["mp4v", "xvid"], index=0)
    video_writer_params = VideoWriterParams(
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
        st.write(video_writer_params)
        create_video_from_images(video_writer_params)

def vid_to_imgs_opencv():
    st.title("Image extractor from video - opencv")
    st.write(f"Current working directory - {os.getcwd()}")
    file_video = st.sidebar.text_input("Video file to load", "sample.mp4")
    dir_images = st.sidebar.text_input("Directory to save images", "images")
    img_prefix = st.sidebar.text_input("Prefix to use for image files", "image-")
    img_format = st.sidebar.selectbox("Image file format for saving", [".png", ".jpg"], index=0)
    img_id_start = st.sidebar.selectbox("Image start id to use", [10000, 100000, 1000000], index=0)
    image_writer_params = ImageWriterParams(
        file_video=file_video,
        dir_images=dir_images,
        img_prefix=img_prefix,
        img_format=img_format,
        img_id_start=img_id_start
    )
    start_button = st.sidebar.button("Start image extraction")
    if start_button:
        st.write(image_writer_params)
        extract_images_from_video(image_writer_params)

video_editor_modes = {
    "Images to video opencv" : imgs_to_vid_opencv,
    "Video to images opencv" : vid_to_imgs_opencv,
}

def main():
    mode = st.sidebar.selectbox("Video editor modes" , list(video_editor_modes.keys()))
    video_editor_modes[mode]()

if __name__ == "__main__" :
    main()
