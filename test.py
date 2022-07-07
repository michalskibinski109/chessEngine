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


if __name__ == '__main__':
    unittest.main()
