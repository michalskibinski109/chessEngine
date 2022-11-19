from chess import Board
from tqdm import tqdm
from miskibin import get_logger
from logging import Logger
from .points import ADD_POINTS, DEPTH
import pandas as pd
from time import time
from pathlib import Path


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
        self.inspected_nodes = 0
        path = Path(__file__).parent / "openings.csv"
        if path.exists():
            self.openings = pd.read_csv(path.resolve())
            self.logger.debug(f"openings loaded {self.openings.shape}")
        else:
            self.logger.warning(f"File {path} not found")
            self.openings = pd.DataFrame(columns=["fen", "move"])
        self.logger.info(f"Initialized engine with depth: {depth}")

    def evaluate(self, board: Board) -> float:
        self.inspected_nodes += 1
        if board.is_game_over():
            if board.is_checkmate():
                return -100 if board.turn else 100
            return 0
        return sum(
            ADD_POINTS[str(piece)][square]
            for square, piece in board.piece_map().items()
        )

    def push_from_san(self, move: str) -> None:
        try:
            self.logger.debug(f"pushing move: {move}")
            self.board.push_san(move)
        except ValueError as err:
            self.logger.warning(f"{str(self.board)}\n")
            self.logger.exception(f"Invalid move {move}")
            raise err
        if self.board.is_game_over():
            self.logger.info(f"Game over: {self.board.result()}")

    def get_move_from_database(self):
        fen = self.board.fen().split(" ")[:4]
        fen = " ".join(fen)
        try:
            return (
                self.openings[self.openings["fen"] == fen].sample(1)["move"].values[0]
            )
        except (IndexError, ValueError):
            self.logger.debug(f"fen not found in database")
            return None

    def __get_engine_move(self, board: Board) -> tuple:
        depth = self.depth + DEPTH.get(len(board.piece_map()), 0)
        legal_moves = list(board.legal_moves)
        legal_moves.sort(key=lambda move: board.is_capture(move), reverse=True)
        bar = tqdm(legal_moves)
        evals = []
        alpha, beta = -100, 100
        for move in legal_moves:
            board.push(move)
            evals.append(
                self.__alpha_beta_puring(
                    board,
                    depth - 1,
                    alpha,
                    beta,
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

    def get_best_move(self, board: Board = None) -> tuple:
        start = time()
        self.inspected_nodes = 0
        if not board:
            board = self.board
        move = self.get_move_from_database()
        if move:
            return move, 0
        move, evaluation = self.__get_engine_move(board)
        self.logger.debug(
            f"\ninspected  {self.inspected_nodes} nodes time: {time()-start:.1f}s"
        )
        self.logger.info(f"best move: {move}, evaluation: {evaluation:.2f}")
        return move, evaluation

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
