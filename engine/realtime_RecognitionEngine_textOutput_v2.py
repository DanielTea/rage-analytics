from statistics import mode
from threading import Thread
from queue import Queue
import cv2
import numpy as np
import tensorflow as tf
import face_recognition

from Engine.utils.datasets import get_labels
from Engine.utils.inference import detect_faces
from Engine.utils.inference import apply_offsets
from Engine.utils.inference import load_detection_model
from Engine.utils.preprocessor import preprocess_input


class RecognitionEngine:
    def __init__(self, VideoStreamer_list, emotion_classifier, graph, queueSize=128, use_gpu=False, gpu_number=0):

        self.VideoStreamer_list = VideoStreamer_list
        # parameters for loading data and images

        # TODO implement gpu capability
        self.use_gpu = use_gpu
        self.gpu_number = gpu_number

        # loading models
        self.Q = Queue(maxsize=queueSize)

        self.emotion_classifier = emotion_classifier
        self.graph = graph

        # getting input model shapes for inference
        self.emotion_target_size = self.emotion_classifier.input_shape[1:3]

        self.start_buffer()

    def start_buffer(self):
        # start a thread to read frames from the file video stream
        p = Thread(target=self.update_buffer, args=())
        p.daemon = True
        p.start()
        return self

    def update_buffer(self):

        #        detection_model_path = './Engine/trained_models/detection_models/haarcascade_frontalface_default.xml'
        #        face_detection = load_detection_model(detection_model_path)
        # hyper-parameters for bounding boxes shape
        frame_window = 10
        emotion_offsets = (20, 40)
        emotion_labels = {0: "angry", 1: "fear", 2: "happy", 3: "sad", 4: "surprise", 5: "neutral"}

        # starting lists for calculating modes
        emotion_window = []

        while True:

            for element in self.VideoStreamer_list:

                if element[1].more():

                    bgr_image = element[1].read()

                    # print(str(faces))

                    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

                    # Resize frame of video to 1/4 size for faster face recognition processing
                    #                    small_frame = cv2.resize(rgb_image, (0, 0), fx=0.25, fy=0.25)
                    small_frame = rgb_image
                    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)


                    gray_image = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

                    # cv2.imshow('Video', gray_image)

                    # Only process every other frame of video to save time

                    # Find all the faces and face encodings in the current frame of video
                    face_locations = face_recognition.face_locations(small_frame)
                    # face_locations = face_recognition.face_locations(frame)

                    for (top, right, bottom, left) in face_locations:

                        gray_face = gray_image[top:bottom, left:right]

                        try:
                            gray_face = cv2.resize(gray_face, (self.emotion_target_size))
                        except:
                            continue

                        gray_face = preprocess_input(gray_face, True)
                        gray_face = np.expand_dims(gray_face, 0)
                        gray_face = np.expand_dims(gray_face, -1)

                        with self.graph.as_default():
                            emotion_prediction = self.emotion_classifier.predict(gray_face)

                        percentage = np.amax(emotion_prediction)
                        emotion_label_arg = np.argmax(emotion_prediction)
                        emotion_text = emotion_labels[emotion_label_arg]

                        if not self.Q.full():

                            self.Q.put([element[0], emotion_text, percentage])

                        else:
                            continue
                else:
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
