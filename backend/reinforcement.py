from dataclasses import dataclass
from pathlib import Path
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
model_path = Path("training/reinforcement_model.pt")
state_dict = torch.load(model_path)
model.load_state_dict(state_dict)
model.eval()

old_model = SimpleModel().to(device)
old_model_path = Path("training/old_reinforcement.pt")
old_state_dict = torch.load(old_model_path)
old_model.load_state_dict(old_state_dict)
old_model.eval()

def puct(win_pct: float, prediction: float, total_rollouts: int, child_rollouts: int):
    if total_rollouts == 0:
        return win_pct
    root = math.sqrt(math.log(total_rollouts))
    return win_pct + EXPLORATION_EXPLOITATION_BALANCE * prediction * root / (1 + child_rollouts)

memo = {}
MAX_MEMO_SIZE = 100000  # Limit memo size to prevent memory bloat

def clear_memo_if_needed():
    """Clear memo if it gets too large"""
    if len(memo) > MAX_MEMO_SIZE:
        memo.clear()

@dataclass
class ReinforcementAgent(MCTSAgent):
    node_type: type = ReinforcementNode
    old: bool = False

    def __post_init__(self):
        if self.old:
            self.model = old_model
        else:
            self.model = model

    def select_child(self, node: Node) -> Node:
        clear_memo_if_needed()
        key = chess.polyglot.zobrist_hash(node.board)
        if key not in memo:
            board_enc = encode_board(node.board)
            board_enc = torch.from_numpy(board_enc).unsqueeze(0).to(device)
            with torch.no_grad():
                _, model_moves = self.model(board_enc)
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

    def rollout(self, board: chess.Board) -> float:
        if board.is_game_over():
            winner = board.outcome().winner
            return 1 if winner is not None else 0
        board_enc = encode_board(board)
        board_enc = torch.from_numpy(board_enc).unsqueeze(0).to(device)
        with torch.no_grad():
            value, _ = self.model(board_enc)
        return value.item()