import time
import math
import random
import chess
from evaluation import evaluate

class MCTSNode:
    __slots__ = ('parent', 'move', 'turn', 'children', 'untried_moves', 'visits', 'wins')

    def __init__(self, parent=None, move=None, turn=chess.WHITE, legal_moves=None):
        self.parent = parent
        self.move = move
        self.turn = turn
        self.children = []
        self.untried_moves = list(legal_moves) if legal_moves is not None else []
        random.shuffle(self.untried_moves)
        self.visits = 0
        self.wins = 0.0

def ucb1(parent_visits, child, c=1.414):
    if child.visits == 0:
        return float("inf")
    return (child.wins / child.visits) + c * math.sqrt(math.log(parent_visits) / child.visits)

def rollout(board, max_steps=6):
    for _ in range(max_steps):
        if board.is_game_over(claim_draw=True):
            break
        moves = list(board.legal_moves)
        if not moves:
            break
        board.push(random.choice(moves))

    if board.is_checkmate():
        return 0.0 if board.turn == chess.WHITE else 1.0
    if board.is_game_over(claim_draw=True):
        return 0.5

    score = evaluate(board)
    scaled = max(-20.0, min(20.0, score / 300.0))
    return 1.0 / (1.0 + math.exp(-scaled))

def choose_move(board, depth=3):
    start = time.perf_counter()
    legal_moves = list(board.legal_moves)
    if not legal_moves:
        return None, evaluate(board), {"nodes": 0, "cutoffs": 0, "simulations": 0, "seconds": 0.0}

    if len(legal_moves) == 1:
        move = legal_moves[0]
        board.push(move)
        score = evaluate(board)
        board.pop()
        return move, score, {"nodes": 1, "cutoffs": 0, "simulations": 1, "seconds": time.perf_counter() - start}

    simulations = max(100, depth * 100)
    root = MCTSNode(parent=None, move=None, turn=board.turn, legal_moves=legal_moves)
    nodes_created = 1

    for _ in range(simulations):
        node = root
        pushed = 0

        # 1. Selection
        while not node.untried_moves and node.children and not board.is_game_over(claim_draw=True):
            node = max(node.children, key=lambda c: ucb1(node.visits, c))
            board.push(node.move)
            pushed += 1

        # 2. Expansion
        if node.untried_moves and not board.is_game_over(claim_draw=True):
            move = node.untried_moves.pop()
            board.push(move)
            pushed += 1
            child = MCTSNode(parent=node, move=move, turn=board.turn, legal_moves=board.legal_moves)
            node.children.append(child)
            node = child
            nodes_created += 1

        # 3. Simulation
        sim_board = board.copy(stack=False)
        white_prob = rollout(sim_board, max_steps=6)

        # Unwind board to root state
        for _ in range(pushed):
            board.pop()

        # 4. Backpropagation
        curr = node
        while curr is not None:
            curr.visits += 1
            if curr.parent is not None:
                # Reward is from the perspective of curr.parent.turn (the player who made curr.move)
                reward = white_prob if curr.parent.turn == chess.WHITE else (1.0 - white_prob)
                curr.wins += reward
            curr = curr.parent

    # Pick the child with the highest visit count
    if not root.children:
        best_move = random.choice(legal_moves)
    else:
        best_child = max(root.children, key=lambda c: c.visits)
        best_move = best_child.move

    board.push(best_move)
    best_score = evaluate(board)
    board.pop()

    elapsed = time.perf_counter() - start
    stats = {
        "nodes": nodes_created,
        "simulations": simulations,
        "cutoffs": 0,
        "seconds": elapsed
    }
    return best_move, best_score, stats
