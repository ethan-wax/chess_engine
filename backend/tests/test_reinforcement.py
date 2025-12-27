import chess

from backend.reinforcement import (
    ReinforcementAgent,
    ReinforcementNode,
    puct
)


def test_init_agent():
    agent = ReinforcementAgent(800)
    assert agent.num_rounds == 800


def test_init_agent_default():
    agent = ReinforcementAgent()
    assert agent.num_rounds == 500


def test_puct_function():
    win_pct = 0.5
    total_rollouts = 100
    child_rollouts = 10
    score = puct(win_pct, 0.5, total_rollouts, child_rollouts)
    assert isinstance(score, float)
    assert score > win_pct  # Should add exploration bonus


def test_mcts_agent_rollout():
    agent = ReinforcementAgent(100)
    board = chess.Board()
    winner = agent.rollout(board.copy())
    assert winner in [chess.WHITE, chess.BLACK]


def test_mcts_agent_rollout_terminates():
    agent = ReinforcementAgent(100)
    board = chess.Board()
    # Rollout should eventually terminate
    winner = agent.rollout(board.copy())
    assert winner is not None


def test_mcts_agent_select_move():
    agent = ReinforcementAgent(10)  # Use fewer rounds for faster testing
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
    agent = ReinforcementAgent(10)
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
    agent = ReinforcementAgent(100)
    board = chess.Board()
    root = ReinforcementNode(board, None)

    # Add some children
    child1 = root.add_random_child()
    child2 = root.add_random_child()
    child1.record_win(chess.WHITE)
    child1.record_win(chess.WHITE)
    child2.record_win(chess.BLACK)

    selected = agent.select_child(root)
    assert selected in [child1, child2]


def test_mcts_agent_select_child_single_child():
    agent = ReinforcementAgent(100)
    board = chess.Board()
    root = ReinforcementNode(board, None)
    child = root.add_random_child()

    selected = agent.select_child(root)
    assert selected == child
