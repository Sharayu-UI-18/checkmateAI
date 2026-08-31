import chess
from evaluation import evaluate


def minimax(board, depth, maximizing_player):
    """
    Recursive Minimax algorithm.

    White = maximizing player
    Black = minimizing player
    """

    # Base case
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    # WHITE tries to maximize score
    if maximizing_player:
        best_score = float("-inf")

        for move in list(board.legal_moves):
            board.push(move)

            score = minimax(
                board,
                depth - 1,
                False
            )

            board.pop()

            best_score = max(best_score, score)

        return best_score

    # BLACK tries to minimize score
    else:
        best_score = float("inf")

        for move in list(board.legal_moves):
            board.push(move)

            score = minimax(
                board,
                depth - 1,
                True
            )

            board.pop()

            best_score = min(best_score, score)

        return best_score


def find_best_move(board, depth=3):
    """
    Finds the best move for the player whose turn it currently is.
    """

    best_move = None

    # WHITE
    if board.turn == chess.WHITE:
        best_score = float("-inf")

        for move in list(board.legal_moves):
            board.push(move)

            score = minimax(
                board,
                depth - 1,
                False
            )

            board.pop()

            if score > best_score:
                best_score = score
                best_move = move

    # BLACK
    else:
        best_score = float("inf")

        for move in list(board.legal_moves):
            board.push(move)

            score = minimax(
                board,
                depth - 1,
                True
            )

            board.pop()

            if score < best_score:
                best_score = score
                best_move = move

    return best_move