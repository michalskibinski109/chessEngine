import pytest
import chess
from engine import ChessEngine


class TestChessEngine:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.e1 = ChessEngine(depth=1)
        self.e2 = ChessEngine(depth=2)
        self.e3 = ChessEngine(depth=2)

    def test_evaluate(self):
        assert self.e1.evaluate(chess.Board()) == 0
        pos = "rnbqkbnr/pppp1ppp/8/8/3pP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3"
        assert self.e1.evaluate(chess.Board(pos)) == -1
        pos = "rnbqkbnr/pp1p1ppp/8/4P3/3p4/8/PPP2PPP/RNB1KBNR w KQkq - 0 5"
        assert self.e1.evaluate(chess.Board(pos)) == -9

    def test_get_best_move(self):
        pos = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2"
        assert self.e1.get_best_move(chess.Board(pos), 1) == ("e4d5", 1)
        pos = "8/5Npk/p7/P1P4P/6r1/4PK2/7P/8 w - - 1 46"
        assert self.e1.get_best_move(chess.Board(pos), 1) == ("f3g4", 6)
        pos = "r1bqkbnr/pppp1pp1/2n4p/4p3/3NP3/8/PPPP1PPP/RNBQKB1R w KQkq - 2 4"
        assert self.e1.get_best_move(chess.Board(pos), 1) == ("d4c6", 3)
        assert self.e2.depth == 2
        assert self.e2.get_best_move(chess.Board(pos), 2) == ("d4c6", 0)
