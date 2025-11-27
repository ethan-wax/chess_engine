import chess
from collections import defaultdict


def classical_move(
    board: chess.Board, depth: int = 5, alpha_beta: bool = True
) -> str:
    """Perform the negamax algorithm to select a move.

    Uses the shannon score for evaluation.
    """
    if alpha_beta:
        move = alpha_beta_max(board, depth, -float("inf"), float("inf"))[1]
    else:
        move = nega_max(board, depth)[1]

    return board.san(move)

def alpha_beta_max(board: chess.Board, depth: int, alpha: float, beta: float) -> str:
    if board.is_checkmate():
        return -float("inf"), ''

    if (
        board.is_stalemate()
        or board.is_insufficient_material()
        or board.is_seventyfive_moves()
        or board.is_fivefold_repetition()
    ):
        return 0, ''
        
    if depth == 0:
        return (1 if board.turn == chess.WHITE else -1) * shannon_score(board), ''

    # Move ordering: prioritize captures and promotions for better alpha-beta pruning
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: (
        0 if board.is_capture(m) else 1,  # Captures first
        0 if m.promotion else 1  # Promotions second
    ))

    max_score, best_move = -float("inf"), ''
    for move in moves:
        board.push(move)
        score = -alpha_beta_max(board, depth - 1, -beta, -alpha)[0]

        board.pop()
        
        if score > max_score:
            max_score = score
            best_move = move
            alpha = max(alpha, score)

        if score >= beta:
            return max_score, best_move
        
    return max_score, best_move
            


def nega_max(board, depth) -> str:
    if board.is_checkmate():
        return -float("inf"), ''

    if (
        board.is_stalemate()
        or board.is_insufficient_material()
        or board.is_seventyfive_moves()
        or board.is_fivefold_repetition()
    ):
        return 0, ''

    if depth == 0:
        return (1 if board.turn == chess.WHITE else -1) * shannon_score(board), ''

    # Move ordering: prioritize captures and promotions
    moves = list(board.legal_moves)
    moves.sort(key=lambda m: (
        0 if board.is_capture(m) else 1,  # Captures first
        0 if m.promotion else 1  # Promotions second
    ))

    max_score, best_move = -float("inf"), ''
    for move in moves:
        board.push(move)
        score = -1 * nega_max(board, depth - 1)[0]

        if score > max_score:
            max_score = score
            best_move = move

        board.pop()

    return max_score, best_move


def shannon_score(board: chess.Board) -> int:
    """Calculate the Shannon score for the current position
    f(p) = 200(K-K')
           + 9(Q-Q')
           + 5(R-R')
           + 3(B-B' + N-N')
           + 1(P-P')
           - 0.5(D-D' + S-S' + I-I')

    KQRBNP = number of kings, queens, rooks, bishops, knights and pawns
    D,S,I = doubled, blocked and isolated pawns
    """
    score = 0
    piece_count = count_pieces(board)
    score = (
        200 * (piece_count["K"] - piece_count["k"])
        + 9 * (piece_count["Q"] - piece_count["q"])
        + 5 * (piece_count["R"] - piece_count["r"])
        + 3 * (piece_count["B"] - piece_count["b"])
        + 3 * (piece_count["N"] - piece_count["n"])
        + 1 * (piece_count["P"] - piece_count["p"])
    )

    doubled, stopped, isolated = pawn_stats(board)

    # doubled = count_doubled_pawns(board)
    # stopped = count_stopped_pawns(board)
    # isolated = count_isolated_pawns(board)
    score -= 0.5 * (
        doubled[0] - doubled[1] + stopped[0] - stopped[1] + isolated[0] - isolated[1]
    )
    return score


def count_pieces(board: chess.Board) -> dict[str, int]:
    piece_count = defaultdict(int)
    for piece in board.piece_map().values():
        p = piece.symbol()
        piece_count[p] = piece_count[p] + 1
    return piece_count

def pawn_stats(board: chess.Board) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    """Optimized pawn statistics calculation using piece_map instead of iterating all squares."""
    doubled_white, doubled_black = 0, 0
    stopped_white, stopped_black = 0, 0
    pawns = [(False, False) for _ in range(8)]
    pawn_counts = [0, 0, 0, 0, 0, 0, 0, 0]  # White pawns per file
    black_pawn_counts = [0, 0, 0, 0, 0, 0, 0, 0]  # Black pawns per file
    
    # Iterate only through existing pieces instead of all 64 squares
    for square, piece in board.piece_map().items():
        if piece.piece_type == chess.PAWN:
            file = chess.square_file(square)
            
            if piece.color == chess.WHITE:
                pawn_counts[file] += 1
                pawns[file] = (True, pawns[file][1])
                # Check if pawn is stopped (piece directly in front)
                square_above = square + 8
                if square_above < 64 and board.piece_at(square_above):
                    stopped_white += 1
            else:  # BLACK
                black_pawn_counts[file] += 1
                pawns[file] = (pawns[file][0], True)
                # Check if pawn is stopped (piece directly behind)
                square_below = square - 8
                if square_below >= 0 and board.piece_at(square_below):
                    stopped_black += 1
    
    # Count doubled pawns
    for file in range(8):
        if pawn_counts[file] >= 2:
            doubled_white += pawn_counts[file]
        if black_pawn_counts[file] >= 2:
            doubled_black += black_pawn_counts[file]

    # Count isolated pawns
    isolated_white, isolated_black = 0, 0
    for i in range(8):
        if i == 0:
            isolated_white += int(pawns[i][0] and not pawns[i + 1][0])
            isolated_black += int(pawns[i][1] and not pawns[i + 1][1])
        elif i == 7:
            isolated_white += int(pawns[i][0] and not pawns[i - 1][0])
            isolated_black += int(pawns[i][1] and not pawns[i - 1][1])
        else:
            isolated_white += int(
                pawns[i][0] and (not pawns[i - 1][0]) and (not pawns[i + 1][0])
            )
            isolated_black += int(
                pawns[i][1] and (not pawns[i - 1][1]) and (not pawns[i + 1][1])
            )
    return (doubled_white, doubled_black), (stopped_white, stopped_black), (isolated_white, isolated_black)

def count_doubled_pawns(board: chess.Board) -> tuple[int, int]:
    white, black = 0, 0
    for j in range(8):
        white_col = 0
        black_col = 0
        for i in range(8):
            square = i * 8 + j
            piece = board.piece_at(square)
            if piece and piece.symbol() == "P":
                white_col += 1
            elif piece and piece.symbol() == "p":
                black_col += 1
        if white_col >= 2:
            white += white_col
        if black_col >= 2:
            black += black_col
    return white, black


def count_stopped_pawns(board: chess.Board) -> tuple[int, int]:
    white, black = 0, 0
    for i in range(8):
        for j in range(8):
            square = i * 8 + j
            piece = board.piece_at(square)
            if piece and piece.symbol() == "P":
                square_above = (i + 1) * 8 + j
                if board.piece_at(square_above):
                    white += 1
            elif piece and piece.symbol() == "p":
                square_below = (i - 1) * 8 + j
                if board.piece_at(square_below):
                    black += 1
    return white, black


def count_isolated_pawns(board: chess.Board) -> tuple[int, int]:
    pawns = [(False, False) for _ in range(8)]
    for i in range(8):
        for j in range(8):
            square = i * 8 + j
            piece = board.piece_at(square)
            if piece and piece.symbol() == "P":
                pawns[j] = (True, pawns[j][1])
            elif piece and piece.symbol() == "p":
                pawns[j] = (pawns[j][0], True)

    white, black = 0, 0
    for i in range(8):
        if i == 0:
            white += int(pawns[i][0] and not pawns[i + 1][0])
            black += int(pawns[i][1] and not pawns[i + 1][1])
        elif i == 7:
            white += int(pawns[i][0] and not pawns[i - 1][0])
            black += int(pawns[i][1] and not pawns[i - 1][1])
        else:
            white += int(
                pawns[i][0] and (not pawns[i - 1][0]) and (not pawns[i + 1][0])
            )
            black += int(
                pawns[i][1] and (not pawns[i - 1][1]) and (not pawns[i + 1][1])
            )

    return white, black
