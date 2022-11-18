import chess
from chess import Board
import numpy as np
from tqdm import tqdm
from miskibin import get_logger
from logging import Logger
from numba import njit


class ChessEngine:
    def __init__(
        self,
        logger: Logger = get_logger(lvl=10),
        board: Board = Board(),
        depth: int = 2,
    ) -> None:
        self.logger = logger
        self.board = board
        self.depth = depth
        self.m = 0
        self.a = 0

    PIECE_VALUES = {
        "P": 1,
        "N": 3,
        "B": 3,
        "R": 5,
        "Q": 9,
        "K": 0,
        "p": -1,
        "n": -3,
        "b": -3,
        "r": -5,
        "q": -9,
        "k": 0,
    }

    def evaluate(self, board: Board) -> float:
        # can be changed to Piece.from_symbol(x)
        return sum(
            [self.PIECE_VALUES[str(piece)] for piece in board.piece_map().values()]
        )

    def minimax(self, board: Board, depth: int, minimize: bool) -> float:
        if depth == 0:
            return self.evaluate(board)
        minimize = not minimize
        best_evaluation = 100 if minimize else -100

        for move in board.legal_moves:
            board.push(move)
            evaluation = self.minimax(board, depth - 1, minimize)
            board.pop()
            if minimize:
                best_evaluation = min(best_evaluation, evaluation)
            else:
                best_evaluation = max(best_evaluation, evaluation)
        return best_evaluation

    def get_best_move(self, board: Board, depth: int) -> tuple:
        legal_moves = [move for move in board.legal_moves]
        bar = tqdm(legal_moves)
        evaluations = []
        alpha, beta = -100, 100
        minimize = bool(int(board.fen().split(" ")[5]) % 2)
        for move in legal_moves:
            board.push(move)
            evaluations.append(
                self.__alpha_beta_puring(
                    board, depth - 1, alpha=alpha, beta=beta, minimize=(not minimize)
                )
            )
            board.pop()
            bar.update(1)
            if minimize:
                beta = min(beta, evaluations[-1])
            else:
                alpha = max(alpha, evaluations[-1])
        if minimize:
            index = evaluations.index(min(evaluations))
        else:
            index = evaluations.index(max(evaluations))
        return str(legal_moves[index]), evaluations[index]

    def __alpha_beta_puring(
        self, board: Board, depth: int, alpha: float, beta: float, minimize: bool
    ) -> float:
        if depth == 0:
            return self.evaluate(board)
        for move in board.legal_moves:
            board.push(move)
            evaluation = self.__alpha_beta_puring(
                board, depth - 1, alpha, beta, minimize
            )
            board.pop()
            if minimize:
                beta = min(beta, evaluation)
            else:
                alpha = max(alpha, evaluation)
            if beta <= alpha:
                break
        return beta if minimize else alpha


if __name__ == "__main__":
    import time

    pos = "r1bqkbnr/pppp1pp1/2n4p/4p3/3NP3/8/PPPP1PPP/RNBQKB1R w KQkq - 2 4"
    board = Board(pos)
    e = ChessEngine(
        board=board,
        depth=4,
    )
    start = time.time()
    print(e.get_best_move(board, e.depth))
