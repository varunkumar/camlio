import cv2
import numpy as np


def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


def make_hologram(original, scale=0.5, scaleR=3, distance=0):
    '''
        Create 3D hologram from image (must have equal dimensions)
    '''

    height = int((scale * original.shape[0]))
    width = int((scale * original.shape[1]))

    image = cv2.resize(original, (width, height),
                       interpolation=cv2.INTER_CUBIC)

    up = image.copy()
    down = rotate_bound(image.copy(), 180)
    right = rotate_bound(image.copy(), 90)
    left = rotate_bound(image.copy(), 270)

    hologram = np.zeros([max(image.shape) * scaleR + distance,
                         max(image.shape) * scaleR + distance, 3], image.dtype)

    center_x = int((hologram.shape[0]) / 2)
    center_y = int((hologram.shape[1]) / 2)

    vert_x = int((up.shape[0]) / 2)
    vert_y = int((up.shape[1]) / 2)
    hologram[0:up.shape[0], center_x - vert_x +
             distance:center_x + vert_x + distance] = up
    hologram[hologram.shape[1] - down.shape[1]:hologram.shape[1],
             center_x - vert_x + distance:center_x + vert_x + distance] = down
    hori_x = int((right.shape[0]) / 2)
    hori_y = int((right.shape[1]) / 2)
    hologram[center_x - hori_x: center_x - hori_x + right.shape[0], hologram.shape[1] -
             int(right.shape[0]) + distance: int(hologram.shape[1]) + distance] = right
    hologram[center_x - hori_x: center_x - hori_x + left.shape[0],
             0 + distance: left.shape[0] + distance] = left

    # cv2.imshow("up",up)
    # cv2.imshow("down",down)
    # cv2.imshow("left",left)
    # cv2.imshow("right",right)
    # cv2.imshow("hologram", hologram)
    # cv2.waitKey()
    return hologram


class HolgramTransformer:
    def __init__(self):
        super().__init__()
        cascPath = "transformers/haarcascade_frontalface_default.xml"
        self.faceCascade = cv2.CascadeClassifier(cascPath)
        self.face = None

    def transform(self, frame, config):
        if (config):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(100, 100)
            )

            # Draw a rectangle around the faces
            face = None
            for (x, y, w, h) in faces:
                face = frame[y:y + h, x:x + w]

            if (face is None):
                face = self.face

            if (face is None):
                face = frame

            self.face = cv2.resize(face, (460, 460),
                                   interpolation=cv2.INTER_NEAREST)
            hsv = cv2.cvtColor(self.face, cv2.COLOR_BGR2HSV)
            hsv[:, :, 2] += 255
            self.face = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            holo = make_hologram(self.face)

            x = holo.shape[1]
            y = holo.shape[0]
            left = right = int((1280 - x) / 2)
            top = bottom = int((720 - y) / 2)
            return cv2.copyMakeBorder(holo, top, bottom, left, right,
                                      cv2.BORDER_CONSTANT, value=[0, 0, 0])
