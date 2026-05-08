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
C_MYTHIC = '\033[38;5;206m\033[1m' # Bright Pink/Magenta (No background)
C_GREEN  = '\033[92m\033[1m'
C_RESET  = '\033[0m'

ITEMS = [
    {'name': 'SCRAP', 'icon': '✖', 'color': C_DARK,   'mult': 0.0,   'weight': 6500},
    {'name': 'COMPS', 'icon': '⚙', 'color': C_WHITE,  'mult': 0.5,   'weight': 2000},
    {'name': 'TECH',  'icon': '▤', 'color': C_CYAN,   'mult': 1.5,   'weight': 1000},
    {'name': 'CORE',  'icon': '◈', 'color': C_PURPLE, 'mult': 5.0,   'weight': 350},
    {'name': 'RELIC', 'icon': '▲', 'color': C_YELLOW, 'mult': 15.0,  'weight': 120},
    {'name': 'OMEGA', 'icon': '★', 'color': C_RED,    'mult': 50.0,  'weight': 25},
    {'name': 'MYTH',  'icon': '☢', 'color': C_MYTHIC, 'mult': 250.0, 'weight': 5},
]

POPULATION = ITEMS
WEIGHTS = [item['weight'] for item in ITEMS]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_tape(length=55):
    return random.choices(POPULATION, weights=WEIGHTS, k=length)

def draw_window(slice_items):
    """Draws a perfectly symmetrical 63-character wide cache window."""
    row = f"{C_CYAN}║{C_RESET} "
    for item in slice_items:
        # Each block is exactly 12 chars: "[ ✖ SCRAP ] "
        row += f"[{item['color']} {item['icon']} {item['name']:<5} {C_RESET}] "
    row += f"{C_CYAN}║{C_RESET}"
    
    # Mathematical centering for the 63-width box
    lines = [
        f"{C_CYAN}╔{'═'*61}╗{C_RESET}",
        row,
        f"{C_CYAN}╚{'═'*61}╝{C_RESET}",
        "                          " + f"{C_YELLOW}▲ WINNER ▲{C_RESET}" + "                           "
    ]
    return "\n".join(lines)

def animate_cache():
    tape = generate_tape(55)
    max_spins = len(tape) - 4 
    
    print("\n" * 4)
    sys.stdout.write('\033[?25l')
    
    final_window = []
    try:
        for i in range(max_spins):
            sys.stdout.write("\033[4A\r\033[2K") 
            
            current_window = tape[i : i+5]
            final_window = current_window 
            
            sys.stdout.write(draw_window(current_window) + "\n")
            sys.stdout.flush()
            
            progress = i / max_spins
            if progress < 0.50: delay = 0.02
            elif progress < 0.75: delay = 0.05
            elif progress < 0.90: delay = 0.15
            elif progress < 0.96: delay = 0.35
            else: delay = 0.60
            
            time.sleep(delay)
            
        time.sleep(1) 
        
    finally:
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
        
    return final_window[2] 

def play(balance):
    last_bet = 100
    
    while True:
        clear()
        print(f"{C_CYAN}==============================================================={C_RESET}")
        print(f"{C_WHITE}                  📦 CYBER CACHE UNLOCKER 📦                 {C_RESET}")
        print(f"{C_CYAN}==============================================================={C_RESET}")
        print(f"💰 Balance: {C_GREEN}${balance:,}{C_RESET}")
        print(f"{C_DARK}---------------------------------------------------------------{C_RESET}")
        print("  PAYTABLE:")
        print(f"  [✖] {C_DARK}SCRAP{C_RESET} -   0x  |  [▲] {C_YELLOW}RELIC{C_RESET} -  15x")
        print(f"  [⚙] {C_WHITE}COMPS{C_RESET} - 0.5x  |  [★] {C_RED}OMEGA{C_RESET} -  50x")
        print(f"  [▤] {C_CYAN}TECH {C_RESET} - 1.5x  |  [☢] {C_MYTHIC}MYTH {C_RESET} - 250x")
        print(f"  [◈] {C_PURPLE}CORE {C_RESET} - 5.0x  |")
        print(f"{C_DARK}---------------------------------------------------------------{C_RESET}")
        
        while True:
            if last_bet > 0:
                print(f"  [ENTER] Open Cache for {C_YELLOW}${last_bet:,}{C_RESET}")
                print(f"  [N] Change Bet Amount")
                print(f"  [Q] Return to Lobby")
                choice = input("\nAction: ").strip().lower()
                
                if choice == 'q': return balance
                elif choice == 'n':
                    last_bet = 0
                    continue
                elif choice == '':
                    if last_bet <= balance: break
                    else: print(f"{C_RED}Insufficient funds.{C_RESET}"); last_bet = 0; continue
            else:
                choice = input(f"Enter bet amount (Balance: ${balance:,}) or [Q]: ").strip().lower()
                if choice == 'q': return balance
                try:
                    bet = int(choice)
                    if 0 < bet <= balance: 
                        last_bet = bet
                        break
                except ValueError: pass
                
        # --- EXECUTION ---
        balance -= last_bet
        clear()
        print(f"{C_DARK}==============================================================={C_RESET}")
        print(f"{C_WHITE}                  📦 DECRYPTING CACHE... 📦                  {C_RESET}")
        print(f"{C_DARK}==============================================================={C_RESET}")
        
        winning_item = animate_cache()
        winnings = int(last_bet * winning_item['mult'])
        net_profit = winnings - last_bet
        balance += winnings
        
        # --- DYNAMIC RESULTS THEME ---
        if winning_item['name'] == 'MYTH':
            theme_color = C_MYTHIC
            title = "☢  MYTHIC DROP DETECTED!  ☢"
        elif winnings > last_bet:
            theme_color = C_GREEN
            title = "🎉  PROFIT HIT!  🎉"
        elif winnings > 0:
            theme_color = C_YELLOW
            title = "📉  PARTIAL RECOVERY  📉"
        else:
            theme_color = C_RED
            title = "💀  TOTAL LOSS  💀"

        print(f"\n{theme_color}==============================================================={C_RESET}")
        print(f"{theme_color}{title.center(63)}{C_RESET}")
        print(f"{theme_color}==============================================================={C_RESET}\n")
        
        # --- RECEIPT ---
        print(f"  {C_CYAN}--- BET RECEIPT ---{C_RESET}")
        print(f"  {C_WHITE}Item Pulled{C_RESET}  : [{winning_item['color']} {winning_item['icon']} {winning_item['name']} {C_RESET}] ({theme_color}{winning_item['mult']}x{C_RESET})")
        print(f"  {C_WHITE}Bet Amount{C_RESET}   : {C_DARK}${last_bet:,}{C_RESET}")
        print(f"  {C_WHITE}Total Payout{C_RESET} : {theme_color}${winnings:,}{C_RESET}")
        
        if net_profit > 0:
            print(f"  {C_WHITE}Net Profit{C_RESET}   : {C_GREEN}+${net_profit:,}{C_RESET}")
        else:
            print(f"  {C_WHITE}Net Loss{C_RESET}     : {C_RED}-${abs(net_profit):,}{C_RESET}")
            
        print(f"\n{C_WHITE}New Balance:{C_RESET} {C_GREEN}${balance:,}{C_RESET}")
        
        while True:
            post_action = input(f"\n{C_DARK}Press [ENTER] to open another, or [Q] for menu: {C_RESET}").strip().lower()
            if post_action == '': break
            elif post_action == 'q': return balance

if __name__ == "__main__":
    play(10000)
