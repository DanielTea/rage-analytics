from statistics import mode
from threading import Thread
from queue import Queue
import cv2
from keras.models import load_model
import numpy as np
import tensorflow as tf

from Engine.utils.datasets import get_labels
from Engine.utils.inference import detect_faces
from Engine.utils.inference import draw_text
from Engine.utils.inference import draw_bounding_box
from Engine.utils.inference import apply_offsets
from Engine.utils.inference import load_detection_model
from Engine.utils.preprocessor import preprocess_input

class RecognitionEngine:
    def __init__(self, VideoStreamer, queueSize=128, use_gpu=False, gpu_number=0):

        self.VideoStreamer = VideoStreamer
        # parameters for loading data and images
        self.emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'

        # TODO implement gpu capability
        self.use_gpu=use_gpu
        self.gpu_numbber=gpu_number

        # loading models
        self.Q = Queue(maxsize=queueSize)

        self.emotion_classifier = load_model(self.emotion_model_path, compile=False)
        self.emotion_classifier._make_predict_function()
        self.graph = tf.get_default_graph()

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

            if self.VideoStreamer.more():

                bgr_image = self.VideoStreamer.read()

                # sleep(1/30)

                # bgr_image = trim_frame(bgr_image)
                gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
                rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

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
                        # print(str(emotion_prediction))

                    # angry = emotion_prediction[0][0]
                    # disgust = emotion_prediction[0][1]
                    # fear = emotion_prediction[0][2]
                    # happy = emotion_prediction[0][3]
                    # sad = emotion_prediction[0][4]
                    # surprise = emotion_prediction[0][5]
                    # neutral = emotion_prediction[0][6]

                    # with open('../emotion.txt', 'a') as f:
                    #     f.write('{},{},{},{},{},{},{}\n'.format(angry, disgust, fear, happy, sad, surprise, neutral))

                    emotion_probability = np.max(emotion_prediction)
                    emotion_label_arg = np.argmax(emotion_prediction)
                    emotion_text = emotion_labels[emotion_label_arg]
                    emotion_window.append(emotion_text)

                    if len(emotion_window) > frame_window:
                        emotion_window.pop(1)
                    try:
                        emotion_mode = mode(emotion_window)
                    except:
                        continue

                    if emotion_text == 'angry':
                        color = emotion_probability * np.asarray((255, 0, 0))
                    elif emotion_text == 'sad':
                        color = emotion_probability * np.asarray((0, 0, 255))
                    elif emotion_text == 'happy':
                        color = emotion_probability * np.asarray((255, 255, 0))
                    elif emotion_text == 'surprise':
                        color = emotion_probability * np.asarray((0, 255, 255))
                    else:
                        color = emotion_probability * np.asarray((0, 255, 0))

                    color = color.astype(int)
                    color = color.tolist()

                    draw_bounding_box(face_coordinates, rgb_image, color)
                    draw_text(face_coordinates, rgb_image, emotion_mode,
                              color, 0, -45, 1, 1)

                    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

                    if not self.Q.full():
                        self.Q.put(bgr_image)
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