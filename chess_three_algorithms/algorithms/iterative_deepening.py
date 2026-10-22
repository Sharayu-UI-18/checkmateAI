
import time
import chess

from evaluation import evaluate


PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}


def order_moves(board):
    """Prioritize captures and promotions."""

    def move_score(move):
        score = 0
        attacker = board.piece_at(move.from_square)

        if board.is_capture(move):
            if board.is_en_passant(move):
                victim_value = PIECE_VALUES[chess.PAWN]
            else:
                victim = board.piece_at(move.to_square)
                victim_value = (
                    PIECE_VALUES[victim.piece_type]
                    if victim else 0
                )

            attacker_value = (
                PIECE_VALUES[attacker.piece_type]
                if attacker else 0
            )

            # Most valuable victim, least valuable attacker first
            score += 10 * victim_value - attacker_value

        if move.promotion:
            score += PIECE_VALUES[move.promotion]

        return score

    return sorted(
        list(board.legal_moves),
        key=move_score,
        reverse=True,
    )


def alpha_beta(board, depth, alpha, beta, stats):
    """Alpha-Beta search with a White-positive evaluation."""

    stats["nodes"] += 1

    if depth == 0 or board.is_game_over(claim_draw=True):
        return evaluate(board)

    maximizing = board.turn == chess.WHITE

    if maximizing:
        best_score = float("-inf")

        for move in order_moves(board):
            board.push(move)
            score = alpha_beta(
                board, depth - 1, alpha, beta, stats
            )
            board.pop()

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)

            if alpha >= beta:
                stats["cutoffs"] += 1
                break

        return best_score

    best_score = float("inf")

    for move in order_moves(board):
        board.push(move)
        score = alpha_beta(
            board, depth - 1, alpha, beta, stats
        )
        board.pop()

        best_score = min(best_score, score)
        beta = min(beta, best_score)

        if alpha >= beta:
            stats["cutoffs"] += 1
            break

    return best_score


def find_best_move(board, depth=3):
    """
    Iterative Deepening with Alpha-Beta pruning.

    Searches depths 1 through `depth` and returns
    the best move from the deepest completed iteration.
    """

    start_time = time.perf_counter()

    stats = {
        "nodes": 0,
        "cutoffs": 0,
        "seconds": 0.0,
    }

    if board.is_game_over(claim_draw=True) or depth < 1:
        return None, evaluate(board), stats

    best_move = None
    best_score = evaluate(board)

    for current_depth in range(1, depth + 1):
        iteration_move = None

        if board.turn == chess.WHITE:
            iteration_score = float("-inf")
        else:
            iteration_score = float("inf")

        moves = order_moves(board)

        # Try the previous iteration's best move first
        if best_move in moves:
            moves.remove(best_move)
            moves.insert(0, best_move)

        for move in moves:
            board.push(move)

            score = alpha_beta(
                board,
                current_depth - 1,
                float("-inf"),
                float("inf"),
                stats,
            )

            board.pop()

            if board.turn == chess.WHITE:
                if score > iteration_score:
                    iteration_score = score
                    iteration_move = move
            else:
                if score < iteration_score:
                    iteration_score = score
                    iteration_move = move

        if iteration_move is not None:
            best_move = iteration_move
            best_score = iteration_score

        print(
            f"Depth {current_depth}: "
            f"move={best_move}, score={best_score}"
        )

    stats["seconds"] = time.perf_counter() - start_time

    return best_move, best_score, stats


# Interface expected by app.py
choose_move = find_best_move
