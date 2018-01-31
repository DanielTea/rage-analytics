from statistics import mode
import time

import cv2
from keras.models import load_model
import numpy as np
from time import sleep
import imutils

from realtime_WebcamStreamer import WebcamVideoStream
from Engine.utils.datasets import get_labels
from Engine.utils.inference import detect_faces
from Engine.utils.inference import draw_text
from Engine.utils.inference import draw_bounding_box
from Engine.utils.inference import apply_offsets
from Engine.utils.inference import load_detection_model
from Engine.utils.preprocessor import preprocess_input
from engine.realtime_RecognitionEngine import RecognitionEngine

# parameters for loading data and images
detection_model_path = './Engine/trained_models/detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_labels = get_labels('fer2013')

# hyper-parameters for bounding boxes shape
frame_window = 10
emotion_offsets = (20, 40)

# loading models
face_detection = load_detection_model(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

# starting lists for calculating modes
emotion_window = []

# starting video streaming
cv2.namedWindow('window_frame', cv2.WINDOW_NORMAL)

vs = WebcamVideoStream(src=0).start()
r_engine =RecognitionEngine(vs)


while True:

    frame = r_engine.read()

    cv2.imshow('window_frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("end")
        break

