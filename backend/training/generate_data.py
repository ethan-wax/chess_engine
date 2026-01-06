from pathlib import Path
import sys

# Add parent directory to path to allow imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

import chess
import chess.pgn
import numpy as np
from training.encoder import encode_board, encode_move

games = []
pgn_path = Path("training/lichess_filtered.pgn")
with open(pgn_path, "r", encoding="utf-8") as pgn:
    while True:
        game = chess.pgn.read_game(pgn)

        if game is None:
            break

        games.append(game)

X_train = []
y_train = []
for game in games:
    board = game.board()
    result = game.headers["Result"]
    match result:
        case "1-0":
            winner = 1
        case "0-1":
            winner = -1
        case "1/2-1/2":
            winner = 0
    for move in game.mainline_moves():
        X_train.append(encode_board(board))
        if board.turn == chess.WHITE:
            outcome = winner
        else:
            outcome = -1 * winner
        y_train.append([encode_move(move),  outcome])
        board.push(move)

X_data = np.array(X_train, dtype=np.float32)
y_data = np.array(y_train, dtype=np.float32)

data_path = Path("training/lichess_data.npz")
np.savez_compressed(
    data_path,
    X=X_data,
    y=y_data,
)
