import os
import time
import random
import sys
import re

# --- Roulette Wheel Configuration ---
WHEEL = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]

RED = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def render_board(winning_idx=-1):
    """Renders the static UI and the row of numbers."""
    clear_screen()
    print("===============================================================================================================")
    print("                                          🎰 ROULETTE 🎰                                               ")
    print("===============================================================================================================\n")
    
    num_row = ""
    for i, num in enumerate(WHEEL):
        if num == 0:
            bg = "\033[42m"  # Green
        elif num in RED:
            bg = "\033[41m"  # Red
        else:
            bg = "\033[40m"  # Black
            
        is_win = (i == winning_idx)
        text = "\033[93m\033[1m" if is_win else "\033[97m"
        end_fmt = "\033[0m"
        
        # 3 characters per slot
        num_row += f"{bg}{text}{num:2} {end_fmt}"
        
    print(num_row)

def animate_spin():
    """Animates the ball using a carriage return (\r) to avoid screen flashing."""
    render_board()
    
    momentum = random.uniform(40.0, 60.0) 
    friction = random.uniform(0.8, 1.2)   
    ball_idx = random.randint(0, len(WHEEL) - 1)
    
    sys.stdout.write('\033[?25l') # Hide cursor
    sys.stdout.flush()
    
    try:
        while momentum > 0:
            ball_row = ("   " * ball_idx) + " O " + ("   " * (len(WHEEL) - ball_idx - 1))
            sys.stdout.write('\r' + ball_row)
            sys.stdout.flush()
            
            delay = 1.0 / max(momentum, 1.6)
            time.sleep(delay)
            
            ball_idx = (ball_idx + 1) % len(WHEEL)
            momentum -= friction * random.uniform(0.5, 1.5)
            
    finally:
        sys.stdout.write('\033[?25h') # Show cursor
        sys.stdout.flush()
        
    return ball_idx

def format_history(history):
    """Formats the recent spins with ANSI colors for the menu."""
    if not history:
        return "None"
    
    formatted = []
    for num in history:
        if num == 0:
            formatted.append(f"\033[32m{num}\033[0m") # Green
        elif num in RED:
            formatted.append(f"\033[31m{num}\033[0m") # Red
        else:
            formatted.append(f"\033[90m{num}\033[0m") # Dark Grey (stands in for Black)
            
    return " | ".join(formatted)

def get_bet_name(b_type, b_val):
    """Formats the bet type and value for cleaner display."""
    if b_type == 'number': return f"Number {b_val}"
    if b_type == 'color': return f"Color {str(b_val).title()}"
    if b_type == 'parity': return f"{str(b_val).title()}s"
    if b_type == 'half': return f"Half ({str(b_val).title()})"
    if b_type == 'dozen':
        if b_val == 1: return "1st Dozen"
        if b_val == 2: return "2nd Dozen"
        if b_val == 3: return "3rd Dozen"
    return f"{b_type} {b_val}"

def evaluate_bets(bets, winning_number):
    """Calculates payouts and generates a detailed breakdown for each bet."""
    total_won = 0
    details = []
    
    for bet in bets:
        b_type, b_val, amount = bet['type'], bet['value'], bet['amount']
        win = False
        multiplier = 0
        
        if b_type == 'number' and b_val == winning_number: win, multiplier = True, 36
        elif b_type == 'color':
            if b_val == 'red' and winning_number in RED: win, multiplier = True, 2
            elif b_val == 'black' and winning_number in BLACK: win, multiplier = True, 2
            elif b_val == 'green' and winning_number == 0: win, multiplier = True, 18
        elif b_type == 'parity' and winning_number != 0:
            if b_val == 'even' and winning_number % 2 == 0: win, multiplier = True, 2
            elif b_val == 'odd' and winning_number % 2 != 0: win, multiplier = True, 2
        elif b_type == 'half' and winning_number != 0:
            if b_val == 'low' and 1 <= winning_number <= 18: win, multiplier = True, 2
            elif b_val == 'high' and 19 <= winning_number <= 36: win, multiplier = True, 2
        elif b_type == 'dozen' and winning_number != 0:
            if b_val == 1 and 1 <= winning_number <= 12: win, multiplier = True, 3
            elif b_val == 2 and 13 <= winning_number <= 24: win, multiplier = True, 3
            elif b_val == 3 and 25 <= winning_number <= 36: win, multiplier = True, 3

        bet_name = get_bet_name(b_type, b_val)
        
        if win: 
            payout = amount * multiplier
            total_won += payout
            details.append(f"  ✅ Bet ${amount:,} on {bet_name:<15} -> WON ${payout:,}")
        else:
            details.append(f"  ❌ Bet ${amount:,} on {bet_name:<15} -> LOST")

    return total_won, details

def get_bet_amount(balance, current_bets_sum=0):
    while True:
        try:
            available = balance - current_bets_sum
            amt = int(input(f"Enter bet amount (Available: ${available:,}): $"))
            if amt <= 0: print("Bet must be greater than 0.")
            elif amt > available: print("Insufficient balance!")
            else: return amt
        except ValueError:
            print("Please enter a valid number.")

def play(balance):
    """Main entry point for the Roulette game."""
    history = []
    
    while True:
        bets = []
        
        while True:
            clear_screen()
            total_active_bets = sum(b['amount'] for b in bets)
            print("===================================")
            print("         🎰 ROULETTE 🎰          ")
            print("===================================")
            print(f"💰 Balance: ${balance:,}")
            print(f"💵 Active Bets: {len(bets)} (Total: ${total_active_bets:,})")
            print(f"🕒 Recent Spins: {format_history(history)}")
            print("===================================")
            print("  [1] Bet on Specific Number (0-36)")
            print("  [2] Bet on Color (Red/Black)")
            print("  [3] Bet on Evens / Odds")
            print("  [4] Bet on Low (1-18) / High (19-36)")
            print("  [5] Bet on Dozen (1st, 2nd, 3rd)")
            print("-----------------------------------")
            print("  [S] SPIN THE WHEEL! 🎡")
            print("  [Q] Return to Lobby")
            
            command = input("\nChoose an option: ").strip().lower()
            
            if command == 'q': return balance + total_active_bets
            if command == 's':
                if not bets:
                    print("Place a bet first!")
                    time.sleep(1.5)
                    continue
                break 

            # --- Complex Command Parsing (Shortcuts) ---
            match = re.match(r'^([1-5])\s*(.*?)\s*(\d+)$', command)
            
            if match:
                option_num = int(match.group(1))
                bet_val_raw = match.group(2).strip()
                amount_str = match.group(3)
                amount = int(amount_str)

                if amount <= 0 or amount > (balance - total_active_bets):
                    print("Invalid or insufficient bet amount.")
                    time.sleep(1)
                    continue
                
                parsed_bet = None
                
                if option_num == 1:
                    if bet_val_raw.isdigit():
                        try:
                            num = int(bet_val_raw)
                            if 0 <= num <= 36: parsed_bet = {'type': 'number', 'value': num, 'amount': amount}
                        except ValueError: pass
                    else:
                         num_match = re.search(r'\d+', bet_val_raw)
                         if num_match:
                             try:
                                 num = int(num_match.group(0))
                                 if 0 <= num <= 36: parsed_bet = {'type': 'number', 'value': num, 'amount': amount}
                             except ValueError: pass
                        
                elif option_num == 2:
                    if bet_val_raw in ['r', 'red', 'b', 'black', 'g', 'green']:
                        val = 'red' if bet_val_raw.startswith('r') else ('black' if bet_val_raw.startswith('b') else 'green')
                        parsed_bet = {'type': 'color', 'value': val, 'amount': amount}
                        
                elif option_num == 3:
                    if bet_val_raw in ['e', 'even', 'o', 'odd']:
                        val = 'even' if bet_val_raw.startswith('e') else 'odd'
                        parsed_bet = {'type': 'parity', 'value': val, 'amount': amount}
                        
                elif option_num == 4:
                    if bet_val_raw in ['l', 'low', 'h', 'high']:
                        val = 'low' if bet_val_raw.startswith('l') else 'high'
                        parsed_bet = {'type': 'half', 'value': val, 'amount': amount}
                        
                elif option_num == 5:
                    if bet_val_raw in ['1', '2', '3', '1st', '2nd', '3rd', 'first', 'second', 'third']:
                        val = 0
                        if '1' in bet_val_raw or 'first' in bet_val_raw or '1st' in bet_val_raw: val = 1
                        elif '2' in bet_val_raw or 'second' in bet_val_raw or '2nd' in bet_val_raw: val = 2
                        elif '3' in bet_val_raw or 'third' in bet_val_raw or '3rd' in bet_val_raw: val = 3
                        if val > 0: parsed_bet = {'type': 'dozen', 'value': val, 'amount': amount}

                if parsed_bet:
                    bets.append(parsed_bet)
                    balance -= amount
                    continue
                else:
                    if command not in ('q', 's'):
                        print("Could not parse your bet command or value is invalid.")
                        time.sleep(1.5)
                        continue

            # --- Normal Menu Choices Fallback ---
            elif command.isdigit():
                choice = command
                if choice == '1':
                    try:
                        num = int(input("Enter number (0-36): "))
                        if 0 <= num <= 36:
                            amt = get_bet_amount(balance, total_active_bets)
                            balance -= amt
                            bets.append({'type': 'number', 'value': num, 'amount': amt})
                        else:
                            print("Invalid number.")
                            time.sleep(1)
                    except ValueError: pass
                        
                elif choice == '2':
                    col = input("Color (R=Red, B=Black, G=Green): ").strip().lower()
                    if col in ['r', 'red', 'b', 'black', 'g', 'green']:
                        amt = get_bet_amount(balance, total_active_bets)
                        balance -= amt
                        val = 'red' if col.startswith('r') else ('black' if col.startswith('b') else 'green')
                        bets.append({'type': 'color', 'value': val, 'amount': amt})
                    else:
                        print("Invalid color choice.")
                        time.sleep(1)
                        
                elif choice == '3':
                    par = input("Parity (E=Even, O=Odd): ").strip().lower()
                    if par in ['e', 'even', 'o', 'odd']:
                        amt = get_bet_amount(balance, total_active_bets)
                        balance -= amt
                        val = 'even' if par.startswith('e') else 'odd'
                        bets.append({'type': 'parity', 'value': val, 'amount': amt})
                    else:
                        print("Invalid parity choice.")
                        time.sleep(1)
                        
                elif choice == '4':
                    half = input("Half (L=Low 1-18, H=High 19-36): ").strip().lower()
                    if half in ['l', 'low', 'h', 'high']:
                        amt = get_bet_amount(balance, total_active_bets)
                        balance -= amt
                        val = 'low' if half.startswith('l') else 'high'
                        bets.append({'type': 'half', 'value': val, 'amount': amt})
                    else:
                        print("Invalid half choice.")
                        time.sleep(1)
                        
                elif choice == '5':
                    try:
                        doz = int(input("Dozen (1=1-12, 2=13-24, 3=25-36): "))
                        if doz in [1, 2, 3]:
                            amt = get_bet_amount(balance, total_active_bets)
                            balance -= amt
                            bets.append({'type': 'dozen', 'value': doz, 'amount': amt})
                        else:
                            print("Invalid dozen choice.")
                            time.sleep(1)
                    except ValueError: pass
            else:
                 if command not in ('q', 's'):
                    print("Invalid choice.")
                    time.sleep(1)

        # --- Spin Phase ---
        winning_idx = animate_spin()
        winning_number = WHEEL[winning_idx]
        
        # Add to history, keep only last 10
        history.append(winning_number)
        history = history[-10:]
        
        # Refresh the entire board one last time to highlight the winning number
        render_board(winning_idx)
        print(("   " * winning_idx) + " O " + ("   " * (len(WHEEL) - winning_idx - 1)))
        
        # --- Results Phase ---
        color_str = "Green" if winning_number == 0 else ("Red" if winning_number in RED else "Black")
        print(f"\n===============================================================================================================")
        print(f"                               🎡 The ball landed on: {color_str} {winning_number}! 🎡")
        print(f"===============================================================================================================\n")
        
        print("  --- BET RECEIPT ---")
        total_winnings, bet_details = evaluate_bets(bets, winning_number)
        
        for detail in bet_details:
            print(detail)
            
        print("  -------------------")
        
        # Calculate net profit/loss
        total_spent = sum(b['amount'] for b in bets)
        net_result = total_winnings - total_spent
        
        print(f"  Total Payout : ${total_winnings:,}")
        
        if net_result > 0:
            print(f"  Net Profit   : \033[32m+${net_result:,}\033[0m")
        elif net_result < 0:
            print(f"  Net Loss     : \033[31m-${abs(net_result):,}\033[0m")
        else:
            print(f"  Net Result   : \033[33m$0 (Broke Even)\033[0m")
        
        balance += total_winnings
            
        print(f"\n===============================================================================================================")
        print(f"New Balance: ${balance:,}")
        
        again = input("\nPress Enter to play again, or 'Q' to return to lobby: ").strip().lower()
        if again == 'q':
            return balance

if __name__ == "__main__":
    play(10000)
