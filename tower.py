import os
import time
import random

# --- Tower Configuration ---
ROWS = 8
COLUMNS = 3
# Exponential multipliers for a 3-block / 1-trap setup
MULTIPLIERS = [1.42, 2.13, 3.20, 4.80, 7.20, 10.80, 16.20, 24.30]

# ANSI Colors for that "Neon" vibe
C_GREEN = '\033[92m\033[1m'
C_RED = '\033[91m\033[1m'
C_YELLOW = '\033[93m\033[1m'
C_DARK = '\033[90m'
C_RESET = '\033[0m'
C_WHITE = '\033[97m\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_tower():
    """Generates the truth layer of the tower (randomly placing 1 bomb per row)."""
    return [random.randint(0, COLUMNS - 1) for _ in range(ROWS)]

def render_tower(truth, player_path, current_row, state="playing"):
    """Renders the entire tower, lighting up blocks based on the current state."""
    clear_screen()
    print("===================================================")
    print("                 🗼 NEON TOWER 🗼                ")
    print("===================================================\n")
    
    # Draw from top (highest row) to bottom (lowest row)
    for r in range(ROWS - 1, -1, -1):
        row_str = ""
        
        # Indicator for the active row
        if r == current_row and state == "playing":
            prefix = f" {C_YELLOW}>{C_RESET} [{MULTIPLIERS[r]:5.2f}x] "
            suffix = f" {C_YELLOW}<{C_RESET}"
        else:
            prefix = f"   [{MULTIPLIERS[r]:5.2f}x] "
            suffix = "  "
            
        for c in range(COLUMNS):
            # 1. The row has already been played by the user
            if r < len(player_path):
                if c == player_path[r]:
                    if c == truth[r]:
                        row_str += f" {C_RED}[ 💥]{C_RESET} " # Hit a bomb!
                    else:
                        row_str += f" {C_GREEN}[ ✔ ]{C_RESET} " # Safe step!
                else:
                    # Reveal what the unpicked blocks were if the game is over
                    if state in ["game_over", "cashed_out"]:
                        if c == truth[r]:
                            row_str += f" {C_RED}[ 💥]{C_RESET} "
                        else:
                            row_str += f" {C_DARK}[ ✔ ]{C_RESET} "
                    else:
                        row_str += f" {C_DARK}[ ? ]{C_RESET} " # Still playing, keep unpicked blocks hidden
            
            # 2. This is the row the user is currently on
            elif r == current_row and state == "playing":
                row_str += f" {C_WHITE}[ ? ]{C_RESET} "
                
            # 3. This is a future row (above the player)
            else:
                if state in ["game_over", "cashed_out"]:
                    # Reveal the whole tower if the game ends
                    if c == truth[r]:
                        row_str += f" {C_RED}[ 💥]{C_RESET} "
                    else:
                        row_str += f" {C_DARK}[ ✔ ]{C_RESET} "
                else:
                    row_str += f" {C_DARK}[ ? ]{C_RESET} "

        print(f"     {prefix}{row_str}{suffix}")
        
    print("\n===================================================")

def play(balance):
    """Main entry point for Neon Tower."""
    last_bet = 0
    show_menu = True
    
    while True:
        # --- Betting Menu ---
        if show_menu:
            clear_screen()
            print("===================================================")
            print("                 🗼 NEON TOWER 🗼                ")
            print("===================================================")
            print(f"💰 Balance: ${balance:,}")
            print("===================================================")
            print("  Rules: 8 Floors. 3 Blocks per floor.")
            print("  2 blocks are safe (✔). 1 block is a trap (💥).")
            print("  Climb the tower to increase your multiplier!")
            print("===================================================")
            
            while True:
                if last_bet > 0:
                    print(f"  [ENTER] Bet ${last_bet:,} and climb")
                    print("  [N] Change Bet Amount")
                    print("  [Q] Return to Lobby")
                    choice = input("\nAction: ").strip().lower()
                    
                    if choice == 'q': return balance
                    elif choice == 'n':
                        last_bet = 0
                        continue
                    elif choice == '':
                        if last_bet > balance:
                            print("Insufficient balance!")
                            last_bet = 0
                            continue
                        bet = last_bet
                        break
                    else: print("Invalid input.")
                else:
                    print("  [Q] Return to Lobby")
                    choice = input(f"\nEnter bet amount (Balance: ${balance:,}): ").strip().lower()
                    if choice == 'q': return balance
                    try:
                        bet = int(choice)
                        if bet <= 0: print("Bet must be greater than $0.")
                        elif bet > balance: print("Insufficient balance!")
                        else:
                            last_bet = bet
                            break
                    except ValueError: print("Please enter a valid number or 'Q'.")
        else:
            bet = last_bet
            if bet > balance:
                print("\nInsufficient balance to repeat last bet! Returning to menu...")
                time.sleep(1.5)
                show_menu = True
                continue

        # --- Game Setup Phase ---
        balance -= bet
        truth = generate_tower()
        player_path = []
        current_row = 0
        state = "playing"

        # --- The Climbing Loop ---
        while state == "playing":
            render_tower(truth, player_path, current_row, state)
            
            print(f"💰 Current Bet: ${bet:,}")
            if current_row > 0:
                current_winnings = int(bet * MULTIPLIERS[current_row - 1])
                print(f"💵 Cashout Value: {C_GREEN}${current_winnings:,}{C_RESET}")
            else:
                print("💵 Cashout Value: $0")
                
            print("\nOptions:")
            print("  [1] Pick Left")
            print("  [2] Pick Middle")
            print("  [3] Pick Right")
            if current_row > 0:
                print("  [C] Cashout & Take Profit")
                
            choice = input("\nMake your move: ").strip().lower()
            
            if choice == 'c' and current_row > 0:
                state = "cashed_out"
            elif choice in ['1', '2', '3']:
                pick_idx = int(choice) - 1
                player_path.append(pick_idx)
                
                # Tiny pause to build suspense after picking
                time.sleep(0.3)
                
                if pick_idx == truth[current_row]:
                    state = "game_over" # Hit a bomb
                else:
                    current_row += 1 # Safe! Move up.
                    if current_row == ROWS:
                        state = "cashed_out" # Cleared the tower! Auto-cashout.
            else:
                print("Invalid choice.")
                time.sleep(0.5)

        # --- Results Phase ---
        render_tower(truth, player_path, current_row, state) # Final render to reveal the board
        
        if state == "cashed_out":
            final_multiplier = MULTIPLIERS[current_row - 1]
            winnings = int(bet * final_multiplier)
            net_result = winnings - bet
            balance += winnings
            
            print(f"\n               🎉 CASHED OUT! 🎉")
            if current_row == ROWS:
                print(f"          👑 YOU CLEARED THE TOWER! 👑")
            print(f"               Locked in at {final_multiplier:.2f}x\n")
            
            print("  --- BET RECEIPT ---")
            print(f"  Floors Cleared : {current_row}/{ROWS}")
            print(f"  Bet Amount     : ${bet:,}")
            print(f"  Total Payout   : ${winnings:,}")
            print(f"  Net Profit     : {C_GREEN}+${net_result:,}{C_RESET}")
            print("  -------------------")
            
        elif state == "game_over":
            net_result = -bet
            print(f"\n                   💸 YOU LOST 💸")
            print(f"               You hit a trap on floor {current_row + 1}!\n")
            
            print("  --- BET RECEIPT ---")
            print(f"  Bet Amount     : ${bet:,}")
            print(f"  Total Payout   : $0")
            print(f"  Net Loss       : {C_RED}-${abs(net_result):,}{C_RESET}")
            print("  -------------------")
            
        print(f"\nNew Balance: ${balance:,}")
        
        # --- Post-Game Prompt ---
        while True:
            post_action = input("\nPress [ENTER] to play again, or [Q] to return to menu: ").strip().lower()
            if post_action == '':
                show_menu = False
                break
            elif post_action == 'q':
                show_menu = True
                break
            else:
                print("Invalid input. Press Enter or Q.")

if __name__ == "__main__":
    play(10000)
