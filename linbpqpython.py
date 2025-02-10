import chess
import os
import time

# Base directory for game storage
GAME_DIR = "/home/pi/bpq_chess"
os.makedirs(GAME_DIR, exist_ok=True)

# BPQMail message storage directory (adjust as needed)
BPQ_MAIL_DIR = "/var/lib/linbpq/messages"

# Mapping chess pieces to their correct text representation
PIECE_MAP = {
    "K": "K",  # King
    "Q": "Q",  # Queen
    "R": "R",  # Rook
    "B": "B",  # Bishop
    "N": "N",  # Knight
    "P": "P"   # Pawn
}

def get_game_files(game_id):
    """ Return paths to game files """
    return (
        os.path.join(GAME_DIR, f"{game_id}_game.txt"),
        os.path.join(GAME_DIR, f"{game_id}_turn.txt"),
        os.path.join(GAME_DIR, f"{game_id}_players.txt"),
    )

def load_board(game_file):
    """ Load board state from a saved game or create a new one """
    if os.path.exists(game_file):
        with open(game_file, "r") as f:
            return chess.Board(f.read().strip())
    return chess.Board()

def save_board(board, game_file):
    """ Save board state """
    with open(game_file, "w") as f:
        f.write(board.fen())

def get_turn(turn_file):
    """ Get the current turn (white or black) """
    if os.path.exists(turn_file):
        with open(turn_file, "r") as f:
            return f.read().strip()
    return "white"

def save_turn(turn, turn_file):
    """ Save turn information """
    with open(turn_file, "w") as f:
        f.write(turn)

def get_players(players_file):
    """ Get list of players in a game """
    if os.path.exists(players_file):
        with open(players_file, "r") as f:
            return f.read().strip().split("\n")
    return []

def save_players(players_file, players):
    """ Save player information """
    with open(players_file, "w") as f:
        f.write("\n".join(players))

def get_latest_move():
    """ Read BPQMail for the latest chess move """
    msg_file = os.path.join(BPQ_MAIL_DIR, "chess_moves.txt")  # Adjust for setup
    if not os.path.exists(msg_file):
        return None, None, None

    with open(msg_file, "r") as f:
        lines = f.readlines()

    for line in reversed(lines):  # Get the latest move
        parts = line.strip().split()
        if len(parts) >= 3 and parts[0] == "CHESS":
            return parts[1], parts[2], parts[3]  # Game ID, Move, Sender

    return None, None, None

def send_bpqmail(recipient, subject, message):
    """ Send a message via BPQMail """
    msg_path = os.path.join(BPQ_MAIL_DIR, "outgoing_msgs.txt")  # Adjust path
    with open(msg_path, "a") as f:
        f.write(f"To: {recipient}\nSubject: {subject}\n\n{message}\n\n")

def get_text_board(board):
    """ Return a simplified board display for BBS with colored initials """

    # Board header
    board_str = "\n  A   B   C   D   E   F   G   H\n"

    for row in range(8):
        board_str += f"{8 - row} "  # Row numbers on the left

        for col in range(8):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)

            if piece:
                color_prefix = "W" if piece.color == chess.WHITE else "B"
                piece_symbol = PIECE_MAP.get(piece.symbol().upper(), "?")
                board_str += f"{color_prefix}{piece_symbol}  "  # Example: WN (White Knight), BK (Black King)
            else:
                board_str += ".   "  # Empty square

        board_str += "\n"

    # Board legend
    board_str += "\n📌 **Chess Piece Legend**:\n"
    board_str += "WK = White King, WQ = White Queen, WR = White Rook, WB = White Bishop, WN = White Knight, WP = White Pawn\n"
    board_str += "BK = Black King, BQ = Black Queen, BR = Black Rook, BB = Black Bishop, BN = Black Knight, BP = Black Pawn\n"
    board_str += "\n🎲 **Enter your move in UCI format** (e.g., `e2e4`).\n"

    return board_str

def process_game():
    """ Main game processing loop for LinBPQ """
    game_id, move, sender = get_latest_move()
    if not game_id or not move:
        return

    game_file, turn_file, players_file = get_game_files(game_id)
    board = load_board(game_file)
    turn = get_turn(turn_file)
    players = get_players(players_file)

    if sender not in players:
        send_bpqmail(sender, "CHESS ERROR", "You are not a player in this game.")
        return

    if (turn == "white" and players[0] != sender) or (turn == "black" and players[1] != sender):
        send_bpqmail(sender, "CHESS ERROR", "It's not your turn!")
        return

    try:
        chess_move = chess.Move.from_uci(move)
        if chess_move in board.legal_moves:
            board.push(chess_move)
            save_board(board, game_file)
            new_turn = "black" if turn == "white" else "white"
            save_turn(new_turn, turn_file)

            # Notify both players with updated board
            board_display = get_text_board(board)
            send_bpqmail(players[0], f"CHESS UPDATE {game_id}", board_display)
            send_bpqmail(players[1], f"CHESS UPDATE {game_id}", board_display)

        else:
            send_bpqmail(sender, "CHESS ERROR", "Invalid move. Try again.")

    except ValueError:
        send_bpqmail(sender, "CHESS ERROR", "Invalid move format. Use UCI notation (e.g., e2e4).")

if __name__ == "__main__":
    process_game()
