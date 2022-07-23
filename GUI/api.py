#$env:pythonpath += ";c:/Users/miskibin/Desktop/CHESS_ENGINE/"
import sys 
sys.path.append('') # fixing import problem [temporary solution] 

from flask import Flask, request,render_template, jsonify
from src.engine import ChessEngine
from src.PosEvaluator import PosEvaluator


app = Flask(__name__) 

eng = ChessEngine(depth = 2)


@app.route("/")
def index_func():
    return render_template("index.html")


@app.route("/human")
def human_move():
    h_move = request.args.get('move', 0, type=str)
    eng.push_move(h_move) 
    return jsonify(eval = PosEvaluator(eng.board)())

@app.route("/AI")
def ai_func():
    move = eng.find_move()
    print(f'eng move: {move}')
    eng.push_move(move) 
    return jsonify(rand_m = move)


if __name__ == '__main__':
    app.run(debug=False, port=5678)