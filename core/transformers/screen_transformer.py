import cv2
import mss
import numpy


class ScreenCapturer:
    def __init__(self):
        super().__init__()

    def transform(self, frame, config):
        if (config):
            sct = mss.mss()
            screen = numpy.array(sct.grab(sct.monitors[1]))
            return screen
