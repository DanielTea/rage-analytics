import streamlink
import numpy
from threading import Thread
import subprocess as sp
from queue import Queue

class VideoStreamer:
    def __init__(self, twitch_url, queueSize=128, resolution='720p', n_frame=10):
        self.stopped = False
        self.twitch_url = twitch_url
        self.res = resolution
        self.n_frame = n_frame

        # initialize the queue used to store frames read from
        # the video stream
        self.Q = Queue(maxsize=queueSize)
        self.create_pipe()
        self.start_buffer()

    def create_pipe(self):

        streams = streamlink.streams(self.twitch_url)

        print("available streams: "+ str(streams))
        stream = streams[self.res]

        if self.res == "720p":

            self.byte_lenght = 1280
            self.byte_width = 720

        elif self.res == "360p":

            self.byte_lenght = 640
            self.byte_width = 360

        self.stream_url = stream.url

        self.pipe = sp.Popen(['ffmpeg', "-i", self.stream_url,
                         "-loglevel", "quiet",  # no text output
                         "-an",  # disable audio
                         "-f", "image2pipe",
                         "-pix_fmt", "bgr24",
                         "-vcodec", "rawvideo", "-"],
                        stdin=sp.PIPE, stdout=sp.PIPE)

    def start_buffer(self):
        # start a thread to read frames from the file video stream
        t = Thread(target=self.update_buffer, args=())
        t.daemon = True
        t.start()
        return self

    def update_buffer(self):

        count_frame = 0

        while True:

            if count_frame % self.n_frame == 0:

                raw_image = self.pipe.stdout.read(
                    self.byte_lenght * self.byte_width * 3)  # read length*width*3 bytes (= 1 frame)

                frame = numpy.fromstring(raw_image, dtype='uint8').reshape((self.byte_width, self.byte_lenght, 3))

                if not self.Q.full():
                    self.Q.put(frame)
                    count_frame += 1
                else:
                    count_frame += 1
                    continue
            else:
                count_frame += 1
                continue

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True