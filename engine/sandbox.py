import cv2
import numpy
import subprocess as sp

from PIL import Image



# command = [ 'ffmpeg',
#             '-i', '/Users/danieltremer/Documents/GIT-Repositories/rage-analytics/Engine/streaming_util/foo.ts',
#             '-s', '1600x900', "/Users/danieltremer/Documents/GIT-Repositories/rage-analytics/Engine/streaming_util/img%d.jpg"]
#
#
#
# pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)
# print(pipe.stdout.read(2))

# import streamlink
#
# streams = streamlink.streams("https://www.twitch.tv/tsm_viss")
# stream = streams["best"]
# fd = stream.open()
# data = fd.read(1900*900)
#
# print(data)
# fd.close()
#
#
# # read 420*360*3 bytes (= 1 frame)
# # raw_image = pipe.stdout.read(1600*900*3)
# # # transform the byte read into a numpy array
# # image =  numpy.fromstring(raw_image, dtype='uint8')
# # image = image.reshape((900,1600,3))
# #
# # img = Image.fromarray(image, 'RGB')
# # img.show()
#
# print(pipe)
# # throw away the data in the pipe's buffer.
# pipe.stdout.flush()
#

# streamlink https://www.twitch.tv/tsm_viss best --stdout | ffmpeg -i pipe:0 -c copy -bsf:a aac_adtstoasc -f mp4 -movflags empty_moov+separate_moof+frag_keyframe pipe:1

import subprocess
import numpy as np
import cv2

# cmd = "streamlink https://www.twitch.tv/tsm_viss best --stdout | ffmpeg -i pipe:0 -c copy -bsf:a aac_adtstoasc -f mp4 -movflags empty_moov+separate_moof+frag_keyframe pipe:1"
#
# proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
# cap = cv2.VideoCapture(proc.stdout.read(proc))
#
# print(cap)
# bytes=''


cap = cv2.VideoCapture('/Users/danieltremer/Documents/GIT-Repositories/rage-analytics/Engine/streaming_util/foo.ts')
fnum = 0
while(True):
    # Capture frame-by-frame
    success, bgr_image = cap.read()

    if success:
        print(bgr_image)
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite('messigray.png', rgb_image)
        cv2.imshow('window_frame', bgr_image)
    else:
        continue

# When everything done, release the capture
cap.release()

# while True:
# # to read mjpeg frame -
#     bytes+= str(proc.stdout.read(1600*900*3))
#
#     print(str(proc.stdout.read(1600*900*3)))
#
#     a = bytes.find('\xff\xd8')
#     b = bytes.find('\xff\xd9')
#
#     if a!=-1 and b!=-1:
#         jpg = bytes[a:b+2]
#         bytes= bytes[b+2:]
#         img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
#         cv2.imwrite('messigray.png', img)
#         # cv2.imshow('cam2', img)
#         # if cv2.waitKey(1) ==27:
#         #     exit(0)
#     else:
#         continue

    # if a!=-1 and b!=-1:
    #     jpg = bytes[a:b+2]
    #     bytes= bytes[b+2:]
    #
    #     frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.CV_LOAD_IMAGE_COLOR)
    #     # we now have frame stored in frame.
    #     print(frame)
    #
    #     cv2.imshow('cam2', frame)

    # Press 'q' to quit
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

# while True:
#     raw_image = proc.stdout.read(1600 * 900 * 3)
#     print(raw_image)
#
#     cv2.imshow('image', raw_image)
#     cv2.waitKey()
#     cv2.destroyAllWindows()
#
#     if not raw_image:
#         break
#     image =  numpy.fromstring(raw_image, dtype='uint8').reshape((640, 360, 3))
