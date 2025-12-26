import chess
import math
from mcts import Node, MCTSAgent
import torch
from training.simple_model import SimpleModel
from training.encoder import encode_board, encode_move
import numpy as np

EXPLORATION_EXPLOITATION_BALANCE = 1

device = "mps" if torch.backends.mps.is_available() else "cpu"
model = SimpleModel().to(device)
state_dict = torch.load("training/reinforcement_model.pt")
model.load_state_dict(state_dict)
model.eval()

def puct(win_pct: float, prediction: float, total_rollouts: int, child_rollouts: int):
    root = math.sqrt(math.log(total_rollouts))
    return win_pct + EXPLORATION_EXPLOITATION_BALANCE * prediction * root / (1 + child_rollouts)

class ReinforcementAgent(MCTSAgent):
    def select_child(self, node: Node) -> Node:
        board_enc = encode_board(node.board)
        board_enc = torch.from_numpy(board_enc).unsqueeze(0).to(device)
        _, model_moves = model(board_enc)
        model_moves = model_moves.squeeze(0)

        legal_moves = np.zeros(4096, dtype=np.bool)
        for move in node.board.legal_moves:
            move_enc = encode_move(move)
            legal_moves[move_enc] = True
        legal_moves = torch.from_numpy(legal_moves).to(device)

        move_candidates = torch.where(legal_moves, model_moves, -float("inf"))
        probs = torch.softmax(move_candidates, dim=-1)

        total_rollouts = sum(child.visits for child in node.children)
        best_node = None
        best_score = -float("inf")

        for child in node.children:
            move_enc = encode_move(child.move)
            child_score = puct(child.wins[node.board.turn], probs[move_enc], total_rollouts, child.visits)
            if child_score > best_score:
                best_node = child
                best_score = child_score

        return best_node

    def rollout(self, board: chess.Board) -> chess.Color:
        board_enc = encode_board(board)
        board_enc = torch.from_numpy(board_enc).unsqueeze(0).to(device)
        value, _ = model(board_enc)
        return value