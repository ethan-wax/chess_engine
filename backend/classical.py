import chess
from collections import defaultdict

def classical_move(board: chess.Board):
    for move in board.legal_moves:
        return board.san(move)


def shannon_score(board: chess.Board) -> int:
    #     f(p) = 200(K-K')
    #        + 9(Q-Q')
    #        + 5(R-R')
    #        + 3(B-B' + N-N')
    #        + 1(P-P')
    #        - 0.5(D-D' + S-S' + I-I')
    #        + 0.1(M-M') + ...

    # KQRBNP = number of kings, queens, rooks, bishops, knights and pawns
    # D,S,I = doubled, blocked and isolated pawns
    # M = Mobility (the number of legal moves)
    score = 0
    piece_count = count_pieces(board)
    score = 200 * (piece_count['K'] - piece_count['k']) \
        + 9 * (piece_count['Q'] - piece_count['q']) \
        + 5 * (piece_count['R'] - piece_count['r']) \
        + 3 * (piece_count['B'] - piece_count['b']) \
        + 3 * (piece_count['N'] - piece_count['n']) \
        + 1 * (piece_count['P'] - piece_count['p']) 
    
    doubled = count_doubled_pawns(board)
    return score

def count_pieces(board: chess.Board) -> dict[str, int]:
    piece_count = defaultdict(int)
    for piece in board.piece_map().values():
        p = piece.symbol()
        piece_count[p] = piece_count[p] + 1
    return piece_count

def count_doubled_pawns(board: chess.Board) -> int:
    """Returns doubled count for white, black"""
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

        


if __name__ == "__main__":
    board = chess.Board()
    print(shannon_score(board))