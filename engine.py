import json
import numpy as np
import matplotlib.pyplot as plt
import chess
from progress.bar import Bar
import multiprocessing
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
        self.history = []
        self.isPosInData = True  # false if pos not in openings
        with open('WCC.json', 'r') as f:
            self.openings = json.load(f)
        np.random.shuffle(self.openings)

    def push(self, move):
        try:
            self.board.push_san(move)
        except ValueError:
            print('was page reloaded ?')
            self.history = []
            self.board.reset()
            self.board.push_san(move)
        self.history.append((move))

    def make_move(self):
        if len(self.history) < 1:
            return self.openings[np.random.choice(len(self.openings))][0]
        if self.isPosInData:  # seraching in database
            for op in self.openings:
                if op[:len(self.history)] == self.history:
                    print('still in prep. . . ')
                    return op[len(self.history)]  # next move from opening
            self.isPosInData = False
        self.color = int(self.board.turn)
        move = self.__engine(self.board.copy(), self.depth)
        try:
            # parse uci to san
            return self.board.san(self.board.parse_uci((move)))
        except ValueError:
            print('move: ', move)
            print(self.board)

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
            return (-2*int(board.turn) + 1)*100  # 100 if black on move
        eval = 0
        """it's taking to much time :(("""
        fen = board.fen().split(' ')[0]
        for i, row in enumerate(fen.split('/')):
            j = 0
            for item in row:
                if item.isdigit():
                    j += int(item)
                else:
                    if item == 'p':
                        eval -= .02 * i
                    elif item == 'P':
                        eval += .02 * i
                    elif item == 'n':
                        eval -= .1*Knight_sq[i*8 + j]
                    elif item == 'N':
                        eval += .1*Knight_sq[i*8 + j]
                    elif item == 'b':
                        eval -= .1*Bishop_sq[i*8 + j]
                    elif item == 'B':
                        eval += .1*Bishop_sq[i*8 + j]
        return eval + sum([PIECE_VALUES[str(i)]
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
        if depth == self.depth: #init display
            l = len([move for move in board.generate_legal_moves()])
            bar = Bar('finding move (depth = ',self.depth,')', max=l+1)
            bar.next()
        curr_col = (self.color + self.depth - depth) % 2
        # moves - dict {move(uci notation): eval}
        moves = {}
        for move in board.generate_legal_moves():
            board.push(move)
            if depth > 0:
                moves[str(move)] = self.__engine(board, depth - 1)
                board.pop()
                if depth == self.depth: #display progress
                    bar.next()#display next
                    
            else:
                moves[str(move)] = self.evaluate_pos(board)
                board.pop()
        if len(moves) == 0:
            return (-2*curr_col + 1)*100
        moves = (sorted(moves.items(), key=lambda item: item[1]))
        if depth == self.depth:
            bar.finish()#end display 
            return moves[-self.color][0]  # return move
        else:
            return moves[-curr_col][1]  # return eval


#c = ChessEngine()
# c.evaluate_pos()
# c.push('e2e4')
# print(c.make_move())
# print(board.turn)
#
