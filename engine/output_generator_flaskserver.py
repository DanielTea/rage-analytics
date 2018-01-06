from flask import stream_with_context, request, Response, Flask
from realtime_VideoStreamer import VideoStreamer
from realtime_RecognitionEngine_textOutput import RecognitionEngine
from keras.models import load_model
import tensorflow as tf

app = Flask(__name__)

#EXAMPLE LINK:
# http://0.0.0.0:8888/stream_zero?link=https://www.twitch.tv/p4wnyhof&resolution=360p

emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_classifier = load_model(emotion_model_path, compile=False)
emotion_classifier._make_predict_function()
graph = tf.get_default_graph()


@app.route('/stream_zero')
def streamed_response_zero():

    link = request.args.get('link', '')
    resolution = request.args.get('resolution', '')

    vs = VideoStreamer(link, queueSize=128, resolution=resolution)
    r_engine = RecognitionEngine(vs, emotion_classifier, graph, queueSize=128)

    def generate():

        # loop over frames from the video file stream
        while True:

            if r_engine.more():

                text = r_engine.read()
                yield text+','

            else:
                continue

    return Response(stream_with_context(generate()))

@app.route('/stream_one')
def streamed_response_one():

    link = request.args.get('link', '')
    resolution = request.args.get('resolution', '')

    vs = VideoStreamer(link, queueSize=128, resolution=resolution)
    r_engine = RecognitionEngine(vs, emotion_classifier, graph, queueSize=128)

    def generate():

        # loop over frames from the video file stream
        while True:

            if r_engine.more():

                text = r_engine.read()
                yield text+','

            else:
                continue

    return Response(stream_with_context(generate()))


if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8888, passthrough_errors=True)