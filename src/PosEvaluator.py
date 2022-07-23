from src.Points import Points

class PosEvaluator(Points):
    """
        Note:
            counting material is based on the fen rep of position
        TODO:
            add motivation to fight for the center
    """
    __slots__ = ['board', 'eval', 'fen']
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
