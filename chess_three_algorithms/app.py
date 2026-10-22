import streamlit as st
import chess
import time

from evaluation import evaluate
from algorithms.minimax import choose_move as minimax
from algorithms.alpha_beta import choose_move as alpha_beta
from algorithms.alpha_beta_ordered import choose_move as ordered
from algorithms.iterative_deepening import choose_move as iterative_deepening
from algorithms.mcts import choose_move as mcts
st.set_page_config(
    page_title="CheckmateAI — Chess Engine",
    page_icon="♟️",
    layout="wide"
)

# st.title("♟️ CheckmateAI")
# st.caption("Explore, Play, and Compare Chess AI Algorithms")

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

if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "selected" not in st.session_state:
    st.session_state.selected = None
if "stats" not in st.session_state:
    st.session_state.stats = None
if "notice" not in st.session_state:
    st.session_state.notice = "Select a white piece, then choose a highlighted square."

st.markdown("""
<style>
    .block-container { max-width: 1600px; padding-top: 1.8rem; padding-bottom: 2rem; }
    [data-testid="stSidebar"] { min-width: 270px; }
    .chess-heading { font-size: 2.5rem; font-weight: 800; letter-spacing: -0.035em; margin-bottom: .2rem; }
    .chess-subtitle { color: #9CA3AF; margin-bottom: 1.4rem; }
    div[data-testid="stButton"] button { transition: transform 100ms ease, filter 100ms ease; }
    div[data-testid="stButton"] button:hover { filter: brightness(1.08); transform: scale(1.015); }
    .metric-card { background: #171B24; border: 1px solid #303744; border-radius: 14px; padding: 14px 16px; margin-bottom: 12px; }
    .metric-label { color: #AAB3C2; font-size: .85rem; }
    .metric-value { font-size: 1.55rem; font-weight: 750; margin-top: 3px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ♟️ CheckmateAI")
    st.caption("Search algorithm comparison")
    algorithm = st.selectbox("Algorithm", list(ALGORITHMS.keys()))
    depth = st.slider("Search depth (plies)", min_value=1, max_value=4, value=3)
    if "MCTS" in algorithm:
        st.caption(f"MCTS budget: {depth * 100} simulations.")
    else:
        st.caption("Higher depth can take significantly longer.")
    if st.button("↻  New game", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.selected = None
        st.session_state.stats = None
        st.session_state.notice = "New game started. White moves first."
        st.rerun()
    st.divider()
    auto_bot = st.checkbox("Auto bot move", value=True, help="Bot automatically plays its move after you play.")
    self_play = st.checkbox("Self-play (Bot vs Bot)", value=False, help="Bot plays both White and Black automatically.")
    st.caption("You play White by default. The selected algorithm plays Black.")

board = st.session_state.board
selected = st.session_state.selected
game_over = board.is_game_over(claim_draw=True)
targets = {
    move.to_square for move in board.legal_moves
    if selected is not None and move.from_square == selected
}

st.markdown('<div class="chess-heading">Checkmate<span style="color:#7C9B78">AI</span></div>', unsafe_allow_html=True)
st.markdown('<div class="chess-subtitle">Play against search algorithms and inspect their decisions.</div>', unsafe_allow_html=True)

board_col, info_col = st.columns([1.45, 1], gap="large")

with board_col:
    st.subheader("Board")
    if board.is_checkmate():
        st.error(f"Checkmate — {board.result(claim_draw=True)}")
    elif game_over:
        st.info(f"Game over — {board.result(claim_draw=True)}")
    elif board.is_check():
        st.warning("Check!")

    st.write("**Your turn · White**" if board.turn == chess.WHITE else "**Bot to move · Black**")

    # Give each square its own checkerboard color and each side's pieces a distinct color.
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
            f'font-family:"Apple Symbols","Segoe UI Symbol","DejaVu Sans",sans-serif !important; '
            f'text-shadow:0 1px 1px rgba(0,0,0,.20); }}'
        )
        piece = board.piece_at(sq)
        if piece:
            piece_color = "#FFFFFF" if piece.color == chess.WHITE else "#202124"
            shadow = "0 1px 2px #303030, 0 0 2px #303030" if piece.color == chess.WHITE else "0 1px 1px rgba(255,255,255,.25)"
            square_css.append(
                f'.st-key-sq{sq} button p {{ color:{piece_color} !important; text-shadow:{shadow} !important; }}'
            )
    square_css.append("</style>")
    st.markdown("\n".join(square_css), unsafe_allow_html=True)

    for rank in range(7, -1, -1):
        cols = st.columns(8, gap="small")
        for file_idx, col in enumerate(cols):
            sq = chess.square(file_idx, rank)
            piece = board.piece_at(sq)
            label = PIECES[(piece.color, piece.piece_type)] if piece else "\u2009"
            if sq in targets and piece is None:
                label = "•"
            with col:
                clicked = st.button(
                    label, key=f"sq{sq}", use_container_width=True,
                    disabled=(board.turn != chess.WHITE or game_over),
                )
            if clicked:
                if selected is None:
                    if piece and piece.color == chess.WHITE:
                        st.session_state.selected = sq
                        st.session_state.notice = f"Selected {chess.square_name(sq)}. Choose a highlighted destination."
                    else:
                        st.session_state.notice = "Select one of your white pieces first."
                elif sq == selected:
                    st.session_state.selected = None
                    st.session_state.notice = "Selection cleared."
                else:
                    legal_options = [
                        move for move in board.legal_moves
                        if move.from_square == selected and move.to_square == sq
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
                        st.session_state.notice = f"Selected {chess.square_name(sq)}. Choose a highlighted destination."
                    else:
                        st.session_state.notice = "That destination is not legal."
                st.rerun()

    st.caption("Light and dark squares are color-coded. Highlighted squares show legal destinations. Promotions default to queen.")

with info_col:
    st.subheader("Engine panel")
    st.markdown(f"**Selected algorithm**  \n{algorithm}")
    st.markdown(f"**Search depth**  \n{depth} plies")
    score = evaluate(board) / 100
    score_color = "#86EFAC" if score > 0 else "#FCA5A5" if score < 0 else "#E5E7EB"
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">Position evaluation · White perspective</div>'
        f'<div class="metric-value" style="color:{score_color}">{score:+.2f}</div>'
        f'<div class="metric-label">Positive favors White · Negative favors Black</div></div>',
        unsafe_allow_html=True,
    )
    st.info(st.session_state.notice)

    should_bot_move = False
    if not game_over:
        if self_play:
            should_bot_move = True
        elif board.turn == chess.BLACK and auto_bot:
            should_bot_move = True

    if should_bot_move:
        with st.spinner(f"{algorithm} is thinking..."):
            if self_play:
                import time; time.sleep(0.3)
            move, score, stats = ALGORITHMS[algorithm](board, depth)
        if move is not None:
            side = "White" if board.turn == chess.WHITE else "Black"
            board.push(move)
            st.session_state.notice = f"Bot ({side}) played {move.uci()}." if self_play else f"Bot played {move.uci()}."
            st.session_state.stats = stats
        else:
            st.session_state.notice = "The engine did not return a move."
        st.rerun()
    elif board.turn == chess.BLACK and not game_over:
        if st.button("🤖  Make bot move", type="primary", use_container_width=True):
            with st.spinner(f"{algorithm} is searching..."):
                move, score, stats = ALGORITHMS[algorithm](board, depth)
            if move is not None:
                board.push(move)
                st.session_state.notice = f"Bot played {move.uci()}."
                st.session_state.stats = stats
            else:
                st.session_state.notice = "The engine did not return a move."
            st.rerun()

    if st.session_state.stats:
        stats = st.session_state.stats
        a, b = st.columns(2)
        with a:
            st.metric("Nodes searched", f"{stats['nodes']:,}")
        with b:
            if "simulations" in stats:
                st.metric("Simulations", f"{stats['simulations']:,}")
            else:
                st.metric("Alpha-Beta cutoffs", f"{stats['cutoffs']:,}")
        st.metric("Search time", f"{stats['seconds']:.4f} s")
        if stats["seconds"] > 0:
            st.metric("Nodes per second", f"{stats['nodes'] / stats['seconds']:,.0f}")

    if board.is_check():
        st.warning("The side to move is in check.")

    # Reconstruct captured pieces from the move history so this also works
    # for games already in progress and does not need separate capture state.
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
        st.markdown(
            " ".join(captured_by_white) if captured_by_white else "—",
            help="Pieces captured by your side."
        )
    with cap_black:
        st.markdown("**Captured by Black**")
        st.markdown(
            " ".join(captured_by_black) if captured_by_black else "—",
            help="Pieces captured by the bot."
        )

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

    if game_over:
        st.success(f"Result: {board.result(claim_draw=True)}")
