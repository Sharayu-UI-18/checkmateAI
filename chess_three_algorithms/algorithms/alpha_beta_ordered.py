import time
import chess
from evaluation import evaluate, VALUES

def ordered_moves(board):
    def score(move):
        value = 0
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            victim_value = VALUES[chess.PAWN] if board.is_en_passant(move) else (VALUES[victim.piece_type] if victim else 0)
            attacker = board.piece_at(move.from_square)
            attacker_value = VALUES[attacker.piece_type] if attacker else 0
            value += 10000 + victim_value * 10 - attacker_value
        if move.promotion:
            value += 8000 + VALUES[move.promotion]
        return value
    return sorted(list(board.legal_moves), key=score, reverse=True)

def search(board, depth, alpha, beta, stats):
    stats["nodes"] += 1
    if depth == 0 or board.is_game_over(claim_draw=True):
        return evaluate(board)
    if board.turn == chess.WHITE:
        best = float("-inf")
        for move in ordered_moves(board):
            board.push(move); score = search(board, depth - 1, alpha, beta, stats); board.pop()
            best = max(best, score); alpha = max(alpha, best)
            if alpha >= beta:
                stats["cutoffs"] += 1
                break
        return best
    best = float("inf")
    for move in ordered_moves(board):
        board.push(move); score = search(board, depth - 1, alpha, beta, stats); board.pop()
        best = min(best, score); beta = min(beta, best)
        if alpha >= beta:
            stats["cutoffs"] += 1
            break
    return best

def choose_move(board, depth):
    start = time.perf_counter()
    stats = {"nodes": 0, "cutoffs": 0}
    best_move = None
    best_score = float("-inf") if board.turn == chess.WHITE else float("inf")
    alpha, beta = float("-inf"), float("inf")
    for move in ordered_moves(board):
        board.push(move); score = search(board, depth - 1, alpha, beta, stats); board.pop()
        if (board.turn == chess.WHITE and score > best_score) or (board.turn == chess.BLACK and score < best_score):
            best_score, best_move = score, move
        if board.turn == chess.WHITE: alpha = max(alpha, best_score)
        else: beta = min(beta, best_score)
    stats["seconds"] = time.perf_counter() - start
    return best_move, best_score, stats
