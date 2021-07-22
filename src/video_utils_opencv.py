import os
import sys
import cv2
import numpy as np
from dataclasses import dataclass

class VideoToImageWriter:
    def __init__(self, file_video, dir_images, img_prefix, img_format, img_id_start):
        """
        Parameters
        ----------
        file_video (str) : full path of video file
        dir_images (str) : full path of directory to save images
        img_prefix (str) : prefix name for image files
        img_format (str) : image file format
        img_id_start (int) : starting image id
        """
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
