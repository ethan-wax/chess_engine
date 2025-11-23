import chess
from classical import count_isolated_pawns, shannon_score, count_doubled_pawns, count_stopped_pawns

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
    board.push_san('e4')
    board.push_san('d5')
    board.push_san('exd5')
    doubled = count_doubled_pawns(board)
    assert doubled == (2, 0)

def test_count_stopped_pawns_initial_position():
    board = chess.Board()
    stopped = count_stopped_pawns(board)
    assert stopped == (0, 0)

def test_count_stopped_pawns_clear_board():
    board = chess.Board()
    board.clear()
    stopped = count_stopped_pawns(board)
    assert stopped == (0, 0)

def test_count_stopped_pawns():
    board = chess.Board()
    board.push_san('e4')
    board.push_san('e5')
    stopped = count_stopped_pawns(board)
    assert stopped == (1, 1)

def test_count_isolated_pawns_initial_position():
    board = chess.Board()
    isolated = count_isolated_pawns(board)
    assert isolated == (0, 0)

def test_count_isolated_pawns_clear_board():
    board = chess.Board()
    board.clear()
    isolated = count_isolated_pawns(board)
    assert isolated == (0, 0)

def test_count_isolated_pawns():
    board = chess.Board()
    board.clear()
    white_pawn = chess.Piece(chess.PAWN, chess.WHITE)
    black_pawn = chess.Piece(chess.PAWN, chess.BLACK)
    board.set_piece_at(chess.E3, white_pawn)
    board.set_piece_at(chess.B3, white_pawn)
    board.set_piece_at(chess.A3, white_pawn)
    board.set_piece_at(chess.A5, black_pawn)
    board.set_piece_at(chess.H5, black_pawn)
    isolated = count_isolated_pawns(board)
    assert isolated == (1, 2)