import os
import time
import random
import sys

# --- Visual Settings (ANSI Colors) ---
C_CYAN = '\033[96m'
C_GREEN = '\033[92m'
C_YELLOW = '\033[93m'
C_RED = '\033[91m'
C_MAGENTA = '\033[95m'
C_WHITE = '\033[97m'
C_RESET = '\033[0m'
C_BOLD = '\033[1m'
C_BG_GREEN = '\033[42m'
C_BG_RED = '\033[41m'
C_BG_BLUE = '\033[44m'

# --- Keno Paytable ---
# Format: { spots_picked: { hits: multiplier } }
PAYTABLE = {
    1: {1: 3},
    2: {1: 1, 2: 12},
    3: {2: 1, 3: 42},
    4: {2: 1, 3: 3, 4: 130},
    5: {3: 1, 4: 15, 5: 700},
    6: {3: 1, 4: 2, 5: 85, 6: 2000},
    7: {3: 1, 4: 2, 5: 20, 6: 400, 7: 5000},
    8: {4: 2, 5: 10, 6: 100, 7: 1500, 8: 10000},
    9: {4: 1, 5: 5, 6: 25, 7: 200, 8: 4000, 9: 25000},
    10: {5: 3, 6: 10, 7: 50, 8: 500, 9: 10000, 10: 100000}
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_multiplier(spots, hits):
    """Returns the multiplier based on how many numbers were picked and hit."""
    if spots in PAYTABLE and hits in PAYTABLE[spots]:
        return PAYTABLE[spots][hits]
    return 0

def print_header(balance, bet=0):
    print(f"{C_CYAN}================================================================================{C_RESET}")
    print(f"{C_MAGENTA}{C_BOLD}                                🎱 K E N O 🎱                                   {C_RESET}")
    print(f"{C_CYAN}================================================================================{C_RESET}")
    if bet > 0:
        print(f"  {C_GREEN}💰 Balance: ${balance:,}{C_RESET}  |  {C_RED}Bet: ${bet:,}{C_RESET}".center(88))
    else:
        print(f"  {C_GREEN}💰 Balance: ${balance:,}{C_RESET}".center(88))
    print(f"{C_CYAN}================================================================================\n{C_RESET}")

def render_board(player_picks, drawn_numbers):
    """Renders the 80-number Keno grid with color-coded statuses."""
    print(" " * 12 + f"{C_BOLD}--- KENO DRAW BOARD ---{C_RESET}")
    print()
    
    for row in range(8):
        row_str = "        "
        for col in range(10):
            num = (row * 10) + col + 1
            num_str = str(num).rjust(2, '0')
            
            if num in player_picks and num in drawn_numbers:
                # HIT! Green Background
                row_str += f"{C_BG_GREEN}{C_WHITE}{C_BOLD} {num_str} {C_RESET}  "
            elif num in player_picks:
                # Player Pick (Not drawn yet)
                row_str += f"{C_BG_BLUE}{C_WHITE}{C_BOLD} {num_str} {C_RESET}  "
            elif num in drawn_numbers:
                # Drawn by Casino (Not picked by player)
                row_str += f"{C_BG_RED}{C_WHITE}{C_BOLD} {num_str} {C_RESET}  "
            else:
                # Normal unselected number
                row_str += f"{C_CYAN} {num_str} {C_RESET}  "
        print(row_str)
        print() # Extra spacing for readability

def parse_user_picks(input_str):
    """Parses space-separated input, cleans it, and ensures validity."""
    raw_parts = input_str.replace(',', ' ').split()
    valid_picks = []
    
    for part in raw_parts:
        try:
            num = int(part)
            if 1 <= num <= 80:
                valid_picks.append(num)
        except ValueError:
            pass # Ignore words or letters
            
    # Remove duplicates by converting to a set, then back to a sorted list
    unique_picks = sorted(list(set(valid_picks)))
    return unique_picks

def animate_draw(player_picks):
    """Animates the random selection of 20 Keno numbers."""
    all_numbers = list(range(1, 81))
    drawn_numbers = []
    
    sys.stdout.write('\033[?25l') # Hide cursor
    sys.stdout.flush()
    
    # Pre-select the 20 numbers
    final_draw = random.sample(all_numbers, 20)
    
    try:
        for i in range(1, 21):
            drawn_numbers.append(final_draw[i-1])
            # Move cursor up 18 lines to redraw the board in place
            sys.stdout.write('\033[18A')
            sys.stdout.flush()
            render_board(player_picks, drawn_numbers)
            time.sleep(0.15)
    finally:
        sys.stdout.write('\033[?25h') # Show cursor again
        sys.stdout.flush()
        
    return drawn_numbers

def play(balance):
    """Main game loop for Keno."""
    last_bet = 0
    last_picks = []
    
    while True:
        clear_screen()
        print_header(balance)
        
        # --- Betting & Selection Menu ---
        if last_bet > 0 and last_picks:
            print(f"  [{C_YELLOW}ENTER{C_RESET}] Re-bet ${last_bet:,} with same numbers: {last_picks}")
            print(f"  [{C_YELLOW}N{C_RESET}]     Change Bet Amount or Numbers")
            print(f"  [{C_YELLOW}Q{C_RESET}]     Return to Lobby")
            choice = input("\n  Action: ").strip().lower()
            
            if choice == 'q':
                return balance
            elif choice == 'n':
                last_bet = 0
                last_picks = []
                continue
            elif choice == '':
                if last_bet > balance:
                    print(f"\n  {C_RED}Insufficient balance!{C_RESET}")
                    time.sleep(1.5)
                    last_bet = 0
                    continue
                bet = last_bet
                picks = last_picks
            else:
                continue
        else:
            print(f"  [{C_YELLOW}Q{C_RESET}] Return to Lobby")
            bet_choice = input(f"\n  Enter bet amount ({C_GREEN}Balance: ${balance:,}{C_RESET}): ").strip().lower()
            
            if bet_choice == 'q':
                return balance
            
            try:
                bet = int(bet_choice)
                if bet <= 0 or bet > balance:
                    print(f"  {C_RED}Invalid or insufficient bet.{C_RESET}")
                    time.sleep(1)
                    continue
            except ValueError:
                continue
                
            print(f"\n  {C_MAGENTA}How to pick:{C_RESET} Enter 1 to 10 numbers (between 1-80) separated by spaces.")
            print(f"  {C_CYAN}Example:{C_RESET} 1 2 45 45 63 48")
            pick_choice = input(f"  Your numbers: ")
            
            picks = parse_user_picks(pick_choice)
            
            if not (1 <= len(picks) <= 10):
                print(f"\n  {C_RED}Error: You must pick between 1 and 10 valid numbers.{C_RESET}")
                print(f"  You picked {len(picks)} valid numbers.")
                time.sleep(2)
                continue
                
            last_bet = bet
            last_picks = picks

        # --- Game Phase ---
        balance -= bet
        spots = len(picks)
        
        clear_screen()
        print_header(balance, bet)
        
        # Print empty board first to set the terminal height for the animation
        print("\n" * 18) 
        
        # Animate and retrieve the 20 drawn numbers
        drawn = animate_draw(picks)
        
        # Evaluate
        hits = sum(1 for p in picks if p in drawn)
        multiplier = get_multiplier(spots, hits)
        winnings = bet * multiplier
        balance += winnings
        net_profit = winnings - bet
        
        # --- Result Phase ---
        print(f"{C_CYAN}================================================================================{C_RESET}")
        print(f"  {C_BOLD}Spots Picked: {spots}  |  Total Hits: {hits}{C_RESET}")
        
        if winnings > 0:
            print(f"  {C_GREEN}{C_BOLD}🎉 {hits} HITS! Payout: {multiplier}x ! 🎉{C_RESET}")
            print(f"  {C_GREEN}Net Profit: +${net_profit:,}{C_RESET}")
        else:
            print(f"  {C_RED}💸 You lost your bet of ${bet:,}. 💸{C_RESET}")
            
        print(f"{C_CYAN}================================================================================{C_RESET}")
        
        input(f"\nPress [{C_YELLOW}ENTER{C_RESET}] to continue...")

if __name__ == "__main__":
    play(10000)
