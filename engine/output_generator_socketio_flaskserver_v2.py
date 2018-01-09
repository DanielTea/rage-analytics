import tensorflow as tf
from flask import stream_with_context, request, Response, Flask
from flask_socketio import SocketIO, send, emit
from engine.realtime_RecognitionEngine_textOutput import RecognitionEngine
from keras.models import load_model
from engine.realtime_VideoStreamer import VideoStreamer

from engine.realtime_RecognitionEngine_textOutput_v2_copy import RecognitionEngine

app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading")

#EXAMPLE LINK:
# http://0.0.0.0:8888/stream?links=https://www.twitch.tv/a541021,https://www.twitch.tv/lostaiming,https://www.twitch.tv/fps_shaka,https://www.twitch.tv/cawai0147&resolution=360p


streamer_list = []
# r_engine = RecognitionEngine(streamer_list,  emotion_classifier, graph, queueSize=128)


from threading import Thread, Event

THREAD = Thread()


class emitData(Thread):
    """Stream data on thread"""

    def __init__(self, arguments):
        self.arguments = arguments
        self._stop_event = Event()
        super(emitData, self).__init__()


    def stop(self):
        self._stop_event.set()

    def get_data(self):
        """
        Get data and emit to socket
        """
        # tf.clear_session()
        emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
        emotion_classifier = load_model(emotion_model_path, compile=False)
        emotion_classifier._make_predict_function()
        graph = tf.get_default_graph()

        print('received args: ' + str(self.arguments))
        socketio.emit("test", "test1")

        link_list = self.arguments
        resolution = '360p'

        video_streamer_list = []

        for link in link_list:
            vs = VideoStreamer("https://www.twitch.tv" + str(link), queueSize=128, resolution=resolution, n_frame=15)
            video_streamer_list.append([link, vs])

        r_engine = RecognitionEngine(video_streamer_list, emotion_classifier, graph, queueSize=128)
        socketio.emit('test', "test2")
        while True:

            if r_engine.more():

                element = r_engine.read()
                text = str(element[0])
                print(text)
                socketio.emit('rageIncoming', {'link': str(element[0]), 'confidence': str(element[1])},
                              namespace='/stream')

            else:
                continue

    def run(self):
        """Default run method"""
        self.get_data()

@socketio.on('sendStreamer', namespace='/stream')
def handle_top_five_streamer(arg1):
    """Handle socket connection"""
    global THREAD

    # if THREAD.isAlive():
    #     THREAD.stop()

    # Start thread
    if not THREAD.isAlive():
        THREAD = emitData(arguments=arg1)
        THREAD.start()

if __name__ == '__main__':
    socketio.run(app)

    # app.run(debug = True, host='0.0.0.0', port=8888, passthrough_errors=True, threaded=True)