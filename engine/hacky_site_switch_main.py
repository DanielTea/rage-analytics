import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
pid = os.getpid()
print("pid "+str(pid))

print('sessionStatus 0')

import tensorflow as tf
from flask import stream_with_context, request, Response, Flask, g
from flask_socketio import SocketIO, send, emit
from keras.models import load_model
from realtime_VideoStreamer import VideoStreamer
from keras import backend as K
import time
import datetime

from realtime_RecognitionEngine_textOutput_v2 import RecognitionEngine
import multiprocessing.dummy as mp

emotion_model_path = './Engine/trained_models/emotion_models/fer_cohn_disgust_to_anger_Tiny_XCEPTION_67.hdf5'
emotion_classifier = load_model(emotion_model_path, compile=False)
emotion_classifier._make_predict_function()

import json
from sys import argv

print(argv[1])

arg1=json.loads(argv[1])


print("")
print('RECEIVED: ' + str(arg1))
print("")

# tf.reset_default_graph()
graph = tf.get_default_graph()

print('sessionStatus 1')  # created Network

link_list = arg1['streamer']
game = arg1['game']

resolution = '720p'
video_streamer_list = []

def get_video(link):
     vs = VideoStreamer("https://www.twitch.tv"+str(link), queueSize=128, resolution=resolution, n_frame=15)
     video_streamer_list.append([link, vs])

p = mp.Pool(len(link_list))
p.map(get_video, link_list)
p.close()
p.join()

print("")
print("STARTING TO ANALYSE " + str(len(link_list)) + " streams")
print("")


r_engine = RecognitionEngine(video_streamer_list, emotion_classifier, graph, queueSize=128)

print('sessionStatus 2')  # initialised FFMPEG

while True:

    if r_engine.more():

        element = r_engine.read()
        text = "[" + str(element[0]) + ", " +str(element[1]) + ", " + str(element[2]) + "]"

        # with open('emotion_logging.txt', 'a') as f:
        #     f.write("{};{};{};{};{}\n".format(str(element[0]), str(element[1]), str(element[2]), str(game), datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
        #     f.close()

        if element[1] == "angry":
            print('123, {"link":'+str(element[0])+', "confidence":'+str(element[2])+', "game":'+game+'}')

    else:
        continue