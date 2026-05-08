import os
import time
import random
import sys

# --- TERMINAL COLORS & STYLES ---
C_DARK   = '\033[90m'
C_WHITE  = '\033[97m\033[1m'
C_CYAN   = '\033[96m\033[1m'
C_PURPLE = '\033[95m\033[1m'
C_YELLOW = '\033[93m\033[1m'
C_RED    = '\033[91m\033[1m'
C_GREEN  = '\033[92m\033[1m'
C_RESET  = '\033[0m'

# --- GAME CONFIG ---
FIXED_COST = 20000
HEX_CHARS = "0123456789ABCDEF"
PAYTABLE = {
    1: 100.0, # $2,000,000
    2: 25.0,  # $500,000
    3: 10.0,  # $200,000
    4: 5.0,   # $100,000
    5: 2.0,   # $40,000
    6: 1.0    # $20,000 (Money back)
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_hash():
    return [random.choice(HEX_CHARS) for _ in range(4)]

def evaluate_guess(guess, secret):
    """Mastermind validation logic to return colors for each character."""
    guess_list = list(guess)
    secret_list = list(secret)
    result_colors = [C_DARK] * 4
    
    # Pass 1: Find Exact Matches (Green)
    for i in range(4):
        if guess_list[i] == secret_list[i]:
            result_colors[i] = C_GREEN
            secret_list[i] = None # Burn it so it can't be matched again
            guess_list[i] = None
            
    # Pass 2: Find Partial Matches (Yellow)
    for i in range(4):
        if guess_list[i] is not None and guess_list[i] in secret_list:
            result_colors[i] = C_YELLOW
            secret_list[secret_list.index(guess_list[i])] = None # Burn it
            
    return result_colors

def draw_board(guesses, max_guesses=6):
    """Draws a perfectly symmetrical 63-character wide Hash-Cracker UI."""
    lines = []
    lines.append(f"{C_CYAN}╔{'═'*61}╗{C_RESET}")
    
    for i in range(max_guesses):
        if i < len(guesses):
            guess_str, colors = guesses[i]
            # Exact 61-char internal width formatting
            row_content = f"  ATTEMPT {i+1}/6  >  "
            for j in range(4):
                row_content += f"[{colors[j]} {guess_str[j]} {C_RESET}] "
            row_content += " " * 19 # Padding
        else:
            row_content = f"{C_DARK}  ATTEMPT {i+1}/6  >  [ ? ] [ ? ] [ ? ] [ ? ]                    {C_RESET}"
            
        lines.append(f"{C_CYAN}║{C_RESET}{row_content}{C_CYAN}║{C_RESET}")
        
    lines.append(f"{C_CYAN}╚{'═'*61}╝{C_RESET}")
    return "\n".join(lines)

def play(balance):
    while True:
        clear()
        print(f"{C_CYAN}==============================================================={C_RESET}")
        print(f"{C_WHITE}                  🔐 HASH-CRACKER UPLINK 🔐                  {C_RESET}")
        print(f"{C_CYAN}==============================================================={C_RESET}")
        print(f"💰 Balance: {C_GREEN}${balance:,}{C_RESET}")
        print(f"{C_DARK}---------------------------------------------------------------{C_RESET}")
        print(f"  RULES: Guess the 4-character Hex code (0-9, A-F).")
        print(f"  [{C_GREEN} 0 {C_RESET}] = Match   |  [{C_YELLOW} 0 {C_RESET}] = Wrong Spot   |  [{C_DARK} 0 {C_RESET}] = Invalid")
        print(f"{C_DARK}---------------------------------------------------------------{C_RESET}")
        print(f"  {C_RED}WARNING: TIER-1 SECURITY. FIXED COST: ${FIXED_COST:,}{C_RESET}")
        print(f"{C_DARK}---------------------------------------------------------------{C_RESET}")
        print("  PAYTABLE:")
        print(f"  Crack in 1: {C_PURPLE}100x{C_RESET}  |  Crack in 4: {C_GREEN} 5x{C_RESET}")
        print(f"  Crack in 2: {C_RED} 25x{C_RESET}  |  Crack in 5: {C_GREEN} 2x{C_RESET}")
        print(f"  Crack in 3: {C_YELLOW} 10x{C_RESET}  |  Crack in 6: {C_WHITE} 1x{C_RESET} (Money Back)")
        print(f"{C_DARK}---------------------------------------------------------------{C_RESET}")
        
        while True:
            print(f"  [ENTER] Initiate Breach (-${FIXED_COST:,})")
            print(f"  [Q] Disconnect")
            choice = input("\nCommand: ").strip().lower()
            
            if choice == 'q': 
                return balance
            elif choice == '':
                if balance >= FIXED_COST: 
                    break
                else: 
                    print(f"{C_RED}Insufficient funds. Grind other games to reach ${FIXED_COST:,}.{C_RESET}")
                    time.sleep(2)
                    return balance # Kick them back to lobby if too broke
                    
        # --- GAME LOOP ---
        balance -= FIXED_COST
        secret_hash = generate_hash()
        guesses = []
        cracked = False
        attempts_used = 0
        
        # Connection Animation
        clear()
        print(f"{C_DARK}Establishing secure connection to mainframe...{C_RESET}")
        time.sleep(0.5)
        print(f"{C_DARK}Bypassing firewall...{C_RESET}")
        time.sleep(0.5)
        
        while attempts_used < 6:
            clear()
            print(f"{C_DARK}==============================================================={C_RESET}")
            print(f"{C_WHITE}                    📡 UPLINK ESTABLISHED 📡                 {C_RESET}")
            print(f"{C_DARK}==============================================================={C_RESET}")
            print(draw_board(guesses))
            
            while True:
                player_input = input(f"\n{C_CYAN}Enter 4-character Hex (0-9, A-F): {C_RESET}").strip().upper()
                
                if len(player_input) != 4:
                    print(f"{C_RED}Error: Input must be exactly 4 characters.{C_RESET}")
                    continue
                if any(c not in HEX_CHARS for c in player_input):
                    print(f"{C_RED}Error: Invalid Hex character. Use 0-9 and A-F only.{C_RESET}")
                    continue
                break
                
            colors = evaluate_guess(player_input, secret_hash)
            guesses.append((player_input, colors))
            attempts_used += 1
            
            if list(player_input) == secret_hash:
                cracked = True
                break

        # --- RESULTS EVALUATION ---
        clear()
        print(f"{C_DARK}==============================================================={C_RESET}")
        print(f"{C_WHITE}                    📡 UPLINK TERMINATED 📡                  {C_RESET}")
        print(f"{C_DARK}==============================================================={C_RESET}")
        print(draw_board(guesses))
        
        multiplier = PAYTABLE[attempts_used] if cracked else 0.0
        winnings = int(FIXED_COST * multiplier)
        net_profit = winnings - FIXED_COST
        balance += winnings
        
        secret_str = "".join(secret_hash)
        
        if cracked:
            if attempts_used == 1: theme_color, title = C_PURPLE, "🔥 LEGENDARY CRACK (1ST TRY) 🔥"
            elif attempts_used <= 3: theme_color, title = C_GREEN, "🎉 MAINFRAME BREACHED 🎉"
            elif attempts_used <= 5: theme_color, title = C_YELLOW, "🔓 ACCESS GRANTED 🔓"
            else: theme_color, title = C_WHITE, "⏳ BARELY MADE IT ⏳"
        else:
            theme_color, title = C_RED, "🚨 ACCESS DENIED - LOCKOUT 🚨"

        print(f"\n{theme_color}==============================================================={C_RESET}")
        print(f"{theme_color}{title.center(63)}{C_RESET}")
        print(f"{theme_color}==============================================================={C_RESET}\n")
        
        # --- RECEIPT ---
        print(f"  {C_CYAN}--- HACK RECEIPT ---{C_RESET}")
        print(f"  {C_WHITE}Target Hash{C_RESET}  : {theme_color}{secret_str}{C_RESET}")
        print(f"  {C_WHITE}Attempts{C_RESET}     : {attempts_used}/6")
        print(f"  {C_WHITE}Buy-in Cost{C_RESET}  : {C_DARK}${FIXED_COST:,}{C_RESET}")
        print(f"  {C_WHITE}Total Payout{C_RESET} : {theme_color}${winnings:,}{C_RESET} ({theme_color}{multiplier}x{C_RESET})")
        
        if net_profit > 0:
            print(f"  {C_WHITE}Net Profit{C_RESET}   : {C_GREEN}+${net_profit:,}{C_RESET}")
        elif net_profit == 0:
            print(f"  {C_WHITE}Net Profit{C_RESET}   : {C_WHITE}$0 (Money Back){C_RESET}")
        else:
            print(f"  {C_WHITE}Net Loss{C_RESET}     : {C_RED}-${abs(net_profit):,}{C_RESET}")
            
        print(f"\n{C_WHITE}New Balance:{C_RESET} {C_GREEN}${balance:,}{C_RESET}")
        
        while True:
            post_action = input(f"\n{C_DARK}Press [ENTER] to breach another node, or [Q] for menu: {C_RESET}").strip().lower()
            if post_action == '': break
            elif post_action == 'q': return balance

if __name__ == "__main__":
    # Test the script with $50k so you can afford 2 hacks
    play(50000)
