from deck_architecture import Deck, Hand
from GUI_architecture import BlackjackUI

class Blackjack_Game:
    def __init__(self):
        self.deck = Deck(decks=6)
        self.player_hand = Hand()
        self.dealer_hand = Hand()
        self.ui = BlackjackUI()

    def deal_initial_hands(self):
        for _ in range(2):
            self.player_hand.add_card(self.deck.deal_card())
            self.dealer_hand.add_card(self.deck.deal_card())
        self.update_ui()

    def hit_player(self):
        self.player_hand.add_card(self.deck.deal_card())
        self.update_ui()

    def hit_dealer(self):
        self.dealer_hand.add_card(self.deck.deal_card())
        self.update_ui()

    def update_ui(self, reveal_dealer=False):
        dealer_card_names = [f"{card.suit.lower()}_{card.rank.lower()}" for card in self.dealer_hand.cards]
        player_card_names = [f"{card.suit.lower()}_{card.rank.lower()}" for card in self.player_hand.cards]

        self.ui.update_dealer(dealer_card_names, reveal_all = reveal_dealer)
        self.ui.update_player(player_card_names)

    def play(self):
        self.deal_initial_hands()
        self.hit_player()
        self.hit_player()
        self.hit_player()

        self.hit_dealer()
        self.hit_dealer()

        self.ui.mainloop()
