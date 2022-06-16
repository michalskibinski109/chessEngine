import chess
import operator
import time
import numpy as np
iteracja = 0

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


"""WC - biale zroszowaly"""


#def evaluate_position(board, color, WC, BC, b_moves):



def evaluate_position(board, color, WC, BC, b_moves):

    pieces = {
        'P': 10,
        'N': 30,
        'B': 30,
        'R': 50,
        'Q': 90,
        'K': 100,
        'p': -10,
        'n': -30,
        'b': -30,
        'r': -50,
        'q': -90,
        'k': -100,
        'None': 0
    }
    '''0  - czarny 1 - bialy'''
    b = 0.01
    w = 0.01
    temp = 1
    """jesli czarne na na ruchu"""
    if color == 0:
        temp = -1
    for i in range(64):
        attackers = []
        defenders = []
        ap = 0
        dp = 0

        """JESLI FIGURA NALEZY DO GOSCIA KTORY WYKONAL RUCH"""
        if pieces[str(board.piece_at(i))] * temp < 0:
            for a in chess.BaseBoard.attackers(board, color, i):
                attackers.append(abs(pieces[str(board.piece_at(a))]))
                attackers.sort(reverse=True)
                """mamy juz atakujacych od najslabszego"""
                """dodajemy obroncow pola posortowanych od najslabszego"""
            for a in chess.BaseBoard.attackers(board, (color + 1) % 2, i):
                defenders.append(abs(pieces[str(board.piece_at(a))]))
            defenders.sort(reverse=True)

            """pierwszego zbija goscia na polu i """
            defenders.append(abs(pieces[str(board.piece_at(i))]))

            while len(attackers) > 0 and len(defenders) > 0:
                ap += defenders[-1]
                defenders.pop(len(defenders) - 1)
                if len(defenders) > 0:
                    dp += attackers[-1]
                    attackers.pop(len(attackers) - 1)
            if dp >= ap:
                b -= pieces[str(board.piece_at(i))]
            else:
                b += temp*(ap - dp)

        else:
            w += pieces[str(board.piece_at(i))]

        """dodajemy za pozycje konuia"""
        if str(board.piece_at(i)) == "N":
            w += Knight_sq[i]
            """dodajemy za gonca"""
        elif str(board.piece_at(i)) == "B":
            w += Bishop_sq[i]
            """dodajemy za nie ruszanie hetmana"""
        elif str(board.piece_at(i)) == "Q":
            w += Queen_sq[i]
            """dodajemy czarnym za pozycje konia"""
        elif str(board.piece_at(i)) == "n":
            b += Knight_sq[i]
        elif str(board.piece_at(i)) == "b":
            b += Bishop_sq[i]
        elif str(board.piece_at(i)) == "q":
            b += Queen_sq[i]

            """pchamy piony A1 = 0"""
        elif str(board.piece_at(i)) == 'p':
            b += 7 - int(i/8)
        elif str(board.piece_at(i)) == 'P':
            w += int(i / 8)

    """DODAJEMY ZA MOZLIWE RUCHY"""
    """TYLKO GDY AKTYYWNY JEST BOT"""
    if board.is_check() == False and b_moves != -1:
        if color == 1:
            w += board.legal_moves.count()
            b += b_moves
        else:
            b += board.legal_moves.count()
            w += b_moves
    """szach mat, szach ,remis"""
    if board.is_checkmate():
        b = 1000 * temp
    elif board.is_check() == True:
        w -= 2*temp
    if board.is_stalemate() == True or board.is_repetition() == True:
        b = 0.1
        w = 0.1

    """roszada i prawo do niej"""
    if board.has_castling_rights(chess.BLACK):
        b += 5
    elif BC == 1:
        b += 9
    if board.has_castling_rights(chess.WHITE):
        w += 5
    elif WC == 1:
        w += 9

    '''jesli wygrywasz da ci dodatni'''
    position = round(temp*(w - b), 4)
    return position

def engine(board, color, deep, WC, BC, alpha = -np.inf, beta = np.inf):
    pass


# def engine(board, color, deep, WC, BC):

#     best_moves = {}
#     global iteracja
#     possible_moves = board.legal_moves.count()
#     if board.is_check() == True:
#         possible_moves = -1
#     for i in board.legal_moves:
#         tempw = 0
#         tempb = 0

#         """sprawdzamy czy zroszowane"""
#         if board.is_castling(i):
#             if color == 1:
#                 tempw = 1
#             else:
#                 tempb = 1
#         board.push(i)
#         color = (color + 1) % 2
#         if deep == 1:
#             best_moves[i] = engine(board, color, 0, WC, BC)
#         elif deep == 0:
#             best_moves[i] = evaluate_position(
#                 board, color, tempw, tempb, possible_moves)
#         board.pop()
#         color = (color + 1) % 2
#     if deep == 0:
#         try:
#             if color == 1:
#                 best_moves = sorted(best_moves.items(),
#                                     key=operator.itemgetter(1))
#             else:
#                 best_moves = sorted(best_moves.items(),
#                                     key=operator.itemgetter(1), reverse=True)
#             """dla engine puszczonego na deep 0 - [0]"""
#             print((best_moves[-1]))
#             return (best_moves[-1])[1]

#         except:
#             if color == 1:
#                 return -1001
#             else:
#                 return 1001
#             print("mat")
#     elif deep == 1:
#         try:
#             best_moves = sorted(best_moves.items(),
#                                 key=operator.itemgetter(1), reverse=True)
#             print(best_moves)
#             return (best_moves[-1])[0]
#         except:
#             return 1001
#             print("mat")
