import json
from multiprocessing import Pool, cpu_count
import time
import numpy as np
import chess
import matplotlib.pyplot as plt
import os

THREADS = cpu_count()


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
    def depth(self):
        return self.__depth

    @depth.setter
    def depth(self, depth):
        self.__depth = min(max(1, depth), 4)

    def reset(self):
        self.history = []
        self.time_on_move = []
        self.is_pos_in_data = True
        self.board.reset()

    def save_to_file(self):
        with open('game.json', 'w', encoding="utf-8") as f:
            json.dump({'HISTORY': self.history,
                      'EVALUATIONS': self.evaluations,
                       'TIMES': self.time_on_move}, f)

    def push_move(self, move):
        try:
            self.board.push_san(move)
            self.history.append((move))
        except ValueError:
            print(f'{move} is illegal')
        if self.board.is_game_over() or self.board.is_repetition():
            print('game is over')
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
            print('invalid computer move: ', move)
            print(self.board)

    def get_move_from_database(self):
        if self.is_pos_in_data:
            if len(self.history) < 1:
                return self.openings[np.random.choice(len(self.openings))][0]
            for op in self.openings:
                if op[:len(self.history)] == self.history:
                    self.time_on_move.append(.1)
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
        print(f'{len(moves)} moves to go, depth: {self.depth}')
        start = time.time()
        with Pool(THREADS) as p:
            ev = p.map(self.engine, ev)
        self.time_on_move.append((time.time() - start))
        print(
            f'done in {(time.time() - start):.1f} sec, avg: {((time.time() - start)/(len(moves)+.001)):.2} per move')
        ev = [ev[e] + castling_index[e] for e in range(len(ev))]
        return self.get_best_eval(moves, ev)

    def get_best_eval(self, moves, ev):
        ev = dict(zip(moves, ev))
        ev = (sorted(ev.items(), key=lambda item: item[1]))
        self.evaluations.append(ev[-self.board.turn])
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
        eval_object = PosEvalObject(board.copy())
        return eval_object()  # using __call__ method


class Plot:
    def __init__(self, path='game.json', ev=[], times=[]):
        self.path = path
        self.evals = ev
        self.time_per_move = times
        self.max_eval = 5

    @property
    def path(self):
        return self.__path

    @path.setter
    def path(self, path):
        if os.path.exists(path):
            self.__path = path
        else:
            print('path is broken')

    def load_from_file(self):
        with open(self.path, encoding="utf-8") as f:
            data = json.load(f)
        self.evals = list(zip(*data['EVALUATIONS']))
        self.time_per_move = data['TIMES']
        if len(self.evals) != len(self.time_per_move):
            print('invalid plot data')

    def __call__(self):
        if len(self.evals < 1):
            self.load_from_file()
        y = [round(e, 2) if abs(e) < self.max_eval else e *
             self.max_eval//abs(e) for e in self.evals[-1]]
        x = list(range(1, 1+len(y)))
        fig, axs = plt.subplots(2)
        fig.suptitle('eval and time per move')
        axs[0].bar(x, y)
        axs[0].set_ylabel('evaluation')
        axs[1].bar(x, self.time_per_move)
        axs[1].set_xlabel('move')
        axs[1].set_ylabel('time [sec]')
        plt.show()


class Points:
    KNIGHT_SQ = [[0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 1, 1, 3, 3, 1, 1, 0],
                 [0, 4, 5, 3, 3, 5, 4, 0],
                 [1, 3, 4, 5, 5, 4, 3, 1],
                 [1, 3, 4, 5, 5, 4, 3, 1],
                 [0, 4, 5, 3, 3, 5, 4, 0],
                 [0, 1, 1, 3, 3, 1, 1, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0]]

    BISHOP_SQ = [[0, 0, 0, 0, 0, 0, 0, 0],
                 [0, 5, 1, 1, 1, 1, 5, 0],
                 [0, 2, 2, 3, 3, 2, 2, 0],
                 [1, 3, 4, 4, 4, 4, 3, 1],
                 [1, 3, 4, 4, 4, 4, 3, 1],
                 [0, 2, 2, 3, 3, 2, 2, 0],
                 [0, 5, 1, 1, 1, 1, 5, 0],
                 [0, 0, 0, 0, 0, 0, 0, 0]]

    QUEEN_SQ = [[0, 0, 0, 9, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 9, 0, 0, 0, 0]]

    PAWN_SQ = [[0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 1, 0, 0, 0, 0, 1, 0],
               [0, 0, 0, 3, 3, 0, 0, 0],
               [0, 0, 0, 3, 3, 0, 0, 0],
               [0, 1, 0, 0, 0, 0, 1, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0]]

    ROOK_SQ = [[0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0]]

    KING_SQ = [[0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0]]
    POINTS = {'N': 3, 'B': 3,
              'R': 5, 'Q': 9, 'P': 1, 'K': 0}

    ADD_POINTS = {'p': PAWN_SQ, 'P': PAWN_SQ, 'n': KNIGHT_SQ, 'N': KNIGHT_SQ, 'b': BISHOP_SQ, 'B': BISHOP_SQ,
                  'r': ROOK_SQ, 'R': ROOK_SQ, 'q': QUEEN_SQ, 'Q': QUEEN_SQ, 'k': KING_SQ, 'K': KING_SQ, }


class PosEvalObject(Points):
    """
        Note:
            counting material is based on the fen rep of position
        TODO:
            add motivation to fight for the center
    """

    def __init__(self, board) -> None:
        self.board = board
        self.eval = 0
        self.fen = self.board.fen().split(' ')[0].split('/')

    def pieces_placement_eval(self):
        for i, row in enumerate(self.fen):
            j = 0
            for item in row:
                if item.isdigit():
                    j += int(item)
                else:
                    self.eval += (2 * item.isupper() - 1) * \
                        (self.POINTS[item.upper()] + .04 *
                         self.ADD_POINTS[item.upper()][j][i])
                    if item == 'p':
                        self.eval -= (.02 * i)
                    elif item == 'P':
                        self.eval += .02 * (7 - i)
                    j += 1

    def legal_moves_eval(self):
        self.eval += .01*(2*self.board.turn - 1) * \
            len([i for i in self.board.generate_legal_moves()])
        self.board.turn = (not self.board.turn)
        self.eval += .01*(2*self.board.turn - 1) * \
            len([i for i in self.board.generate_legal_moves()])

    def is_over(self):
        if self.board.is_checkmate():
            self.eval = (-2*int(self.board.turn) + 1)*100
            return True  # 100 if black on move
        if self.board.is_insufficient_material() or self.board.is_stalemate() or self.board.is_fivefold_repetition():
            return True
        return False

    def __call__(self):
        if not self.is_over():
            self.pieces_placement_eval()
        return self.eval

    def __repr__(self):
        return str(self.eval)


if __name__ == "__main__":
    c = ChessEngine(depth=1, board=chess.Board(
        'r1bqkb1r/2p2ppp/p1pp1n2/4p3/4P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 7'))
    p = PosEvalObject(chess.Board())
    p.pieces_placement_eval()
    print(p)
    # while(True):

    #     # c.push_move(move)
    #     #computer = c.find_move()
    #     m = input()
    #     # print(computer)
    #     c.push_move(m)
    #     print(c.board)
