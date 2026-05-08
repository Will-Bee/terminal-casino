import os
import time
import random
import sys
import json

# --- TERMINAL COLORS ---
C_RED    = '\033[91m\033[1m'
C_DARK   = '\033[90m'
C_WHITE  = '\033[97m\033[1m'
C_GREEN  = '\033[92m\033[1m'
C_YELLOW = '\033[93m\033[1m'
C_RESET  = '\033[0m'

SAVE_FILE = "market_save.json"

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def glitch_text(text, duration, color=C_RED):
    """Simulates a corrupted screen segment."""
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*!?"
    end_time = time.time() + duration
    while time.time() < end_time:
        corrupted = "".join(random.choice(chars) if random.random() > 0.7 else char for char in text)
        sys.stdout.write(f"\r{color}{corrupted}{C_RESET}")
        sys.stdout.flush()
        time.sleep(0.03)
    sys.stdout.write(f"\r{color}{text}{C_RESET}\n")

def play(balance):
    """The standard entry point for the casino lobby."""
    clear()
    
    # --- PHASE 1: THE WARNING ---
    print(f"{C_RED}==============================================================={C_RESET}")
    print(f"{C_RED}⚠  WARNING: INITIATING PROTOCOL 'SCORCHED EARTH' ⚠{C_RESET}".center(72))
    print(f"{C_RED}==============================================================={C_RESET}\n")
    print(f"{C_WHITE}Current Balance : {C_YELLOW}${balance:,}{C_RESET}")
    print(f"{C_WHITE}Market Assets   : {C_YELLOW}FLAGGED FOR LIQUIDATION{C_RESET}\n")
    print(f"{C_DARK}This action will irreversibly wipe your funds and portfolio.{C_RESET}")
    
    confirm = input(f"\n{C_RED}Type 'WIPE' to confirm destruction: {C_RESET}").strip()
    
    if confirm != 'WIPE':
        print(f"\n{C_GREEN}Protocol aborted. Returning to safe environment.{C_RESET}")
        time.sleep(1.5)
        return balance # Return funds untouched back to the lobby
        
    # --- PHASE 2: THE INFECTION ---
    clear()
    sys.stdout.write('\033[?25l') # Hide cursor for the animation
    
    try:
        glitch_text("CRITICAL OVERRIDE ACCEPTED. DISABLING FAILSAFES...", 1.5, C_RED)
        time.sleep(0.5)
        
        # --- PHASE 3: THE MEMORY DUMP ---
        print(f"\n{C_DARK}Beginning sector overwrite...{C_RESET}")
        time.sleep(0.5)
        
        # Rapidly print fake hex codes to simulate data shredding
        for _ in range(80):
            hex_addr = "".join(random.choices("0123456789ABCDEF", k=8))
            fake_data = "".join(random.choices("0123456789ABCDEF ", k=32))
            
            # Occasionally flash red "CORRUPTED" or green "WIPED"
            if random.random() < 0.1:
                status = f"{C_RED}[SHREDDED]{C_RESET}"
            else:
                status = f"{C_DARK}[0x000000]{C_RESET}"
                
            print(f"{C_DARK}0x{hex_addr} : {fake_data} {status}")
            time.sleep(random.uniform(0.005, 0.03))
            
        # --- PHASE 4: THE FILE WIPE ---
        clear()
        print(f"{C_RED}TERMINATING ASSETS...{C_RESET}")
        time.sleep(0.5)
        
        # Actually delete the market JSON file
        if os.path.exists(SAVE_FILE):
            print(f"{C_DARK}Locating {SAVE_FILE}... {C_GREEN}FOUND{C_RESET}")
            time.sleep(0.3)
            os.remove(SAVE_FILE)
            print(f"{C_DARK}Executing rm -rf /sys/portfolio/ ... {C_RED}DELETED{C_RESET}")
        else:
            print(f"{C_DARK}Market data not found. Skipping file wipe...{C_RESET}")
            
        time.sleep(0.3)
        print(f"{C_DARK}Overwriting main ledger... {C_RED}BALANCE ZEROED{C_RESET}")
        time.sleep(1)
        
        # --- PHASE 5: THE COLD REBOOT ---
        clear()
        for _ in range(3):
            sys.stdout.write(f"\r{C_DARK}Rebooting system.{C_RESET}")
            sys.stdout.flush()
            time.sleep(0.5)
            sys.stdout.write(f"\r{C_DARK}Rebooting system..{C_RESET}")
            sys.stdout.flush()
            time.sleep(0.5)
            sys.stdout.write(f"\r{C_DARK}Rebooting system...{C_RESET}")
            sys.stdout.flush()
            time.sleep(0.5)
            
        clear()
        print(f"{C_GREEN}SYSTEM RESTORED.{C_RESET}")
        print(f"{C_WHITE}Welcome, New User.{C_RESET}")
        print(f"{C_DARK}A complimentary stipend of $10,000 has been deposited.{C_RESET}")
        time.sleep(3)
        
    finally:
        sys.stdout.write('\033[?25h') # Show cursor again
        sys.stdout.flush()
        
    return 10000 # Return the fresh starting balance

if __name__ == "__main__":
    play(50000)

