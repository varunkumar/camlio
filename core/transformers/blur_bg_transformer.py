import cv2
import numpy as np


def make_frame_transparent(src):
    tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    b, g, r = cv2.split(src)
    rgba = [b, g, r, alpha]
    dst = cv2.merge(rgba, 4)
    return dst


class BlurBgTransformer:
    def __init__(self):
        super().__init__()

    def transform(self, frame):
        # Image operation using thresholding
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Noise removal using Morphological closing operation
        kernel = np.ones((1, 1), np.uint8)
        closing = cv2.morphologyEx(
            thresh, cv2.MORPH_CLOSE, kernel, iterations=10)

        # Finding foreground area
        dist_transform = cv2.distanceTransform(closing, cv2.DIST_L2, 0)
        ret, fg = cv2.threshold(dist_transform, 0.02 *
                                dist_transform.max(), 255, 0)
        fg = fg.astype(np.uint8)
        foreground_without_bg = make_frame_transparent(
            cv2.bitwise_and(frame, frame, mask=fg))
        original_bg_without_fg = cv2.bitwise_and(
            frame, frame, mask=cv2.bitwise_not(fg))
        # make_frame_transparent is required here, as blur changes the shape to 3dimesion, where as the add
        # operation that is subsequently followed requires the bg to be a 4dimesion
        blurred_bg_without_fg = make_frame_transparent(
            cv2.blur(original_bg_without_fg, (30, 30)))
        blurred_bg_with_fg = cv2.add(
            blurred_bg_without_fg, foreground_without_bg)
        return blurred_bg_with_fg
