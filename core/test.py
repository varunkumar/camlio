import asyncio

import cv2
from av import VideoFrame

from video_stream import CamlioVideoStreamTrack

loop = asyncio.get_event_loop()


videoStream = CamlioVideoStreamTrack(4)
videoStream.configuration = {
    "overlay": [{"position": {"top": 700, "left": 850}, "text": "Varunkumar Nagarajan"},
                {"position": {"top": 20, "left": 20}, "image": "./overlay/arc.png"}, {"position": {"left": 20, "top": 600}, "image": "./overlay/camlio.png"}],
    # "presentation": {"layout": 1}
    "hologram": 1
}


async def execute():
    while(1):
        frame = await videoStream.recv()
        cv2.imshow("Image", frame.to_ndarray())

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            break

cv2.destroyAllWindows()
asyncio.ensure_future(execute())
loop.run_forever()
