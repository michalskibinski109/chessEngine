import chess
from chess import Board
import numpy as np
from tqdm import tqdm
from miskibin import get_logger
from logging import Logger
from numba import njit
import json


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
        self.history = []
        self.is_pos_in_data = True
        self.openings = []
        try:
            with open("WCC.json", "r", encoding="utf-8") as f:
                self.openings = json.load(f)
        except FileNotFoundError:
            self.logger.warning("WCC.json not found")
            self.is_pos_in_data = False
        np.random.shuffle(self.openings)

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
        if board.is_checkmate():
            return -100 if board.turn else 100
        return sum(
            [self.PIECE_VALUES[str(piece)] for piece in board.piece_map().values()]
        )

    def push_from_san(self, move: str) -> None:
        try:
            self.logger.info(f"pushing move: {move}")
            self.history.append(str(self.board.san(self.board.parse_san(move))))
            self.board.push_san(move)
        except ValueError as err:
            self.logger.warning(f"{str(self.board)}\n")
            self.logger.exception(f"Invalid move {move}")
            raise err

    def get_move_from_database(self):
        if self.is_pos_in_data:
            if len(self.history) < 1:
                return self.openings[np.random.choice(len(self.openings))][0]
            for op in self.openings:
                if op[: len(self.history)] == self.history:
                    return op[len(self.history)]  # next move from opening
            self.is_pos_in_data = False
        return -1

    def get_best_move(self, board: Board = None) -> tuple:
        if not board:
            board = self.board
        if self.is_pos_in_data:
            move = self.get_move_from_database()
            if move != -1:
                return move, 0
        legal_moves = list(board.legal_moves)
        # sort moves by capture
        legal_moves.sort(key=lambda move: board.is_capture(move), reverse=True)
        bar = tqdm(legal_moves)
        evals = []
        alpha, beta = -100, 100
        for move in legal_moves:
            board.push(move)
            evals.append(
                self.__alpha_beta_puring(
                    board,
                    self.depth - 1,
                    alpha=alpha,
                    beta=beta,
                )
            )
            board.pop()
            bar.update(1)
            if board.turn:
                alpha = max(alpha, evals[-1])
            else:
                beta = min(beta, evals[-1])

        index = evals.index(max(evals)) if board.turn else evals.index(min(evals))
        return board.san(legal_moves[index]), evals[index]

    def __alpha_beta_puring(
        self, board: Board, depth: int, alpha: float, beta: float
    ) -> float:
        if depth == 0:
            return self.evaluate(board)
        legal_moves = list(board.legal_moves)
        legal_moves.sort(key=lambda move: board.is_capture(move), reverse=True)
        for move in legal_moves:
            board.push(move)
            evaluation = self.__alpha_beta_puring(board, depth - 1, alpha, beta)
            board.pop()
            if board.turn:
                alpha = max(alpha, evaluation)
            else:
                beta = min(beta, evaluation)
            if beta <= alpha:
                break
        return alpha if board.turn else beta
