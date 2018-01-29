import itertools
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import cv2
from keras.models import load_model

from engine.Engine.utils.datasets import get_labels
from engine.Engine.utils.inference import detect_faces
from engine.Engine.utils.preprocessor import preprocess_input
from engine.Engine.utils.video_transformation import trim_frame
from engine.Engine.streaming_util.streaming_handler import create_new_streaming_file

emotion_model_path = '/Users/danieltremer/Documents/GIT-Repositories/rageanalytics-new/engine/Engine/trained_models/emotion_models/fer2013_simple_CNN.50-0.67.hdf5

emotion_classifier = load_model(emotion_model_path, compile=False)