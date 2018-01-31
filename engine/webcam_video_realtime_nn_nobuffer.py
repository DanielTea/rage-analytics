import face_recognition
import cv2

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

# loading models
face_detection = load_detection_model(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

vs = WebcamVideoStream(src=0).start()

cv2.namedWindow('Faces')

frame_window = 10
emotion_window = []
cv2.namedWindow('Video')

# video_capture = cv2.VideoCapture(0)

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    # Grab a single frame of video
    frame = vs.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    # rgb_small_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # rgb_small_frame = small_frame[:, :, ::-1]

    gray_image = cv2.cvtColor(rgb_small_frame, cv2.COLOR_BGR2GRAY)

    # cv2.imshow('Video', gray_image)

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        # face_locations = face_recognition.face_locations(frame)

        for (top, right, bottom, left) in face_locations:

            gray_face = gray_image[top:bottom, left:right]

            cv2.imshow('Faces', gray_face)

            try:
                gray_face = cv2.resize(gray_face, (emotion_target_size))
            except:
                continue

            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            emotion_prediction = emotion_classifier.predict(gray_face)
            emotion_probability = np.max(emotion_prediction)

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

            output_text = str(emotion_text) + " " + "%d" % (round(emotion_probability, 2) * 100) + "%"

            emotion_window.append(output_text)

            if len(emotion_window) > frame_window:
                emotion_window.pop(1)
            try:
                emotion_mode = mode(emotion_window)
            except:
                continue

            if emotion_text == 'angry':
                color = np.asarray((186, 18, 0))
            elif emotion_text == 'disgust':
                color = np.asarray((126, 105, 88))
            elif emotion_text == 'fear':
                color = np.asarray((255, 255, 255))
            elif emotion_text == 'happy':
                color = np.asarray((255, 186, 8))
            elif emotion_text == 'sad':
                color = np.asarray((45, 114, 143))
            elif emotion_text == 'surprise':
                color = np.asarray((136, 73, 143))
            elif emotion_text == 'neutral':
                color = np.asarray((83, 221, 108))

            color = color.astype(int)
            color = color.tolist()


            name = output_text
            face_names.append(name)

            print(output_text)

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
vs.release()
cv2.destroyAllWindows()