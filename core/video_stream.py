import json

import cv2
import numpy
from aiortc import VideoStreamTrack
from av import VideoFrame

from transformers.blur_bg_transformer import BlurBgTransformer
from transformers.hologram_transformer import HolgramTransformer
from transformers.image_overlay_transformer import ImageOverlayTransformer
from transformers.scene_transformer import SceneTransformer
from transformers.screen_transformer import ScreenCapturer


class CamlioVideoStreamTrack(VideoStreamTrack):
    def __init__(self, video_device_index):
        super().__init__()
        self.video_capture = cv2.VideoCapture(video_device_index)
        self.overlayTransformer = ImageOverlayTransformer()
        self.screenCapturer = ScreenCapturer()
        self.hologramTransformer = HolgramTransformer()
        self.blur_bg_transformer = BlurBgTransformer()
        self.scene_transformer = SceneTransformer()

    def setConfiguration(self, configuration):
        self.configuration = json.loads(configuration)

    async def recv(self):
        try:
            pts, time_base = await self.next_timestamp()
            ret, raw = self.video_capture.read()

            # Apply transformations based on config
            if (self.configuration and "scene" in self.configuration.keys()):
                raw = self.scene_transformer.transform(
                    raw, self.configuration["scene"])
                raw = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)

            if (self.configuration and "blur" in self.configuration and self.configuration["blur"]):
                raw = self.blur_bg_transformer.transform(raw)
                raw = cv2.cvtColor(raw, cv2.COLOR_BGRA2BGR)

            if (self.configuration and "overlay" in self.configuration.keys()):
                self.overlayTransformer.transform(
                    raw, self.configuration["overlay"])

            if (self.configuration and "presentation" in self.configuration.keys()):
                raw = self.screenCapturer.transform(
                    raw, self.configuration["presentation"])

            if (self.configuration and "hologram" in self.configuration.keys()):
              # TODO: remove background
                raw = self.hologramTransformer.transform(
                    raw, self.configuration["hologram"])

            frame = VideoFrame.from_ndarray(raw, format="bgr24")
            frame.pts = pts
            frame.time_base = time_base
            return frame
        except Exception as e:
            print(e)
