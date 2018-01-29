from statistics import mode
from threading import Thread
from queue import Queue
import cv2
import numpy as np
import tensorflow as tf

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
        self.use_gpu=use_gpu
        self.gpu_number=gpu_number

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
        p.daemon=True
        p.start()
        return self

    def update_buffer(self):

        detection_model_path = './Engine/trained_models/detection_models/haarcascade_frontalface_default.xml'
        face_detection = load_detection_model(detection_model_path)
        # hyper-parameters for bounding boxes shape
        frame_window = 10
        emotion_offsets = (20, 40)
        emotion_labels = get_labels('fer2013')

        # starting lists for calculating modes
        emotion_window = []

        while True:

            for element in self.VideoStreamer_list:

                if element[1].more():

                    bgr_image = element[1].read()

                    # sleep(1/30)

                    # bgr_image = trim_frame(bgr_image)
                    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)

                    faces = detect_faces(face_detection, gray_image)
                    # print(str(faces))

                    for face_coordinates in faces:

                        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
                        gray_face = gray_image[y1:y2, x1:x2]
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
