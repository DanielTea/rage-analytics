from statistics import mode

import cv2
from keras.models import load_model
import numpy as np
from time import sleep

from Engine.utils.datasets import get_labels
from Engine.utils.inference import detect_faces
from Engine.utils.inference import draw_text
from Engine.utils.inference import draw_bounding_box
from Engine.utils.inference import apply_offsets
from Engine.utils.inference import load_detection_model
from Engine.utils.preprocessor import preprocess_input
from Engine.utils.video_transformation import trim_frame
from Engine.streaming_util.streaming_handler import create_new_streaming_file
from Engine.streaming_util.streaming_handler import test_open_file

# parameters for loading data and images
detection_model_path = './Engine/trained_models/detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_labels = get_labels('fer2013')

# streaming Parameter
stream_filename="stream0"
stream_link="https://www.twitch.tv/tsm_viss"

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

create_new_streaming_file(stream_filename=stream_filename, stream_link=stream_link)

while test_open_file("./Engine/streaming_util/"+stream_filename+".ts", attempts=0, timeout=5000, sleep_int=5) != True:
    print("stream not ready ")

sleep(10)

# ////////////////////////////////
# ///capturing mp4///
video_capture = cv2.VideoCapture('./Engine/streaming_util/'+stream_filename+'.ts')

# ///////////////////////////////
# ///capturing camera///
# video_capture = cv2.VideoCapture(0)

while True:

    success, bgr_image = video_capture.read()

    if success:
        bgr_image = trim_frame(bgr_image)
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
            cv2.imshow('window_frame', bgr_image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("end")
                break
                
        else:
            print("error no frame")
            continue