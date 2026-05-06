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

# --- Plinko Configuration ---
ROWS = 10
# Calculated to have a ~93% RTP (Return to Player) across 1024 possible paths
MULTIPLIERS = [29, 7, 2.5, 1.1, 0.5, 0.2, 0.5, 1.1, 2.5, 7, 29]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_multiplier_color(m):
    """Returns the appropriate color code based on the multiplier value."""
    if m >= 10: return C_MAGENTA
    if m >= 2:  return C_GREEN
    if m >= 1:  return C_YELLOW
    return C_RED

def render_board(step_index, path, highlight_bucket=None):
    """
    Renders the Plinko board precisely centered, showing the ball, 
    the trail it left behind, and the bottom multiplier buckets.
    """
    ball_r, ball_c = path[step_index]
    lines = []
    
    # 1. Draw the Pegs, Trail, and Ball
    for r in range(ROWS + 1):
        raw_row = []
        color_row = []
        for c in range(r + 1):
            if r == ball_r and c == ball_c:
                # The Ball
                raw_row.append("O")
                color_row.append(f"{C_RED}{C_BOLD}O{C_RESET}")
            elif (r, c) in path[:step_index]:
                # The Trail left behind
                raw_row.append("o")
                color_row.append(f"{C_YELLOW}o{C_RESET}")
            else:
                # Standard Peg
                raw_row.append(".")
                color_row.append(f"{C_CYAN}.{C_RESET}")
        
        # Space out the pegs
        raw_str = "     ".join(raw_row)
        
        # Calculate padding for strict 80-character centering
        pad_len = (80 - len(raw_str)) // 2
        
        # Apply padding to the colored version so ANSI codes don't break the centering
        colored_str = (" " * pad_len) + "     ".join(color_row)
        lines.append(colored_str)

    # 2. Draw the Buckets
    bucket_strs = []
    for i, m in enumerate(MULTIPLIERS):
        m_str = f"{m}x"
        # Pad strings to exactly 5 characters wide (e.g. " 29x ", " 0.2x")
        if len(m_str) < 5:
            m_str = m_str.center(5)
            
        color = get_multiplier_color(m)
        
        # Highlight the winning bucket if the game is over
        if highlight_bucket == i:
            bucket_strs.append(f"{C_BG_GREEN}{C_WHITE}{C_BOLD}{m_str}{C_RESET}")
        else:
            bucket_strs.append(f"{color}{C_BOLD}{m_str}{C_RESET}")

    # Join buckets with 1 space. 
    # Math magic: This aligns the 5-char buckets perfectly beneath the 1-char pegs!
    colored_buckets = " ".join(bucket_strs)
    raw_buckets_len = len(" ".join(["12345"] * len(MULTIPLIERS))) 
    
    bucket_pad_len = (80 - raw_buckets_len) // 2
    final_bucket_line = (" " * bucket_pad_len) + colored_buckets
    lines.append("\n" + final_bucket_line)

    # Print the board
    for line in lines:
        print(line)

def print_header(balance, bet=0):
    print(f"{C_CYAN}================================================================================{C_RESET}")
    print(f"{C_YELLOW}{C_BOLD}                                🔴 P L I N K O 🔴                               {C_RESET}")
    print(f"{C_CYAN}================================================================================{C_RESET}")
    if bet > 0:
        print(f"  {C_GREEN}💰 Balance: ${balance:,}{C_RESET}  |  {C_RED}Bet: ${bet:,}{C_RESET}".center(88))
    else:
        print(f"  {C_GREEN}💰 Balance: ${balance:,}{C_RESET}".center(88))
    print(f"{C_CYAN}================================================================================\n{C_RESET}")

def animate_drop(balance, bet):
    """Calculates the path and animates the frame-by-frame drop."""
    # Pre-calculate the path
    path = [(0, 0)]
    curr_c = 0
    for r in range(ROWS):
        # 50/50 chance to go left (+0 to column) or right (+1 to column)
        curr_c += random.choice([0, 1])
        path.append((r + 1, curr_c))

    sys.stdout.write('\033[?25l') # Hide cursor
    sys.stdout.flush()

    try:
        # Animate frame by frame
        for i in range(len(path)):
            clear_screen()
            print_header(balance, bet)
            render_board(i, path)
            time.sleep(0.12) # Delay between frames
            
        time.sleep(0.3) # Suspense pause at the bottom
        
    finally:
        sys.stdout.write('\033[?25h') # Show cursor again
        sys.stdout.flush()

    return path[-1][1], path

def play(balance):
    """Main game loop."""
    last_bet = 0
    
    while True:
        clear_screen()
        print_header(balance)
        
        # --- Betting Menu ---
        if last_bet > 0:
            print(f"  [{C_YELLOW}ENTER{C_RESET}] Drop ball for ${last_bet:,}")
            print(f"  [{C_YELLOW}N{C_RESET}]     Change Bet Amount")
            print(f"  [{C_YELLOW}Q{C_RESET}]     Return to Lobby")
            choice = input("\n  Action: ").strip().lower()
            
            if choice == 'q':
                return balance
            elif choice == 'n':
                last_bet = 0 
                continue 
            elif choice == '':
                if last_bet > balance:
                    print(f"\n  {C_RED}Insufficient balance for your last bet!{C_RESET}")
                    time.sleep(1.5)
                    last_bet = 0
                    continue
                bet = last_bet
            else:
                continue
        else:
            print(f"  [{C_YELLOW}Q{C_RESET}] Return to Lobby")
            choice = input(f"\n  Enter bet amount ({C_GREEN}Balance: ${balance:,}{C_RESET}): ").strip().lower()
            
            if choice == 'q':
                return balance
            
            try:
                bet = int(choice)
                if bet <= 0:
                    print(f"  {C_RED}Bet must be greater than $0.{C_RESET}")
                    time.sleep(1)
                    continue
                elif bet > balance:
                    print(f"  {C_RED}Insufficient balance!{C_RESET}")
                    time.sleep(1)
                    continue
                else:
                    last_bet = bet
            except ValueError:
                continue

        # --- Game Phase ---
        balance -= bet
        
        # Run animation
        final_col, full_path = animate_drop(balance, bet)
        
        # Calculate Winnings
        multiplier = MULTIPLIERS[final_col]
        winnings = int(bet * multiplier)
        balance += winnings
        net_profit = winnings - bet
        
        # --- Result Phase ---
        clear_screen()
        print_header(balance, bet)
        
        # Re-render board with the winning bucket highlighted
        render_board(len(full_path) - 1, full_path, highlight_bucket=final_col)
        
        print(f"\n{C_CYAN}================================================================================{C_RESET}")
        
        color = get_multiplier_color(multiplier)
        print(f"  Landed on {color}{C_BOLD}{multiplier}x{C_RESET} multiplier!")
        
        if net_profit > 0:
            print(f"  {C_GREEN}{C_BOLD}🎉 YOU WON ${winnings:,} ! 🎉{C_RESET}")
            print(f"  Net Profit: {C_GREEN}+${net_profit:,}{C_RESET}")
        elif net_profit < 0:
            print(f"  {C_RED}💸 You won ${winnings:,} ... but lost -${abs(net_profit):,} overall. 💸{C_RESET}")
        else:
            print(f"  {C_YELLOW}⚖️ Broke even. Returned ${winnings:,}. ⚖️{C_RESET}")
            
        print(f"{C_CYAN}================================================================================{C_RESET}")
        
        input(f"\nPress [{C_YELLOW}ENTER{C_RESET}] to continue...")

if __name__ == "__main__":
    play(10000)
