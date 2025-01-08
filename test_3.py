from game_architecture import Blackjack_Hand
from deck_architecture import Deck, Card, Hand

# Mock UI for testing
class MockRoot:
    def after(self, delay, callback):
        print(f"Simulating root.after with delay {delay}ms")
        callback()

class MockUI:
    def __init__(self):
        self.root = MockRoot()

    def update_player(self, hands):
        print(f"MockUI: Player hands: {[hand.get_deckstring() for hand in hands]}")

    def update_dealer(self, cards):
        print(f"MockUI: Dealer cards: {[card.get_cardname() for card in cards]}")

# Initialise Blackjack_Hand with a mock UI
mock_ui = MockUI()
blackjack_hand = Blackjack_Hand(deck=Deck(), ui=mock_ui)

# Add a pair to the first hand for splitting
blackjack_hand.player_hands[0].add_card(Card("8", "Hearts"))
blackjack_hand.player_hands[0].add_card(Card("8", "Clubs"))

# Display the initial hand
print("Before splitting:")
blackjack_hand.update_ui()

# Split the hand
blackjack_hand.split_hand()

# Play both hands
for _ in blackjack_hand.player_hands:
    blackjack_hand.deal_card_to_player()
    blackjack_hand.player_stands()

# Dealer phase should start automatically in player_stands, so no explicit dealer_play here
# Debugging information will show the transition from player to dealer phase
print("End of round.")
