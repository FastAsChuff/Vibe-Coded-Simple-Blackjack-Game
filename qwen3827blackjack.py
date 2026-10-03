# 'Vibe Coded' Simple Blackjack game playable from the command line.
# Generated using qwen3.8:27b Q4_K_M using prompt "Write a Python program that plays a Blackjack card game from the command line."
# 2 lines had erroneous code removed.
# Blackjack winnings weren't always calculated correctly. Also, floating point errors fixed.
# Made to end when player runs out of chips without asking if player wants to continue.
# Otherwise, as was generated.

import random
import os
import sys

# ──────────────────────────────────────────────
#  Card & Deck
# ──────────────────────────────────────────────

SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]


def card_value(rank: str) -> int:
    """Return the point value of a card rank."""
    if rank in ("J", "Q", "K"):
        return 10
    if rank == "A":
        return 1  # Ace base value; Hand handles the +10 option
    return int(rank)


def make_deck():
    """Create and shuffle a standard 52-card deck."""
    deck = [(s, r) for s in SUITS for r in RANKS]
    random.shuffle(deck)
    return deck


def format_card(suit: str, rank: str) -> str:
    return f"{rank}{suit}"


# ──────────────────────────────────────────────
#  Hand
# ──────────────────────────────────────────────

class Hand:
    def __init__(self):
        self.cards: list[tuple[str, str]] = []

    def add(self, suit: str, rank: str):
        self.cards.append((suit, rank))

    def clear(self):
        self.cards.clear()

    @property
    def value(self) -> int:
        """Best total (Ace counts as 11 if it doesn't bust)."""
        total = sum(card_value(r) for _, r in self.cards)
        aces = sum(1 for _, r in self.cards if r == "A")
        # Upgrade aces from 1 → 11 while we don't bust
        while aces > 0 and total + 10 <= 21:
            total += 10
            aces -= 1
        return total

    @property
    def is_bust(self) -> bool:
        return self.value > 21

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.value == 21

    def __repr__(self) -> str:
        return " + ".join(format_card(s, r) for s, r in self.cards)


# ──────────────────────────────────────────────
#  Display helpers
# ──────────────────────────────────────────────

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    banner = r"""
    _   _  ___  ____
   / \ / /  / _ \/ __/
  / _ \ /  /  __/\ \
 / ___ \ / / |___/___/
/_/  \_// /_____/____/
     |__/  Blackjack
    """
    print(banner)


def show_hand(label: str, hand: Hand, hide_first=False):
    if hide_first:
        hidden = format_card(*hand.cards[0])
        rest = " + ".join(format_card(s, r) for s, r in hand.cards[1:])
        print(f"  {label:>6s}:  {hidden} (hidden) + {rest}   [{hand.value - card_value(hand.cards[0][1]) + 1 if hand.cards[0][1]=='A' else hand.value - card_value(hand.cards[0][1])}]")
        # simpler: just show "X + cards..."
        print(f"  {label:>6s}:  ? + {rest}   [?]")
    else:
        print(f"  {label:>6s}:  {hand}")


def print_separator():
    print("  " + "─" * 46)


# ──────────────────────────────────────────────
#  Game logic
# ──────────────────────────────────────────────

def play_hand(player: Hand, dealer: Hand, deck: list) -> str:
    """
    Run a single round.  Returns: 'win', 'lose', 'push', or 'blackjack'.
    """
    # Deal
    for _ in range(2):
        player.add(*deck.pop())
        dealer.add(*deck.pop())

    # Check for immediate blackjacks
    player_bj = player.is_blackjack
    dealer_bj = dealer.is_blackjack

    if player_bj or dealer_bj:
        # Reveal dealer
        if player_bj and not dealer_bj:
            return "blackjack"
        elif dealer_bj and not player_bj:
            return "lose"
        else:
            return "push"

    # ── Player's turn ──
    while True:
        show_hand("Dealer", Hand().add(dealer.cards[0][0], 
dealer.cards[0][1]))
        show_hand("You", player)
        print()
        choice = input("  Hit (h) or Stand (s)? ").strip().lower()
        if choice == "s":
            break
        if choice in ("h", "hit", ""):
            player.add(*deck.pop())
            if player.is_bust:
                return "lose"
        else:
            print("  Invalid input – defaulting to Hit.")
            player.add(*deck.pop())
            if player.is_bust:
                return "lose"

    # ── Dealer's turn (hit until 17) ──
    while dealer.value < 17:
        dealer.add(*deck.pop())

    if dealer.is_bust:
        return "win"
    if player.value > dealer.value:
        return "win"
    if player.value < dealer.value:
        return "lose"
    return "push"


# ──────────────────────────────────────────────
#  Main game loop
# ──────────────────────────────────────────────

def main():
    print_banner()

    chips = 100
    round_num = 0

    while True:
        print_separator()
        print(f"  Round {round_num + 1}    Chips: {chips}")
        print_separator()

        if chips <= 0:
            print("\n  You're broke!  Game over.\n")
            sys.exit(0)

        # ── Betting ──
        while True:
            bet_input = input(f"  Place your bet (1-{chips}) [default 10]: ").strip()
            if bet_input == "":
                bet = min(10, chips)
            else:
                try:
                    bet = int(bet_input)
                except ValueError:
                    print("  Invalid number.")
                    continue
            if 1 <= bet <= chips:
                break
            print(f"  Bet must be between 1 and {chips}.")

        # ── Build deck (reshuffle if < 15 cards left) ──
        deck = make_deck()

        player = Hand()
        dealer = Hand()

        result = play_hand(player, dealer, deck)

        # ── Reveal & settle ──
        print()
        print_separator()
        show_hand("Dealer", dealer)
        show_hand("You", player)
        print_separator()

        if result == "blackjack":
            winnings = int((3 * bet) // 2)  # 3:2 payout → total = bet + 1.5*bet
            chips += winnings
            print(f"\n  🎉 BLACKJACK!  You win {winnings} chips.  (Total: {chips})")
        elif result == "win":
            chips += bet
            print(f"\n  ✅ You win!  +{bet} chips.  (Total: {chips})")
        elif result == "lose":
            chips -= bet
            print(f"\n  ❌ Dealer wins.  -{bet} chips.  (Total: {chips})")
        else:  # push
            print(f"\n  ⚖️  Push.  Bet returned.  (Total: {chips})")

        print()
        if chips > 0:
          again = input("  Play again?  (y/n) [y]: ").strip().lower()
          if again == "n":
              break
        round_num += 1

    print(f"\n  Final chips: {chips}\n  Thanks for playing!\n")


# ──────────────────────────────────────────────
if __name__ == "__main__":
    main()
