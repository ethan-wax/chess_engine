import chess

from backend.mcts import (
    Node,
    MCTSAgent,
    uct,
)


def test_init_agent():
    agent = MCTSAgent(800)
    assert agent.num_rounds == 800


def test_init_agent_default():
    agent = MCTSAgent()
    assert agent.num_rounds == 500


def test_init_node():
    board = chess.Board()
    move = list(board.legal_moves)[0]
    node = Node(board, move)
    assert node.board == board
    assert node.move == move
    assert node.parent is None
    assert len(node.children) == 0
    assert node.visits == 0
    assert node.wins[chess.WHITE] == 0.0
    assert node.wins[chess.BLACK] == 0.0
    assert len(node.unvisited_moves) > 0


def test_init_node_root():
    board = chess.Board()
    root = Node(board, None)
    assert root.move is None
    assert root.parent is None
    assert len(root.unvisited_moves) == len(list(board.legal_moves))


def test_node_can_add_child():
    board = chess.Board()
    move = list(board.legal_moves)[0]
    node = Node(board, move)
    assert node.can_add_child()
    assert len(node.unvisited_moves) > 0


def test_node_can_add_child_false():
    board = chess.Board()
    move = list(board.legal_moves)[0]
    node = Node(board, move)
    # Remove all unvisited moves
    node.unvisited_moves.clear()
    assert not node.can_add_child()


def test_node_is_terminal():
    board = chess.Board()
    move = list(board.legal_moves)[0]
    node = Node(board, move)
    assert not node.is_terminal()


def test_node_is_terminal_checkmate():
    # Test with a known checkmate position
    terminal_board = chess.Board()
    terminal_board.set_fen("4k3/4Q3/4K3/8/8/8/8/8 b - - 0 1")  # Checkmate
    terminal_node = Node(terminal_board, None)
    assert terminal_node.is_terminal()


def test_node_record_win():
    board = chess.Board()
    move = list(board.legal_moves)[0]
    node = Node(board, move)
    initial_visits = node.visits
    initial_wins_white = node.wins[chess.WHITE]

    node.record_win(chess.WHITE)
    assert node.visits == initial_visits + 1
    assert node.wins[chess.WHITE] == initial_wins_white + 1
    assert node.wins[chess.BLACK] == 0.0


def test_node_record_win_black():
    board = chess.Board()
    move = list(board.legal_moves)[0]
    node = Node(board, move)
    node.record_win(chess.BLACK)
    assert node.visits == 1
    assert node.wins[chess.BLACK] == 1.0
    assert node.wins[chess.WHITE] == 0.0


def test_node_win_percent():
    board = chess.Board()
    move = list(board.legal_moves)[0]
    node = Node(board, move)
    node.record_win(chess.WHITE)
    node.record_win(chess.WHITE)
    node.record_win(chess.BLACK)

    assert node.win_percent(chess.WHITE) == 2.0 / 3.0
    assert node.win_percent(chess.BLACK) == 1.0 / 3.0


def test_node_add_random_child():
    board = chess.Board()
    move = list(board.legal_moves)[0]
    node = Node(board, move)
    initial_unvisited_count = len(node.unvisited_moves)
    initial_children_count = len(node.children)

    child = node.add_random_child()
    assert len(node.unvisited_moves) == initial_unvisited_count - 1
    assert len(node.children) == initial_children_count + 1
    assert child.parent == node
    assert child.move in board.legal_moves


def test_uct_function():
    # Test UCT calculation
    win_pct = 0.5
    total_rollouts = 100
    child_rollouts = 10
    score = uct(win_pct, total_rollouts, child_rollouts)
    assert isinstance(score, float)
    assert score > win_pct  # Should add exploration bonus


def test_uct_exploration():
    # Test that UCT increases with fewer visits (more exploration)
    win_pct = 0.5
    total_rollouts = 100

    score_low_visits = uct(win_pct, total_rollouts, 1)
    score_high_visits = uct(win_pct, total_rollouts, 50)

    assert score_low_visits > score_high_visits


def test_mcts_agent_rollout():
    agent = MCTSAgent(100)
    board = chess.Board()
    winner = agent.rollout(board.copy())
    assert winner in [chess.WHITE, chess.BLACK]


def test_mcts_agent_rollout_terminates():
    agent = MCTSAgent(100)
    board = chess.Board()
    # Rollout should eventually terminate
    winner = agent.rollout(board.copy())
    assert winner is not None


def test_mcts_agent_select_move():
    agent = MCTSAgent(10)  # Use fewer rounds for faster testing
    board = chess.Board()
    move = agent.select_move(board)
    assert isinstance(move, str)
    assert len(move) > 0
    # Should be a valid SAN move
    test_board = chess.Board()
    try:
        test_board.push_san(move)
        assert True  # Move is valid
    except Exception:
        assert False, f"Invalid move returned: {move}"


def test_mcts_agent_select_move_after_one_move():
    agent = MCTSAgent(10)
    board = chess.Board()
    board.push_san("e4")
    move = agent.select_move(board)
    assert isinstance(move, str)
    test_board = chess.Board()
    test_board.push_san("e4")
    try:
        test_board.push_san(move)
        assert True
    except Exception:
        assert False, f"Invalid move returned: {move}"


def test_mcts_agent_select_child():
    agent = MCTSAgent(100)
    board = chess.Board()
    root = Node(board, None)

    # Add some children
    child1 = root.add_random_child()
    child2 = root.add_random_child()
    child1.record_win(chess.WHITE)
    child1.record_win(chess.WHITE)
    child2.record_win(chess.BLACK)

    selected = agent.select_child(root)
    assert selected in [child1, child2]


def test_mcts_agent_select_child_single_child():
    agent = MCTSAgent(100)
    board = chess.Board()
    root = Node(board, None)
    child = root.add_random_child()

    selected = agent.select_child(root)
    assert selected == child
