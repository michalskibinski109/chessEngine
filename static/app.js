var times = [60, 60];
var rand_m = null;
var evaluate = 0;
// $.ajaxSetup({
//   async: false,
// });

var board = null;
var game = new Chess();

function onDragStart(source, piece, position, orientation) {
  // do not pick up pieces if the game is over
  if (game.game_over()) return false;

  // only pick up pieces for White
  if (piece.search(/^b/) !== -1) return false;
}

function makeRandomMove() {
  $(function () {
    var req = $.getJSON("/AI", {}, function (data) {
      rand_m = data.rand_m;
    });
    req.success(function(response){
    console.log(rand_m);
    game.move(rand_m);
    board.position(game.fen());
    });
  });
}

function send() {
  $(function () {
    $.getJSON(
      "/human",
      {
        move: game.history()[game.history().length - 1],
      },
      function (data) {
        evaluate = data.eval;
        console.log(evaluate)
        document.getElementById("eval").innerHTML = evaluate
      }
    );
  });
}

function onDrop(source, target) {
  // see if the move is legal
  var move = game.move({
    from: source,
    to: target,
    promotion: "q", // NOTE: always promote to a queen for example simplicity
  });

  // illegal move
  if (move === null) return "snapback";

  // make random legal move for black
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd() {
  board.position(game.fen());
  window.setTimeout(send, 250);
  window.setTimeout(makeRandomMove, 250);
}

var config = {
  draggable: true,
  position: "start",
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd,
};
board = Chessboard("myBoard", config);

function showTime() {
  //if (move > 0) times[move % 2] -= 0.1;
  document.getElementById("timeO").innerHTML = times[0].toFixed(1);
  document.getElementById("timeX").innerHTML = times[1].toFixed(1);
}

showTime();
