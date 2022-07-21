# $env:pythonpath += ";c:/Users/miskibin/Desktop/CHESS_ENGINE/"

import json
import time
import numpy as np
import chess
from src.Log import Log
from src.MoveFinder import MoveFinder
from src.PlotClass import Plot


class InvalidComputerMoveError(Exception):
    pass


class PushingInvalidMoveException(Exception):
    pass


class NoLegalMovesException(Exception):
    pass


class ChessEngine:

    """Chess Engine class based on chess module

    Atributes:
        push_move(): push_move a move
        find_move(): returns best move
        evaluate_pos(): evaluate given position 

    Todo:
        optimalization
        improve evaluate position func
    """
    logger = Log.get_logger(save_to_file=False)

    def __init__(self, depth=3, board=chess.Board()) -> None:

        self.board = board
        self.depth = depth
        self.history = []
        self.evaluations = []
        self.time_on_move = []
        self.is_pos_in_data = True
        if str(self.board.fen()) != 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1':
            self.is_pos_in_data = False  # false if pos not in openings
        with open('OpeningsDatabase.json', 'r', encoding="utf-8") as f:
            self.openings = json.load(f)
        np.random.shuffle(self.openings)

    @property
    def depth(self) -> int:
        return self.__depth

    @depth.setter
    def depth(self, depth: int) -> int:
        self.__depth = min(max(1, depth), 4)

    def reset(self):
        self.history = []
        self.time_on_move = []
        self.is_pos_in_data = True
        self.board.reset()

    def save_to_file(self) -> None:
        with open('game.json', 'w', encoding="utf-8") as f:
            json.dump({'HISTORY': self.history,
                      'EVALUATIONS': self.evaluations,
                       'TIMES': self.time_on_move}, f)

    def push_move(self, move: str) -> None:
        try:
            self.board.push_san(move)
            self.history.append((move))
        except ValueError:
            self.logger.error(f'{move} is illegal')
            raise PushingInvalidMoveException
        if self.board.is_game_over() or self.board.is_repetition():
            self.logger.info('game is over')
            self.save_to_file()

    def find_move(self):
        move = self.get_move_from_database()
        if move != -1:
            self.evaluations.append([move, 0])
            self.time_on_move.append(.1)
            return move
        move = self.engine_move()
        if move in [str(m) for m in self.board.generate_legal_moves()]:
            return self.board.san(self.board.parse_uci((move)))
        else:
            self.logger.error(f'invalid computer move: {move}')
            print(self.board)
            raise InvalidComputerMoveError

    def get_move_from_database(self):
        if self.is_pos_in_data:
            if len(self.history) < 1:
                return self.openings[np.random.choice(len(self.openings))][0]
            for op in self.openings:
                if op[:len(self.history)] == self.history:
                    return op[len(self.history)]  # next move from opening
            self.is_pos_in_data = False
        return -1

    def engine_move(self):
        start = time.time()
        m = MoveFinder(self.depth, self.board, self.logger)
        (move, eval) = m()
        self.time_on_move.append((time.time() - start))
        self.evaluations.append((move, eval))
        return move


if __name__ == "__main__":
    c = ChessEngine(depth=1, board=chess.Board(
        'r1bqkb1r/2p2ppp/p1pp1n2/4p3/4P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 7'))
    #p = Plot()
    #p()
    while(True):

        # c.push_move(move)
        #computer = c.find_move()
        m = input()
        # print(computer)
        c.push_move(m)
        print(c.board)
