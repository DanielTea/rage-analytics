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
cv2.namedWindow('window_frame')

vs = WebcamVideoStream(src=0).start()

while True:

    # if vs.more():

    bgr_image = vs.read()
    bgr_image= imutils.resize(bgr_image, width=1700)

    # sleep(1/30)

    #bgr_image = trim_frame(bgr_image)
    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

    faces = detect_faces(face_detection, gray_image)

    for face_coordinates in faces:

        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]
        try:
            gray_face = cv2.resize(gray_face, (emotion_target_size))
        except:
            continue

        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_prediction = emotion_classifier.predict(gray_face)

        angry = emotion_prediction[0][0]
        disgust = emotion_prediction[0][1]
        fear = emotion_prediction[0][2]
        happy = emotion_prediction[0][3]
        sad = emotion_prediction[0][4]
        surprise = emotion_prediction[0][5]
        neutral = emotion_prediction[0][6]

        with open('../emotion.txt', 'a') as f:
            f.write('{},{},{},{},{},{},{}\n'.format(angry, disgust, fear, happy, sad, surprise, neutral))

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
            color = emotion_probability * np.asarray((186,18,0))
        elif emotion_text == 'disgust':
            color = emotion_probability * np.asarray((126,105,88))
        elif emotion_text == 'fear':
            color = emotion_probability * np.asarray((255, 255, 255))
        elif emotion_text == 'happy':
            color = emotion_probability * np.asarray((255,186,8))
        elif emotion_text == 'sad':
            color = emotion_probability * np.asarray((45,114,143))
        elif emotion_text == 'surprise':
            color = emotion_probability * np.asarray((136,73,143))
        elif emotion_text == 'neutral':
            color = emotion_probability * np.asarray((83,221,108))

        color = color.astype(int)
        color = color.tolist()

        draw_bounding_box(face_coordinates, rgb_image, color)
        draw_text(face_coordinates, rgb_image, emotion_mode,
                  color, 0, -45, 1, 1)


    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    cv2.imshow('window_frame', bgr_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("end")
        break

