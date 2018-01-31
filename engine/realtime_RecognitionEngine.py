from statistics import mode
from threading import Thread
from queue import Queue
import cv2
from keras.models import load_model
import numpy as np
import tensorflow as tf
import face_recognition

from Engine.utils.datasets import get_labels
from Engine.utils.preprocessor import preprocess_input

class RecognitionEngine:

    def __init__(self, VideoStreamer, queueSize=10, use_gpu=False, gpu_number=0):

        self.VideoStreamer = VideoStreamer
        # parameters for loading data and images
        # self.emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
        self.emotion_model_path = './Engine/trained_models/emotion_models/fer_cohn_disgust_to_anger_Tiny_XCEPTION_67.hdf5'

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

        count = 0

        # emotion_labels = get_labels('fer2013')
        # emotion_labels ={0:"angry", 1:"happy", 2:"sad", 3:"surprise", 4:"neutral", 5:"fear"}
        emotion_labels = {0: "angry", 1: "fear", 2: "happy", 3: "sad", 4: "surprise", 5: "neutral"}



        # starting lists for calculating modes
        emotion_window = []
        face_names = []
        frame_window = 10

        # Load our overlay image: mustache.png


        while True:

            frame = self.VideoStreamer.read()

            if count %2000 == 0:



                # Resize frame of video to 1/4 size for faster face recognition processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

                # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                # rgb_small_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # rgb_small_frame = small_frame[:, :, ::-1]

                gray_image = cv2.cvtColor(rgb_small_frame, cv2.COLOR_BGR2GRAY)

                # cv2.imshow('Video', gray_image)

                # Only process every other frame of video to save time

                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                # face_locations = face_recognition.face_locations(frame)
                print(face_locations)

                if face_locations != None:

                    for (top, right, bottom, left) in face_locations:

                        gray_face = gray_image[top:bottom, left:right]

                        # cv2.imshow('Faces', gray_face)

                        try:
                            gray_face = cv2.resize(gray_face, (self.emotion_target_size))
                        except:
                            continue

                        gray_face = preprocess_input(gray_face, True)
                        gray_face = np.expand_dims(gray_face, 0)
                        gray_face = np.expand_dims(gray_face, -1)
                        emotion_prediction = self.emotion_classifier.predict(gray_face)



                        # angry = emotion_prediction[0][0]
                        # disgust = emotion_prediction[0][1]
                        # fear = emotion_prediction[0][2]
                        # happy = emotion_prediction[0][3]
                        # sad = emotion_prediction[0][4]
                        # surprise = emotion_prediction[0][5]
                        # neutral = emotion_prediction[0][6]

                        # with open('../emotion.txt', 'a') as f:
                        #     f.write(
                        #         '{},{},{},{},{},{},{}\n'.format(angry, disgust, fear, happy, sad, surprise, neutral))

                        emotion_probability = np.max(emotion_prediction)
                        emotion_label_arg = np.argmax(emotion_prediction)
                        # print(emotion_prediction)

                        emotion_text = emotion_labels[emotion_label_arg]

                        output_text = str(emotion_text) + " " + "%d" % (round(emotion_probability, 2) * 100) + "%"

                        emotion_window.append(output_text)

                        # if len(emotion_window) > frame_window:
                        #     emotion_window.pop(1)
                        # try:
                        #     emotion_mode = mode(emotion_window)
                        # except:
                        #     continue

                        # name = output_text

                        if emotion_text == 'angry':
                            color = np.asarray((0, 0, 255))
                            color_text = (255, 255, 255)
                        # elif emotion_text == 'disgust':
                        #     color = np.asarray((88, 105, 126))
                        #     color_text = (255, 255, 255)
                        elif emotion_text == 'fear':
                            color = np.asarray((160, 160, 160))
                            color_text = (255, 255, 255)
                        elif emotion_text == 'happy':
                            color = np.asarray((0, 255, 255))
                            color_text = (0, 0, 0)
                        elif emotion_text == 'sad':
                            color = np.asarray(( 255, 0, 0))
                            color_text = (255, 255, 255)
                        elif emotion_text == 'surprise':
                            color = np.asarray((136, 73, 143))
                            color_text = ( 255, 255, 255)

                        elif emotion_text == 'neutral':
                            # emotion_text= 'neutral'
                            color = np.asarray((83, 221, 108))
                            color_text = (255, 255, 255)

                        output_text = str(emotion_text) + " " + "%d" % (round(emotion_probability, 2) * 100) + "%"
                        emotion_window.append(output_text)
                        name = output_text


                        color = color.astype(int)
                        color = color.tolist()

                        face_names.append(name)

                        print(output_text)

                        top *= 4
                        right *= 4
                        bottom *= 4
                        left *= 4


                        # Draw a box around the face
                        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

                        # Draw a label with a name below the face
                        cv2.rectangle(frame, (left, bottom - 30), (right, bottom), color, cv2.FILLED)
                        font = cv2.FONT_HERSHEY_DUPLEX

                        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, color_text, 1)

                    if not self.Q.full():
                        self.Q.put(frame)
                        count +=1

                    else:
                        with self.Q.mutex:
                            self.Q.queue.clear()

                        print("clean queue")
                        continue

                else:
                    self.Q.put(frame)
                    count += 1
            else:
                count += 1

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True