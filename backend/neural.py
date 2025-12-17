import chess
import torch
from torch.distributions import Categorical
import numpy as np
from training.simple_model import SimpleModel
from training.encoder import encode_board, encode_move, decode_move

device = "mps" if torch.backends.mps.is_available() else "cpu"
model = SimpleModel().to(device)
state_dict = torch.load('training/simple_nn_model.pt')
model.load_state_dict(state_dict)
model.eval()

def neural_move(board: chess.Board) -> str:
    board_enc = encode_board(board)
    board_enc.to(device)
    model_moves = model(board_enc)

    legal_moves = np.zeroes(4096)
    for move in board.legal_moves:
        move_enc = encode_move(move)
        legal_moves[move_enc] = 1
    legal_moves = torch.from_numpy(legal_moves).to(device)
    
    move_candidates = legal_moves & model_moves
    probs = Categorical(logits=move_candidates)
    move = probs.sample().item()

    return board.san(decode_move(move))

