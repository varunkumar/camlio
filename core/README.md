# Camlio Core

Core module responsible for processing webcam stream

## Start engine

```bash
python engine.py --port 8081 --cert-file secrets/server.crt --key-file secrets/server.key --video_device_index=4
```

### FAQs

1. How to find the webcam index?

```bash
ffmpeg -f avfoundation -list_devices true -i ""
```
