from msilib.schema import MoveFile
import pytest
from src.MoveFinder import MoveFinder
from src.engine import ChessEngine, PushingInvalidMoveException
from chess import Board
import sys
sys.path.append('')  # fixing import problem [temporary solution]


# have to end this refactoring


class TestChessEngine:

    @pytest.fixture()
    def setup_engine(self):
        self.c = ChessEngine(1, Board())
        yield
        del self.c

    @pytest.mark.usefixtures("setup_engine")
    def test_init(self):
        assert type(self.c.openings) == list

    @pytest.mark.usefixtures("setup_engine")
    def test_get_move_from_database(self):
        for _ in range(3):
            database_move = self.c.get_move_from_database()
            self.c.push_move(database_move)
            assert type(database_move) == str

    @pytest.mark.usefixtures("setup_engine")
    def test_find_move(self):
        moves = ['a3', 'a6',  'b3', 'b6']
        for m in moves:
            self.c.push_move(m)
        engine_moves = 2
        for _ in range(engine_moves):
            self.c.push_move(self.c.find_move())
        assert len(self.c.history) == len(moves) + engine_moves
        should_castle = Board(
            'r1bqkb1r/2p2ppp/p1pp1n2/4p3/4P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 7')
        self.c = ChessEngine(1, should_castle)
        assert self.c.find_move() == 'O-O'

    @pytest.mark.usefixtures("setup_engine")
    def test_push_move(self):
        moves = ['e4', 'e5',  'Bc4', 'a6', 'Qf3', 'b6',  'Qxf7#']
        for m in moves:
            self.c.push_move(m)
        assert moves == self.c.history
        # here game is over, so cant push_move
        with pytest.raises(PushingInvalidMoveException) as exc:
            self.c.push_move('a5')
        assert exc

### to be done in different module

    # @pytest.mark.usefixtures("setup_engine")
    # def test_evaluate_position(self):
    #     stealmate = Board(
    #         '8/8/2k5/5K2/8/8/2N5/8 w - - 0 1')
    #     white_wins = Board('8/8/k1K5/8/8/8/2N5/R7 b - - 0 1')
    #     plus_2_pos = Board(
    #         'rnbqkbnr/3pp3/8/8/3PP3/8/1B1NN1B1/R2Q1RK1 w kq - 0 1')
    #     minus_2_pos = Board(
    #         'r2qk2r/1b1nn1b1/8/3pp3/8/8/3PP3/RNBQKBNR b KQkq - 0 1')
    #     plus_24_pos = Board(
    #         'rnb1k2B/pppp1p1p/6p1/4P3/8/8/PPP1PPPP/RN1QKBNR b KQq - 0 6')
    #     assert self.c.evaluate_pos(stealmate) == 0
    #     assert self.c.evaluate_pos(white_wins) == 100
    #     assert (self.c.evaluate_pos(plus_2_pos) > .2)
    #     assert (-.2 > self.c.evaluate_pos(minus_2_pos))
    #     assert(self.c.evaluate_pos(plus_24_pos) > 20)

    # @pytest.mark.usefixtures("setup_engine")
    # def test_engine_method(self):
    #     w_mate_in_1 = Board(
    #         '8/8/8/8/8/5K2/1R6/5k2 w - - 0 1')
    #     b_mate_in_1 = Board('8/K1k5/1r6/8/8/8/8/8 w - - 0 1')
    #     b_mate_in_2 = Board('8/K7/2k5/8/8/1r6/8/8 w - - 0 1')
    #     w_mate_in_3 = Board('k7/8/8/1RK5/8/8/8/8 w - - 0 1')
    #     assert MoveFinder(0,w_mate_in_1)() == 100
    #     assert MoveFinder(1,b_mate_in_1)() == -100
    #     assert MoveFinder(3,b_mate_in_2)() == -100
    #     assert MoveFinder(4,w_mate_in_3)() == 100
