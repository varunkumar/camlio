import cv2


class ImageOverlayTransformer:
    def __init__(self):
        super().__init__()

    @staticmethod
    def __draw_label(img, text, pos, bg_color):
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        scale = 10
        color = (0, 0, 0)
        thickness = cv2.FILLED
        margin = 2

        txt_size = cv2.getTextSize(text, font_face, scale, thickness)
        end_x = pos[0] + txt_size[0][0] + margin
        end_y = pos[1] + txt_size[0][1] + margin

        cv2.rectangle(img, pos, (end_x, end_y), bg_color, thickness)
        cv2.putText(img, text, pos, font_face, scale,
                    color, 10, cv2.LINE_AA, False)

    def transform(self, frame, config):
        if (config and len(config) > 0):
            for item in config:
                if (item["text"]):
                    self.__draw_label(
                        frame, item["text"], (item["position"]["top"], item["position"]["left"]), (0, 0, 255))
