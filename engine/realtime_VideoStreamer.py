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
        self.stopped = False

        # initialize the queue used to store frames read from
        # the video stream
        self.Q = Queue(maxsize=queueSize)
        checkIfStreamsWorks = self.create_pipe()

        if checkIfStreamsWorks:
            self.start_buffer()

    def create_pipe(self):
        streamer_name = self.twitch_url.split("/")[3]


        try:
            streams = streamlink.streams(self.twitch_url)
        except streamlink.exceptions.NoPluginError:
            print("NO STREAM AVAILABLE for " + streamer_name)
            return False
        except:
            print("NO STREAM AVAILABLE no exception " + streamer_name)
            return False

        #print("available streams: "+ str(streams))

        resolutions = {'360p': {"byte_lenght": 640, "byte_width": 360}, '480p': {"byte_lenght": 854, "byte_width": 480}, '720p': {"byte_lenght": 1280, "byte_width": 720}, '1080p': {"byte_lenght": 1920, "byte_width": 1080}}

        if self.res in streams:
            finalRes = self.res
        else:
            for key in resolutions:
                if key != self.res and key in streams:
                    print("USED FALL BACK " + key)
                    finalRes = key
                    break
            else: # das else gehört zur foor loop! wenn sie nicht breaked dann wird der teil ausgeführt https://docs.python.org/2/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops
                print("COULD NOT FIND STREAM " + streamer_name)
                return False

        self.byte_lenght = resolutions[finalRes]["byte_lenght"]
        self.byte_width = resolutions[finalRes]["byte_width"]

        print("FINAL RES " + finalRes + " " + streamer_name)

        stream = streams[finalRes]
        self.stream_url = stream.url

        self.pipe = sp.Popen(['ffmpeg', "-i", self.stream_url,
                         "-loglevel", "quiet",  # no text output
                         "-an",  # disable audio
                         "-f", "image2pipe",
                         "-pix_fmt", "bgr24",
                         "-vcodec", "rawvideo", "-"],
                        stdin=sp.PIPE, stdout=sp.PIPE)
        return True

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
