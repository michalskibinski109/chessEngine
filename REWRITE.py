import json
from chess import Board
import chess.pgn
from copy import deepcopy

"""ugliest script i ever made"""


with open("Duda.pgn", "r") as f:
   with open("Duda2.pgn", "w") as f2: 
       f2.write(f.read())

with open("Duda2.pgn", "r") as f:
    pgn = f
    pgn2 = f.read().split('\n')
    
    
games = []
i = 0
line = 1
while(i<2931):
    line = 1
    with open("Duda2.pgn", "r") as f:
        pgn = f
        first_game = chess.pgn.read_game(f)
        pgn2 = f.read().split('\n')
    games.append([])
    print(i)
    board = Board()
    for j in first_game.mainline_moves():
        games[i].append(board.san(board.parse_uci(str(j))) )
        board.push(j)
    while("[Event" not in pgn2[line]):
        line += 1
    pgn = '\n'.join(pgn2[line:])
    with open("Duda2.pgn", "w") as f:
        f.write(pgn)
    if len(pgn2[line:])<30:
        break
    line += 1
    i+=1

"""convert to san"""



with open('WCC.json', 'w') as f:
     json.dump(games,f)
