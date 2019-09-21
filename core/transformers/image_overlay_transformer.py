import cv2


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
