from multiprocessing import Pool, cpu_count
import chess
from src.Log import Log
from src.PosEvaluator import PosEvaluator
import time



class NoLegalMovesException(Exception):
    pass

class MoveFinder:
    def __init__(self, depth, board:chess.Board, logger: Log) -> None:
        self.logger = logger
        self.board = board
        self.depth = depth


    THREADS = cpu_count()

    def __call__(self):
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
        with Pool(self.THREADS) as p:
            ev = p.map(self.engine, ev)
        self.logger.debug(
            f'done in {(time.time() - start):.1f} sec, avg: {((time.time() - start)/(len(moves)+.001)):.2} per move')
        ev = [ev[e] + castling_index[e] for e in range(len(ev))]
        return self.get_best_eval(moves, ev)

    def get_best_eval(self, moves, ev):
        ev = dict(zip(moves, ev))
        ev = (sorted(ev.items(), key=lambda item: item[1]))
        return ev[-self.board.turn]

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
