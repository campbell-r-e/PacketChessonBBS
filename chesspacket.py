import chess
import os
import random

# Base directory for saved games
GAME_DIR = "/Users/admin/Documents/javafun"

# Ensure the directory exists
os.makedirs(GAME_DIR, exist_ok=True)

# Improved piece mapping with correct initials and order
PIECE_MAP = {
    "K": "K",  # King
    "Q": "Q",  # Queen
    "R": "R",  # Rook
    "B": "B",  # Bishop
    "N": "N",  # Knight
    "P": "P"   # Pawn
}

# Function to get file paths based on game ID
def get_game_files(game_id):
    game_file = os.path.join(GAME_DIR, f"{game_id}_game.txt")
    turn_file = os.path.join(GAME_DIR, f"{game_id}_turn.txt")
    players_file = os.path.join(GAME_DIR, f"{game_id}_players.txt")
    return game_file, turn_file, players_file

# List available games with an open player slot
def list_available_games():
    available_games = []
    for filename in os.listdir(GAME_DIR):
        if filename.endswith("_players.txt"):
            game_id = filename.replace("_players.txt", "")
            players_file = os.path.join(GAME_DIR, filename)
            with open(players_file, "r") as f:
                players = f.read().strip().split("\n")
            if len(players) == 1:
                available_games.append(game_id)
    return available_games

# Load board state from a saved game
def load_board(game_file):
    if os.path.exists(game_file):
        with open(game_file, "r") as f:
            board_fen = f.read().strip()
            return chess.Board(board_fen)
    return chess.Board()

# Save board state
def save_board(board, game_file):
    with open(game_file, "w") as f:
        f.write(board.fen())

# Get the current turn from the saved game
def get_turn(turn_file):
    if os.path.exists(turn_file):
        with open(turn_file, "r") as f:
            return f.read().strip()
    return "white"  # Default to White moving first

# Save turn information
def save_turn(turn, turn_file):
    with open(turn_file, "w") as f:
        f.write(turn)

# Get or assign players to a game
def get_or_assign_players(players_file, call_sign):
    if os.path.exists(players_file):
        with open(players_file, "r") as f:
            players = f.read().strip().split("\n")
        if call_sign not in players and len(players) < 2:
            players.append(call_sign)
            with open(players_file, "w") as f:
                f.write("\n".join(players))
        return players
    else:
        with open(players_file, "w") as f:
            f.write(call_sign)
        return [call_sign]

# Generate a text-based chessboard with correct order and initials
def get_text_board(board):
    board_layout = [["." for _ in range(8)] for _ in range(8)]
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = divmod(square, 8)
            color_prefix = "B" if piece.color == chess.BLACK else "W"
            piece_letter = PIECE_MAP.get(piece.symbol().upper(), "?")
            board_layout[7 - row][col] = f"{color_prefix}{piece_letter}"
    
    board_str = "\n🔹 **How to Submit a Move:**\n"
    board_str += "1️⃣ Moves must be entered in **UCI notation**.\n"
    board_str += "   - Example: Move a pawn from e2 to e4 → Type: **e2e4**\n"
    board_str += "   - Example: Move a knight from g1 to f3 → Type: **g1f3**\n"
    board_str += "\n🏰 **Castling Instructions:**\n"
    board_str += "   - Kingside (O-O): White → **e1g1**, Black → **e8g8**\n"
    board_str += "   - Queenside (O-O-O): White → **e1c1**, Black → **e8c8**\n"
    board_str += "\n2️⃣ To resign, type: **resign**\n"
    board_str += "3️⃣ To quit without resigning, type: **quit**\n\n"
    board_str += "  A  B  C  D  E  F  G  H\n"
    for row_num in range(8):
        board_str += f"{8 - row_num} " + " ".join(board_layout[row_num]) + "\n"
    return board_str

# Main game logic
def main():
    print("Welcome to BBS Chess!")
    call_sign = input("Enter your ham radio call sign (e.g., KD9GEK): ").strip().upper()
    available_games = list_available_games()
    if available_games:
        print("Available games with open slots:", ", ".join(available_games))
    game_id = input("Enter game ID or create a new one: ").strip()
    game_file, turn_file, players_file = get_game_files(game_id)

    players = get_or_assign_players(players_file, call_sign)
    if len(players) > 2:
        print("❌ This game already has two players. Please join another game.")
        return

    assigned_color = "white" if players[0] == call_sign else "black"

    if os.path.exists(game_file):
        board = load_board(game_file)
    else:
        board = chess.Board()
        save_turn("white", turn_file)

    save_board(board, game_file)
    current_turn = get_turn(turn_file)
    if assigned_color != current_turn:
        print(f"It is not your turn yet! Please wait for {current_turn.capitalize()}.")
        return

    while True:
        print(get_text_board(board))
        move = input(f"{assigned_color.capitalize()}'s move: ").strip().lower()

        if move == "quit":
            print("Game exited. Your progress is saved.")
            return
        if move == "resign":
            print(f"{assigned_color.capitalize()} has resigned. The game is over.")
            os.remove(game_file)
            os.remove(turn_file)
            os.remove(players_file)
            return

        try:
            chess_move = chess.Move.from_uci(move)
            if chess_move in board.legal_moves:
                board.push(chess_move)
                save_board(board, game_file)
                save_turn("black" if current_turn == "white" else "white", turn_file)
                print(f"Move accepted: {move}. It is now {get_turn(turn_file).capitalize()}'s turn.")
                return
            else:
                print("❌ Invalid move. Try again.")
        except ValueError:
            print("❌ Invalid move format. Use UCI notation (e.g., e2e4). Try again.")

if __name__ == "__main__":
    main()
