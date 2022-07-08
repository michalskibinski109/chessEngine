import json
import time
import numpy as np
import chess
import multiprocessing
from multiprocessing import Pool
import matplotlib.pyplot as plt

THREADS = multiprocessing.cpu_count()

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

KNIGHT_SQ = [0, 0, 0, 0, 0, 0, 0, 0,
             0, 1, 1, 3, 3, 1, 1, 0,
             0, 2, 5, 3, 3, 5, 2, 0,
             1, 3, 4, 5, 5, 4, 3, 1,
             1, 3, 4, 5, 5, 4, 3, 1,
             0, 2, 5, 3, 3, 5, 2, 0,
             0, 1, 1, 3, 3, 1, 1, 0,
             0, 0, 0, 0, 0, 0, 0, 0]

BISHOP_SQ = [0, 0, 0, 0, 0, 0, 0, 0,
             0, 5, 1, 1, 1, 1, 5, 0,
             0, 2, 2, 3, 3, 2, 2, 0,
             1, 3, 4, 4, 4, 4, 3, 1,
             1, 3, 4, 4, 4, 4, 3, 1,
             0, 2, 2, 3, 3, 2, 2, 0,
             0, 5, 1, 1, 1, 1, 5, 0,
             0, 0, 0, 0, 0, 0, 0, 0]

QUEEN_SQ = [0, 0, 0, 9, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 9, 0, 0, 0, 0]


class ChessEngine:

    """Chess Engine class based on chess module

    Atributes:
        push(): push a move
        make_move(): returns best move
        evaluate_pos(): evaluate given position 

    Todo:
        optimalization
        improve evaluate position func
    """

    def __init__(self, depth=3, board=chess.Board()) -> None:

        self.board = board
        self.depth = depth
        self.history = []
        self.evaluations = []
        self.timeOnMove = []
        self.isPosInData = True
        if str(self.board.fen()) != 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1':
            self.isPosInData = False # false if pos not in openings
        with open('WCC.json', 'r') as f:
            self.openings = json.load(f)
        np.random.shuffle(self.openings)

    @property
    def depth(self):
        return self.__depth

    @depth.setter
    def depth(self, depth):
        if depth < 1:
            depth = 1
        self.__depth = min(depth, 4)

    def reset(self):
        self.history = []
        self.timeOnMove = []
        self.isPosInData = True
        self.board.reset()

    def plot_last_game(self):
        with open('game.json', 'r') as f:
            data = json.load(f)
        evals = list(zip(*data['EVALUATIONS']))
        times = data['TIMES']
        y = [round(e, 2) if abs(e) < 5 else e*5//abs(e) for e in evals[-1]]
        x = list(range(1, 1+len(y)))
        fig, axs = plt.subplots(2)
        fig.suptitle('eval and time per move')
        axs[0].bar(x, y)
        axs[0].set_ylabel('evaluation')
        axs[1].bar(list(range(len(times))), times)
        axs[1].set_xlabel('move')
        axs[1].set_ylabel('time [sec]')
        plt.show()

    def save_to_file(self):
        with open('game.json', 'w') as f:
            json.dump({'HISTORY': self.history,
                      'EVALUATIONS': self.evaluations,
                       'TIMES': self.timeOnMove}, f)

    def push(self, move):
        try:
            self.board.push_san(move)
            self.history.append((move))
        except:
            print(f'{move} is illegal')
        if self.board.is_game_over():
            print(f'game is over')
            self.save_to_file()

    def make_move(self):
        move = self.get_move_from_database()
        if move != -1:
            return move
        move = self.__process_allocator()
        if move in [str(m) for m in self.board.generate_legal_moves()]:
            return self.board.san(self.board.parse_uci((move)))
        else:
            print('invalid computer move: ', move)
            print(self.board)

    def get_move_from_database(self):
        if self.isPosInData:
            if len(self.history) < 1:
                return self.openings[np.random.choice(len(self.openings))][0]
            for op in self.openings:
                if op[:len(self.history)] == self.history:
                    self.timeOnMove.append(.1)
                    return op[len(self.history)]  # next move from opening
            self.isPosInData = False
        return -1

    def __process_allocator(self):
        """
        TODO check only moves that change evaluate a lot
        """
        moves = []
        eval = []
        castling_index = []
        for move in self.board.generate_legal_moves():
            moves.append(str(move))
            castling_index.append(
                int(self.board.is_castling(move))*(2*self.board.turn - 1))
            self.board.push(move)
            eval.append(self.board.copy())
            self.board.pop()
        print(f'{len(moves)} moves to go, depth: {self.depth}')
        start = time.time()
        with Pool(THREADS) as p:
            eval = p.map(self.engine, eval)
        self.timeOnMove.append((time.time() - start))
        print(
            f'done in {(time.time() - start):.1f} sec, avg: {((time.time() - start)/len(moves)+.001):.2} per move')
        eval = [eval[e] + castling_index[e] for e in range(len(eval))]
        eval = dict(zip(moves, eval))
        eval = (sorted(eval.items(), key=lambda item: item[1]))
        self.evaluations.append(eval[-self.board.turn])
        return eval[-self.board.turn][0]  # return move

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

    def pieces_placement_eval(self, board: chess.Board()):
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
                        eval -= (1+.04 * (7 - i))
                    elif item == 'P':
                        eval += 1+.04 * i
                    elif item == 'n':
                        eval -= 3+.04*KNIGHT_SQ[i*8 + j]
                    elif item == 'N':
                        eval += 3+.04*KNIGHT_SQ[i*8 + j]
                    elif item == 'b':
                        eval -= 3+.04*BISHOP_SQ[i*8 + j]
                    elif item == 'B':
                        eval += 3+.04*BISHOP_SQ[i*8 + j]
                    elif item == 'r':
                        eval -= 5
                    elif item == 'R':
                        eval += 5
                    elif item == 'q':
                        eval -= 9+.05*QUEEN_SQ[i*8 + j]
                    elif item == 'Q':
                        eval += 9+.05*QUEEN_SQ[i*8 + j]

                    j += 1
        return eval

    def legal_moves_eval(self, board):
        eval = .01*(2*board.turn - 1) * \
            len([i for i in board.generate_legal_moves()])
        board.turn = (not board.turn)
        eval += .01*(2*board.turn - 1) * \
            len([i for i in board.generate_legal_moves()])
        return eval

    def evaluate_pos(self, board=None):
        """
        Note:
            counting material is based on the fen rep of position
        TODO:
            add motivation to fight for the center
        """
        if not board:
            board = self.board
        if board.is_checkmate():
            return (-2*int(board.turn) + 1)*100  # 100 if black on move
        elif board.is_insufficient_material() or board.is_stalemate() or board.is_fivefold_repetition():
            return 0
        return self.pieces_placement_eval(board)
        # return self.pieces_placement_eval(board) + self.legal_moves_eval(board)


if __name__ == "__main__":
    plt.show()
    c = ChessEngine(depth=1, board = chess.Board('r1bqkb1r/2p2ppp/p1pp1n2/4p3/4P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 7'))
    #c.plot_last_game()
    while(True):
        print(c.evaluate_pos())
        # c.push(move)
        computer = c.make_move()
        move = input()
        print(computer)
        c.push(computer)
        print(c.board)
