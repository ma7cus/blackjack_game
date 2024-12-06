from deck_architecture import Deck, Card, Hand
from GUI_architecture import BlackjackUI

class Blackjack_Hand:
    def __init__(self,deck,ui):
        self.deck = deck
        self.ui = ui
        self.dealer_hand = Hand()  # Hand object to store dealer's cards
        self.player_hand = Hand()  # Hand object to store player's cards
        self.player_turn_over = False  # Track if the player's turn is over
        self.hand_over = False

    def reset_hand(self):
        # Reset player and dealer hands using the reset method in Hand
        self.dealer_hand.reset()
        self.player_hand.reset()
        self.player_turn_over = False
        self.hand_over = False

    def update_hand_values_in_ui(self):
        """ 
        Updates the player and dealer hand values in the UI.
        """
        # Determine if player is standing based on player_turn_over flag
        player_standing = self.player_turn_over

        # Player's hand value
        player_total_str = self.player_hand.display_score_string(reveal_cards=True, standing=player_standing)

        # Determine if dealer is standing based on hand_over and card reveal status
        dealer_revealed = all(card.revealed for card in self.dealer_hand.cards)
        dealer_standing = self.hand_over and dealer_revealed
        dealer_total_str = self.dealer_hand.display_score_string(reveal_cards=dealer_revealed, standing=dealer_standing)

        # Update the UI with the formatted totals
        self.ui.update_hand_values(player_total_str, dealer_total_str, dealer_revealed)



    def update_ui(self):
        # Update the UI to reflect the current hands
        self.ui.update_player(self.player_hand.cards)
        self.ui.update_dealer(self.dealer_hand.cards)

        # Also update the hand values in the UI
        self.update_hand_values_in_ui()  


    def display_hand(self, hand, owner, standing=False):
        """
        Display the hand of a player or dealer in the terminal.
        Args:
            hand (Hand): The player's or dealer's hand.
            owner (str): The owner of the hand (Player or Dealer).
            standing (bool): Whether the player or dealer is standing.
        """
        if len(hand.cards) < 2:
            return

        # Determine if we should reveal the cards or keep them hidden
        reveal_cards = (owner == "Player" or all(card.revealed for card in hand.cards))
    
        # Generate card strings and totals based on standing status
        cards_str = hand.get_deckstring(reveal_cards=reveal_cards)
        total_str = hand.display_score_string(reveal_cards=reveal_cards, standing=standing)

        print(f"{owner}'s Hand: [{cards_str}] - Total: {total_str}")


    def deal_card_to_player(self,print_to_terminal=True):
        
        if self.player_turn_over:
            raise ValueError("Player trying to be dealt to after turn end")
        
        # Deal a new card to the player, always revealed
        new_card = self.deck.deal_card()
        new_card.revealed = True
        self.player_hand.add_card(new_card)

        if print_to_terminal:
            self.display_hand(self.player_hand, "Player")
            self.display_hand(self.dealer_hand, "Dealer")
            print(" ")

        self.update_ui()
        

    def deal_card_to_dealer(self,revealed=True,print_to_terminal=True):
        
        if self.hand_over:
            raise ValueError("Dealer trying to be dealt to after hand end")
        
        new_card = self.deck.deal_card()

        if revealed:    
            new_card.revealed = True
        else:
            new_card.revealed = False

        self.dealer_hand.add_card(new_card)

        if print_to_terminal:
            self.display_hand(self.player_hand, "Player")
            self.display_hand(self.dealer_hand, "Dealer")
            print(" ")

        self.update_ui()

    def deal_initial_hands(self):
        # Deal two cards to the player
        for i in range(2):
            self.deal_card_to_player(print_to_terminal=False)
            if i == 1:
                self.deal_card_to_dealer(revealed=False,print_to_terminal=True)
            else:
                self.deal_card_to_dealer(revealed=True,print_to_terminal=False)
        
        self.ui.player_display.enable_buttons()
        

    def player_stands(self):
        """
        Handle the player's decision to stand.
        """        
        print(f"Player stands on {self.player_hand.total()}")
        self.player_turn_over = True

        self.display_hand(self.player_hand, "Player", standing=True)
        self.update_ui() 

        self.dealer_play()
        

    def check_bust(self):
        """
        Check if the player's hand has gone bust using the existing `is_bust()` method.
        """
        if self.player_hand.is_bust():
            print(f"Player busts at {self.player_hand.hard_total()}")
            print(" ")
            self.player_turn_over = True
            self.dealer_play()
            
            
    def dealer_play(self):
        """
        Dealer's turn to play after player stands or goes bust.
        Dealer hits until reaching at least a hard 17.
        """
        if not self.player_turn_over:
            raise ValueError("Dealer trying to play before player turn end")
        elif self.hand_over:
            raise ValueError("Dealer trying to play after hand end")
            
        print(f"Dealer's turn begins at {self.dealer_hand.total()}")
        print("")
        
        self.reveal_dealer_cards()
        self.dealer_turn_step()

    def determine_winner(self):
        if self.hand_over:
            if self.player_hand.is_bust():
                if self.dealer_hand.is_bust():
                    print(f"Draw: Player busts on {self.player_hand.hard_total()}, Dealer busts on {self.dealer_hand.hard_total()}")
                else:
                    print(f"Player loses: Player busts on {self.player_hand.hard_total()}, Dealer stands on {self.dealer_hand.total()}")
            elif self.dealer_hand.is_bust():
                print(f"Player wins: Player stands on {self.player_hand.total()}, Dealer busts on {self.dealer_hand.hard_total()}")
            elif self.player_hand.total() < self.dealer_hand.total():
                print(f"Player loses: Player stands on {self.player_hand.total()}, Dealer stands on {self.dealer_hand.total()}")
            elif self.player_hand.total() > self.dealer_hand.total():
                print(f"Player wins: Player stands on {self.player_hand.total()}, Dealer stands on {self.dealer_hand.total()}")
            else:
                print(f"Draw: Player stands on {self.player_hand.total()}, Dealer stands on {self.dealer_hand.total()}")

    def dealer_turn_step(self):
        """
        Execute one step of the dealer's play sequence.
        """
        # Calculate current dealer's hard total
        hard_total = self.dealer_hand.hard_total()

        # Dealer stands if total is > 17 or exactly 17 and not soft
        if self.dealer_hand.is_bust():
            print(f"Dealer busts at {hard_total}")
            self.hand_over = True
            self.determine_winner()
            self.update_ui()
            return
        elif hard_total > 17 or (hard_total == 17 and not self.dealer_hand.is_soft()):
            print(f"Dealer stands on {hard_total}")
            self.hand_over = True
            self.display_hand(self.dealer_hand, "Dealer", standing=True)
            self.determine_winner()
            self.update_ui()
            return

        # Dealer hits if the total is <= 17 or is a soft 17
        self.deal_card_to_dealer(revealed=True)
        self.update_ui()

        # Schedule the next step in the dealer's turn after a short delay
        self.ui.root.after(1000, self.dealer_turn_step)

    def reveal_dealer_cards(self):
        # Reveal all dealer cards at the end of the game
        for card in self.dealer_hand.cards:
            card.reveal()
        self.update_ui()
    
    def is_hand_over(self):
        return self.hand_over

    def play_hand(self):
        # Play a new hand
        self.reset_hand()
        self.deal_initial_hands()
        self.update_ui()

class Blackjack_Game:
    def __init__(self):
        self.deck = Deck(decks=6)  # Standard 6-deck shoe
        self.ui = BlackjackUI(self)
        self.current_hand = None
        self.round_number = 1 

    def new_hand(self):
        if self.deck.should_shuffle():
            self.deck.new_deck()
    
        self.current_hand = Blackjack_Hand(self.deck, self.ui)
        print("\n" + "=" * 50)
        print(f"Starting Hand {self.round_number}")
        print("=" * 50 + "\n")
        self.current_hand.play_hand()

        self.round_number += 1

    def play(self):
        # Start the first hand
        self.new_hand()
        self.ui.mainloop()


