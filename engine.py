import json
import time
from multiprocessing import Pool
import numpy as np
import chess
import multiprocessing
import matplotlib.pyplot as plt

THREADS = multiprocessing.cpu_count()


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

    @staticmethod
    def plot_last_game():
        with open('game.json', 'r', encoding="utf-8") as f:
            data = json.load(f)
        evals = list(zip(*data['EVALUATIONS']))
        times = data['TIMES']
        y = [round(e, 2) if abs(e) < 5 else e*5//abs(e) for e in evals[-1]]
        x = list(range(1, 1+len(y)))
        fig, axs = plt.subplots(2)
        fig.suptitle('eval and time per move')
        axs[0].bar(x, y)
        axs[0].set_ylabel('evaluation')
        axs[1].bar(x, times)
        axs[1].set_xlabel('move')
        axs[1].set_ylabel('time [sec]')
        plt.show()

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
        self.time_on_move.append((time.time() - start))
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

    def evaluate_pos(self, board=None):
        if not board: # so we can run this method for whatever position
            board = self.board
        eval_object = PosEvalObject(board)
        return eval_object()


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
    POINTS = {'n': -3, 'N': 3, 'b': -3, 'B': 3,
              'r': -5, 'R': 5, 'q': -9, 'Q': 9, 'p': -1, 'P': 1, 'k': 0, 'K': 0}

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
                        self.POINTS[item] + .04 * \
                        self.ADD_POINTS[item.upper()][j][i]
                    if item == 'p':
                        self.eval -= 1+(.02 * i)
                    elif item == 'P':
                        self.eval += 1+.02 * (7 - i)
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


if __name__ == "__main__":
    c = ChessEngine(depth=1, board=chess.Board(
        'r1bqkb1r/2p2ppp/p1pp1n2/4p3/4P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 7'))
    # c.plot_last_game()
    p = PosEvalObject(c.board)
    print(p())
    while(True):

        # c.push_move(move)
        #computer = c.find_move()
        m = input()
        # print(computer)
        c.push_move(m)
        print(c.board)
