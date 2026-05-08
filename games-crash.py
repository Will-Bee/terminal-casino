import os
import time
import random
import sys
import threading
import math

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def calculate_crash_point():
    """
    Generates a Crash multiplier. 
    Uses industry-standard math to create a ~1% instant crash rate 
    and an exponentially decreasing chance to hit massive multipliers.
    """
    e = 0.99 / (1.0 - random.random())
    if e < 1.00:
        return 1.00
    return e

def play(balance):
    """Main entry point for Crash."""
    last_bet = 0
    show_menu = True
    
    while True:
        # --- Betting Menu ---
        if show_menu:
            clear_screen()
            print("===================================================")
            print("                  📈 CRASH 📉                    ")
            print("===================================================")
            print(f"💰 Balance: ${balance:,}")
            print("===================================================")
            
            while True:
                if last_bet > 0:
                    print(f"  [ENTER] Bet ${last_bet:,} and start")
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
        
        target_crash = calculate_crash_point()
        
        # Shared variables between threads
        cashed_out = False
        crashed = False
        current_multiplier = 1.00
        
        clear_screen()
        print("===================================================")
        print("                  📈 CRASH 📉                    ")
        print("===================================================")
        print(f"💰 Balance: ${balance:,} (-${bet:,} Bet)")
        print("===================================================\n")
        
        print("  Preparing launch in 3...", end="", flush=True)
        time.sleep(0.6)
        print("\r  Preparing launch in 2...", end="", flush=True)
        time.sleep(0.6)
        print("\r  Preparing launch in 1...", end="", flush=True)
        time.sleep(0.6)
        print("\r  🚀 LIFTOFF!                      \n")
        
        sys.stdout.write('\033[?25l') # Hide cursor for clean animation
        sys.stdout.flush()
        
        # --- The Background Thread (Animation Loop) ---
        def run_multiplier():
            nonlocal current_multiplier, crashed
            start_time = time.time()
            
            while not cashed_out and not crashed:
                elapsed = time.time() - start_time
                
                # Exponential curve: multiplier rises faster the longer you wait
                current_multiplier = 1.00 * math.exp(elapsed * 0.15)
                
                if current_multiplier >= target_crash:
                    current_multiplier = target_crash
                    crashed = True
                    break
                    
                # The visual update
                sys.stdout.write(f"\r      🚀 \033[1m\033[93m{current_multiplier:.2f}x\033[0m  [Press ENTER to Cash Out!]   ")
                sys.stdout.flush()
                time.sleep(0.04) # Roughly 25 FPS for smooth animation
                
            if crashed:
                # If it crashes, change the prompt so the user presses Enter to proceed
                sys.stdout.write(f"\r      💥 \033[1m\033[31mCRASHED AT {current_multiplier:.2f}x\033[0m [Press ENTER to continue]\n")
                sys.stdout.flush()

        # Start the background thread
        crash_thread = threading.Thread(target=run_multiplier)
        crash_thread.daemon = True
        crash_thread.start()
        
        # --- The Main Thread (Input Listener) ---
        # The script completely freezes right here and waits for the user to hit Enter.
        input() 
        
        sys.stdout.write('\033[?25h') # Show cursor again
        sys.stdout.flush()
        
        # --- Results Phase ---
        if not crashed:
            # Player hit Enter BEFORE the crash
            cashed_out = True
            crash_thread.join() # Wait for background thread to cleanly exit
            
            winnings = int(bet * current_multiplier)
            net_result = winnings - bet
            balance += winnings
            
            print(f"\n===================================================")
            print(f"               🎉 CASHED OUT! 🎉")
            print(f"               Locked in at {current_multiplier:.2f}x")
            print("===================================================\n")
            
            print("  --- BET RECEIPT ---")
            print(f"  Bet Amount   : ${bet:,}")
            print(f"  Multiplier   : {current_multiplier:.2f}x")
            print(f"  Total Payout : ${winnings:,}")
            print(f"  Net Profit   : \033[32m+${net_result:,}\033[0m")
            print("  -------------------")
            
        else:
            # Player waited too long. 
            # (They pressed Enter to satisfy the "Press ENTER to continue" prompt)
            crash_thread.join()
            
            net_result = -bet
            
            print(f"\n===================================================")
            print("                   💸 YOU LOST 💸")
            print(f"               Crashed at {current_multiplier:.2f}x")
            print("===================================================\n")
            
            print("  --- BET RECEIPT ---")
            print(f"  Bet Amount   : ${bet:,}")
            print(f"  Multiplier   : 0.00x")
            print(f"  Total Payout : $0")
            print(f"  Net Loss     : \033[31m-${abs(net_result):,}\033[0m")
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
