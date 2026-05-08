import os
import sys
import time
import json
import importlib.util
import random

# --- TERMINAL COLORS ---
C_DARK   = '\033[90m'
C_WHITE  = '\033[97m\033[1m'
C_CYAN   = '\033[96m\033[1m'
C_PURPLE = '\033[95m\033[1m'
C_YELLOW = '\033[93m\033[1m'
C_RED    = '\033[91m\033[1m'
C_GREEN  = '\033[92m\033[1m'
C_RESET  = '\033[0m'

SAVE_FILE = "market_save.json"
WALLET_FILE = "balance.json"
CATEGORIES = ['games', 'funds', 'extra']

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def boot_sequence():
    """Cinematic boot using total gibberish jargon."""
    clear()
    sys.stdout.write('\033[?25l') 
    
    jargon = [
        "Syncing V-Phased Inductors...",
        "Calibrating Flux-Capacitance Matrix...",
        "Injecting Sub-Etheric Nanites...",
        "Bypassing Chronos-Filter...",
        "Defragmenting Neural-Link Latches...",
        "Priming Core-Siphon..."
    ]
    
    try:
        print(f"{C_DARK}[ NODE-01 INITIALIZED ]{C_RESET}")
        time.sleep(0.4)
        
        for line in jargon:
            sys.stdout.write(f"{C_DARK}{line} {C_RESET}")
            sys.stdout.flush()
            time.sleep(random.uniform(0.1, 0.3))
            print(f"{C_CYAN}[OK]{C_RESET}")
            
        print(f"\n{C_WHITE}EXTRACTING OMEGA-KAPPA PROTOCOLS...{C_RESET}")
        
        # Fast hex stream
        for _ in range(12):
            stream = "".join(random.choices("0123456789ABCDEF", k=50))
            print(f"{C_DARK}{stream}{C_RESET}")
            time.sleep(0.02)
            
        print(f"\n{C_YELLOW}Linking Local Node Modules...{C_RESET}")
        for file in sorted(os.listdir()):
            if file.endswith('.py') and '-' in file:
                sys.stdout.write(f"{C_DARK}Mounting /{file}... {C_RESET}")
                sys.stdout.flush()
                time.sleep(0.05)
                print(f"{C_GREEN}[SYNCED]{C_RESET}")
                
        time.sleep(0.5)
        clear()
        
        logo = f"""{C_CYAN}
  ██████╗ █████╗ ███████╗██╗███╗   ██╗ ██████╗ 
 ██╔════╝██╔══██╗██╔════╝██║████╗  ██║██╔═══██╗
 ██║     ███████║███████╗██║██╔██╗ ██║██║   ██║
 ██║     ██╔══██║╚════██║██║██║╚██╗██║██║   ██║
 ╚██████╗██║  ██║███████║██║██║ ╚████║╚██████╔╝
  ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ 
        {C_RESET}"""
        print(logo)
        print(f"{C_WHITE}{'TERMINAL INTERFACE v9.4.1'.center(48)}{C_RESET}\n")
        time.sleep(1)
        
    finally:
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

def shutdown_animation(balance, portfolio):
    """Sleek, high-tech shutdown sequence with stat readout and progress bar."""
    clear()
    sys.stdout.write('\033[?25l')
    net_worth = balance + portfolio
    
    try:
        print(f"\n{C_YELLOW}>>> INITIATING PROTOCOL: OMEGA-SLEEP <<<{C_RESET}\n")
        time.sleep(0.5)
        
        # Encrypting Data sequence
        sys.stdout.write(f"{C_DARK}Encrypting Session Ledger... {C_RESET}")
        sys.stdout.flush()
        time.sleep(0.8)
        print(f"{C_GREEN}[SECURED]{C_RESET}")
        
        # Display Final Stats
        print(f"\n{C_CYAN}    FINAL SESSION AUDIT{C_RESET}")
        print(f"    {C_WHITE}Liquid Cash: ${balance:,.2f}{C_RESET}")
        print(f"    {C_WHITE}Portfolio:   ${portfolio:,.2f}{C_RESET}")
        print(f"    {C_PURPLE}Net Worth:   ${net_worth:,.2f}{C_RESET}\n")
        time.sleep(1.5)
        
        # Disconnect progress bar
        bar_width = 40
        sys.stdout.write(f"{C_RED}Severing Uplink: {C_RESET}[")
        for i in range(bar_width):
            sys.stdout.write(f"{C_RED}█{C_RESET}")
            sys.stdout.flush()
            time.sleep(random.uniform(0.01, 0.05))
        print(f"{C_RED}] 100%{C_RESET}")
        
        time.sleep(0.6)
        clear()
        
        # Final fade out
        print(f"\n\n{C_DARK}{'--- TERMINAL OFFLINE ---'.center(60)}{C_RESET}\n\n")
        time.sleep(0.8)
        clear()
        
    finally:
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()

def load_balance():
    if os.path.exists(WALLET_FILE):
        try:
            with open(WALLET_FILE, 'r') as f:
                return json.load(f).get('balance', 10000)
        except: pass
    return 10000 

def save_balance(balance):
    with open(WALLET_FILE, 'w') as f:
        json.dump({'balance': balance}, f)

def get_portfolio_value():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                state = json.load(f)
                total = 0.0
                for ticker, config in state['history'].items():
                    shares = state['portfolio'].get(ticker, 0)
                    total += shares * config[-1]
                return total
    except: pass
    return 0.0

def scan_plugins():
    plugins = {cat: [] for cat in CATEGORIES}
    menu_map = {}
    counter = 1
    for file in sorted(os.listdir()):
        if file.endswith('.py') and '-' in file and file != 'main.py' and not file.startswith('x-'):
            parts = file.split('-', 1)
            if parts[0] in CATEGORIES:
                display_name = parts[1].replace('.py', '').replace('_', ' ').title()
                plugins[parts[0]].append({'id': str(counter), 'name': display_name, 'file': file})
                menu_map[str(counter)] = file
                counter += 1
    return plugins, menu_map

def run_plugin(filepath, balance):
    try:
        spec = importlib.util.spec_from_file_location("plugin_module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return int(module.play(balance))
    except Exception as e:
        print(f"{C_RED}Protocol Error: {e}{C_RESET}"); time.sleep(2)
        return balance

def draw_lobby(balance, portfolio, plugins):
    """Ultra-stable formatting that doesn't break on ANSI codes."""
    net_worth = balance + portfolio
    clear()
    
    # Border strings (No ANSI in width calculations)
    INNER_WIDTH = 61
    top_edge = f"╔{'═'*INNER_WIDTH}╗"
    mid_edge = f"╠{'═'*INNER_WIDTH}╣"
    bot_edge = f"╚{'═'*INNER_WIDTH}╝"

    print(f"{C_CYAN}{top_edge}{C_RESET}")
    print(f"{C_CYAN}║{C_RESET}{C_WHITE}{'CASINO TERMINAL'.center(INNER_WIDTH)}{C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}{mid_edge}{C_RESET}")
    
    # Line 1: Balance & Portfolio
    l_raw = f" Liquid Cash: ${balance:,.2f}"
    r_raw = f"Portfolio: ${portfolio:,.2f} "
    pad = INNER_WIDTH - len(l_raw) - len(r_raw)
    
    # Removed the rogue leading space here to keep it strictly 61 characters
    line1 = f"{C_GREEN}{l_raw}{C_RESET}{' '*pad}{C_YELLOW}{r_raw}"
    print(f"{C_CYAN}║{C_RESET}{line1}{C_CYAN}║{C_RESET}")
    
    # Line 2: Net Worth
    n_raw = f" Net Worth:   ${net_worth:,.2f}"
    
    # Removed the rogue leading space here too
    line2 = f"{C_WHITE}{n_raw}{' '*(INNER_WIDTH-len(n_raw))}"
    print(f"{C_CYAN}║{C_RESET}{line2}{C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}{mid_edge}{C_RESET}")
    
    # Categories
    for cat in CATEGORIES:
        if plugins[cat]:
            c_raw = f" [ {cat.upper()} ]"
            print(f"{C_CYAN}║{C_RESET}{C_PURPLE}{c_raw}{' '*(INNER_WIDTH-len(c_raw))}{C_RESET}{C_CYAN}║{C_RESET}")
            for p in plugins[cat]:
                p_raw = f"   [{p['id']}] {p['name']}"
                print(f"{C_CYAN}║{C_RESET}{C_WHITE}{p_raw}{' '*(INNER_WIDTH-len(p_raw))}{C_RESET}{C_CYAN}║{C_RESET}")
            print(f"{C_CYAN}║{' '*INNER_WIDTH}║{C_RESET}")

    q_raw = " [Q] Disconnect"
    print(f"{C_CYAN}║{C_RESET}{C_DARK}{q_raw}{' '*(INNER_WIDTH-len(q_raw))}{C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}{bot_edge}{C_RESET}")

def main():
    if os.name == 'nt': os.system('') 
    boot_sequence()
    balance = load_balance() 
    
    while True:
        port_val = get_portfolio_value()
        plugins, menu_map = scan_plugins()
        draw_lobby(balance, port_val, plugins)
        
        choice = input(f"\nAction: ").strip().lower()
        
        if choice == 'q':
            save_balance(balance)
            shutdown_animation(balance, port_val)
            sys.exit(0)
        elif choice in ['bankrupt', 'wipe']:
            if os.path.exists('funds-bankrupt.py'):
                balance = run_plugin('funds-bankrupt.py', balance)
                save_balance(balance)
        elif choice in menu_map:
            balance = run_plugin(menu_map[choice], balance)
            save_balance(balance)
        else:
            print(f"{C_RED}Invalid Protocol.{C_RESET}"); time.sleep(0.5)

if __name__ == "__main__":
    main()
