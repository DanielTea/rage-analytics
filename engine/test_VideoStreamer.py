from realtime_VideoStreamer import VideoStreamer
import cv2

link = "https://www.twitch.tv/destiny"

vs = VideoStreamer(link, queueSize=256, resolution="720p")

# loop over frames from the video file stream
while True:

    if vs.more():

        frame = vs.read()
        cv2.imshow("Frame", frame)

        # sleep(1/30)
        cv2.waitKey(1)

    else:
        continue