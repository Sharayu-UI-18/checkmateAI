import os
import sys
import time

# Ensure current directory is in sys.path so modules import reliably
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import chess
import chess.svg
import streamlit as st

from evaluation import evaluate
from algorithms.minimax import choose_move as minimax
from algorithms.alpha_beta import choose_move as alpha_beta
from algorithms.alpha_beta_ordered import choose_move as ordered
from algorithms.iterative_deepening import choose_move as iterative_deepening
from algorithms.mcts import choose_move as mcts

st.set_page_config(
    page_title="CheckmateAI Chess Engine",
    page_icon="♟️",
    layout="wide"
)

ALGORITHMS = {
    "Minimax": minimax,
    "Alpha-Beta Pruning": alpha_beta,
    "Alpha-Beta + Move Ordering": ordered,
    "Alpha-Beta + Iterative Deepening": iterative_deepening,
    "Monte Carlo Tree Search (MCTS)": mcts,
}

PIECES = {
    (chess.WHITE, chess.KING): "♔", (chess.WHITE, chess.QUEEN): "♕",
    (chess.WHITE, chess.ROOK): "♖", (chess.WHITE, chess.BISHOP): "♗",
    (chess.WHITE, chess.KNIGHT): "♘", (chess.WHITE, chess.PAWN): "♙",
    (chess.BLACK, chess.KING): "♚", (chess.BLACK, chess.QUEEN): "♛",
    (chess.BLACK, chess.ROOK): "♜", (chess.BLACK, chess.BISHOP): "♝",
    (chess.BLACK, chess.KNIGHT): "♞", (chess.BLACK, chess.PAWN): "♟",
}

# ---- Session state init ------------------------------------------------------
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected" not in st.session_state:
    st.session_state.selected = None
if "stats" not in st.session_state:
    st.session_state.stats = None
if "notice" not in st.session_state:
    st.session_state.notice = "Select a white piece, then choose a highlighted square."
if "bot_running" not in st.session_state:
    st.session_state.bot_running = False

# ---- Styles ------------------------------------------------------------------
st.markdown("""
<style>
    .block-container { max-width: 1500px; padding-top: 1.6rem; padding-bottom: 2rem; }
    [data-testid="stSidebar"] { min-width: 290px; }
    .chess-heading { font-size: 2.3rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: .2rem; }
    .chess-subtitle { color: #9CA3AF; margin-bottom: 1.2rem; font-size: 0.95rem; }
    div[data-testid="stButton"] button { transition: transform 100ms ease, filter 100ms ease; }
    div[data-testid="stButton"] button:hover { filter: brightness(1.08); transform: scale(1.015); }
    .metric-card { background: #171B24; border: 1px solid #303744; border-radius: 12px; padding: 14px 16px; margin-bottom: 12px; }
    .metric-label { color: #AAB3C2; font-size: .85rem; }
    .metric-value { font-size: 1.45rem; font-weight: 750; margin-top: 3px; }
    .svg-board-container { display: flex; justify-content: center; align-items: center; width: 100%; margin: 0.5rem 0; }
    .svg-board-container svg { max-width: 480px; width: 100%; height: auto; border-radius: 8px; box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
    .winner-banner {
        background: linear-gradient(135deg, #10B981, #059669);
        color: #FFFFFF;
        padding: 16px 20px;
        border-radius: 12px;
        font-size: 1.35rem;
        font-weight: 800;
        text-align: center;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35);
        margin: 10px 0 16px 0;
        letter-spacing: -0.01em;
    }
    .draw-banner {
        background: linear-gradient(135deg, #6B7280, #4B5563);
        color: #FFFFFF;
        padding: 16px 20px;
        border-radius: 12px;
        font-size: 1.35rem;
        font-weight: 800;
        text-align: center;
        box-shadow: 0 4px 15px rgba(107, 114, 128, 0.3);
        margin: 10px 0 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# ---- Helper: Game Result & Winner --------------------------------------------
def get_winner_declaration(board, self_play, white_algo, black_algo, algorithm):
    """Returns (is_over, banner_html, short_label) declaring the exact winner."""
    if not board.is_game_over(claim_draw=True):
        return False, None, None

    if board.is_checkmate():
        if board.turn == chess.BLACK:
            winner_title = f"🏆 White Bot ({white_algo}) Wins by Checkmate!" if self_play else "🏆 You Win by Checkmate!"
            short = "White wins by Checkmate"
        else:
            winner_title = f"🏆 Black Bot ({black_algo}) Wins by Checkmate!" if self_play else f"🤖 Bot ({algorithm}) Wins by Checkmate!"
            short = "Black wins by Checkmate"
        banner = f'<div class="winner-banner">{winner_title}</div>'
        return True, banner, short

    elif board.is_stalemate():
        banner = '<div class="draw-banner">🤝 Draw by Stalemate!</div>'
        return True, banner, "Draw (Stalemate)"

    elif board.is_insufficient_material():
        banner = '<div class="draw-banner">🤝 Draw by Insufficient Material!</div>'
        return True, banner, "Draw (Insufficient Material)"

    elif board.can_claim_threefold_repetition() or board.is_fivefold_repetition():
        banner = '<div class="draw-banner">🤝 Draw by Threefold Repetition!</div>'
        return True, banner, "Draw (Repetition)"

    elif board.can_claim_fifty_moves() or board.is_seventyfive_moves():
        banner = '<div class="draw-banner">🤝 Draw by 50-Move Rule!</div>'
        return True, banner, "Draw (50-move rule)"

    else:
        res = board.result(claim_draw=True)
        if res == "1-0":
            title = f"🏆 White Bot ({white_algo}) Wins!" if self_play else "🏆 You Win!"
            banner = f'<div class="winner-banner">{title}</div>'
            short = "White wins"
        elif res == "0-1":
            title = f"🏆 Black Bot ({black_algo}) Wins!" if self_play else f"🤖 Bot ({algorithm}) Wins!"
            banner = f'<div class="winner-banner">{title}</div>'
            short = "Black wins"
        else:
            banner = f'<div class="draw-banner">🤝 Draw ({res})</div>'
            short = f"Draw ({res})"
        return True, banner, short

# ---- Sidebar -----------------------------------------------------------------
with st.sidebar:
    st.markdown("## CheckmateAI")
    st.caption("Search algorithm comparison")

    self_play = st.checkbox(
        "Bot vs Bot",
        value=False,
        help="Two bots play automatically against each other."
    )

    if self_play:
        st.markdown("### Bot Match Setup")
        white_algo = st.selectbox("White bot algorithm", list(ALGORITHMS.keys()), index=0, key="white_algo")
        black_algo = st.selectbox("Black bot algorithm", list(ALGORITHMS.keys()), index=1, key="black_algo")
        depth = st.slider("Search depth (plies)", min_value=1, max_value=4, value=2)
        delay = st.slider("Move delay (seconds)", min_value=0.1, max_value=2.0, value=0.4, step=0.1)

        st.markdown("---")
        # Match control button: Start / Pause
        board_check = st.session_state.board
        game_is_done = board_check.is_game_over(claim_draw=True)

        if game_is_done:
            st.session_state.bot_running = False

        if not st.session_state.bot_running:
            if st.button("▶ Start Bot Match", type="primary", use_container_width=True, disabled=game_is_done):
                st.session_state.bot_running = True
                st.rerun()
        else:
            if st.button("⏸ Pause Match", type="secondary", use_container_width=True):
                st.session_state.bot_running = False
                st.rerun()

        auto_bot = True
        algorithm = None
    else:
        st.session_state.bot_running = False
        white_algo = None
        black_algo = None
        delay = 0.3
        algorithm = st.selectbox("Algorithm (plays Black)", list(ALGORITHMS.keys()))
        depth = st.slider("Search depth (plies)", min_value=1, max_value=4, value=3)
        if "MCTS" in algorithm:
            st.caption(f"MCTS budget: {depth * 100} simulations.")
        else:
            st.caption("Higher depth takes longer to compute.")
        auto_bot = st.checkbox("Auto bot move", value=True,
                               help="Bot automatically plays after you move.")

    st.markdown("---")
    if st.button("🔄 New game", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.selected = None
        st.session_state.stats = None
        st.session_state.notice = "New game started. White moves first."
        st.session_state.bot_running = False
        st.rerun()

# ---- Aliases -----------------------------------------------------------------
board = st.session_state.board
selected = st.session_state.selected
is_over, winner_banner, winner_label = get_winner_declaration(
    board, self_play, white_algo, black_algo, algorithm
)
if is_over:
    st.session_state.bot_running = False

targets = {
    move.to_square for move in board.legal_moves
    if selected is not None and move.from_square == selected
}

# ---- Header ------------------------------------------------------------------
st.markdown('<div class="chess-heading">Checkmate<span style="color:#7C9B78">AI</span></div>',
            unsafe_allow_html=True)
st.markdown('<div class="chess-subtitle">Play against search algorithms and inspect their decisions.</div>',
            unsafe_allow_html=True)

board_col, info_col = st.columns([1.45, 1], gap="large")

# ---- Board column ------------------------------------------------------------
with board_col:
    # Display Winner banner prominently above the board if game finished
    if is_over and winner_banner:
        st.markdown(winner_banner, unsafe_allow_html=True)
    elif board.is_check():
        st.warning("⚠️ Check!")

    # Clean board rendering slot
    board_slot = st.empty()

    if self_play:
        with board_slot.container():
            current_turn_name = "White" if board.turn == chess.WHITE else "Black"
            current_bot_algo = white_algo if board.turn == chess.WHITE else black_algo
            if not is_over:
                status_icon = "🟢 Running" if st.session_state.bot_running else "⏸ Paused (Click 'Start Bot Match' to begin)"
                st.write(f"**Turn:** {current_turn_name} ({current_bot_algo}) &nbsp;|&nbsp; Status: *{status_icon}*")
            else:
                st.write(f"**Match Finished:** {winner_label}")

            last_move = board.peek() if board.move_stack else None
            check_sq = board.king(board.turn) if board.is_check() else None
            board_svg = chess.svg.board(board, size=480, lastmove=last_move, check=check_sq)
            st.markdown(f'<div class="svg-board-container">{board_svg}</div>', unsafe_allow_html=True)

    else:
        with board_slot.container():
            st.write("**Your turn - White**" if board.turn == chess.WHITE else f"**Bot to move - Black ({algorithm})**")

            square_css = ["<style>"]
            for sq in chess.SQUARES:
                file_idx = chess.square_file(sq)
                rank_idx = chess.square_rank(sq)
                is_light = (file_idx + rank_idx) % 2 == 1
                bg = "#EEEED2" if is_light else "#769656"
                fg = "#F8F8F0" if is_light else "#20251C"
                border = "3px solid #F6C453" if sq == selected else "1px solid rgba(20,25,30,.20)"
                if sq in targets:
                    bg = "#BACA44" if is_light else "#A3B832"
                square_css.append(
                    f'.st-key-sq{sq} button {{ background:{bg} !important; color:{fg} !important; '
                    f'border:{border} !important; border-radius:5px !important; '
                    f'width:100% !important; aspect-ratio:1 / 1 !important; '
                    f'height:auto !important; min-height:0 !important; padding:0 !important; '
                    f'box-shadow:none !important; display:flex !important; align-items:center !important; '
                    f'justify-content:center !important; }}'
                )
                square_css.append(
                    f'.st-key-sq{sq} button p {{ font-size:clamp(1.25rem, 3vw, 2.65rem) !important; '
                    f'line-height:1 !important; margin:0 !important; '
                    f'font-family:\"Apple Symbols\",\"Segoe UI Symbol\",\"DejaVu Sans\",sans-serif !important; '
                    f'text-shadow:0 1px 1px rgba(0,0,0,.20); }}'
                )
                piece = board.piece_at(sq)
                if piece:
                    piece_color = "#FFFFFF" if piece.color == chess.WHITE else "#202124"
                    shadow = ("0 1px 2px #303030, 0 0 2px #303030" if piece.color == chess.WHITE
                              else "0 1px 1px rgba(255,255,255,.25)")
                    square_css.append(
                        f'.st-key-sq{sq} button p {{ color:{piece_color} !important; '
                        f'text-shadow:{shadow} !important; }}'
                    )
            square_css.append("</style>")
            css_payload = "\n".join(square_css)
            st.markdown(css_payload, unsafe_allow_html=True)

            for rank in range(7, -1, -1):
                cols = st.columns(8, gap="small")
                for file_idx, col in enumerate(cols):
                    sq = chess.square(file_idx, rank)
                    piece = board.piece_at(sq)
                    label = PIECES[(piece.color, piece.piece_type)] if piece else "\u2009"
                    if sq in targets and piece is None:
                        label = "\u00b7"
                    with col:
                        clicked = st.button(
                            label, key=f"sq{sq}", use_container_width=True,
                            disabled=(board.turn != chess.WHITE or is_over),
                        )
                    if clicked:
                        if selected is None:
                            if piece and piece.color == chess.WHITE:
                                st.session_state.selected = sq
                                st.session_state.notice = (
                                    f"Selected {chess.square_name(sq)}. Choose a highlighted destination.")
                            else:
                                st.session_state.notice = "Select one of your white pieces first."
                        elif sq == selected:
                            st.session_state.selected = None
                            st.session_state.notice = "Selection cleared."
                        else:
                            legal_options = [
                                m for m in board.legal_moves
                                if m.from_square == selected and m.to_square == sq
                            ]
                            if legal_options:
                                move = legal_options[0]
                                if move.promotion:
                                    move = chess.Move(selected, sq, promotion=chess.QUEEN)
                                board.push(move)
                                st.session_state.selected = None
                                st.session_state.stats = None
                                st.session_state.notice = f"You played {move.uci()}."
                            elif piece and piece.color == chess.WHITE:
                                st.session_state.selected = sq
                                st.session_state.notice = (
                                    f"Selected {chess.square_name(sq)}. Choose a highlighted destination.")
                            else:
                                st.session_state.notice = "That destination is not legal."
                        st.rerun()

            st.caption("Highlighted squares show legal destinations. Promotions default to queen.")

# ---- Info / Engine panel -----------------------------------------------------
with info_col:
    st.subheader("Engine panel")

    if self_play:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">White Bot (plays first)</div>'
            f'<div class="metric-value" style="font-size:1.05rem;color:#E5E7EB">{white_algo}</div>'
            f'<div class="metric-label" style="margin-top:10px">Black Bot</div>'
            f'<div class="metric-value" style="font-size:1.05rem;color:#E5E7EB">{black_algo}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(f"**Selected algorithm**  \n{algorithm}")

    st.markdown(f"**Search depth**  \n{depth} plies")

    score = evaluate(board) / 100
    score_color = "#86EFAC" if score > 0 else "#FCA5A5" if score < 0 else "#E5E7EB"
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">Position evaluation - White perspective</div>'
        f'<div class="metric-value" style="color:{score_color}">{score:+.2f}</div>'
        f'<div class="metric-label">Positive favors White - Negative favors Black</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.info(st.session_state.notice)

    # ---- Bot move execution --------------------------------------------------
    if not is_over:
        if self_play and st.session_state.bot_running:
            current_algo_name = white_algo if board.turn == chess.WHITE else black_algo
            current_algo_fn = ALGORITHMS[current_algo_name]
            with st.spinner(f"{current_algo_name} ({'White' if board.turn == chess.WHITE else 'Black'}) is thinking..."):
                time.sleep(delay)
                move, score, stats = current_algo_fn(board, depth)
            if move is not None:
                side = "White" if board.turn == chess.WHITE else "Black"
                board.push(move)
                st.session_state.notice = f"Bot ({side} - {current_algo_name}) played {move.uci()}."
                st.session_state.stats = stats
            else:
                st.session_state.notice = "The engine did not return a move."
                st.session_state.bot_running = False

            # Check if this move ended the game
            if board.is_game_over(claim_draw=True):
                st.session_state.bot_running = False

            st.rerun()

        elif not self_play and board.turn == chess.BLACK:
            black_fn = ALGORITHMS[algorithm]
            if auto_bot:
                with st.spinner(f"{algorithm} is thinking..."):
                    move, score, stats = black_fn(board, depth)
                if move is not None:
                    board.push(move)
                    st.session_state.notice = f"Bot played {move.uci()}."
                    st.session_state.stats = stats
                else:
                    st.session_state.notice = "The engine did not return a move."
                st.rerun()
            else:
                if st.button("Make bot move", type="primary", use_container_width=True):
                    with st.spinner(f"{algorithm} is searching..."):
                        move, score, stats = black_fn(board, depth)
                    if move is not None:
                        board.push(move)
                        st.session_state.notice = f"Bot played {move.uci()}."
                        st.session_state.stats = stats
                    else:
                        st.session_state.notice = "The engine did not return a move."
                    st.rerun()

    # ---- Stats ---------------------------------------------------------------
    if st.session_state.stats:
        stats = st.session_state.stats
        a, b = st.columns(2)
        with a:
            st.metric("Nodes searched", f"{stats['nodes']:,}")
        with b:
            if "simulations" in stats:
                st.metric("Simulations", f"{stats['simulations']:,}")
            else:
                st.metric("Alpha-Beta cutoffs", f"{stats.get('cutoffs', 0):,}")
        st.metric("Search time", f"{stats['seconds']:.4f} s")
        if stats["seconds"] > 0:
            st.metric("Nodes per second", f"{stats['nodes'] / stats['seconds']:,.0f}")

    # ---- Captured pieces -----------------------------------------------------
    captured_by_white = []
    captured_by_black = []
    replay_board = chess.Board()
    for historical_move in board.move_stack:
        if replay_board.is_capture(historical_move):
            if replay_board.is_en_passant(historical_move):
                captured_piece = chess.Piece(chess.PAWN, not replay_board.turn)
            else:
                captured_piece = replay_board.piece_at(historical_move.to_square)
            if captured_piece:
                symbol = PIECES[(captured_piece.color, captured_piece.piece_type)]
                if replay_board.turn == chess.WHITE:
                    captured_by_white.append(symbol)
                else:
                    captured_by_black.append(symbol)
        replay_board.push(historical_move)

    st.markdown("### Captured pieces")
    cap_white, cap_black = st.columns(2)
    with cap_white:
        st.markdown("**Captured by White**")
        st.markdown(" ".join(captured_by_white) if captured_by_white else "-",
                    help="Pieces captured by White.")
    with cap_black:
        st.markdown("**Captured by Black**")
        st.markdown(" ".join(captured_by_black) if captured_by_black else "-",
                    help="Pieces captured by Black.")

    with st.expander("Move history", expanded=False):
        if board.move_stack:
            replay = chess.Board()
            san_moves = []
            for move in board.move_stack:
                san_moves.append(replay.san(move))
                replay.push(move)
            st.write(" ".join(
                f"{i // 2 + 1}. {san_moves[i]}" if i % 2 == 0 else san_moves[i]
                for i in range(len(san_moves))
            ))
        else:
            st.write("No moves yet.")

    if is_over and winner_label:
        st.success(f"Final Outcome: {winner_label}")
