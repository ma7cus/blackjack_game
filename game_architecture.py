from deck_architecture import Deck, Card, Hand
from GUI_architecture import BlackjackUI

class Blackjack_Game:
    def __init__(self):
        self.deck = Deck()  # Initialize a deck of cards
        self.ui = BlackjackUI(self)  # Initialize the UI
        self.dealer_hand = Hand()  # Hand object to store dealer's cards
        self.player_hand = Hand()  # Hand object to store player's cards
        self.game_over = False  # Track if the game is over

    def update_ui(self):
        # Update the UI to reflect the current hands
        self.ui.update_player(self.player_hand.cards)
        self.ui.update_dealer(self.dealer_hand.cards)

    def deal_card_to_player(self):

        if self.game_over:
            return
        
        # Deal a new card to the player, always revealed
        new_card = self.deck.deal_card()
        new_card.revealed = True
        self.player_hand.add_card(new_card)
        self.update_ui()

    def deal_card_to_dealer(self,revealed=True):

        if self.game_over:
            return
        
        new_card = self.deck.deal_card()

        if revealed:    
            new_card.revealed = True
        else:
            new_card.revealed = False

        self.dealer_hand.add_card(new_card)
        self.update_ui()

    def deal_initial_hands(self):
        # Deal two cards to the player
        for i in range(2):
            self.deal_card_to_player()
            if i == 1:
                self.deal_card_to_dealer(revealed=False)
            else:
                self.deal_card_to_dealer()
    
    def player_stands(self):
        """
        Handle the player's decision to stand.
        """
        if self.game_over:
            return
        
        print("Player stands. Dealer's turn begins.")
        self.reveal_dealer_cards()
        self.game_over = True
        print("Game over: Player stands.")

    def check_bust(self):
        """
        Check if the player's hand has gone bust using the existing `is_bust()` method.
        """
        if self.player_hand.is_bust():
            print("Player went bust! Game over.")
            self.game_over = True
            self.reveal_dealer_cards()  # Reveal dealer's cards at the end

    def reveal_dealer_cards(self):
        # Reveal all dealer cards at the end of the game
        for card in self.dealer_hand.cards:
            card.reveal()
        self.update_ui()


    def play(self):
        # Deal initial hands
        self.deal_initial_hands()
        self.update_ui() 
