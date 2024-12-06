from deck_architecture import Deck, Card, Hand
from GUI_architecture import BlackjackUI

class Blackjack_Hand:
    def __init__(self,deck,ui,is_split_hand=False):
        self.deck = deck
        self.ui = ui
        self.dealer_hand = Hand()  # Hand object to store dealer's cards
        self.player_hands = [Hand()]  # Hand object to store player's cards
        self.player_turn_over = [False]  # Track if the player's turn is over
        self.hand_over = False

    def split_hand(self, hand_index):
        """
        Perform a split on the given hand by index.
        """
        if len(self.player_hands) >= 2:  # Limit to one split for now, can be extended easily
            raise ValueError("Maximum number of splits reached.")

        original_hand = self.player_hands[hand_index]

        if not original_hand.is_pair():
            raise ValueError("Attempted to split a hand that isn't a pair.")

        # Create two new hands from the original hand by splitting its cards
        first_card = original_hand.cards[0]
        second_card = original_hand.cards[1]

        original_hand.reset()  # Clear the original hand
        original_hand.add_card(first_card)  # Add the first card back to the original hand

        new_hand = Hand()  # Create a new hand for the split
        new_hand.add_card(second_card)  # Add the second card to the new hand

        self.player_hands.insert(hand_index + 1, new_hand)  # Add the new hand next to the original
        self.player_turn_over.insert(hand_index + 1, False)

        # Update the UI to display the new player window for the split hand
        self.ui.add_split_player_window(new_hand)

        # Deal one additional card to each split hand using existing deal_card_to_player function
        self.deal_card_to_player(hand_index)
        self.deal_card_to_player(hand_index + 1)


    def offer_split(self):
        """
        Check if splitting is possible for the current hand and enable the split button in the UI.
        """
        main_hand = self.player_hands[0]
        if main_hand.is_pair() and len(self.player_hands) == 1:  # Only offer split if there's a single hand
            self.ui.player_display.enable_split_button()
            
    def reset_hand(self):
        """
        Reset player and dealer hands using the reset method in Hand.
        """
        self.dealer_hand.reset()
        for hand in self.player_hands:
            hand.reset()
        self.player_turn_over = [False] * len(self.player_hands)
        self.hand_over = False


    def update_hand_values_in_ui(self):
        """
        Updates the player and dealer hand values in the UI.
        """
        for index, hand in enumerate(self.player_hands):
            player_standing = self.player_turn_over[index]
            player_total_str = hand.display_score_string(reveal_cards=True, standing=player_standing)
            self.ui.update_player_hand_value(player_total_str, hand_index=index)
    
        # Determine if dealer is standing based on hand_over and card reveal status
        dealer_revealed = all(card.revealed for card in self.dealer_hand.cards)
        dealer_standing = self.hand_over and dealer_revealed
        dealer_total_str = self.dealer_hand.display_score_string(reveal_cards=dealer_revealed, standing=dealer_standing)
        self.ui.update_dealer_hand_value(dealer_total_str, dealer_revealed)

    def update_ui(self):
        """
        Update the UI to reflect the current state of all player hands.
        """
        for index, hand in enumerate(self.player_hands):
            self.ui.update_player(hand.cards, hand_index=index)
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


    def deal_card_to_player(self, hand_index, print_to_terminal=True):
        if hand_index >= len(self.player_hands):
            raise ValueError("Invalid hand index.")

        new_card = self.deck.deal_card()
        new_card.revealed = True
        self.player_hands[hand_index].add_card(new_card)

        if print_to_terminal:
            for idx, hand in enumerate(self.player_hands):
                self.display_hand(hand, f"Player Hand {idx+1}")
            self.display_hand(self.dealer_hand, "Dealer")
            print(" ")

        self.update_ui()


    def deal_card_to_dealer(self, revealed=True, print_to_terminal=True):
        if self.hand_over:
            raise ValueError("Dealer trying to be dealt to after hand end")
    
        new_card = self.deck.deal_card()

        if revealed:    
            new_card.revealed = True
        else:
            new_card.revealed = False

        self.dealer_hand.add_card(new_card)

        if print_to_terminal:
            # Display all player hands
            for idx, hand in enumerate(self.player_hands):
                self.display_hand(hand, f"Player Hand {idx + 1}")

            # Display dealer hand
            self.display_hand(self.dealer_hand, "Dealer")
            print(" ")

        self.update_ui()


    def deal_initial_hands(self):
        """
        Deal initial cards to all player hands and the dealer.
        """
        for i in range(2):
            for hand_index in range(len(self.player_hands)):
                self.deal_card_to_player(hand_index, print_to_terminal=False)
            if i == 1:
                self.deal_card_to_dealer(revealed=False, print_to_terminal=True)
            else:
                self.deal_card_to_dealer(revealed=True, print_to_terminal=False)

        # Enable buttons for each player hand window
        for player_display in self.ui.player_displays:
            player_display.enable_buttons()


    def player_stands(self, hand_index):
        """
        Handle the player's decision to stand for a specific hand.
        """
        if hand_index >= len(self.player_hands):
            raise ValueError("Invalid hand index.")

        print(f"Player stands on {self.player_hands[hand_index].total()}")
        self.player_turn_over[hand_index] = True

        self.display_hand(self.player_hands[hand_index], f"Player Hand {hand_index+1}", standing=True)
        self.update_ui()

        # Check if all hands are complete before moving to dealer
        if all(self.player_turn_over):
            self.dealer_play()


    def check_bust(self, hand_index):
        """
        Check if a specific player's hand has gone bust.
        """
        if hand_index >= len(self.player_hands):
            raise ValueError("Invalid hand index.")

        if self.player_hands[hand_index].is_bust():
            print(f"Player Hand {hand_index+1} busts at {self.player_hands[hand_index].hard_total()}")
            print(" ")
            self.player_turn_over[hand_index] = True

            # If all hands are complete, move to dealer play
            if all(self.player_turn_over):
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


