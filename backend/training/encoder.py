import chess
import numpy as np


def encode_board(board: chess.Board) -> np.ndarray:
    """Returns an 8 x 8 x 18 numpy array showing where each player's pieces are.
    
    Planes 0 - 5 are White's pieces
    Planes 6 - 11 are Black's pieces
    Planes 12 - 15 represent castling rights - a 1 on each rook that is legal
    Plane 16 represents turn to move - all 1s for white and all 0s for black
    Plane 17 represents all pawns where en passant is possible
    
    Returns:
        np.ndarray: Shape (18, 8, 8) with dtype uint8
    """
    # Initialize all planes to zeros: shape (18, 8, 8)
    planes = np.zeros((18, 8, 8), dtype=np.uint8)
    
    # Fill piece planes (0-11)
    for square, piece in board.piece_map().items():
        p_type = piece.piece_type
        color_shift = 0 if piece.color == chess.WHITE else 6
        i = chess.square_rank(square)
        j = chess.square_file(square)
        if p_type == chess.PAWN:
            piece_shift = 0
        elif p_type == chess.KNIGHT:
            piece_shift = 1
        elif p_type == chess.BISHOP:
            piece_shift = 2
        elif p_type == chess.ROOK:
            piece_shift = 3
        elif p_type == chess.QUEEN:
            piece_shift = 4
        else:  # KING
            piece_shift = 5
        planes[color_shift + piece_shift, i, j] = 1

    # Castling rights (planes 12-15)
    plane_idx = 12
    for color in [chess.WHITE, chess.BLACK]:
        if board.has_kingside_castling_rights(color):
            planes[plane_idx] = 1
        plane_idx += 1
        if board.has_queenside_castling_rights(color):
            planes[plane_idx] = 1
        plane_idx += 1

    # Turn to move (plane 16)
    if board.turn == chess.WHITE:
        planes[16] = 1

    # En passant (plane 17)
    if board.ep_square is not None:
        square = board.ep_square
        i = chess.square_rank(square)
        j = chess.square_file(square)
        planes[17, i, j] = 1

    return planes


def encode_move(move: chess.Move) -> int:
    start = move.from_square
    end = move.to_square
    return start * 64 + end