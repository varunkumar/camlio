import json

import cv2
import numpy
from aiortc import VideoStreamTrack
from av import VideoFrame

from transformers.image_overlay_transformer import ImageOverlayTransformer


class CamlioVideoStreamTrack(VideoStreamTrack):
    def __init__(self, video_device_index):
        super().__init__()
        self.video_capture = cv2.VideoCapture(video_device_index)
        self.overlayTransformer = ImageOverlayTransformer()

    def setConfiguration(self, configuration):
        self.configuration = json.loads(configuration)

    async def recv(self):
        try:
            pts, time_base = await self.next_timestamp()
            ret, raw = self.video_capture.read()

            # Apply transformations based on config
            if (self.configuration["overlay"]):
                self.overlayTransformer.transform(
                    raw, self.configuration["overlay"])

            frame = VideoFrame.from_ndarray(raw, format="bgr24")
            frame.pts = pts
            frame.time_base = time_base
            return frame
        except Exception as e:
            print(e)
