from dataclasses import dataclass, field
import chess
import random
import math

import logging

logger = logging.getLogger(__name__)

EXPLORATION_EXPLOITATION_BALANCE = 1


@dataclass
class Node:
    board: chess.Board
    move: chess.Move
    parent: "Node | None" = None
    children: list["Node"] = field(default_factory=list)
    visits: int = 0
    wins: dict[chess.Color, float] = field(
        default_factory=lambda: {chess.WHITE: 0.0, chess.BLACK: 0.0}
    )
    unvisited_moves: set[str] = field(default_factory=set)

    def __post_init__(self):
        """Called after __init__ sets all fields. Add custom initialization logic here."""
        for m in self.board.legal_moves:
            self.unvisited_moves.add(m)

    def add_random_child(self):
        new_move = random.choice(list(self.unvisited_moves))
        self.unvisited_moves.remove(new_move)
        new_board = self.board.copy()
        new_board.push(new_move)
        new_node = Node(new_board, new_move, parent=self)
        self.children.append(new_node)
        return new_node

    def record_win(self, winner: chess.Color):
        self.wins[winner] += 1
        self.visits += 1

    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    def is_terminal(self):
        return self.board.is_game_over()

    def win_percent(self, player: chess.Color):
        return self.wins[player] / self.visits


def uct(win_pct: float, total_rollouts: int, child_rollouts: int):
    # If child hasn't been visited, give it infinite score to encourage exploration
    if child_rollouts == 0:
        return float("inf")
    # If parent hasn't been visited, avoid log(0) error
    if total_rollouts == 0:
        return win_pct
    root = math.sqrt(math.log(total_rollouts) / child_rollouts)
    return win_pct + EXPLORATION_EXPLOITATION_BALANCE * root


@dataclass
class MCTSAgent:
    num_rounds: int = 500

    def select_move(self, board) -> chess.Move:
        logger.info(f"{'white' if board.turn else 'black'}'s move")

        root = Node(board, None)

        for _ in range(self.num_rounds):
            node = root
            while (not node.can_add_child()) and (not node.is_terminal()):
                node = self.select_child(node)

            if node.can_add_child():
                node = node.add_random_child()

            winner = self.rollout(node.board)

            while node is not None:
                node.record_win(winner)
                node = node.parent

        best_move = None
        best_score = -1
        for child in root.children:
            child_score = child.win_percent(board.turn)
            if child_score > best_score:
                best_move = child.move
                best_score = child_score

        return board.san(best_move)

    def select_child(self, node: Node) -> Node:
        total_rollouts = sum(child.visits for child in node.children)
        best_node = None
        best_score = -float("inf")

        for child in node.children:
            child_score = uct(child.wins[node.board.turn], total_rollouts, child.visits)
            if child_score > best_score:
                best_node = child
                best_score = child_score
        return best_node

    def rollout(self, board: chess.Board) -> chess.Color:
        board = board.copy()

        while not board.is_game_over():
            moves = list(board.legal_moves)
            move = random.choice(moves)
            board.push(move)

        if board.is_checkmate():
            return chess.WHITE if board.turn == chess.BLACK else chess.BLACK
        elif (
            board.is_stalemate()
            or board.is_insufficient_material()
            or board.is_seventyfive_moves()
            or board.is_fivefold_repetition()
        ):
            return board.turn
        else:
            return board.turn
