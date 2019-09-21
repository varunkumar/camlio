import argparse
import asyncio
import json
import logging
import os
import platform
import ssl

import aiohttp_cors
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

from video_stream import CamlioVideoStreamTrack

ROOT = os.path.dirname(__file__)


async def configure(request):
    params = await request.json()
    videoStream.configuration = params["configuration"]

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"200": "OK"}
        ),
    )


async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print("ICE connection state is %s" % pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    # open media source
    if args.play_from:
        player = MediaPlayer(args.play_from)
    else:
        player = None

    await pc.setRemoteDescription(offer)
    for t in pc.getTransceivers():
        if t.kind == "audio" and player and player.audio:
            pc.addTrack(player.audio)
        elif t.kind == "video":
            pc.addTrack(videoStream)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


pcs = set()


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

videoStream = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Camlio engine")
    parser.add_argument("--video-device-index",
                        help="Index of video camera", type=int, default=0)
    parser.add_argument("--cert-file", help="SSL certificate file (for HTTPS)")
    parser.add_argument("--key-file", help="SSL key file (for HTTPS)")
    parser.add_argument(
        "--play-from", help="Read the media from a file and stream it."),
    parser.add_argument(
        "--port", type=int, default=8080, help="Port for HTTP server (default: 8080)"
    )
    parser.add_argument("--verbose", "-v", action="count")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    if args.cert_file:
        ssl_context = ssl.SSLContext()
        ssl_context.load_cert_chain(args.cert_file, args.key_file)
    else:
        ssl_context = None

    videoStream = CamlioVideoStreamTrack(args.video_device_index)
    videoStream.configuration = {
        "overlay": [{"position": {"top": 0, "left": 0}, "text": "Varunkumar Nagarajan"}, {"position": {"top": 100, "left": 0}, "text": "Sreekanth Gunda"}],
    }
    app = web.Application()
    cors = aiohttp_cors.setup(app, defaults={
        # Allow all to read all CORS-enabled resources from
        # *.
        "*": aiohttp_cors.ResourceOptions(expose_headers="*",
                                          allow_headers="*"),
    })
    app.on_shutdown.append(on_shutdown)
    cors.add(
        app.router.add_route("POST", "/offer", offer)
    )
    cors.add(
        app.router.add_route("POST", "/configure", configure)
    )
    web.run_app(app, port=args.port, ssl_context=ssl_context)
