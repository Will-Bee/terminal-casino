import os
import json
import importlib.util
import sys

# --- Configuration ---
BALANCE_FILE = 'balance.json'
DEFAULT_BALANCE = 10000

# --- Balance Management ---
def load_balance():
    """Loads the balance from a JSON file, or returns default if not found."""
    if os.path.exists(BALANCE_FILE):
        try:
            with open(BALANCE_FILE, 'r') as f:
                data = json.load(f)
                return data.get('balance', DEFAULT_BALANCE)
        except json.JSONDecodeError:
            return DEFAULT_BALANCE
    return DEFAULT_BALANCE

def save_balance(balance):
    """Saves the current balance to a JSON file."""
    with open(BALANCE_FILE, 'w') as f:
        json.dump({'balance': balance}, f)

# --- Addon Scanner ---
def get_available_games():
    """Scans the current directory for .py files to use as games."""
    games = []
    current_script = os.path.basename(__file__)
    
    for file in os.listdir('.'):
        if file.endswith('.py') and file != current_script:
            # Remove the .py extension for the menu name
            games.append(file[:-3]) 
            
    return sorted(games)

def run_game(game_module_name, current_balance):
    """Dynamically imports the game file and runs its play() function."""
    print(f"\n--- Loading {game_module_name.capitalize()} ---")
    
    file_path = f"{game_module_name}.py"
    
    try:
        # Dynamically load the python file as a module
        spec = importlib.util.spec_from_file_location(game_module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[game_module_name] = module
        spec.loader.exec_module(module)
        
        # Check if the required entry function exists
        if hasattr(module, 'play'):
            # The game must return the updated balance when it finishes
            new_balance = module.play(current_balance)
            return new_balance
        else:
            print(f"Error: '{file_path}' is missing the required 'play(balance)' function.")
            input("Press Enter to return to lobby...")
            return current_balance
            
    except Exception as e:
        print(f"Failed to load or run game '{game_module_name}': {e}")
        input("Press Enter to return to lobby...")
        return current_balance

# --- Main Menu UI ---
def main():
    balance = load_balance()
    
    while True:
        # Clear terminal screen (works on Windows/Mac/Linux)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("===================================")
        print("      🎰 TERMINAL CASINO 🎰      ")
        print("===================================")
        print(f"💰 Current Balance: ${balance:,}")
        print("===================================\n")
        
        games = get_available_games()
        
        print("Available Games:")
        if not games:
            print("  (No game addons found. Add .py files to this directory!)")
        else:
            for i, game in enumerate(games, 1):
                print(f"  [{i}] {game.replace('_', ' ').title()}")
                
        print("\nOptions:")
        print("  [R] Reset Balance to $10,000")
        print("  [Q] Quit Casino")
        
        choice = input("\nSelect an option: ").strip().lower()
        
        if choice == 'q':
            print("Thanks for playing! Exiting...")
            break
        elif choice == 'r':
            balance = DEFAULT_BALANCE
            save_balance(balance)
            print("\nBalance has been reset to $10,000!")
            input("Press Enter to continue...")
        elif choice.isdigit():
            game_index = int(choice) - 1
            if 0 <= game_index < len(games):
                selected_game = games[game_index]
                # Run the game and update the balance with the result
                balance = run_game(selected_game, balance)
                # Save immediately after returning to lobby
                save_balance(balance) 
            else:
                print("Invalid game number.")
                input("Press Enter to continue...")
        else:
            print("Invalid input.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
