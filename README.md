# RageAnalytics

## What it is

## How to run it

### Extension

- run the extension server under `extenstion-server/extension-server.py`
- open Chrome and go to `chrome://extensions/` 
- tick the `Developer mode` and click on `Load unpacked extension`
- upload the `extension` folder from this repo

### AI-Server

The AI-Server is located in the `engine` subfolder. The relevant files are:

```
engine/realtime_VideoStreamer.py
engine/realtime_RecognitionEngine.py
engine/output_generator_flaskserver.py
engine/video_realtime.py
engine/realtime_VideoStreamer.py
```

- 

Regarding Port-Routing:

`ssh -L 8888:localhost:8888 dt024@deepthought.mi.hdm-stuttgart.de`

`http://0.0.0.0:8888/stream_zero?link=https://www.twitch.tv/sacriel&resolution=360p`

`http://0.0.0.0:8888/stream?links=https://www.twitch.tv/a541021,https://www.twitch.tv/lostaiming,https://www.twitch.tv/fps_shaka,https://www.twitch.tv/cawai0147&resolution=360p`

`http://deepthought.mi.hdm-stuttgart.de:8888/stream?links=https://www.twitch.tv/a541021,https://www.twitch.tv/lostaiming,https://www.twitch.tv/fps_shaka,https://www.twitch.tv/cawai0147&resolution=360p`