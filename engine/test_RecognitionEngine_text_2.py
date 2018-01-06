from realtime_VideoStreamer import VideoStreamer
from realtime_RecognitionEngine_textOutput_v2 import RecognitionEngine
from keras.models import load_model
import tensorflow as tf

emotion_model_path = './Engine/trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_classifier = load_model(emotion_model_path, compile=False)
emotion_classifier._make_predict_function()
graph = tf.get_default_graph()

link1 = "https://www.twitch.tv/a541021"
link2 = "https://www.twitch.tv/lostaiming"
link3 = "https://www.twitch.tv/fps_shaka"
link4 = "https://www.twitch.tv/cawai0147"

linklist = [link1, link2, link3, link4]
video_streamer_list = []

for link in linklist:

    vs = VideoStreamer(link, queueSize=128, resolution="720p")
    video_streamer_list.append([link, vs])


r_engine = RecognitionEngine(video_streamer_list, emotion_classifier, graph, queueSize=128)

# loop over frames from the video file stream
while True:

        if r_engine.more():

            element = r_engine.read()
            print(str(element[0])+" , "+str(element[1]))

        else:
            continue