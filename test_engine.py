
from engine import ChessEngine
from chess import Board


class TestChessEngine:

    def test_init(self):
        c = ChessEngine(1, Board())
        assert (type(c.openings) == list)
        del c

    def test_get_move_from_database(self):
        c = ChessEngine(1, Board())
        for _ in range(3):
            database_move = c.get_move_from_database()
            c.push(database_move)
            assert (type(database_move) == str)
        del c

    def test_push(self):
        c = ChessEngine(1, Board())
        moves = ['e4', 'e5',  'Bc4', 'a6', 'Qf3', 'b6',  'Qxf7#']
        [c.push(m) for m in moves]
        assert moves == c.history
        assert (c.push('a5') == -1)  # here game is over, so cant push
        del c

    def test_pieces_placement_eval(self):
        c = ChessEngine(1, Board())
        # white positionaly better(+1)
        plus_2_pos = Board(
            'r1bq1bnr/pp1p1k1p/n1p1ppp1/8/2BPP3/1P3N2/PBPN1PPP/R2Q1RK1 w - - 2 9')
        minus_2_pos = Board(
            'r1bq1rk1/ppp1ppbp/2n2np1/3p4/8/P5P1/1PPPPP1P/RNBQKBNR w KQ - 4 7')
        # inbalance material
        plus_24_pos = Board(
            'rnb1k2B/pppp1p1p/6p1/4P3/8/8/PPP1PPPP/RN1QKBNR b KQq - 0 6')
        assert (c.pieces_placement_eval(plus_2_pos) > .2)
        assert (-.2 > c.pieces_placement_eval(minus_2_pos))
        assert(c.pieces_placement_eval(plus_24_pos) > 20)
        del c

    def test_engine_method(self):
        c = ChessEngine(1, Board())
        w_mate_in_1 = Board(
            'rnbqkbnr/1pp2ppp/p2p4/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 4')
        b_mate_in_1 = Board('8/K1k5/1r6/8/8/8/8/8 w - - 0 1')
        b_mate_in_2 = Board('8/K7/2k5/8/8/1r6/8/8 w - - 0 1')
        w_mate_in_3 = Board('k7/8/8/1RK5/8/8/8/8 w - - 0 1')
        assert c.engine(w_mate_in_1, 0) == 100
        assert c.engine(b_mate_in_1, 1) == -100
        assert c.engine(b_mate_in_2, 3) == -100
        assert c.engine(w_mate_in_3, 4) == 100
        del c
