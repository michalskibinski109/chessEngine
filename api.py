from flask import Flask, request,render_template, jsonify
from engine import ChessEngine


app = Flask(__name__) 

eng = ChessEngine(depth = 2)


@app.route("/")
def index_func():
    return render_template("index.html")


@app.route("/human")
def human_move():
    h_move = request.args.get('move', 0, type=str)
    eng.push_move(h_move) 
    return jsonify(eval = eng.evaluate_pos())

@app.route("/AI")
def ai_func():
    move = eng.find_move()
    print(f'eng move: {move}')
    eng.push_move(move) 
    print(eng.evaluations, eng.time_on_move)
    return jsonify(rand_m = move)


if __name__ == '__main__':
    app.run(debug=False, port=5678)