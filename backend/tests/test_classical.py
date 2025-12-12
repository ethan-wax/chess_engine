import chess

from backend.classical import (
    classical_move,
    mobility,
    pawn_stats,
    shannon_score,
)


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
    doubled, _, _ = pawn_stats(board)
    assert doubled == (0, 0)


def test_count_doubled_clear_board():
    board = chess.Board()
    board.clear()
    doubled, _, _ = pawn_stats(board)
    assert doubled == (0, 0)


def test_count_doubled_pawns():
    board = chess.Board()
    board.push_san("e4")
    board.push_san("d5")
    board.push_san("exd5")
    doubled, _, _ = pawn_stats(board)
    assert doubled == (2, 0)


def test_count_stopped_pawns_initial_position():
    board = chess.Board()
    _, stopped, _ = pawn_stats(board)
    assert stopped == (0, 0)


def test_count_stopped_pawns_clear_board():
    board = chess.Board()
    board.clear()
    _, stopped, _ = pawn_stats(board)
    assert stopped == (0, 0)


def test_count_stopped_pawns():
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    _, stopped, _ = pawn_stats(board)
    assert stopped == (1, 1)


def test_count_isolated_pawns_initial_position():
    board = chess.Board()
    _, _, isolated = pawn_stats(board)
    assert isolated == (0, 0)


def test_count_isolated_pawns_clear_board():
    board = chess.Board()
    board.clear()
    _, _, isolated = pawn_stats(board)
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
    _, _, isolated = pawn_stats(board)
    assert isolated == (1, 2)


def test_classical_move():
    classical_move(chess.Board(), depth=2, alpha_beta=False)
    one_move = chess.Board()
    one_move.push_san("e4")
    classical_move(one_move, depth=2, alpha_beta=False)


def test_alpha_beta_move():
    classical_move(chess.Board(), depth=2, alpha_beta=True)
    one_move = chess.Board()
    one_move.push_san("e4")
    classical_move(one_move, depth=2, alpha_beta=True)


def test_mobililty_initial_position():
    board = chess.Board()
    mob = mobility(board)
    assert mob == (20, 20)


def test_mobility():
    board = chess.Board()
    board.push_san("e4")
    mob = mobility(board)
    assert mob == (30, 20)
