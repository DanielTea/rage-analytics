import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import ctypes

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

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading", ping_timeout=10000)

analyseAll = False

# r_engine = RecognitionEngine(streamer_list,  emotion_classifier, graph, queueSize=128)

@socketio.on('connect', namespace='/stream')
def handle_connect():
    print("connected")
    emit('test', 'test0', namespace='/stream')

@socketio.on('message', namespace='/stream')
def handle_message(arg1):
    print(arg1)
    emit('test', 'test1', namespace='/stream')

@socketio.on('disconnect', namespace='/stream')
def handle_disconnect():
    #K.clear_session()
    print('disconnected')

@socketio.on('analyseAll', namespace='/stream')
def handle_analyse(arg1):
    print("changed analyse satus to " + arg1)
    analyseAll = arg1

@socketio.on('sendStreamer', namespace='/stream')
def handle_top_five_streamer(arg1):

    print("")
    print('RECEIVED: ' + str(arg1))
    print("")

    emit('sessionStatus', '0', namespace='/stream') # deleted network

    tf.reset_default_graph()
    graph = tf.get_default_graph()

    emit('sessionStatus', '1', namespace='/stream')  # created Network

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

    emit('sessionStatus', '2', namespace='/stream')  # initialised FFMPEG

    while True:

        if r_engine.more():

            element = r_engine.read()
            text = "[" + str(element[0]) + ", " +str(element[1]) + ", " + str(element[2]) + "]"
            print(text)

            with open('emotion_logging.txt', 'a') as f:
                f.write("{};{};{};{};{}\n".format(str(element[0]), str(element[1]), str(element[2]), str(game), datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')))
                f.close()

            if element[1] == "angry":
                emit('rageIncoming', {'link': str(element[0]), 'confidence': str(element[2]), 'game':game}, namespace='/stream', broadcast=True)

        else:
            continue

if __name__ == '__main__':
    socketio.run(app, port=5000)
