import cv2
import mss
import numpy


class ScreenCapturer:
    def __init__(self):
        super().__init__()

    @staticmethod
    def __overlay_transparent(background, overlay, x, y):
        background_width = background.shape[1]
        background_height = background.shape[0]

        if x >= background_width or y >= background_height:
            return background

        h, w = overlay.shape[0], overlay.shape[1]

        if x + w > background_width:
            w = background_width - x
            overlay = overlay[:, :w]

        if y + h > background_height:
            h = background_height - y
            overlay = overlay[:h]

        if overlay.shape[2] < 4:
            overlay = numpy.concatenate(
                [
                    overlay,
                    numpy.ones(
                        (overlay.shape[0], overlay.shape[1], 1), dtype=overlay.dtype) * 255
                ],
                axis=2,
            )

        overlay_image = overlay[..., :3]
        mask = overlay[..., 3:] / 255.0

        background[y:y + h, x:x + w] = (1.0 - mask) * \
            background[y:y + h, x:x + w] + mask * overlay_image

        return background

    def transform(self, frame, config):
        if (config):
            sct = mss.mss()
            screen = numpy.array(sct.grab(sct.monitors[1]))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
            screen = cv2.resize(screen, (1280, 720))
            if (config == "layout-1.svg"):
                scale_percent = 25  # percent of original size
                width = int(frame.shape[1] * scale_percent / 100)
                height = int(frame.shape[0] * scale_percent / 100)
                dim = (width, height)
                # resize image
                frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
                return self.__overlay_transparent(screen, frame, 1280 - width, 0)
            elif (config == "layout-2.svg"):
                scale_percent = 25  # percent of original size
                width = int(screen.shape[1] * scale_percent / 100)
                height = int(screen.shape[0] * scale_percent / 100)
                dim = (width, height)
                # resize image
                screen = cv2.resize(screen, dim, interpolation=cv2.INTER_AREA)
                return self.__overlay_transparent(frame, screen, 0, 720 - height)
            elif (config == "layout-3.svg"):
                return screen
        return frame
