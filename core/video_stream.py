import json

import cv2
import numpy
from aiortc import VideoStreamTrack
from av import VideoFrame

from transformers.image_overlay_transformer import ImageOverlayTransformer
from transformers.screen_transformer import ScreenCapturer


class CamlioVideoStreamTrack(VideoStreamTrack):
    def __init__(self, video_device_index):
        super().__init__()
        self.video_capture = cv2.VideoCapture(video_device_index)
        self.overlayTransformer = ImageOverlayTransformer()
        self.screenCapturer = ScreenCapturer()

    def setConfiguration(self, configuration):
        self.configuration = json.loads(configuration)

    async def recv(self):
        try:
            pts, time_base = await self.next_timestamp()
            ret, raw = self.video_capture.read()

            # Apply transformations based on config
            if (self.configuration and "overlay" in self.configuration.keys()):
                self.overlayTransformer.transform(
                    raw, self.configuration["overlay"])

            if (self.configuration and "presentation" in self.configuration.keys()):
                raw = self.screenCapturer.transform(
                    raw, self.configuration["presentation"])

            frame = VideoFrame.from_ndarray(raw, format="bgr24")
            frame.pts = pts
            frame.time_base = time_base
            return frame
        except Exception as e:
            print(e)
