import os, signal
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

import sys
import subprocess
from flask import Flask, g
from flask_socketio import SocketIO, send, emit
import json

f = open("./pid.txt", 'r+')
text = ("test")
f.seek(0)
f.write(text)
f.truncate()
f.close()



app = Flask(__name__)
socketio = SocketIO(app, async_mode="threading", ping_timeout=10000)

analyseAll = False

# r_engine = RecognitionEngine(streamer_list,  emotion_classifier, graph, queueSize=128)

@socketio.on('connect', namespace='/stream')
def handle_connect():
    print("connected")
    emit('test', 'test0', namespace='/stream')

@socketio.on('message', namespace='/stream')
def handle_message(arg1):
    print(arg1)
    emit('test', 'test1', namespace='/stream')

@socketio.on('disconnect', namespace='/stream')
def handle_disconnect():
    print('disconnected')

@socketio.on('analyseAll', namespace='/stream')
def handle_analyse(arg1):
    print("changed analyse satus to " + arg1)
    analyseAll = arg1

@socketio.on('sendStreamer', namespace='/stream')
def handle_top_five_streamer(arg1):

    with open('pid.txt', 'r') as f:
        first_line = f.readline()

    if first_line == "test":
        print("first access")
    else:
        os.kill(int(first_line), signal.SIGKILL)
        print(int(first_line)+"killed")

    argument = arg1
    print(argument)
    arg = str(json.dumps(argument))

    command = ["/Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6", "/Users/danieltremer/Documents/GIT-Repositories/rageanalytics-new/engine/hacky_site_switch_main.py", arg]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while True:
        line = p.stdout.readline()
        # error = p.stderr.readline()
        # stdout.append(line)
        # print(error)
        print(str(line))
        # print(line[0:5])
        if line == b"sessionStatus 0\n":
            emit('sessionStatus', '0', namespace='/stream')  # deleted network
        elif line[0:4] == b"pid ":
            pid = str(line[4:-1].decode("utf-8"))
            print(pid)
            f = open("./pid.txt", 'r+')
            text = (pid)
            f.seek(0)
            f.write(text)
            f.truncate()
            f.close()

        elif line == b"sessionStatus 1\n":
            emit('sessionStatus', '1', namespace='/stream')
        elif line == b"sessionStatus 2\n":
            emit('sessionStatus', '2', namespace='/stream')
        elif line[0:5] == b"123, ":
            print(line[5:-1])
            # print(dict(str(line[5:-1])[2:]))
            emit('rageIncoming', json.dumps(str(line[5:-1])[2:]),
                 namespace='/stream', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=5000)
