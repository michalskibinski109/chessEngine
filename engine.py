import numpy as np
import matplotlib.pyplot as plt
import chess


PIECE_VALUES = {
    'p': -1,
    'P': 1,
    'n': -3,
    'N': 3,
    'q': -9,
    'Q': 9,
    'r': -5,
    'R': 5,
    'b': -3,
    'B': 3,
    'k': 0,
    'K': 0
}

Knight_sq = [0, 0, 0, 0, 0, 0, 0, 0,
             0, 1, 1, 1, 1, 1, 1, 0,
             0, 2, 3, 3, 3, 3, 2, 0,
             1, 3, 4, 5, 5, 4, 3, 1,
             1, 3, 4, 5, 5, 4, 3, 1,
             0, 2, 3, 3, 3, 3, 2, 0,
             0, 1, 1, 1, 1, 1, 1, 0,
             0, 0, 0, 0, 0, 0, 0, 0]

Bishop_sq = [0, 0, 0, 0, 0, 0, 0, 0,
             0, 4, 1, 1, 1, 1, 4, 0,
             0, 3, 2, 3, 3, 2, 3, 0,
             1, 2, 4, 4, 4, 4, 2, 1,
             1, 3, 4, 4, 4, 4, 3, 1,
             0, 2, 2, 3, 3, 2, 2, 0,
             0, 4, 1, 1, 1, 1, 4, 0,
             0, 0, 0, 0, 0, 0, 0, 0]

Queen_sq = [0, 0, 0, 8, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 8, 0, 0, 0, 0]


class ChessEngine:
    """Chess Engine class based on chess module

    Atributes:
        push(): push a move
        make_move(): returns best move
        evaluate_pos(): evaluate given position 

    Todo:
        multiprocessing  
        optimalization
        improve evaluate position func
    """

    def __init__(self, board=chess.Board(), depth=3) -> None:
        """
        Args:
            board: chess.Board() object
            depth: depth of engine. greater - better
        """
        self.board = board
        self.depth = depth
        self.color = int(board.turn)

    def push(self, move):
        self.board.push_san(move)

    def make_move(self):
        self.color = int(self.board.turn)
        move = self.__engine(self.board.copy(), self.depth)
        return self.board.san(self.board.parse_uci((move)))  # parse uci to san

    def evaluate_pos(self, board=None):
        """
        Note:
            counting material is based on the fen rep of position
        Todo:
            add points becouse of pieces position
        """
        if not board: 
            board = self.board
        if board.is_checkmate():
            return (-2*int(board.turn) + 1)*100 # 100 if black on move
        return sum([PIECE_VALUES[str(i)]
                        for i in board.piece_map().values()])


    def __engine(self, board: chess.Board(), depth):
        """
        Private method designed to find best move
        Note:
            used alghoritm: minimax
        Args:
            color: 0 - black 1 - white
            board: COPY of current board 
        return:
            best move 
        """
        curr_col = (self.color + self.depth - depth) % 2
        # moves - dict {move(uci notation): eval}
        moves = {}
        for move in board.generate_legal_moves():
            board.push(move)
            if depth > 0:
                moves[str(move)] = self.__engine(board, depth - 1)
                board.pop()
            else:
                moves[str(move)] = self.evaluate_pos(board)
                board.pop()
        moves = (sorted(moves.items(), key=lambda item: item[1]))
        if depth == self.depth:
            try:
                return moves[-self.color][0]  # return move
            except IndexError:
                print('I LOSE :((')
                return 
        else:
            try:
                return moves[-curr_col][1]  # return eval
            except IndexError: # when check mate in variant
                return (-2*curr_col +1)*100
# c = ChessEngine(board)
# print(c.make_move())
# print(board.turn)
# c.push('g1h3')
