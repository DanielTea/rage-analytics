import subprocess
import os
import time
import re

def create_new_streaming_file(stream_filename="stream0", stream_link="https://www.twitch.tv/tsm_viss"):

    try:
        os.remove('./Engine/streaming_util/'+stream_filename+'.ts')
    except OSError:
        pass

    cmd = "streamlink --force --output ./Engine/streaming_util/"+stream_filename+".ts "+stream_link+" best"
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Grab stdout line by line as it becomes available.  This will loop until
    # p terminates.
    # while p.poll() is None:
    #     l = p.stdout.readline()  # This blocks until it receives a newline.
    #     print(str(l))
    #
    #     if "[cli][info] Opening stream: 1080p (hls)\n":
    #         print("match!")
    #         return

    # When the subprocess terminates there might be unconsumed output
    # that still needs to be processed.
    # print(p.stdout.read())

def test_open_file(path_to_file, attempts=0, timeout=5000, sleep_int=5):
    if attempts < timeout and os.path.exists(path_to_file) and os.path.isfile(path_to_file):
        try:
            open(path_to_file)
            return True
        except:
            # perform an action
            time.sleep(sleep_int)
            return False
