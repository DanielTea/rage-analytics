# packages to install:
# dlib - https://gist.github.com/ageitgey/629d75c1baac34dfa5ca2a1928a7aeaf
# face_recognition -

# Imports
from PIL import Image
import face_recognition
import time


def face_recognition_tester(image_path):
    # Load the jpg file into a numpy array
    image = face_recognition.load_image_file(image_path)

    # Find all the faces in the image using the default HOG-based model.
    # This method is fairly accurate, but not as accurate as the CNN model and not GPU accelerated.
    # See also: find_faces_in_picture_cnn.py
    face_locations = face_recognition.face_locations(image)

    print("I found {} face(s) in this photograph.".format(len(face_locations)))

    for face_location in face_locations:

        # Print the location of each face in this image
        top, right, bottom, left = face_location
        print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))

        # You can access the actual face itself like this:
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        pil_image.show()


def face_recognition_tester_cnn(image_path):
    # Load the jpg file into a numpy array
    image = face_recognition.load_image_file(image_path)

    # Find all the faces in the image using a pre-trained convolutional neural network.
    # This method is more accurate than the default HOG model, but it's slower
    # unless you have an nvidia GPU and dlib compiled with CUDA extensions. But if you do,
    # this will use GPU acceleration and perform well.
    # See also: find_faces_in_picture.py
    face_locations = face_recognition.face_locations(image, number_of_times_to_upsample=0, model="cnn")

    print("I found {} face(s) in this photograph.".format(len(face_locations)))

    for face_location in face_locations:
        # Print the location of each face in this image
        top, right, bottom, left = face_location
        print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom,
                                                                                                    right))

        # You can access the actual face itself like this:
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        pil_image.show()

start_time = time.time()

face_recognition_tester("images/streamer_1.png")
face_recognition_tester("images/streamer_2.png")
face_recognition_tester("images/streamer_3.png")
normal_end_time = time.time()
normal_duration = normal_end_time - start_time

face_recognition_tester_cnn("images/streamer_1.png")
face_recognition_tester_cnn("images/streamer_2.png")
face_recognition_tester_cnn("images/streamer_3.png")
cnn_end_time = time.time()
cnn_duration = cnn_end_time - normal_end_time

print("normal duration:", normal_duration, "s")
print("cnn duration:", cnn_duration, "s")

## RESULTS
# normal duration:  4.3114540576934814 s
# cnn duration:     17.572876930236816 s