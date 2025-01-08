from deck_architecture import Deck, Card, Hand
from GUI_architecture import BlackjackUI

class Blackjack_Hand:
    def __init__(self,deck,ui):
        self.deck = deck
        self.ui = ui
        self.dealer_card_set = Hand()  # Hand object to store dealer's cards
        self.player_card_sets = [Hand()] #Start with an empty set of 1 hand

        self.player_hand_turn_over = [False] #Track which of the player's hands' turns are over

        self.player_turn_over = False  # Track if the player's turn is over for all hands
        self.round_over = False #Track if the player and dealer turns are both over

    def reset_hand(self):
        # Reset player and dealer hands using the reset method in Hand
        self.dealer_card_set.reset() #Reset the dealer's hand
        self.player_card_sets = [Hand()] #Reset any number of hands back to a standard 1 new hand object
        self.player_hand_turn_over = [False]

        self.player_turn_over = False
        self.round_over = False

        self.ui.reset_player_windows()

    def num_hands(self):
        """Return the number of hands currently in play."""
        return len(self.player_card_sets)
    
    def update_card_set_values_in_ui(self):
        """ 
        Updates the player and dealer hand values in the UI.
        """
        # Determine if player is standing based on player_turn_over flag
        player_standing = self.player_turn_over

        # Player's card sets values
        player_totals_str_set = []
        for card_set in self.player_card_sets:
            score_string = card_set.display_score_string(reveal_cards=True, standing=self.player_turn_over)
            player_totals_str_set.append(score_string)

        # Determine if dealer is standing based on round_over and card reveal status
        dealer_revealed = all(card.revealed for card in self.dealer_card_set.cards)
        dealer_standing = self.round_over and dealer_revealed
        dealer_total_str = self.dealer_card_set.display_score_string(reveal_cards=dealer_revealed, standing=dealer_standing)

        # Update the UI with the formatted totals
        self.ui.update_hand_values()

    def update_ui(self):
        # Update the UI to reflect the current hands
        for card_set in self.player_card_sets:
            self.ui.update_player()

        self.ui.update_dealer()

        # Also update the hand values in the UI
        self.update_card_set_values_in_ui()  


    def display_card_set(self, card_set, owner, standing=False):
        """
        Display the hand of a player or dealer in the terminal.
        Args:
            hand (Hand): The player's or dealer's hand.
            owner (str): The owner of the hand (Player or Dealer).
            standing (bool): Whether the player or dealer is standing.
        """
        if len(card_set.cards) < 2:
            return

        # Determine if we should reveal the cards or keep them hidden
        reveal_cards = ("Player" in owner or all(card.revealed for card in card_set.cards))
    
        # Generate card strings and totals based on standing status
        cards_str = card_set.get_deckstring(reveal_cards=reveal_cards)
        total_str = card_set.display_score_string(reveal_cards=reveal_cards, standing=standing)

        if standing:
            print(f"{owner}'s Hand: [{cards_str}] - Total: {total_str} (Standing)")
        else:
            print(f"{owner}'s Hand: [{cards_str}] - Total: {total_str}")

    def display_card_sets(self):
        for i, hand in enumerate(self.player_card_sets):
                standing = self.player_hand_turn_over[i]
                self.display_card_set(hand,f"Player Hand {i+1}",standing=standing)
            
        self.display_card_set(self.dealer_card_set, "Dealer")
        print(" ")

    def deal_card_to_player(self,hand_index = 0, print_to_terminal=True):
        
        if self.player_turn_over:
            raise ValueError("Player trying to be dealt to after turn end")
        
        # Deal a new card to the player, always revealed
        new_card = self.deck.deal_card()
        new_card.revealed = True
        self.player_card_sets[hand_index].add_card(new_card)    

        if print_to_terminal:
            self.display_card_sets()

        self.update_ui()
        

    def deal_card_to_dealer(self,revealed=True,print_to_terminal=True):
        
        if self.round_over:
            raise ValueError("Dealer trying to be dealt to after hand end")
        
        new_card = self.deck.deal_card()

        if revealed:    
            new_card.revealed = True
        else:
            new_card.revealed = False

        self.dealer_card_set.add_card(new_card)

        if print_to_terminal:
            self.display_card_sets()

        self.update_ui()

    def deal_initial_hands(self):
        """Deal two cards to each player's hand and one to the dealer."""
        for i in range(2):
            self.deal_card_to_player(0, print_to_terminal=False)

            if i == 1:
                self.deal_card_to_dealer(revealed=False,print_to_terminal=True)
            else:
                self.deal_card_to_dealer(revealed=True,print_to_terminal=False)

        self.ui.update_player()
        self.ui.update_dealer()

        self.ui.player_displays[0].enable_buttons()

        

    def player_stands(self, hand_index = 0):
        """
        Handle the player's decision to stand.
        """        
        print(f"Player stands on hand {hand_index+1} with {self.player_card_sets[hand_index].total()}")
        self.player_hand_turn_over[hand_index] = True
        self.display_card_sets()
        self.update_ui() 

        if all(self.player_hand_turn_over):
            self.player_turn_over = True
            self.dealer_play()
    
    def can_split(self, hand_index=0):
        """Check if the specified hand can be split."""
        return self.player_card_sets[hand_index].is_pair()

    def split_hand(self, hand_index):
        """Split the specified hand."""
        if self.can_split(hand_index):
            # Create a new hand for the second card
            new_hand = Hand()
            new_hand.add_card(self.player_card_sets[hand_index].cards.pop())
            self.player_card_sets.append(new_hand)
            self.player_hand_turn_over.append(False)

            # Notify the UI to add a new window for the new hand
            new_hand_index = len(self.player_card_sets) - 1
            self.ui.add_player_window(new_hand_index)

            # Update hand values for both hands
            self.ui.player_displays[hand_index].update_hand_values(self.player_card_sets[hand_index].total(), self.dealer_card_set.total(), dealer_revealed=False)
            self.ui.player_displays[new_hand_index].update_hand_values(new_hand.total(), self.dealer_card_set.total(), dealer_revealed=False)

            print(f"Split performed on Hand {hand_index + 1}")     

    def check_bust(self, hand_index = 0):
        """
        Check if the player's hand has gone bust using the existing `is_bust()` method.
        """
        if self.player_card_sets[hand_index].is_bust():
            print(f"Player hand {hand_index + 1} busts at {self.player_card_sets[hand_index].hard_total()}")
            print(" ")
            self.player_hand_turn_over[hand_index] = True
            
            if all(self.player_hand_turn_over):
                self.player_turn_over = True
                self.dealer_play()
            
            
    def dealer_play(self):
        """
        Dealer's turn to play after player stands or goes bust.
        Dealer hits until reaching at least a hard 17.
        """
        if not self.player_turn_over:
            raise ValueError("Dealer trying to play before player turn end")
        elif self.round_over:
            raise ValueError("Dealer trying to play after hand end")
            
        print(f"Dealer's turn begins at {self.dealer_card_set.total()}")
        print("")
        
        self.reveal_dealer_cards()
        self.dealer_turn_step()

    def determine_winner(self):
        """
        Determine the result for each player hand (win/lose/draw) against the dealer.
        """
        if self.round_over:
            for i, player_hand in enumerate(self.player_card_sets):
                # Player's hand identifier for output
                if i==0 and len(self.player_card_sets) == 1:
                    hand_label = "Player Hand"
                else:
                    hand_label = f"Player Hand {i+1}"

                # Check if the player's hand is a bust
                if player_hand.is_bust():
                    if self.dealer_card_set.is_bust():
                        print(f"Draw: {hand_label} busts on {player_hand.hard_total()}, Dealer busts on {self.dealer_card_set.hard_total()}")
                    else:
                        print(f"{hand_label} loses: Busts on {player_hand.hard_total()}, Dealer stands on {self.dealer_card_set.total()}")
                elif self.dealer_card_set.is_bust():
                    # Dealer busts, player wins
                    print(f"{hand_label} wins: Stands on {player_hand.total()}, Dealer busts on {self.dealer_card_set.hard_total()}")
                elif player_hand.total() < self.dealer_card_set.total():
                    # Dealer has higher total, player loses
                    print(f"{hand_label} loses: Stands on {player_hand.total()}, Dealer stands on {self.dealer_card_set.total()}")
                elif player_hand.total() > self.dealer_card_set.total():
                    # Player has higher total, player wins
                    print(f"{hand_label} wins: Stands on {player_hand.total()}, Dealer stands on {self.dealer_card_set.total()}")
                else:
                    # Totals are equal, it's a draw
                    print(f"Draw: {hand_label} stands on {player_hand.total()}, Dealer stands on {self.dealer_card_set.total()}")


    def dealer_turn_step(self):
        """
        Execute one step of the dealer's play sequence.
        """
        # Calculate current dealer's hard total
        hard_total = self.dealer_card_set.hard_total()

        # Dealer stands if total is > 17 or exactly 17 and not soft
        if self.dealer_card_set.is_bust():
            print(f"Dealer busts at {hard_total}")
            self.round_over = True
            self.determine_winner()
            self.update_ui()
            return
        elif hard_total > 17 or (hard_total == 17 and not self.dealer_card_set.is_soft()):
            print(f"Dealer stands on {hard_total}")
            self.round_over = True
            self.display_card_set(self.dealer_card_set, "Dealer", standing=True)
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
        for card in self.dealer_card_set.cards:
            card.reveal()
        self.update_ui()
    
    def is_round_over(self):
        return self.round_over

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
