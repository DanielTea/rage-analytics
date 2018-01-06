from flask import stream_with_context, request, Response, Flask
from realtime_VideoStreamer import VideoStreamer
from realtime_RecognitionEngine_textOutput_v2 import RecognitionEngine
from keras.models import load_model
import tensorflow as tf

app = Flask(__name__)

#EXAMPLE LINK:
# http://0.0.0.0:8888/stream?links=https://www.twitch.tv/a541021,https://www.twitch.tv/lostaiming,https://www.twitch.tv/fps_shaka,https://www.twitch.tv/cawai0147&resolution=360p


streamer_list = []
# r_engine = RecognitionEngine(streamer_list,  emotion_classifier, graph, queueSize=128)


@app.route('/stream')
def streamed_response():
    emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
    emotion_classifier = load_model(emotion_model_path, compile=False)
    emotion_classifier._make_predict_function()
    graph = tf.get_default_graph()

    links = request.args.get('links', '')
    resolution = request.args.get('resolution', '')

    link_list = links.split(',')
    print("links: "+ str(link_list))

    video_streamer_list = []

    for link in link_list:
        vs = VideoStreamer(link, queueSize=128, resolution=resolution, n_frame=15)
        video_streamer_list.append([link, vs])

    r_engine = RecognitionEngine(video_streamer_list, emotion_classifier, graph, queueSize=128)

    def generate():

        # loop over frames from the video file stream
        while True:

            if r_engine.more():

                element = r_engine.read()
                text = "["+str(element[0]) + "," + str(element[1])+"]"
                print(text)

                yield text+","

            else:
                continue

    return Response(stream_with_context(generate()))


if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8888, passthrough_errors=True, threaded=True)