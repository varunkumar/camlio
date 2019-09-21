import cv2
import numpy
import os
from transformer_utils import make_frame_transparent

class SceneTransformer:
  def __init__(self):
    super().__init__()
    self.scene_base_path = os.path.abspath('../core/scenes')

  def transform(self, frame, config):
    img_name = config['scene']
    o_background_scene = make_frame_transparent(cv2.imread(os.path.join(self.scene_base_path, img_name)))
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
    return bg_and_fg_together
