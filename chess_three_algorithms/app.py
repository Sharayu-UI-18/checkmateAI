import streamlit as st
import chess
from evaluation import evaluate
from algorithms.minimax import choose_move as minimax
from algorithms.alpha_beta import choose_move as alpha_beta
from algorithms.alpha_beta_ordered import choose_move as ordered

st.set_page_config(page_title="Chess AI", page_icon="♟", layout="wide")
st.title("Chess AI — Compare Algorithms")

ALGORITHMS = {
    "Minimax": minimax,
    "Alpha-Beta Pruning": alpha_beta,
    "Alpha-Beta + Move Ordering": ordered,
}
PIECES = {
    (True, chess.KING): "♔", (True, chess.QUEEN): "♕",
    (True, chess.ROOK): "♖", (True, chess.BISHOP): "♗",
    (True, chess.KNIGHT): "♘", (True, chess.PAWN): "♙",
    (False, chess.KING): "♚", (False, chess.QUEEN): "♛",
    (False, chess.ROOK): "♜", (False, chess.BISHOP): "♝",
    (False, chess.KNIGHT): "♞", (False, chess.PAWN): "♟",
}

if "board" not in st.session_state: st.session_state.board = chess.Board()
if "selected" not in st.session_state: st.session_state.selected = None
if "stats" not in st.session_state: st.session_state.stats = None
if "notice" not in st.session_state: st.session_state.notice = "Click a White piece, then its destination."

with st.sidebar:
    algorithm = st.selectbox("Algorithm", list(ALGORITHMS))
    depth = st.slider("Search depth (plies)", 1, 4, 3)
    if st.button("New game"):
        st.session_state.board = chess.Board()
        st.session_state.selected = None
        st.session_state.stats = None
        st.session_state.notice = "New game started."
        st.rerun()

board = st.session_state.board
selected = st.session_state.selected
targets = {m.to_square for m in board.legal_moves if selected is not None and m.from_square == selected}

left, right = st.columns([1.4, 1])
with left:
    st.subheader("Chessboard")
    if board.is_checkmate():
        st.error(f"Checkmate — {board.result()}")
    elif board.is_game_over(claim_draw=True):
        st.info(f"Game over — {board.result(claim_draw=True)}")
    else:
        st.write("Your turn (White)" if board.turn else "Bot's turn (Black)")

    for rank in range(7, -1, -1):
        cols = st.columns(8, gap="small")
        for file_idx, col in enumerate(cols):
            sq = chess.square(file_idx, rank)
            piece = board.piece_at(sq)
            label = PIECES[(piece.color, piece.piece_type)] if piece else " "
            if sq == selected: label = f"🔸{label}"
            elif sq in targets: label = f"🟢{label}" if piece else "•"
            with col:
                if st.button(label, key=f"sq{sq}", use_container_width=True,
                             disabled=(board.turn != chess.WHITE or board.is_game_over(claim_draw=True))):
                    if selected is None:
                        if piece and piece.color == chess.WHITE:
                            st.session_state.selected = sq
                            st.session_state.notice = "Now click a highlighted destination."
                        else:
                            st.session_state.notice = "Select a White piece first."
                    elif sq == selected:
                        st.session_state.selected = None
                    else:
                        options = [m for m in board.legal_moves if m.from_square == selected and m.to_square == sq]
                        if options:
                            move = options[0]
                            if move.promotion:
                                move = chess.Move(selected, sq, promotion=chess.QUEEN)
                            board.push(move)
                            st.session_state.selected = None
                            st.session_state.notice = f"You played {move.uci()}."
                        elif piece and piece.color == chess.WHITE:
                            st.session_state.selected = sq
                            st.session_state.notice = "Piece selected. Click a legal destination."
                        else:
                            st.session_state.notice = "Illegal destination."
                    st.rerun()
    st.caption("Click a piece, then its destination. Pawn promotion defaults to queen.")

with right:
    st.subheader("Engine")
    st.write(f"**Algorithm:** {algorithm}")
    st.write(f"**Depth:** {depth}")
    st.metric("Evaluation (White perspective)", f"{evaluate(board)/100:+.2f}")
    st.caption("Positive favors White; negative favors Black.")
    st.info(st.session_state.notice)

    if board.turn == chess.BLACK and not board.is_game_over(claim_draw=True):
        if st.button("Make bot move", type="primary", use_container_width=True):
            with st.spinner("Searching..."):
                move, score, stats = ALGORITHMS[algorithm](board, depth)
            if move:
                board.push(move)
                st.session_state.notice = f"Bot played {move.uci()}."
                st.session_state.stats = stats
            st.rerun()

    if st.session_state.stats:
        stats = st.session_state.stats
        st.write(f"**Nodes searched:** {stats['nodes']:,}")
        st.write(f"**Cutoffs:** {stats['cutoffs']:,}")
        st.write(f"**Search time:** {stats['seconds']:.4f} seconds")
    if board.is_check(): st.warning("Check!")
    with st.expander("Move history"):
        st.write(" ".join(m.uci() for m in board.move_stack) or "No moves yet.")
