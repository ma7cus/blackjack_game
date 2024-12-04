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
        # Deal a new card to the player, always revealed
        new_card = self.deck.deal_card()
        new_card.revealed = True
        self.player_hand.add_card(new_card)
        self.update_ui()
        print(f"{new_card.__str__()} dealt to player, raising total to: {self.player_hand.total()}")

    def deal_card_to_dealer(self,revealed=True):
        
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

        print("Initial hands dealt")
    
    def player_stands(self):
        """
        Handle the player's decision to stand.
        """        
        print(f"Player stands on {self.player_hand.total()}")
        self.dealer_play()
        self.game_over = True

    def check_bust(self):
        """
        Check if the player's hand has gone bust using the existing `is_bust()` method.
        """
        if self.player_hand.is_bust():
            print(f"Player went bust at {self.player_hand.hard_total()}")
            self.dealer_play()
            self.game_over = True
            
    def dealer_play(self):
        """
        Dealer's turn to play after player stands or goes bust.
        Dealer hits until reaching at least a hard 17.
        """
        # Reveal dealer's hidden cards and update the UI initially
        print("Dealer's turn begins.")
        self.reveal_dealer_cards()
        self.dealer_turn_step()

    def dealer_turn_step(self):
        """
        Execute one step of the dealer's play sequence.
        """
        # Calculate current dealer's hard total
        hard_total = self.dealer_hand.hard_total()

        # Dealer stands if total is > 17 or exactly 17 and not soft
        if hard_total > 17 or (hard_total == 17 and not self.dealer_hand.is_soft()):
            print(f"Dealer stands with a total of: {hard_total}")
            self.update_ui()
            return

        # Dealer hits if the total is <= 17 or is a soft 17
        print("Dealer hits.")
        self.deal_card_to_dealer(revealed=True)
        self.update_ui()

        # Schedule the next step in the dealer's turn after a short delay
        self.ui.root.after(1000, self.dealer_turn_step)

    def reveal_dealer_cards(self):
        # Reveal all dealer cards at the end of the game
        for card in self.dealer_hand.cards:
            card.reveal()
        self.update_ui()

    def play(self):
        # Deal initial hands
        self.deal_initial_hands()
        self.update_ui() 

