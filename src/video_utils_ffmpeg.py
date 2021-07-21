import os
import sys
import argparse
import numpy as np
import streamlit as st
from dataclasses import dataclass
from subprocess import Popen, PIPE, DEVNULL

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

    cmd_ffmpeg = f"ffmpeg -framerate {ffmpeg_params.fps} -pattern_type glob -i '{ffmpeg_params.dir_images}/*{ffmpeg_params.img_format}' -c:v {ffmpeg_params.video_encoder} -profile:v high -crf {ffmpeg_params.crf} -pix_fmt {ffmpeg_params.video_pixel_format} {ffmpeg_params.file_video}"
    st.write(f"{cmd_ffmpeg}")

    try:
        os.system(cmd_ffmpeg)
    except:
        st.error("error while running ffmpeg")
        return

class FFMPEGImageToVideoWriter:
    def __init__(self, file_video, fps=30, video_encoder="libx264", width=640, height=480, pixel_format_in="bgr24", pixel_format_out="yuv420p"):
        self.dtype = np.uint8
        self.ffmpeg_params = self.FFMPEGParams(
            fps=fps, width=width, height=height,
            file_video=file_video, video_encoder=video_encoder,
            pixel_format_in=pixel_format_in,
            pixel_format_out=pixel_format_out
        )
        self.cmd_ffmpeg = self.get_ffmpeg_command()
        self.popen_params = {"stdout": DEVNULL, "stdin": PIPE}
        self.process = None

    @dataclass
    class FFMPEGParams:
        fps : int
        width : int
        height : int
        file_video : str
        video_encoder : str
        pixel_format_in : str
        pixel_format_out : str

    def open_ffmpeg_process(self):
        if self.process is None:
            self.process = Popen(self.cmd_ffmpeg, **self.popen_params)

    def close_ffmpeg_process(self):
        self.process.stdin.flush()
        self.process.communicate(input="q".encode("GBK"))

    def get_ffmpeg_command(self):
        cmd_ffmpeg = ["ffmpeg",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.ffmpeg_params.width}x{self.ffmpeg_params.height}",
            "-pix_fmt", self.ffmpeg_params.pixel_format_in,
            "-r", f"{self.ffmpeg_params.fps}",
            "-an",
            "-i", "-",
            "-c:v", self.ffmpeg_params.video_encoder,
            "-pix_fmt", self.ffmpeg_params.pixel_format_out,
            self.ffmpeg_params.file_video
        ]
        return cmd_ffmpeg

    def write_image_to_video(self, image_array):
        self.process.stdin.write(image_array.astype(self.dtype).tobytes())
