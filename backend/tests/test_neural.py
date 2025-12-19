import chess

from backend.neural import neural_move

def test_neural_move_initial_position():
    board = chess.Board()
    move = neural_move(board)
    assert move is not None
    legal_moves = [board.san(move) for move in board.legal_moves]
    assert move in legal_moves

def test_neural_move_one_move():
    board = chess.Board()
    board.push_san("e4")
    move = neural_move(board)
    assert move is not None
    legal_moves = [board.san(move) for move in board.legal_moves]
    assert move in legal_moves