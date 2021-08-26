import os
import sys
import cv2
import numpy as np
from dataclasses import dataclass
from subprocess import Popen, PIPE, DEVNULL

class FFMPEGSavedImageToVideoWriter:
    def __init__(self, dir_images, file_video, fps=30, crf=23, img_format=".png", video_encoder="libx264", video_pixel_format="yuv420p"):
        self.cmd_ffmpeg = None
        self.ffmpeg_params = self.FFMPEGParams(fps=fps, crf=crf, dir_images=dir_images,
            file_video=file_video, img_format=img_format, video_encoder=video_encoder,
            video_pixel_format=video_pixel_format)

    @dataclass
    class FFMPEGParams:
        fps : int
        crf : int
        dir_images : str
        file_video : str
        img_format : str
        video_encoder : str
        video_pixel_format : str

    def generate_video_from_saved_images(self):
        self.cmd_ffmpeg = f"ffmpeg -framerate {self.ffmpeg_params.fps} \
            -pattern_type glob -i '{self.ffmpeg_params.dir_images}/*{self.ffmpeg_params.img_format}' \
            -c:v {self.ffmpeg_params.video_encoder} -profile:v high -crf {self.ffmpeg_params.crf} \
            -pix_fmt {self.ffmpeg_params.video_pixel_format} {self.ffmpeg_params.file_video}"
        print(f"{self.cmd_ffmpeg}")

        os.system(self.cmd_ffmpeg)
        return

class FFMPEGImageToVideoWriter:
    def __init__(self, file_video, fps=30, video_encoder="libx264", width=640, height=480, pixel_format_in="bgr24", pixel_format_out="yuv420p"):
        self.dtype = np.uint8
        self.ffmpeg_params = self.FFMPEGParams(fps=fps, width=width, height=height,
            file_video=file_video, video_encoder=video_encoder,
            pixel_format_in=pixel_format_in, pixel_format_out=pixel_format_out)
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
            "-an", "-i", "-",
            "-c:v", self.ffmpeg_params.video_encoder,
            "-pix_fmt", self.ffmpeg_params.pixel_format_out,
            self.ffmpeg_params.file_video]
        return cmd_ffmpeg

    def write_image_to_video(self, image_array):
        self.process.stdin.write(image_array.astype(self.dtype).tobytes())
