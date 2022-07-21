import sys
sys.path.append('')

from chess import Board
from src.engine import ChessEngine, PushingInvalidMoveException
import pytest

class TestChessEngine:
    
    @staticmethod
    @pytest.fixture(autouse=True)
    def c():
        return ChessEngine(1, Board())
    
    @staticmethod
    def test_init(c):
        assert type(c.openings) == list

    @staticmethod
    def test_get_move_from_database(c):
        for _ in range(3):
            database_move = c.get_move_from_database()
            c.push_move(database_move)
            assert type(database_move) == str
            
    @staticmethod
    def test_find_move(c):
        moves = ['a3', 'a6',  'b3', 'b6']
        for m in moves:
            c.push_move(m)
        engine_moves = 2
        for _ in range(engine_moves):
            c.push_move(c.find_move())
        assert len(c.history) == len(moves) + engine_moves
        should_castle = Board(
            'r1bqkb1r/2p2ppp/p1pp1n2/4p3/4P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 7')
        c = ChessEngine(1, should_castle)
        assert c.find_move() == 'O-O'

    @staticmethod
    def test_push_move(c):
        moves = ['e4', 'e5',  'Bc4', 'a6', 'Qf3', 'b6',  'Qxf7#']
        for m in moves:
            c.push_move(m)
        assert moves == c.history
        # here game is over, so cant push_move
        with pytest.raises(PushingInvalidMoveException) as exc:
            c.push_move('a5')
        assert exc

    @staticmethod
    def test_evaluate_position(c):
        stealmate = Board(
            '8/8/2k5/5K2/8/8/2N5/8 w - - 0 1')
        white_wins = Board('8/8/k1K5/8/8/8/2N5/R7 b - - 0 1')
        plus_2_pos = Board(
            'rnbqkbnr/3pp3/8/8/3PP3/8/1B1NN1B1/R2Q1RK1 w kq - 0 1')
        minus_2_pos = Board(
            'r2qk2r/1b1nn1b1/8/3pp3/8/8/3PP3/RNBQKBNR b KQkq - 0 1')
        plus_24_pos = Board(
            'rnb1k2B/pppp1p1p/6p1/4P3/8/8/PPP1PPPP/RN1QKBNR b KQq - 0 6')
        assert c.evaluate_pos(stealmate) == 0
        assert c.evaluate_pos(white_wins) == 100
        assert (c.evaluate_pos(plus_2_pos) > .2)
        assert (-.2 > c.evaluate_pos(minus_2_pos))
        assert(c.evaluate_pos(plus_24_pos) > 20)


    @staticmethod
    def test_engine_method(c):
        w_mate_in_1 = Board(
            '8/8/8/8/8/5K2/1R6/5k2 w - - 0 1')
        b_mate_in_1 = Board('8/K1k5/1r6/8/8/8/8/8 w - - 0 1')
        b_mate_in_2 = Board('8/K7/2k5/8/8/1r6/8/8 w - - 0 1')
        w_mate_in_3 = Board('k7/8/8/1RK5/8/8/8/8 w - - 0 1')
        assert c.engine(w_mate_in_1, 0) == 100
        assert c.engine(b_mate_in_1, 1) == -100
        assert c.engine(b_mate_in_2, 3) == -100
        assert c.engine(w_mate_in_3, 4) == 100
