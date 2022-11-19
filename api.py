from flask import Flask, request, render_template, jsonify, Response
from engine.engine import ChessEngine
from miskibin import get_logger

LOGGER = get_logger(lvl=10)

app = Flask(__name__)
engine = ChessEngine(depth=5)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/move", methods=["POST"])
def move():
    data = request.get_json()
    move = str(data["from"] + data["to"])
    engine.push_from_san(move)
    evaluation = engine.evaluate(engine.board)
    return jsonify({"evaluation": round(evaluation, 2)})


@app.route("/AI", methods=["GET"])
def AI():
    # data = request.get_json()
    # LOGGER.warn(f"Received data: {data}")
    move = engine.get_best_move()
    san_move = engine.board.san(engine.board.parse_san(move[0]))
    LOGGER.warning(f"AI move: {san_move}")
    engine.push_from_san(move[0])
    return jsonify({"move": san_move, "evaluation": move[1]})


if __name__ == "__main__":
    app.run(debug=False, port=5678)
