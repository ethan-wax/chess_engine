from dataclasses import dataclass
import chess
import chess.polyglot
import math
from mcts import Node, MCTSAgent
import torch
from training.simple_model import SimpleModel
from training.encoder import encode_board, encode_move
import numpy as np

EXPLORATION_EXPLOITATION_BALANCE = 1

@dataclass
class ReinforcementNode(Node):
    wins: float = 0

    def add_child(self, new_board: chess.Board, new_move: chess.Move):
        return ReinforcementNode(new_board, new_move, parent=self)

    def record_win(self, value: float):
        self.wins += value

    def win_percent(self, color: chess.Color):
        same_color = 1 if color == chess.WHITE else -1
        if self.visits == 0:
            return same_color * self.wins
        return same_color * self.wins / self.visits


device = "mps" if torch.backends.mps.is_available() else "cpu"
model = SimpleModel().to(device)
state_dict = torch.load("training/reinforcement_model.pt")
model.load_state_dict(state_dict)
model.eval()

def puct(win_pct: float, prediction: float, total_rollouts: int, child_rollouts: int):
    if total_rollouts == 0:
        return win_pct
    root = math.sqrt(math.log(total_rollouts))
    return win_pct + EXPLORATION_EXPLOITATION_BALANCE * prediction * root / (1 + child_rollouts)

memo = {}

@dataclass
class ReinforcementAgent(MCTSAgent):
    node_type: type = ReinforcementNode

    def select_child(self, node: Node) -> Node:
        key = chess.polyglot.zobrist_hash(node.board)
        if key not in memo:
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

            memo[key] = probs
        
        probs = memo[key]

        total_rollouts = sum(child.visits for child in node.children)
        best_node = None
        best_score = -float("inf")

        for child in node.children:
            move_enc = encode_move(child.move)
            child_score = puct(child.win_percent(child.board.turn), probs[move_enc], total_rollouts, child.visits)
            if child_score > best_score:
                best_node = child
                best_score = child_score

        return best_node

    def rollout(self, board: chess.Board) -> chess.Color:
        board_enc = encode_board(board)
        board_enc = torch.from_numpy(board_enc).unsqueeze(0).to(device)
        value, _ = model(board_enc)
        return value