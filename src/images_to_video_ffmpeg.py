import os
import sys
import argparse
import streamlit as st
from dataclasses import dataclass

@dataclass
class FFMPEGVideoWriterParams:
    fps : int
    crf : int
    dir_images : str
    file_video : str
    img_format : str
    video_encoder : str
    video_pixel_format : str

def create_video_from_images(ffmpeg_params):
    """
    Parameters
    ----------
    ffmpeg_params (FFMPEGVideoWriterParams) : object of class FFMPEGVideoWriterParams
    """
    if not os.path.isdir(ffmpeg_params.dir_images):
        st.error(f"Images directory {ffmpeg_params.dir_images} does not exist")
        return

    if os.path.isfile(ffmpeg_params.file_video):
        st.write(f"Deleting the already existing video file : {ffmpeg_params.file_video}")
        os.unlink(ffmpeg_params.file_video)

    ffmpeg_cmd = f"ffmpeg -framerate {ffmpeg_params.fps} -pattern_type glob -i '{ffmpeg_params.dir_images}/*{ffmpeg_params.img_format}' -c:v {ffmpeg_params.video_encoder} -profile:v high -crf {ffmpeg_params.crf} -pix_fmt {ffmpeg_params.video_pixel_format} {ffmpeg_params.file_video}"
    st.write(f"{ffmpeg_cmd}")

    try:
        os.system(ffmpeg_cmd)
    except:
        st.error("error while running ffmpeg")
        return
