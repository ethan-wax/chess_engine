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
    score = 200 * (piece_count['k'] - piece_count['K']) \
        + 9 * (piece_count['q'] - piece_count['Q']) \
        + 5 * (piece_count['r'] - piece_count['R']) \
        + 3 * (piece_count['b'] - piece_count['B']) \
        + 3 * (piece_count['n'] - piece_count['N']) \
        + 1 * (piece_count['p'] - piece_count['P']) 

    return score

    

def count_pieces(board: chess.Board) -> dict[str, int]:
    piece_count = defaultdict(int)
    for piece in board.piece_map().values():
        p = piece.symbol()
        piece_count[p] = piece_count[p] + 1
    return dict(piece_count) 


if __name__ == "__main__":
    board = chess.Board()
    print(shannon_score(board))