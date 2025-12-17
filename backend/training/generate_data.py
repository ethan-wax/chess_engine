import chess
import chess.pgn
import numpy as np
from encoder import encode_board, encode_move

games = []
with open("lichess_filtered.pgn", "r", encoding="utf-8") as pgn:
    while True:
        game = chess.pgn.read_game(pgn)

        if game is None:
            break

        games.append(game)

X_train = []
y_train = []
for game in games:
    board = game.board()
    for move in game.mainline_moves():
        X_train.append(encode_board(board))
        y_train.append(encode_move(move))
        board.push(move)

X_data = np.array(X_train, dtype=np.float32)
y_data = np.array(y_train, dtype=np.float32)

np.savez_compressed(
    "lichess_data.npz",
    X=X_data,
    y=y_data,
)
