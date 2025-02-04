import os

# Base directory for saved games
GAME_DIR = "/Users/admin/Documents/javafun"

# Ensure the directory exists
os.makedirs(GAME_DIR, exist_ok=True)

# List available games with only one player assigned
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

# Main function to display open games
def main():
    available_games = list_available_games()
    if available_games:
        print("Open games waiting for a second player:")
        for game in available_games:
            print(f"- {game}")
    else:
        print("No open games available.")

if __name__ == "__main__":
    main()
