import numpy as np
import cv2
import sys

def make_frame_transparent(src):
    tmp = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    _, alpha = cv2.threshold(tmp, 0, 255, cv2.THRESH_BINARY)
    b, g, r = cv2.split(src)
    rgba = [b,g,r, alpha]
    dst = cv2.merge(rgba,4)
    return dst

video_capture = cv2.VideoCapture(0)
o_background_scene = make_frame_transparent(cv2.imread('office.jpeg'))

while(1):
    ret, frame = video_capture.read()

    # Image operation using thresholding 
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Noise removal using Morphological closing operation 
    kernel = np.ones((1, 1), np.uint8) 
    closing = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations = 10) 

    # Background area using Dialation 
    bg = cv2.dilate(closing, kernel, iterations = 2)

    # Finding foreground area
    dist_transform = cv2.distanceTransform(closing, cv2.DIST_L2, 0) 
    ret, fg = cv2.threshold(dist_transform, 0.02 * dist_transform.max(), 255, 0) 
    fg = fg.astype(np.uint8)

    # Prepare new background (scene) and foreground and finally overlay them together
    background_scene_without_fg = cv2.bitwise_and(o_background_scene, o_background_scene, mask = cv2.bitwise_not(fg))
    foreground_without_bg = make_frame_transparent(cv2.bitwise_and(frame, frame, mask = fg))
    bg_and_fg_together = cv2.add(foreground_without_bg, background_scene_without_fg)

    original_bg_without_fg = cv2.bitwise_and(frame, frame, mask = cv2.bitwise_not(fg))
    # make_frame_transparent is required here, as blur changes the shape to 3dimesion, where as the add
    # operation that is subsequently followed requires the bg to be a 4dimesion
    blurred_bg_without_fg = make_frame_transparent(cv2.blur(original_bg_without_fg,(30, 30)))
    blurred_bg_with_fg = cv2.add(blurred_bg_without_fg, foreground_without_bg)
    cv2.imshow('blurred', blurred_bg_with_fg)
    # Display the new background
    cv2.imshow('fg', bg_and_fg_together)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

video_capture.release()
cv2.destroyAllWindows()