from realtime_VideoStreamer import VideoStreamer
from realtime_RecognitionEngine import RecognitionEngine
import cv2

link = "https://www.twitch.tv/jk_fifa"

vs = VideoStreamer(link, queueSize=128, resolution="720p")
r_engine = RecognitionEngine(vs, queueSize=128)

# loop over frames from the video file stream
while True:

    if r_engine.more():

        frame = r_engine.read()
        cv2.imshow("Frame", frame)

        # sleep(1/30)
        cv2.waitKey(1)

    else:
        continue