import numpy as np
import matplotlib.pyplot as plt

import chess

board = chess.Board()
# color True - white False - black

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
    def __init__(self, board = chess.Board(), depth=3) -> None:
        """
        Args:
            board: chess.Board() object
            depth: depth of engine. greater - better
        """
        self.board = board
        self.depth = depth
        self.color = 0
        
    def push(self, move):
        self.board.push_san(move)
        
    def make_move(self):
        self.color = int(self.board.turn)
        move = self.__engine(self.board.copy(), self.depth)
        return self.board.san(self.board.parse_uci((move))) # parse uci to san

    def evaluate_pos(self, board=None):
        """
        
        Note:
            counting material is based on the fen rep of position
        """
        if board:  # for evaluate copy of board
            return sum([PIECE_VALUES[str(i)]
                        for i in board.piece_map().values()])
        # for evalueate orginal board
        return round(sum([PIECE_VALUES[str(i)]
                          for i in self.board.piece_map().values()]), 2)

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
            return moves[-self.color][0] # return move
        else:
            return moves[-curr_col][1] # return eval

# c = ChessEngine(board)
# print(c.make_move())
# print(board.turn)
# c.push('g1h3')
