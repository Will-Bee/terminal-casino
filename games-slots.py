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
C_RESET = '\033[0m'
C_BOLD = '\033[1m'

# --- Slot Configuration ---
# Just add a new dictionary here to add a new symbol to the entire game!
SYMBOL_DATA = [
    {'icon': '🍒', 'name': 'Cherries',   'weight': 30, 'payout_3': 1,   'payout_2': 0.5},
    {'icon': '🍋', 'name': 'Lemon',      'weight': 20, 'payout_3': 10,   'payout_2': 0},
    {'icon': '🍇', 'name': 'Grapes',     'weight': 13, 'payout_3': 20,   'payout_2': 0},
    {'icon': '🍉', 'name': 'Watermelon', 'weight': 9, 'payout_3': 50,  'payout_2': 5},
    {'icon': '🔔', 'name': 'Bell',       'weight': 6,  'payout_3': 100,  'payout_2': 10},
    {'icon': '💎', 'name': 'Diamond',    'weight': 3,  'payout_3': 1000, 'payout_2': 250},
    {'icon': '👑', 'name': 'Crown',      'weight': 2,  'payout_3': 2000, 'payout_2': 500}
]

# Create a weighted pool for the random choice
WHEEL_POOL = []
for sym in SYMBOL_DATA:
    WHEEL_POOL.extend([sym] * sym['weight'])

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_random_symbol():
    return random.choice(WHEEL_POOL)

def print_dynamic_paytable():
    """Generates a dynamic 2-column paytable based on SYMBOL_DATA."""
    print(f"  {C_MAGENTA}Paytable (Bet covers all 5 lines!):{C_RESET}")
    
    # Gather all payouts to display dynamically
    display_items = []
    # Sort symbols by highest 3-of-a-kind payout for a logical display hierarchy
    sorted_symbols = sorted(SYMBOL_DATA, key=lambda x: x['payout_3'], reverse=True)
    
    for sym in sorted_symbols:
        display_items.append(f"{sym['icon']} 3 {sym['name'].ljust(10)} - {sym['payout_3']}x")
        if sym['payout_2'] > 0:
            display_items.append(f"{sym['icon']} 2 {sym['name'].ljust(10)} - {sym['payout_2']}x")
            
    # Print in 2 columns
    for i in range(0, len(display_items), 2):
        col1 = display_items[i].ljust(25)
        col2 = display_items[i+1] if i + 1 < len(display_items) else ""
        print(f"  {col1} |  {col2}")

def animate_spin():
    """Animates a 3x3 slot machine with vertical columns spinning."""
    spins = 25
    delay = 0.05
    
    final_cols = [
        [get_random_symbol() for _ in range(3)], 
        [get_random_symbol() for _ in range(3)], 
        [get_random_symbol() for _ in range(3)]  
    ]
    
    sys.stdout.write('\033[?25l') 
    sys.stdout.flush()
    print("\n\n\n")
    
    try:
        for i in range(spins):
            sys.stdout.write('\033[3A')
            
            c1 = final_cols[0] if i >= spins - 12 else [get_random_symbol() for _ in range(3)]
            c2 = final_cols[1] if i >= spins - 6  else [get_random_symbol() for _ in range(3)]
            c3 = final_cols[2] if i >= spins - 1  else [get_random_symbol() for _ in range(3)]
            
            for row in range(3):
                sys.stdout.write(f"\r          {C_YELLOW}🎰 [  {C_RESET}{c1[row]['icon']}  |  {c2[row]['icon']}  |  {c3[row]['icon']}  {C_YELLOW}] 🎰{C_RESET}\n")
            
            sys.stdout.flush()
            time.sleep(delay)
            
        time.sleep(0.5) 
        
    finally:
        sys.stdout.write('\033[?25h') 
        sys.stdout.flush()
        
    grid = [
        [final_cols[0][0], final_cols[1][0], final_cols[2][0]], 
        [final_cols[0][1], final_cols[1][1], final_cols[2][1]], 
        [final_cols[0][2], final_cols[1][2], final_cols[2][2]]  
    ]
    return grid

def evaluate_slots(grid, bet_amount):
    """Evaluates all 5 paylines (3 horizontal, 2 diagonal)."""
    total_winnings = 0
    messages = []
    
    paylines = [
        ("Top Row   ", [grid[0][0], grid[0][1], grid[0][2]]),
        ("Middle Row", [grid[1][0], grid[1][1], grid[1][2]]),
        ("Bottom Row", [grid[2][0], grid[2][1], grid[2][2]]),
        ("Diagonal \\", [grid[0][0], grid[1][1], grid[2][2]]),
        ("Diagonal /", [grid[2][0], grid[1][1], grid[0][2]])
    ]
    
    for line_name, line in paylines:
        sym1, sym2, sym3 = line[0], line[1], line[2]
        
        # 3 of a kind
        if sym1['name'] == sym2['name'] == sym3['name']:
            multiplier = sym1['payout_3']
            win = bet_amount * multiplier
            total_winnings += win
            messages.append(f"  {C_GREEN}✅ {line_name}: 3 {sym1['name']}s! ({multiplier}x) -> ${win:,}{C_RESET}")
            
        # 2 of a kind (Left and Middle matches)
        elif sym1['name'] == sym2['name'] and sym1['payout_2'] > 0:
            multiplier = sym1['payout_2']
            win = bet_amount * multiplier
            total_winnings += win
            messages.append(f"  {C_GREEN}✅ {line_name}: 2 {sym1['name']}s! ({multiplier}x) -> ${win:,}{C_RESET}")

    if not messages:
        messages.append(f"  {C_RED}❌ No winning paylines.{C_RESET}")

    return total_winnings, messages

def play(balance):
    """Main entry point for the Slot Machine."""
    last_bet = 0
    show_menu = True
    
    while True:
        if show_menu:
            clear_screen()
            print(f"{C_CYAN}==================================================={C_RESET}")
            print(f"                {C_YELLOW}{C_BOLD}🎰 3x3 SLOT MACHINE 🎰{C_RESET}             ")
            print(f"{C_CYAN}==================================================={C_RESET}")
            print(f"{C_GREEN}💰 Balance: ${balance:,}{C_RESET}")
            print(f"{C_CYAN}==================================================={C_RESET}")
            
            print_dynamic_paytable()
            
            print(f"{C_CYAN}==================================================={C_RESET}")
            
            # --- Betting Menu ---
            while True:
                if last_bet > 0:
                    print(f"  [{C_YELLOW}ENTER{C_RESET}] Spin again for ${last_bet:,}")
                    print(f"  [{C_YELLOW}N{C_RESET}]     Change Bet Amount")
                    print(f"  [{C_YELLOW}Q{C_RESET}]     Return to Lobby")
                    choice = input("\nAction: ").strip().lower()
                    
                    if choice == 'q':
                        return balance
                    elif choice == 'n':
                        last_bet = 0 
                        continue 
                    elif choice == '':
                        if last_bet > balance:
                            print(f"{C_RED}Insufficient balance for your last bet!{C_RESET}")
                            last_bet = 0
                            continue
                        bet = last_bet
                        break
                    else:
                        print(f"{C_RED}Invalid input.{C_RESET}")
                else:
                    print(f"  [{C_YELLOW}Q{C_RESET}] Return to Lobby")
                    choice = input(f"\nEnter bet amount ({C_GREEN}Balance: ${balance:,}{C_RESET}): ").strip().lower()
                    
                    if choice == 'q':
                        return balance
                    
                    try:
                        bet = int(choice)
                        if bet <= 0:
                            print(f"{C_RED}Bet must be greater than $0.{C_RESET}")
                        elif bet > balance:
                            print(f"{C_RED}Insufficient balance!{C_RESET}")
                        else:
                            last_bet = bet
                            break
                    except ValueError:
                        print(f"{C_RED}Please enter a valid number or 'Q'.{C_RESET}")
        else:
            bet = last_bet
            if bet > balance:
                print(f"\n{C_RED}Insufficient balance to repeat last bet! Returning to menu...{C_RESET}")
                time.sleep(1.5)
                show_menu = True
                continue

        # --- Spin Phase ---
        balance -= bet
        
        clear_screen()
        print(f"{C_CYAN}==================================================={C_RESET}")
        print(f"                {C_YELLOW}{C_BOLD}🎰 3x3 SLOT MACHINE 🎰{C_RESET}             ")
        print(f"{C_CYAN}==================================================={C_RESET}")
        print(f"{C_GREEN}💰 Balance: ${balance:,} {C_RED}(-${bet:,} Bet){C_RESET}")
        print(f"{C_CYAN}==================================================={C_RESET}")
        
        grid = animate_spin()
        winnings, messages = evaluate_slots(grid, bet)
        
        print(f"\n{C_CYAN}==================================================={C_RESET}")
        if winnings > 0:
            print(f"                {C_GREEN}{C_BOLD}🎉 YOU WON ${winnings:,}! 🎉{C_RESET}")
            balance += winnings
            net_result = winnings - bet
        else:
            print(f"                    {C_RED}💸 You lost. 💸{C_RESET}")
            net_result = -bet
        print(f"{C_CYAN}===================================================\n{C_RESET}")
        
        # Receipt
        print(f"  {C_MAGENTA}--- BET RECEIPT ---{C_RESET}")
        for msg in messages:
            print(msg)
        print(f"  {C_MAGENTA}-------------------{C_RESET}")
        print(f"  Bet Amount   : ${bet:,}")
        print(f"  Total Payout : ${winnings:,}")
        
        if net_result > 0:
            print(f"  Net Profit   : {C_GREEN}+${net_result:,}{C_RESET}")
        else:
            print(f"  Net Loss     : {C_RED}-${abs(net_result):,}{C_RESET}")
            
        print(f"\n{C_GREEN}{C_BOLD}New Balance: ${balance:,}{C_RESET}")
        
        # --- Post-Game Prompt ---
        while True:
            post_action = input(f"\nPress [{C_YELLOW}ENTER{C_RESET}] to spin again, or [{C_YELLOW}Q{C_RESET}] to return to menu: ").strip().lower()
            if post_action == '':
                show_menu = False
                break
            elif post_action == 'q':
                show_menu = True
                break
            else:
                print(f"{C_RED}Invalid input. Press Enter or Q.{C_RESET}")

if __name__ == "__main__":
    play(10000)
