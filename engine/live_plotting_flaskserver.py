from flask import Flask, render_template, jsonify

app = Flask(__name__)


@app.route('/')
def main_render():

    return render_template("index.html")

@app.route('/data',  methods= ['GET',  'POST'])
def get_data():
    graph_data = open('emotion.txt', 'r').read()
    lines = str(graph_data.split('\n')[-2])
    data_list = lines.split(",")

    data = {"angry": data_list[0],
            "disgust": data_list[1],
            "fear": data_list[2],
            "happy": data_list[3],
            "sad": data_list[4],
            "surprise": data_list[5],
            "neutral": data_list[6]}

    return jsonify(data)



if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=8888, passthrough_errors=True)