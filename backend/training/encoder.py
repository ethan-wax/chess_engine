import chess


def encode(board: chess.Board) -> list[list[list[int]]]:
    """Returns an 8 x 8 x 12 board showing where each player's pieces are."""
    planes = [[[0 for _ in range(8)] for _ in range(8)] for _ in range(12)]
    for square, piece in board.piece_map().items():
        p_type = piece.piece_type
        color_shift = 0 if piece.color == chess.WHITE else 6
        i = square // 8
        j = square % 8
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
        else:
            piece_shift = 5
        planes[color_shift + piece_shift][i][j] = 1

    return planes
