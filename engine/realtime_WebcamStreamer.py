from threading import Thread
from queue import Queue

import cv2

class WebcamVideoStream:
    def __init__(self, src=0, queueSize=128):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        self.Q = Queue(maxsize=queueSize)

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            if not self.Q.full():
                (grabbed, frame) = self.stream.read()

                self.Q.put(frame)
            else:
                continue

            # otherwise, read the next frame from the stream


    def read(self):
        # return the frame most recently read
        return self.Q.get()

    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
