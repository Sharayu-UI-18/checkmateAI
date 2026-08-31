import chess
from minimax import find_best_move


def announce_move(board, move):
    """Announce important events and then play the move."""

    # Check for capture BEFORE making the move
    if board.is_capture(move):

        captured_piece = board.piece_at(move.to_square)

        # Special case: en passant
        if board.is_en_passant(move):
            captured_piece = chess.Piece(
                chess.PAWN,
                not board.turn
            )

        if captured_piece:
            captured_name = chess.piece_name(
                captured_piece.piece_type
            )

            print(f"⚔️ Captured: {captured_name}")

    # Actually make the move
    board.push(move)

    # Checkmate
    if board.is_checkmate():

        winner = "Black" if board.turn == chess.WHITE else "White"

        print(f"\n🏆 CHECKMATE! {winner} wins!")

    # Stalemate
    elif board.is_stalemate():

        print("\n🤝 STALEMATE! The game is a draw.")

    # Check
    elif board.is_check():

        player = "White" if board.turn == chess.WHITE else "Black"

        print(f"\n⚠️ CHECK! {player}'s king is in check.")


board = chess.Board()


while not board.is_game_over():

    print("\nCurrent board:")
    print(board)

    # -------------------------
    # HUMAN = WHITE
    # -------------------------
    if board.turn == chess.WHITE:

        user_input = input(
            "\nYour move (example e2e4): "
        )

        try:

            move = chess.Move.from_uci(user_input)

            if move in board.legal_moves:

                announce_move(board, move)

            else:

                print("❌ Illegal move.")
                continue

        except ValueError:

            print("❌ Invalid move format.")
            continue

    # -------------------------
    # BOT = BLACK
    # -------------------------
    else:

        

        move = find_best_move(board, depth=3)

        if move is None:
            break

        print("🤖 Bot plays:", move)

        announce_move(board, move)


print("\n====================")
print("♟️ GAME OVER!")
print("====================")

print("\nFinal Board:")
print(board)

print("\nResult:", board.result())