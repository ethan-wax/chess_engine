from itertools import count
import chess
from classical import shannon_score, count_doubled_pawns

def test_shannon_score_initial_position():
    board = chess.Board()
    score = shannon_score(board)
    assert score == 0

def test_shannon_score_clear_board():
    board = chess.Board()
    board.clear()
    score = shannon_score(board)
    assert score == 0

def test_count_doubled_pawns_initial_position():
    board = chess.Board()
    doubled = count_doubled_pawns(board)
    assert doubled == (0, 0)

def test_count_doubled_clear_board():
    board = chess.Board()
    board.clear()
    doubled = count_doubled_pawns(board)
    assert doubled == (0, 0)

def test_count_doubled_pawns():
    board = chess.Board()

    # Create a doubled pawn
    board.push_san('e4')
    board.push_san('d5')
    board.push_san('exd5')
    
    doubled = count_doubled_pawns(board)
    assert doubled == (2, 0)