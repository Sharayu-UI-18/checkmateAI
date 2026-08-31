import chess


piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0
}


def evaluate(board):

    # Checkmate
    if board.is_checkmate():

        # board.turn is the player who is checkmated
        if board.turn == chess.WHITE:
            return -100000
        else:
            return 100000

    # Draw conditions
    if (
        board.is_stalemate()
        or board.is_insufficient_material()
    ):
        return 0

    score = 0

    # Material evaluation
    for piece_type, value in piece_values.items():

        white_count = len(
            board.pieces(piece_type, chess.WHITE)
        )

        black_count = len(
            board.pieces(piece_type, chess.BLACK)
        )

        score += white_count * value
        score -= black_count * value

    # Center bonus
    center_squares = [
        chess.D4,
        chess.E4,
        chess.D5,
        chess.E5
    ]

    for square in center_squares:
        piece = board.piece_at(square)

        if piece:
            if piece.color == chess.WHITE:
                score += 20
            else:
                score -= 20

    return score