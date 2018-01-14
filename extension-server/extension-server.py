from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
from random import randint


app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def main_render():
    return render_template("index.html")


@socketio.on('message')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))

@socketio.on('sendStreamer')
def handle_top_five_streamer(arg1):
    print('received args: ' + str(arg1))


    if (randint(0,10) > 3):
        print("rage")
        emit('rageIncoming', str(arg1[randint(0, 4)]))
    else:
        print("no rage")
        emit('rageIncoming', "%no-rage")


#http://127.0.0.1:5000/
if __name__ == '__main__':
    socketio.run(app)
    #app.run(debug = True, host='0.0.0.0', port=8888, passthrough_errors=True, threaded=True)


