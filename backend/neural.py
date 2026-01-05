from pathlib import Path
import chess
import numpy as np
import torch

from training.encoder import decode_move, encode_board, encode_move
from training.simple_model import SimpleModel

device = "mps" if torch.backends.mps.is_available() else "cpu"
model = SimpleModel().to(device)
model_path = Path("training/simple_nn_model.pt")
state_dict = torch.load(model_path)
model.load_state_dict(state_dict)
model.eval()


def neural_move(board: chess.Board) -> str:
    board_enc = encode_board(board)
    board_enc = torch.from_numpy(board_enc).unsqueeze(0).to(device)
    _, model_moves = model(board_enc)

    legal_moves = np.zeros(4096, dtype=np.bool)
    for move in board.legal_moves:
        move_enc = encode_move(move)
        legal_moves[move_enc] = True
    legal_moves = torch.from_numpy(legal_moves).to(device)

    move_candidates = torch.where(legal_moves, model_moves, -float("inf"))
    probs = torch.softmax(move_candidates, dim=-1)
    move = torch.multinomial(probs, 1).item()

    return board.san(decode_move(move))
