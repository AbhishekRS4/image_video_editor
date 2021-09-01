import os
import sys
import cv2
import numpy as np
import streamlit as st

from file_utils import get_list_images, get_abs_path, delete_file, create_directory
from video_utils_ffmpeg import FFMPEGImageToVideoWriter, FFMPEGSavedImageToVideoWriter
from utils_opencv import VideoWriter, VideoReader, get_font_dict, get_font_preview_image, get_preview_image_with_text

def saved_images_to_video_ffmpeg():
    st.title("FFMPEG - video generator from saved images")
    st.write(f"Current working dir - {os.getcwd()}")
    fps = st.sidebar.selectbox("FPS", [10, 15, 30, 60], index=0)
    crf = st.sidebar.number_input("CRF (0-51)", value=23, min_value=0, max_value=51)
    file_video = st.sidebar.text_input("Video file to be created", "sample.mp4")
    dir_images = st.sidebar.text_input("Directory with images", "images")
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
            st.error(f"Not found, images dir : {dir_images}")
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
                st.error("Unknown ffmpeg error")
        else:
            st.error(f"Num images : {num_images}, not enough")
    return

def streaming_images_to_video_ffmpeg():
    st.title("FFMPEG - video generator from streaming images")
    st.write(f"Current working dir - {os.getcwd()}")
    dict_fonts = get_font_dict()
    fps = st.sidebar.selectbox("FPS", [10, 15, 30, 60], index=0)
    width = st.sidebar.number_input("Image width", value=640)
    height = st.sidebar.number_input("Image height", value=480)
    file_video = st.sidebar.text_input("Video file to be created", "sample.mp4")
    dir_images = st.sidebar.text_input("Directory with images", "images")
    img_format = st.sidebar.selectbox("Image file format to be used", [".png", ".jpg"], index=0)
    video_encoder = st.sidebar.selectbox("Video encoder to use", ["libx264", "libx265"], index=0)
    num_prologue_sec = st.sidebar.slider("Prologue for the video (in sec.)", value=0, min_value=0, max_value=4)
    num_epilogue_sec = st.sidebar.slider("Epilogue for the video (in sec.)", value=0, min_value=0, max_value=4)
    color_background = st.sidebar.radio("Prologue and epilogue background color", ["black", "white"], index=0)
    color_text = st.sidebar.radio("Prologue and epilogue text color", ["white", "black"], index=0)
    font_text = st.sidebar.selectbox("Select font", list(dict_fonts.keys()), index=0)
    font_scale = st.sidebar.slider("Select font scale", value=2, min_value=1, max_value=5)
    prologue_text_pos_x = st.sidebar.slider("Prologue text position x", value=250, min_value=0, max_value=int(0.75*width))
    prologue_text_pos_y = st.sidebar.slider("Prologue text position y", value=height//2, min_value=0, max_value=int(0.75*height))
    prologue_text = st.sidebar.text_input("Enter prologue text", "Title")
    epilogue_text_pos_x = st.sidebar.slider("Epilogue text position x", value=12, min_value=0, max_value=int(0.75*width))
    epilogue_text_pos_y = st.sidebar.slider("Epilogue text position y", value=height//2, min_value=0, max_value=int(0.75*height))
    epilogue_text = st.sidebar.text_input("Enter epilogue text", "Thank you, the end")
    start_button = st.sidebar.button("Start video encoding")

    file_video = get_abs_path(file_video)
    dir_images = get_abs_path(dir_images)

    st.header("Font preview image")
    font_preview_img = get_font_preview_image()
    st.image(font_preview_img, caption="Font preview image")

    if num_prologue_sec > 0:
        prologue_caption = "Prologue preview image"
        prologue_img = get_preview_image_with_text(dict_fonts[font_text], prologue_text, height, width,
            (prologue_text_pos_x, prologue_text_pos_y), color_background=color_background,
            color_text=color_text, font_scale=font_scale)
        st.header(prologue_caption)
        st.image(prologue_img, caption=prologue_caption)

    if num_epilogue_sec > 0:
        epilogue_caption = "Epilogue preview image"
        epilogue_img = get_preview_image_with_text(dict_fonts[font_text], epilogue_text, height, width,
            (epilogue_text_pos_x, epilogue_text_pos_y), color_background=color_background,
            color_text=color_text, font_scale=font_scale)
        st.header(epilogue_caption)
        st.image(epilogue_img, caption=epilogue_caption)

    if start_button:
        num_images = 0
        ffmpeg_video_writer = FFMPEGImageToVideoWriter(fps=fps, width=width,
            height=height, file_video=file_video, video_encoder=video_encoder)
        st.write(ffmpeg_video_writer.ffmpeg_params)

        if os.path.isdir(dir_images):
            list_images = get_list_images(dir_images, img_format)
            num_images_dir = len(list_images)
            num_images_prologue = num_prologue_sec * fps
            num_images_epilogue = num_epilogue_sec * fps
            num_images_blank = 2 * fps
            num_images = num_images_prologue + num_images_dir + num_images_epilogue + num_images_blank

            img = cv2.imread(os.path.join(dir_images, list_images[0]))
            if (img.shape[0] != height) or (img.shape[1] != width):
                st.error(f"Image dimensions {img.shape[1]}x{img.shape[0]} mismatch with video encoding dimensions {width}x{height}")
                return
        else:
            st.error(f"Not found, images dir : {dir_images}")
            return

        if os.path.isfile(file_video):
            delete_file(file_video)
            st.write(f"Deleting existing video : {file_video}")

        if num_images > fps:
            st.write(f"Images dir : {dir_images}")
            st.write(f"Starting video generation with {num_images} images")
            ffmpeg_video_writer.open_ffmpeg_process()
            progress_bar = st.progress(0.0)

            if num_prologue_sec > 0:
                blank_img = np.zeros((height, width, 3), dtype=np.uint8)
                for p in range(num_images_prologue):
                    ffmpeg_video_writer.write_image_to_video(prologue_img)
                    progress_bar.progress((p+1)/num_images)
                for p_b in range(fps):
                    ffmpeg_video_writer.write_image_to_video(blank_img)
                    progress_bar.progress((p+1+p_b+1)/num_images)

            for i in range(num_images_dir):
                img = cv2.imread(os.path.join(dir_images, list_images[i]))
                ffmpeg_video_writer.write_image_to_video(img)
                progress_bar.progress((p+1+p_b+1+i+1)/num_images)

            if num_epilogue_sec > 0:
                blank_img = np.zeros((height, width, 3), dtype=np.uint8)
                for e_b in range(fps):
                    ffmpeg_video_writer.write_image_to_video(blank_img)
                    progress_bar.progress((p+1+p_b+1+i+1+e_b+1)/num_images)
                for e in range(num_images_epilogue):
                    ffmpeg_video_writer.write_image_to_video(epilogue_img)
                    progress_bar.progress((p+1+p_b+1+i+1+e_b+1+e+1)/num_images)

            ffmpeg_video_writer.close_ffmpeg_process()
            st.success(f"Video successfully created, saved in {file_video}")
        else:
            st.error(f"Num images : {num_images}, not enough")
    return

def add_prologue_epilogue_to_video_ffmpeg():
    st.warning("Yet to be implemented")

def images_to_video_opencv():
    st.title("OpenCV - video generator from images")
    st.write(f"Current working dir - {os.getcwd()}")
    fps = st.sidebar.selectbox("FPS", [10, 15, 30, 60], index=0)
    width = st.sidebar.number_input("Image width", value=640)
    height = st.sidebar.number_input("Image height", value=480)
    file_video = st.sidebar.text_input("Video file to be created", "sample.mp4")
    dir_images = st.sidebar.text_input("Directory with images", "images")
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
            st.error(f"Not found, images dir : {dir_images}")
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
    return

def video_to_images_opencv():
    st.title("OpenCV - image extractor from video")
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
            st.error(f"Not found, video file: {file_video}")
            return

        opencv_video_reader = VideoReader(file_video)

        try:
            opencv_video_reader.init_video_reader()
        except:
            st.error(f"Failed to load the video: {file_video}")
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
    return

def image_viewer():
    st.title("Image viewer")
    st.write(f"Current working dir - {os.getcwd()}")
    dir_images = st.sidebar.text_input("Directory with images", "images")
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
        st.error(f"Not found, images dir : {dir_images}")
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

def app_info():
    st.title("Image and video editor app info")
    st.markdown("_About app - Useful for image and video editing_")
    st.markdown("_Developer - Abhishek R. S._")
    st.markdown("_Github - [github.com/AbhishekRS4](https://github.com/AbhishekRS4)_")
    return

video_editor_modes = {
    "FFMPEG - streaming images to video" : streaming_images_to_video_ffmpeg,
    "FFMPEG - add prologue and epilogue to video" : add_prologue_epilogue_to_video_ffmpeg,
    "FFMPEG - saved images to video" : saved_images_to_video_ffmpeg,
    "OpenCV - images to video" : images_to_video_opencv,
    "OpenCV - video to images" : video_to_images_opencv,
    "Image viewer" : image_viewer,
    "Video player" : video_player,
    "App info" : app_info,
}

def main():
    mode = st.sidebar.selectbox("Video editor modes" , list(video_editor_modes.keys()))
    video_editor_modes[mode]()

if __name__ == "__main__" :
    main()
