import chess

VALUES = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0,
}
MATE = 100000

def evaluate(board):
    """Simple material + center bonus. Positive score favors White."""
    if board.is_checkmate():
        return -MATE if board.turn == chess.WHITE else MATE
    if board.is_game_over(claim_draw=True):
        return 0
    score = 0
    center = {chess.D4, chess.E4, chess.D5, chess.E5}
    for square, piece in board.piece_map().items():
        sign = 1 if piece.color == chess.WHITE else -1
        score += sign * VALUES[piece.piece_type]
        if square in center:
            score += sign * 20
    return score
