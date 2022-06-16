import numpy as np
from engine import ChessEngine
from flask import Flask, request,render_template, jsonify


app = Flask(__name__) 

eng = ChessEngine()


@app.route("/")
def index_func():
    return render_template("index.html")


@app.route("/human")
def human_move():
    h_move = request.args.get('move', 0, type=str)
    eng.push(h_move) 
    return jsonify(eval = eng.evaluate_pos())

@app.route("/AI")
def ai_func():
    move = eng.make_move()
    eng.push(move) 
    print(move)
    return jsonify(rand_m = move)




app.run(debug=False, port=5678)