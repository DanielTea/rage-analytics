import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import tensorflow as tf
from flask import stream_with_context, request, Response, Flask
from flask_socketio import SocketIO, send, emit
from realtime_VideoStreamer import VideoStreamer
from realtime_RecognitionEngine_textOutput import RecognitionEngine
from keras.models import load_model
from realtime_VideoStreamer import VideoStreamer
from keras import backend as K

from realtime_RecognitionEngine_textOutput_v2 import RecognitionEngine
import multiprocessing.dummy as mp

# emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
# emotion_classifier = load_model(emotion_model_path, compile=False)
# emotion_classifier._make_predict_function()
# graph = tf.get_default_graph()

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading", ping_timeout=10000)

streamer_list = []
analyseAll = False
# r_engine = RecognitionEngine(streamer_list,  emotion_classifier, graph, queueSize=128)

@socketio.on('connect')
def handle_connect():
    print("connected")
    emit('test', "test0")

@socketio.on('disconnect')
def handle_disconnect():
    K.clear_session()
    print("disconnected")

@socketio.on('analyseAll')
def handle_analyse(arg1):
    print("changed analyse satus to " + arg1)
    analyseAll = arg1

@socketio.on('sendStreamer', namespace='/stream')
def handle_top_five_streamer(arg1):
    print("")
    print("")
    print('received args: ' + str(arg1))
    print("")
    print("")

    K.clear_session()
    emit('sessionStatus', '0') # deleted network

    tf.reset_default_graph()
    emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
    emotion_classifier = load_model(emotion_model_path, compile=False)
    emotion_classifier._make_predict_function()
    graph = tf.get_default_graph()

    emit('sessionStatus', '1')  # created Network

    link_list = arg1
    resolution = '480p'

    video_streamer_list = []

    def get_video(link):
         vs = VideoStreamer("https://www.twitch.tv"+str(link), queueSize=128, resolution=resolution, n_frame=15)
         video_streamer_list.append([link, vs])

    p = mp.Pool(len(link_list))
    p.map(get_video, link_list)
    p.close()
    p.join()

    r_engine = RecognitionEngine(video_streamer_list, emotion_classifier, graph, queueSize=128)

    emit('sessionStatus', '2')  # initialised FFMPEG

    while True:

        if r_engine.more():

            element = r_engine.read()
            text = "[" + str(element[0]) + "," + str(element[1]) + "]"
            print(text)
            emit('rageIncoming', {'link': str(element[0]), 'confidence': str(element[1])})

        else:
            continue

if __name__ == '__main__':
    socketio.run(app)
