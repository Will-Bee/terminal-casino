import os
import time
import random
import sys
import re

# --- UI Helpers ---
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Deck Configuration ---
SUITS = [
    ('\033[31m♥\033[0m', 'red', 'Hearts'), 
    ('\033[31m♦\033[0m', 'red', 'Diamonds'), 
    ('\033[97m♣\033[0m', 'black', 'Clubs'), 
    ('\033[97m♠\033[0m', 'black', 'Spades')
]
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}

def create_and_shuffle_deck(num_decks=6):
    """Creates a fresh, sorted shoe of cards and shuffles it randomly."""
    deck = []
    for _ in range(num_decks):
        for suit_icon, suit_color, suit_name in SUITS:
            for rank in RANKS:
                deck.append({
                    'rank': rank,
                    'suit_icon': suit_icon,
                    'suit_color': suit_color,
                    'suit_name': suit_name,
                    'value': VALUES[rank]
                })
    
    # Real random shuffle before the game
    random.shuffle(deck)
    return deck

def format_hand(hand, hide_second=False):
    """Formats a list of card dictionaries into a printable string."""
    cards_str = []
    for i, card in enumerate(hand):
        if hide_second and i == 1:
            cards_str.append("[🂠 ?]")
        else:
            cards_str.append(f"[{card['rank']}{card['suit_icon']}]")
    return " ".join(cards_str)

def calculate_total(hand):
    """Calculates the best possible total for a hand, handling Aces."""
    total = sum(card['value'] for card in hand)
    aces = sum(1 for card in hand if card['rank'] == 'A')
    
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
        
    return total

# --- Side Bet Evaluators ---
def eval_perfect_pairs(hand):
    if hand[0]['rank'] != hand[1]['rank']:
        return 0, "No Pair"
    if hand[0]['suit_name'] == hand[1]['suit_name']:
        return 25, "Perfect Pair! (25:1)"
    if hand[0]['suit_color'] == hand[1]['suit_color']:
        return 12, "Colored Pair! (12:1)"
    return 5, "Mixed Pair! (5:1)"

def eval_21_plus_3(player_hand, dealer_upcard):
    cards = [player_hand[0], player_hand[1], dealer_upcard]
    ranks_in_hand = [c['rank'] for c in cards]
    suits_in_hand = [c['suit_name'] for c in cards]
    
    is_flush = len(set(suits_in_hand)) == 1
    is_three_of_a_kind = len(set(ranks_in_hand)) == 1
    
    # Check straight
    rank_indices = sorted([RANKS.index(r) for r in ranks_in_hand])
    is_straight = (rank_indices[2] - rank_indices[1] == 1 and rank_indices[1] - rank_indices[0] == 1)
    # Special case A-2-3
    if set(ranks_in_hand) == {'A', '2', '3'}:
        is_straight = True
        
    if is_three_of_a_kind and is_flush: return 100, "Suited Trips! (100:1)"
    if is_straight and is_flush: return 40, "Straight Flush! (40:1)"
    if is_three_of_a_kind: return 30, "Three of a Kind! (30:1)"
    if is_straight: return 10, "Straight! (10:1)"
    if is_flush: return 5, "Flush! (5:1)"
    
    return 0, "Loss"

# --- Main Game Loop ---
def play(balance):
    """Main entry point for Blackjack."""
    while True:
        bets = {'main': 0, 'pp': 0, '21p3': 0}
        
        # --- Betting Phase ---
        while True:
            clear_screen()
            total_active_bets = sum(bets.values())
            print("======================================================")
            print("                     🃏 BLACKJACK 🃏                  ")
            print("======================================================")
            print(f"💰 Balance: ${balance:,}")
            print(f"💵 Active Bets: ${total_active_bets:,}")
            print("======================================================")
            print(f"  [1] Main Bet       : ${bets['main']:,}")
            print(f"  [2] Perfect Pairs  : ${bets['pp']:,}")
            print(f"  [3] 21 + 3         : ${bets['21p3']:,}")
            print("------------------------------------------------------")
            print("  [D] DEAL CARDS! 🃏")
            print("  [Q] Return to Lobby")
            
            command = input("\nChoose an option or bet directly (e.g., '1 100'): ").strip().lower()
            
            if command == 'q':
                return balance + total_active_bets
            
            if command == 'd':
                if bets['main'] <= 0:
                    print("You must place a Main Bet to play!")
                    time.sleep(1.5)
                    continue
                break
                
            # Shortcut Parsing (e.g., "1 100")
            match = re.match(r'^([1-3])\s*(\d+)$', command)
            if match:
                option = int(match.group(1))
                amount = int(match.group(2))
                if amount <= 0 or amount > balance:
                    print("Invalid or insufficient bet amount.")
                    time.sleep(1)
                    continue
                    
                if option == 1: bets['main'] += amount
                elif option == 2: bets['pp'] += amount
                elif option == 3: bets['21p3'] += amount
                balance -= amount
                continue

            # Standard Menu
            if command in ['1', '2', '3']:
                try:
                    amt = int(input(f"Enter bet amount (Available: ${balance:,}): $"))
                    if amt <= 0 or amt > balance:
                        print("Invalid or insufficient balance!")
                        time.sleep(1)
                    else:
                        if command == '1': bets['main'] += amt
                        elif command == '2': bets['pp'] += amt
                        elif command == '3': bets['21p3'] += amt
                        balance -= amt
                except ValueError:
                    pass

        # --- Dealing Phase ---
        deck = create_and_shuffle_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        details = [] # Receipt details
        total_winnings = 0
        
        # Resolve Side Bets immediately
        if bets['pp'] > 0:
            multiplier, msg = eval_perfect_pairs(player_hand)
            if multiplier > 0:
                payout = bets['pp'] + (bets['pp'] * multiplier)
                total_winnings += payout
                details.append(f"  ✅ Perfect Pairs: ${bets['pp']:,} -> WON ${payout:,} ({msg})")
            else:
                details.append(f"  ❌ Perfect Pairs: ${bets['pp']:,} -> LOST")
                
        if bets['21p3'] > 0:
            multiplier, msg = eval_21_plus_3(player_hand, dealer_hand[0])
            if multiplier > 0:
                payout = bets['21p3'] + (bets['21p3'] * multiplier)
                total_winnings += payout
                details.append(f"  ✅ 21 + 3:        ${bets['21p3']:,} -> WON ${payout:,} ({msg})")
            else:
                details.append(f"  ❌ 21 + 3:        ${bets['21p3']:,} -> LOST")

        # --- Player Phase ---
        player_busted = False
        just_doubled = False
        
        while True:
            clear_screen()
            print("======================================================")
            print("                     🃏 BLACKJACK 🃏                  ")
            print("======================================================")
            print(f"🤵 Dealer's Hand: {format_hand(dealer_hand, hide_second=True)}")
            print(f"   Total: {dealer_hand[0]['value']}")
            print("------------------------------------------------------")
            print(f"👤 Your Hand:     {format_hand(player_hand)}")
            p_total = calculate_total(player_hand)
            print(f"   Total: {p_total}")
            print("======================================================")
            
            if p_total == 21 and len(player_hand) == 2:
                print("\n🌟 BLACKJACK! 🌟")
                time.sleep(2)
                break
            
            if p_total > 21:
                print("\n💥 BUSTED! You went over 21. 💥")
                player_busted = True
                time.sleep(2)
                break
                
            if just_doubled:
                time.sleep(1)
                break # Turn ends immediately after a double down
                
            print("\nOptions:")
            print("  [H] Hit")
            print("  [S] Stand")
            if len(player_hand) == 2 and balance >= bets['main']:
                print("  [D] Double Down")
                
            action = input("\nChoose action: ").strip().lower()
            
            if action == 'h':
                player_hand.append(deck.pop())
            elif action == 's':
                break
            elif action == 'd' and len(player_hand) == 2 and balance >= bets['main']:
                balance -= bets['main']
                bets['main'] *= 2
                player_hand.append(deck.pop())
                just_doubled = True
                
        # --- Dealer Phase ---
        dealer_total = calculate_total(dealer_hand)
        
        if not player_busted:
            clear_screen()
            print("======================================================")
            print("                 🤵 DEALER'S TURN 🤵                  ")
            print("======================================================")
            print(f"🤵 Dealer's Hand: {format_hand(dealer_hand)}")
            print(f"   Total: {dealer_total}")
            print("------------------------------------------------------")
            print(f"👤 Your Hand:     {format_hand(player_hand)}")
            print(f"   Total: {calculate_total(player_hand)}")
            print("======================================================")
            time.sleep(1.5)
            
            while dealer_total < 17:
                dealer_hand.append(deck.pop())
                dealer_total = calculate_total(dealer_hand)
                
                clear_screen()
                print("======================================================")
                print("                 🤵 DEALER HITS 🤵                  ")
                print("======================================================")
                print(f"🤵 Dealer's Hand: {format_hand(dealer_hand)}")
                print(f"   Total: {dealer_total}")
                print("------------------------------------------------------")
                print(f"👤 Your Hand:     {format_hand(player_hand)}")
                print(f"   Total: {calculate_total(player_hand)}")
                print("======================================================")
                time.sleep(1.5)

        # --- Final Evaluation Phase ---
        p_total = calculate_total(player_hand)
        d_total = calculate_total(dealer_hand)
        
        main_payout = 0
        if player_busted:
            details.append(f"  ❌ Main Bet:      ${bets['main']:,} -> LOST (Bust)")
        elif d_total > 21:
            main_payout = bets['main'] * 2
            details.append(f"  ✅ Main Bet:      ${bets['main']:,} -> WON ${main_payout:,} (Dealer Bust)")
        elif p_total == 21 and len(player_hand) == 2 and not (d_total == 21 and len(dealer_hand) == 2):
            main_payout = bets['main'] + int(bets['main'] * 1.5) # Blackjack pays 3:2
            details.append(f"  🌟 Main Bet:      ${bets['main']:,} -> WON ${main_payout:,} (BLACKJACK 3:2)")
        elif p_total > d_total:
            main_payout = bets['main'] * 2
            details.append(f"  ✅ Main Bet:      ${bets['main']:,} -> WON ${main_payout:,} (Player Wins)")
        elif p_total == d_total:
            main_payout = bets['main'] # Push returns original bet
            details.append(f"  🔄 Main Bet:      ${bets['main']:,} -> PUSH (Tie, bet returned)")
        else:
            details.append(f"  ❌ Main Bet:      ${bets['main']:,} -> LOST (Dealer Wins)")

        total_winnings += main_payout
        balance += total_winnings
        
        # --- Receipt ---
        print("\n  --- BET RECEIPT ---")
        for detail in details:
            print(detail)
        print("  -------------------")
        
        total_spent = sum(bets.values())
        net_result = total_winnings - total_spent
        
        print(f"  Total Payout : ${total_winnings:,}")
        if net_result > 0:
            print(f"  Net Profit   : \033[32m+${net_result:,}\033[0m")
        elif net_result < 0:
            print(f"  Net Loss     : \033[31m-${abs(net_result):,}\033[0m")
        else:
            print(f"  Net Result   : \033[33m$0 (Broke Even)\033[0m")
            
        print(f"\n======================================================")
        print(f"New Balance: ${balance:,}")
        
        again = input("\nPress Enter to play again, or 'Q' to return to lobby: ").strip().lower()
        if again == 'q':
            return balance

if __name__ == "__main__":
    play(10000)
