# imports
import numpy as np
import pandas as pd
import time
import cv2

# VIDEO TO ARRAY
# What does this do?
# ==================
# removes inner part of frame

def trim_frame(frame, v_trim=0.25, h_trim=0.15, fill_colour=[127, 127, 127]):
    v_height = frame.shape[0]
    h_height = frame.shape[1]
    v_cut = int(v_height * v_trim)
    h_cut = int(h_height * h_trim)

    frame[v_cut:(v_height - v_cut), h_cut:(h_height - h_cut)] = fill_colour

    cv2.imshow('image', frame)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return frame

# VIDEO TO ARRAY
# What does this do?
# ==================
# gets every nth second of a video
# resize to 960x540
# save to array
# return an array of 3d numpy arrays

def video_to_array(imagePath, captureRate = 5):
    # parameters
    # capture rate = capture every nth second
    # greyscale = whether the images should be turned into greyscale

    # get video from file system
    vid_cap = cv2.VideoCapture('../../media/test-video-2-outlast-short.mp4')
    success,image = vid_cap.read()

    # calculate frameSkip
    fps = int(vid_cap.get(cv2.CAP_PROP_FPS))
    frame_skip = fps * captureRate

    processed_array = []
    count = 0
    start = time.time()

    while success:
        success,image = vid_cap.read()

        if count % frame_skip == 0:
            print('Read frame ', count)

            # resize image to fit requirements
            resized_image = cv2.resize(image, (960, 540))
            resized_image = trim_frame(resized_image)
            # add image to array to be returned
            processed_array.append(resized_image)
            # cv2.imwrite("frame%d.jpg" % count, resized_image)
        count += 1

    end = time.time()
    duration = end - start
    print("Video Length:", count/frame_skip * captureRate)
    print("Total Processing Time: %.2fs" % duration)

    return processed_array

# img_array = video_to_array(imagePath='../media/test-video-2-outlast-short.mp4')

# TESTING
# for img in img_array:
#     cv2.imshow('image', img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()



