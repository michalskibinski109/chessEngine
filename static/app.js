var times = [30 * 60, 30 * 60];
var engine_move = null;
var evaluate = 0;
// $.ajaxSetup({
//   async: false,
// });

var illegal_audio = new Audio("/static/sounds/illegal.wav");
var move_self_audio = new Audio("/static/sounds/move-self.wav");
var capture_audio = new Audio("/static/sounds/minceraft_capture.wav");
var check_audio = new Audio("/static/sounds/move-check.wav");
var frajer_audio = new Audio("/static/sounds/frajer.mp3");

document.getElementById("timeO").innerHTML =
  Math.floor(times[1] / 60) + ":" + (times[1] % 60 ? times[1] % 60 : "00");
document.getElementById("timeX").innerHTML =
  Math.floor(times[0] / 60) + ":" + (times[0] % 60 ? times[0] % 60 : "00");

var board = null;
var game = new Chess();
function onDragStart(source, piece, position, orientation) {
  // do not pick up pieces if the game is over
  if (game.game_over()) return false;

  // only pick up pieces for White
  if (piece.search(/^b/) !== -1) return false;
}

// get computer move from AI/

// post human move to server and get computer move
function sendMove() {
  console.log("onMoveEnd");
  if (game.game_over()) {
    alert("Game over");
    return;
  }
  if (game.turn() == "b") {
    var move = game.history({ verbose: true }).slice(-1)[0];
    var move = {
      from: move.from,
      to: move.to,
      promotion: move.promotion,
    };
    $.ajax({
      type: "POST",
      url: "/move",
      data: JSON.stringify(move),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function (data) {
        console.log("from server: ", data);
      },
      failure: function (errMsg) {
        alert(errMsg);
      },
    });
  }
}

// get computer move from server
function getServerMove() {
  $.ajax({
    type: "GET",
    url: "/AI",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (data) {
      console.log("get from server: ", data);
      var move = game.move(data.move);
      board.position(game.fen());
      if (move === null) {
        illegal_audio.play();
        alert("Illegal move");
      } else {
        if (move.captured) {
          capture_audio.play();
        } else {
          move_self_audio.play();
        }
        if (game.in_check()) {
          check_audio.play();
        }
      }
    },
    failure: function (errMsg) {
      alert(errMsg);
    },
  });
}

function makeComputermMove() {
  $(function () {
    var req = $.getJSON("/AI", {}, function (data) {
      engine_move = data.move;
    });
    req.success(function (response) {
      game.move(engine_move);
      board.position(game.fen());
      console.log("from engine: ", engine_move);
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
        evaluate = data.evaluation;
        document.getElementById("eval").innerHTML = evaluate.toFixed(1);
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
  window.setTimeout(sendMove, 250);
  window.setTimeout(getServerMove, 550);
}

function onChange(oldPos, newPos) {
  //tutaj wyswietlam pgn
  var history = "";
  var temp = game.history();

  for (var i = 0; i < temp.length; i++) {
    if (i % 2 === 0) {
      history +=
        (Math.round(i / 2) + 1).toString() +
        "." +
        " ".repeat(4 - (Math.round(i / 2) + 1).toString().length) +
        temp[i] +
        " ".repeat(7 - temp[i].length);
    } else {
      history += temp[i] + " <br/>";
    }
  }
  document.getElementById("pgn").innerHTML = history;
  var scroll = document.getElementById("pgn");
  scroll.scrollTop = scroll.scrollHeight;
  //koniec wyswietlania

  //gram dzwieki
  if (Object.keys(newPos).length < Object.keys(oldPos).length)
    capture_audio.play();
  else if (game.in_check()) check_audio.play();
  else if (game.game_over()) frajer_audio.play();
  else move_self_audio.play();
}

var config = {
  draggable: true,
  position: "start",
  onDragStart: onDragStart,
  onDrop: onDrop,
  onChange: onChange,
  onSnapEnd: onSnapEnd,
};
board = Chessboard("myBoard", config);

function showTime() {
  if (game.history().length != 0) {
    times[game.history().length % 2] -= 1;

    document.getElementById("timeO").innerHTML =
      Math.floor(times[1] / 60) + ":" + (times[1] % 60 ? times[1] % 60 : "00");
    document.getElementById("timeX").innerHTML =
      Math.floor(times[0] / 60) + ":" + (times[0] % 60 ? times[0] % 60 : "00");
  }
}

setInterval(showTime, 1000);
