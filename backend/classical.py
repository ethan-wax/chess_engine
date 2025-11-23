import chess
from collections import defaultdict

def classical_move(board: chess.Board):
    for move in board.legal_moves:
        return board.san(move)


def shannon_score(board: chess.Board) -> int:
    """Calculate the Shannon score for the current position
    f(p) = 200(K-K')
           + 9(Q-Q')
           + 5(R-R')
           + 3(B-B' + N-N')
           + 1(P-P')
           - 0.5(D-D' + S-S' + I-I')
           + 0.1(M-M') + ...

    KQRBNP = number of kings, queens, rooks, bishops, knights and pawns
    D,S,I = doubled, blocked and isolated pawns
    M = Mobility (the number of legal moves)
    """
    score = 0
    piece_count = count_pieces(board)
    score = 200 * (piece_count['K'] - piece_count['k']) \
        + 9 * (piece_count['Q'] - piece_count['q']) \
        + 5 * (piece_count['R'] - piece_count['r']) \
        + 3 * (piece_count['B'] - piece_count['b']) \
        + 3 * (piece_count['N'] - piece_count['n']) \
        + 1 * (piece_count['P'] - piece_count['p']) 
    
    doubled = count_doubled_pawns(board)
    stopped = count_stopped_pawns(board)
    isolated = count_isolated_pawns
    score -= 0.5 * (doubled[0] - doubled[1] + stopped[0] - stopped[1] + isolated[0] - isolated[1])
    score += 0.1 * board.legal_moves.count()
    return score

def count_pieces(board: chess.Board) -> dict[str, int]:
    piece_count = defaultdict(int)
    for piece in board.piece_map().values():
        p = piece.symbol()
        piece_count[p] = piece_count[p] + 1
    return piece_count

def count_doubled_pawns(board: chess.Board) -> tuple[int, int]:
    white, black = 0, 0
    for j in range(8):
        white_col = 0
        black_col = 0
        for i in range(8):
            square = i * 8 + j
            piece = board.piece_at(square)
            if piece and piece.symbol() == 'P':
                white_col += 1
            elif piece and piece.symbol() == 'p':
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
            if piece and piece.symbol() == 'P':
                square_above = (i + 1) * 8 + j
                if board.piece_at(square_above):
                    white += 1
            elif piece and piece.symbol() == 'p':
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
            if piece and piece.symbol() == 'P':
                pawns[j] = (True, pawns[j][1])
            elif piece and piece.symbol() == 'p':
                pawns[j] = (pawns[j][0], True)

    white, black = 0, 0
    for i in range(8):
        if i == 0:
            white += int(pawns[i][0] and not pawns[i+1][0])
            black += int(pawns[i][1] and not pawns[i+1][1])
        elif i == 7: 
            white += int(pawns[i][0] and not pawns[i-1][0])
            black += int(pawns[i][1] and not pawns[i-1][1])
        else:
            white += int(pawns[i][0] and (not pawns[i-1][0]) and (not pawns[i+1][0]))
            white += int(pawns[i][1] and (not pawns[i-1][1]) and (not pawns[i+1][1]))
    
    return white, black