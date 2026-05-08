import os
import time
import random
import sys
import threading

# --- UNIVERSAL ANSI COLORS ---
C_CYAN   = '\033[96m\033[1m'
C_GREEN  = '\033[92m\033[1m'
C_PURPLE = '\033[95m\033[1m'
C_BLUE   = '\033[94m\033[1m'
C_YELLOW = '\033[93m\033[1m'
C_RED    = '\033[91m\033[1m'
C_DARK   = '\033[90m'
C_RESET  = '\033[0m'

# --- THE GEOMETRIC PAYTABLE ---
# Win by getting 3, 4, or 5 of the same symbol ANYWHERE on the 5-slot line.
SYMBOLS = [
    {'char': '●', 'name': 'Sphere',  'color': C_CYAN,   'x3': 2,   'x4': 5,   'x5': 15,   'weight': 40},
    {'char': '■', 'name': 'Cube',    'color': C_GREEN,  'x3': 3,   'x4': 10,  'x5': 30,   'weight': 30},
    {'char': '▲', 'name': 'Prism',   'color': C_PURPLE, 'x3': 5,   'x4': 20,  'x5': 75,   'weight': 20},
    {'char': '◆', 'name': 'Diamond', 'color': C_BLUE,   'x3': 10,  'x4': 50,  'x5': 200,  'weight': 10},
    {'char': '★', 'name': 'Star',    'color': C_YELLOW, 'x3': 25,  'x4': 150, 'x5': 1000, 'weight': 4},
    {'char': 'Ω', 'name': 'Omega',   'color': C_RED,    'x3': 100, 'x4': 500, 'x5': 5000, 'weight': 1},
]

POOL = []
for s in SYMBOLS:
    POOL.extend([s] * s['weight'])

# Global flag for the background thread
stop_autospin = False

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def autospin_listener():
    """Background thread that waits for the user to press Enter."""
    global stop_autospin
    try:
        input()
        stop_autospin = True
    except:
        pass

def run_sequence(balance, bet):
    """Handles the UI rendering and the spinning coin animation."""
    clear()
    # The UI frame is drawn first. It is exactly 55 characters wide.
    print(f"{C_CYAN}╔═════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}║{C_RESET}                   T E S S E R A C T                 {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╠═════════════════════════════════════════════════════╣{C_RESET}")
    print(f"{C_CYAN}║{C_RESET}                                                     {C_CYAN}║{C_RESET}")
    
    final_symbols = [random.choice(POOL) for _ in range(5)]
    spinner = ['|', '/', '-', '\\']
    
    sys.stdout.write('\033[?25l') # Hide Cursor
    
    try:
        # We animate only this single line using carriage return (\r)
        # This prevents ALL formatting bugs because the cursor never moves up or down.
        for frame in range(30):
            line = f"{C_CYAN}║{C_RESET}       "
            for slot in range(5):
                lock_frame = (slot + 1) * 5 # Slots lock one by one
                
                if frame >= lock_frame:
                    sym = final_symbols[slot]
                    line += f"[ {sym['color']}{sym['char']}{C_RESET} ]"
                else:
                    spin_char = spinner[frame % 4]
                    line += f"{C_DARK}[ {spin_char} ]{C_RESET}"
                
                if slot < 4:
                    line += f"{C_DARK} == {C_RESET}"
            
            line += f"       {C_CYAN}║{C_RESET}"
            sys.stdout.write(f"\r{line}")
            sys.stdout.flush()
            time.sleep(0.04)
            
        print() # Drop down to finish the bottom of the box
        print(f"{C_CYAN}║{C_RESET}                                                     {C_CYAN}║{C_RESET}")
        print(f"{C_CYAN}╠═════════════════════════════════════════════════════╣{C_RESET}")
        
        # Format the balance and bet to fit perfectly inside the box
        bal_str = f"Balance: ${balance:,}"
        bet_str = f"Bet: ${bet:,}"
        print(f"{C_CYAN}║{C_RESET} {bal_str:<25} {bet_str:>25} {C_CYAN}║{C_RESET}")
        print(f"{C_CYAN}╚═════════════════════════════════════════════════════╝{C_RESET}")
        
    finally:
        sys.stdout.write('\033[?25h') # Show Cursor
        
    # --- EVALUATION (Count occurrences anywhere on the line) ---
    counts = {}
    for s in final_symbols:
        counts[s['name']] = counts.get(s['name'], 0) + 1
        
    # Find the symbol that appeared the most
    best_sym_name = max(counts, key=counts.get)
    best_count = counts[best_sym_name]
    
    winnings = 0
    win_sym = None
    if best_count >= 3:
        win_sym = next(s for s in SYMBOLS if s['name'] == best_sym_name)
        winnings = bet * win_sym[f'x{best_count}']
        
    return winnings, win_sym, best_count

def play(balance):
    global stop_autospin
    last_bet = 100
    
    while True:
        clear()
        print(f"{C_CYAN}=== 💠 TESSERACT SYSTEM TERMINAL 💠 ==={C_RESET}")
        print(f"💰 Funds: ${balance:,}")
        print("---------------------------------------")
        print(" Rules: Match 3+ shapes ANYWHERE on the line.")
        print("---------------------------------------")
        print(f" [ENTER] Decrypt Once (${last_bet})")
        print(f" [A]     Start Autospin")
        print(f" [B]     Change Bet Amount")
        print(f" [Q]     Disconnect")
        
        choice = input("\nCommand: ").strip().lower()
        
        if choice == 'q': return balance
        elif choice == 'b':
            try:
                new_bet = int(input("Enter new bet: "))
                if 0 < new_bet <= balance: last_bet = new_bet
            except: pass
            continue
            
        mode = "auto" if choice == 'a' else "single"
        
        # --- AUTOSPIN THREAD SETUP ---
        if mode == "auto":
            stop_autospin = False
            t = threading.Thread(target=autospin_listener, daemon=True)
            t.start()
            
        while True:
            if balance < last_bet:
                print(f"\n{C_RED} [!] INSUFFICIENT FUNDS.{C_RESET}")
                time.sleep(2)
                break
                
            balance -= last_bet
            winnings, win_sym, count = run_sequence(balance, last_bet)
            balance += winnings
            
            # --- RESULTS OUTPUT ---
            if winnings > 0:
                print(f"\n  ✨ {C_GREEN}ACCESS GRANTED:{C_RESET} {count}x {win_sym['name']} Detected!")
                print(f"  💰 {C_GREEN}PAYOUT: +${winnings:,}{C_RESET}")
            else:
                print(f"\n  ❌ {C_RED}Sequence Failed.{C_RESET} No matching patterns.")
                
            # --- AUTOSPIN LOGIC & DELAY ---
            if mode == "auto":
                print(f"\n{C_DARK}  [ AUTOSPIN ACTIVE - PRESS ENTER TO HALT ]{C_RESET}")
                
                # We break the 2.5 second delay into tiny chunks.
                # This way, if you press Enter, the thread flips the flag, 
                # and the loop exits instantly without making you wait.
                for _ in range(25):
                    if stop_autospin: break
                    time.sleep(0.1)
                    
                if stop_autospin:
                    print(f"\n{C_YELLOW}  🛑 AUTOSPIN HALTED BY USER.{C_RESET}")
                    time.sleep(1)
                    break
            else:
                input("\nPress [ENTER] to return to terminal...")
                break

if __name__ == "__main__":
    play(10000)
