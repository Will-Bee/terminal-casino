import os
import time
import random
import sys
import json

# --- TERMINAL COLORS & STYLES ---
C_DARK   = '\033[90m'
C_WHITE  = '\033[97m\033[1m'
C_CYAN   = '\033[96m\033[1m'
C_PURPLE = '\033[95m\033[1m'
C_YELLOW = '\033[93m\033[1m'
C_RED    = '\033[91m\033[1m'
C_GREEN  = '\033[92m\033[1m'
C_RESET  = '\033[0m'

SAVE_FILE = "market_save.json"
UPDATE_INTERVAL = 5 # 1 minute per "tick"

# --- EXPANDABLE ASSET CONFIGURATION ---
# volatility: max % change per minute (0.05 = 5%)
# trend: 1.001 = slight upward bias, 0.995 = slight decay
ASSETS = {
    'AGS':  {'name': 'Aegis Secure Data', 'base': 150.0, 'volatility': 0.03, 'trend': 1.001, 'color': C_CYAN},
    'OMNI': {'name': 'OmniCorp Synth',    'base': 50.0,  'volatility': 0.06, 'trend': 1.000, 'color': C_WHITE},
    'TDM':  {'name': 'Tesseract Mining',  'base': 15.0,  'volatility': 0.12, 'trend': 1.000, 'color': C_YELLOW},
    'VDC':  {'name': 'VOIDCoin',          'base': 1.0,   'volatility': 0.35, 'trend': 0.998, 'color': C_PURPLE},
    'SCRP': {'name': 'ScrapToken',        'base': 0.1,   'volatility': 0.60, 'trend': 0.985, 'color': C_DARK}
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_sparkline(history):
    """Converts a list of prices into an ASCII mini-chart."""
    bars = [' ', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    if not history or len(history) < 2: return "          "
    
    # We only show the last 10 points
    plot_data = history[-10:]
    min_val = min(plot_data)
    max_val = max(plot_data)
    
    if max_val == min_val: return bars[3] * len(plot_data)
    
    spark = ""
    for val in plot_data:
        # Normalize between 0 and 7
        normalized = int((val - min_val) / (max_val - min_val) * 7)
        spark += bars[normalized]
        
    return spark.ljust(10) # Ensure it's always 10 chars wide

def load_market():
    """Loads state or creates a fresh market if none exists."""
    current_time = time.time()
    
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r') as f:
                state = json.load(f)
                return state
        except: pass
        
    # Fresh Initialization
    state = {
        'last_updated': current_time,
        'portfolio': {ticker: 0 for ticker in ASSETS.keys()},
        'history': {}
    }
    
    # Generate 10 minutes of backward history so charts aren't empty
    for ticker, config in ASSETS.items():
        price = config['base']
        hist = []
        for _ in range(10):
            hist.append(price)
            change = random.uniform(-config['volatility'], config['volatility'])
            price = price * config['trend'] * (1 + change)
            price = max(0.01, price) # Floor price at 1 cent
        state['history'][ticker] = hist
        
    return state

def save_market(state):
    with open(SAVE_FILE, 'w') as f:
        json.dump(state, f)

def sync_market_time(state):
    """Calculates real-world time passed and simulates market movements."""
    current_time = time.time()
    delta_seconds = current_time - state['last_updated']
    
    ticks_passed = int(delta_seconds / UPDATE_INTERVAL)
    
    if ticks_passed > 0:
        # Cap offline simulation to 1440 ticks (24 hours) to prevent insane math/lag
        ticks_passed = min(ticks_passed, 1440)
        
        for ticker, config in ASSETS.items():
            hist = state['history'][ticker]
            price = hist[-1]
            
            for _ in range(ticks_passed):
                # Random walk: base trend + random volatility swing
                # Occasionally trigger a "Pump" or "Dump" for volatile assets
                change = random.uniform(-config['volatility'], config['volatility'])
                
                # 5% chance for a volatile crypto to do something crazy
                if config['volatility'] > 0.2 and random.random() < 0.05:
                    change *= 3 
                    
                price = price * config['trend'] * (1 + change)
                price = max(0.01, round(price, 2))
                hist.append(price)
                
            # Keep only the last 60 minutes of history to save file size
            state['history'][ticker] = hist[-60:]
            
        state['last_updated'] = current_time
        save_market(state)
        return True
    return False

def draw_exchange(state, balance):
    print(f"{C_CYAN}==============================================================={C_RESET}")
    print(f"{C_WHITE}                 🌐 THE DARK WEB EXCHANGE 🌐                 {C_RESET}")
    print(f"{C_CYAN}==============================================================={C_RESET}")
    
    # Calculate total portfolio value
    portfolio_value = 0.0
    for t in ASSETS.keys():
        shares = state['portfolio'].get(t, 0)
        price = state['history'][t][-1]
        portfolio_value += (shares * price)
        
    print(f"💰 Fiat Cash: {C_GREEN}${balance:,.2f}{C_RESET}")
    print(f"📈 Portfolio: {C_YELLOW}${portfolio_value:,.2f}{C_RESET}")
    print(f"🏦 Net Worth: {C_WHITE}${(balance + portfolio_value):,.2f}{C_RESET}")
    print(f"{C_DARK}---------------------------------------------------------------{C_RESET}")
    print(f"  {C_WHITE}TICKER   PRICE      24H CHART   SHARES   VALUE{C_RESET}")
    
    for ticker, config in ASSETS.items():
        hist = state['history'][ticker]
        curr_price = hist[-1]
        prev_price = hist[-2] if len(hist) > 1 else curr_price
        shares = state['portfolio'].get(ticker, 0)
        
        # Determine color based on recent movement
        if curr_price > prev_price: price_color = C_GREEN
        elif curr_price < prev_price: price_color = C_RED
        else: price_color = C_WHITE
        
        spark = generate_sparkline(hist)
        val_str = f"${(shares * curr_price):,.2f}"
        
        # Formatting to fit exactly
        t_str = f"{config['color']}[{ticker:<4}]{C_RESET}"
        p_str = f"{price_color}${curr_price:<8.2f}{C_RESET}"
        s_str = f"{C_DARK}{spark}{C_RESET}"
        sh_str = f"{shares:<8}"
        v_str = f"{C_YELLOW}{val_str:>9}{C_RESET}"
        
        print(f"  {t_str} {p_str} {s_str}  {sh_str} {v_str}")
        
    print(f"{C_DARK}---------------------------------------------------------------{C_RESET}")

def play(balance):
    state = load_market()
    sync_market_time(state) # Catch up on time passed since last boot
    
    while True:
        clear()
        # Always check if time has passed while we are staring at the menu
        if sync_market_time(state):
            pass # Data was updated
            
        draw_exchange(state, balance)
        
        print("  [B] Buy Asset      [S] Sell Asset")
        print("  [R] Refresh Market [Q] Return to Lobby")
        
        choice = input("\nCommand: ").strip().lower()
        
        if choice == 'q':
            save_market(state)
            return int(balance) # Return integer to keep main casino clean
            
        elif choice == 'r':
            clear()
            print(f"{C_DARK}Fetching live market data...{C_RESET}")
            time.sleep(0.5)
            continue
            
        elif choice == 'b':
            ticker = input(f"Enter Ticker to {C_GREEN}BUY{C_RESET} (e.g., VDC) or [C]ancel: ").strip().upper()
            if ticker in ASSETS:
                curr_price = state['history'][ticker][-1]
                max_shares = int(balance // curr_price)
                if max_shares <= 0:
                    input(f"{C_RED}Insufficient funds to buy even 1 share. Press Enter...{C_RESET}")
                    continue
                    
                amount = input(f"Shares to buy? (Max: {max_shares}): ").strip()
                try:
                    amount = int(amount)
                    cost = amount * curr_price
                    if 0 < amount <= max_shares:
                        balance -= cost
                        state['portfolio'][ticker] = state['portfolio'].get(ticker, 0) + amount
                        save_market(state)
                        input(f"{C_GREEN}Transaction successful: -${cost:,.2f}. Press Enter...{C_RESET}")
                except ValueError: pass
                
        elif choice == 's':
            ticker = input(f"Enter Ticker to {C_RED}SELL{C_RESET} (e.g., VDC) or [C]ancel: ").strip().upper()
            if ticker in ASSETS:
                owned = state['portfolio'].get(ticker, 0)
                if owned <= 0:
                    input(f"{C_RED}You do not own any shares of {ticker}. Press Enter...{C_RESET}")
                    continue
                    
                amount = input(f"Shares to sell? (Max: {owned}, or 'ALL'): ").strip().upper()
                if amount == 'ALL': amount = owned
                try:
                    amount = int(amount)
                    curr_price = state['history'][ticker][-1]
                    revenue = amount * curr_price
                    if 0 < amount <= owned:
                        balance += revenue
                        state['portfolio'][ticker] -= amount
                        save_market(state)
                        input(f"{C_GREEN}Transaction successful: +${revenue:,.2f}. Press Enter...{C_RESET}")
                except ValueError: pass

if __name__ == "__main__":
    play(5000)
