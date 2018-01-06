from realtime_VideoStreamer import VideoStreamer
from realtime_RecognitionEngine_textOutput import RecognitionEngine

link = "https://www.twitch.tv/sacriel"

vs = VideoStreamer(link, queueSize=128, resolution="720p")
r_engine = RecognitionEngine(vs, queueSize=128)

# loop over frames from the video file stream
while True:

    if r_engine.more():

        text = r_engine.read()
        print(text)

    else:
        continue