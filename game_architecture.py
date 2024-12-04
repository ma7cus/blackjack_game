from deck_architecture import Deck, Card
from GUI_architecture import BlackjackUI

class Blackjack_Game:
    def __init__(self):
        self.deck = Deck()  # Initialize a deck of cards
        self.ui = BlackjackUI()  # Initialize the UI
        self.dealer_hand = []  # List to store dealer's cards
        self.player_hand = []  # List to store player's cards

    def update_ui(self):
        # Update the UI to reflect the current hands
        self.ui.update_player(self.player_hand)
        self.ui.update_dealer(self.dealer_hand)

    def deal_card_to_player(self):
        # Deal a new card to the player, always revealed
        new_card = self.deck.deal_card()
        new_card.revealed = True
        self.player_hand.append(new_card)
        self.update_ui()

    def deal_card_to_dealer(self,revealed=True):
        
        new_card = self.deck.deal_card()

        if revealed:    
            new_card.revealed = True
        else:
            new_card.revealed = False

        self.dealer_hand.append(new_card)
        self.update_ui()

    def deal_initial_hands(self):
        # Deal two cards to the player
        for i in range(2):
            self.deal_card_to_player()
            if i == 1:
                self.deal_card_to_dealer(revealed=False)
            else:
                self.deal_card_to_dealer()
    
    def reveal_dealer_cards(self):
        # Reveal all dealer cards at the end of the game
        for card in self.dealer_hand:
            card.revealed = True
        self.update_ui(reveal_dealer=True)

    def play(self):
        # Deal initial hands
        self.deal_initial_hands()
        self.update_ui() 
