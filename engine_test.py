import unittest
from engine import ChessEngine
from chess import Board


class TestChessEngine(unittest.TestCase):

    def test_init(self):
        c = ChessEngine(1, Board())
        self.assertEqual(type(c.openings), list)
        del c

    def test_get_move_from_database(self):
        c = ChessEngine(1, Board())
        for _ in range(3):
            database_move = c.get_move_from_database()
            c.push(database_move)
            self.assertTrue(type(database_move) == str)
        del c

    def test_push(self):
        c = ChessEngine(1, Board())
        moves = ['e4', 'e5',  'Bc4', 'a6', 'Qf3', 'b6',  'Qxf7#']
        [c.push(m) for m in moves]
        self.assertEqual(moves, c.history)
        self.assertEqual(c.push('a5'), -1)  # here game is over, so cant push
        del c

    def test_pieces_placement_eval(self):
        c = ChessEngine(1, Board())
        # white positionaly better(+1)
        plus_1 = Board(
            'r1bq1bnr/pp1p1k1p/n1p1ppp1/8/2BPP3/1P3N2/PBPN1PPP/R2Q1RK1 w - - 2 9')
        minus_1 = Board(
            'r1bq1rk1/ppp1ppbp/2n2np1/3p4/8/P5P1/1PPPPP1P/RNBQKBNR w KQ - 4 7')
        # inbalance material
        plus_20 = Board(
            'rnb1k2B/pppp1p1p/6p1/4P3/8/8/PPP1PPPP/RN1QKBNR b KQq - 0 6')
        self.assertGreater(c.pieces_placement_eval(plus_1),.2)
        self.assertGreater(-.2,c.pieces_placement_eval(minus_1))
        self.assertGreater(c.pieces_placement_eval(plus_20),1)
        del c


if __name__ == '__main__':
    unittest.main()
