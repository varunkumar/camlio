import cv2
import numpy


class ImageOverlayTransformer:
    def __init__(self):
        super().__init__()

    @staticmethod
    def __draw_label(img, text, pos, bg, fg):
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1
        bg_color = (bg["blue"], bg["green"], bg["red"])
        fg_color = (fg["blue"], fg["green"], fg["red"])
        thickness = cv2.FILLED
        margin = 10

        txt_size = cv2.getTextSize(text, font_face, scale, thickness)
        end_x = pos[0] + txt_size[0][0] - margin
        end_y = pos[1] + txt_size[0][1] - margin

        cv2.rectangle(img, (pos[0] - margin, pos[1] + margin),
                      (end_x + 20, end_y - 40), bg_color, thickness)
        cv2.putText(img, text, pos, font_face, scale,
                    fg_color, 1, cv2.LINE_AA, False)

    @staticmethod
    def __overlay_transparent1(background, overlay, x, y):
        background_width = background.shape[1]
        background_height = background.shape[0]

        if x >= background_width or y >= background_height:
            return background

        rows, cols, channels = overlay.shape
        overlay = cv2.addWeighted(
            background[y:y+rows, x:x+cols], 0.8, overlay, 0.5, 0)
        background[y:y+rows, x:x+cols] = overlay

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
        if (config and len(config) > 0):
            for item in config:
                bg_color = {
                    "red": 200,
                    "green": 200,
                    "blue": 200
                }
                if ("bg_color" in item.keys()):
                    bg_color = item.bg_color
                fg_color = {
                    "red": 128,
                    "green": 0,
                    "blue": 0
                }
                if ("fg_color" in item.keys()):
                    fg_color = item.fg_color
                if ("text" in item.keys()):
                    self.__draw_label(
                        frame, item["text"], (item["position"]["left"], item["position"]["top"]), bg_color, fg_color)
                elif ("image" in item.keys()):
                    img = cv2.imread(item["image"])
                    # self.__overlay_transparent(
                    #    frame, img, item["position"]["left"], item["position"]["top"])
                    self.__overlay_transparent1(
                        frame, img, item["position"]["left"], item["position"]["top"])
