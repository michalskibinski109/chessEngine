#$env:pythonpath += ";c:/Users/miskibin/Desktop/CHESS_ENGINE/"

import json
from multiprocessing import Pool, cpu_count
import time
import numpy as np
import chess
from src.Log import Log
from src.PosEvaluator import PosEvaluator
from src.PlotClass import Plot

THREADS = cpu_count()


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
        with open('WCC.json', 'r', encoding="utf-8") as f:
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
        move = self.__process_allocator()
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

    def __process_allocator(self):
        moves, ev, castling_index = [], [], []
        for move in self.board.generate_legal_moves():
            moves.append(str(move))
            castling_index.append(
                int(self.board.is_castling(move))*(2*self.board.turn - 1))
            self.board.push(move)
            ev.append(self.board.copy())
            self.board.pop()
        self.logger.debug(f'{len(moves)} moves to go, depth: {self.depth}')
        start = time.time()
        with Pool(THREADS) as p:
            ev = p.map(self.engine, ev)
        self.time_on_move.append((time.time() - start))
        self.logger.debug(
            f'done in {(time.time() - start):.1f} sec, avg: {((time.time() - start)/(len(moves)+.001)):.2} per move')
        ev = [ev[e] + castling_index[e] for e in range(len(ev))]
        return self.get_best_eval(moves, ev)

    def get_best_eval(self, moves, ev):
        ev = dict(zip(moves, ev))
        ev = (sorted(ev.items(), key=lambda item: item[1]))
        try:
            self.evaluations.append(ev[-self.board.turn])
        except IndexError:
            raise NoLegalMovesException
        return ev[-self.board.turn][0]

    def engine(self, board: chess.Board(), depth=None):
        """
        Private method designed to find best move
        Note:
            used alghoritm: minimax
        Args:
            color: 0 - black 1 - white
            board: COPY of current board 
        return:
            eval of best move 
        """
        if depth == None:
            depth = self.depth - 1
        curr_col = board.turn
        moves = {}
        for move in board.generate_legal_moves():
            board.push(move)
            if depth > 0:
                moves[str(move)] = self.engine(board, depth - 1)
                board.pop()
            else:
                moves[str(move)] = self.evaluate_pos(board)
                board.pop()
        if len(moves) == 0:
            return (-2*curr_col + 1)*100
        moves = (sorted(moves.items(), key=lambda item: item[1]))
        return moves[-curr_col][1]  # return eval

    def evaluate_pos(self, board=None):
        if not board:  # so we can run this method for whatever position
            board = self.board
        eval_object = PosEvaluator(board.copy())
        return eval_object()  # using __call__ method




if __name__ == "__main__":
    c = ChessEngine(depth=1, board=chess.Board(
        'r1bqkb1r/2p2ppp/p1pp1n2/4p3/4P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 7'))
    p = Plot()
    p()
    # while(True):

    #     # c.push_move(move)
    #     #computer = c.find_move()
    #     m = input()
    #     # print(computer)
    #     c.push_move(m)
    #     print(c.board)
