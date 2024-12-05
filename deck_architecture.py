import random
from tkinter import PhotoImage
from cairosvg import svg2png

class Card:
    """
    Represents the state of a single card, i.e:
    rank (str): The rank from set [2-10, Jack, Queen, King]
    suit (str): The suit from set [Hearts, Diamonds, Clubs, Spades]
    """
    
    def __init__(self,rank,suit):
        """
        Initialises a card with a given rank and suit and a status of either revealed or not
        """
        self.rank = rank
        self.suit = suit
        self.revealed = True #Initialise as revealed
    
    def value(self):
        """
        Returns the value of the card 
        """
        if self.rank.isdigit():
            return int(self.rank)
        elif self.rank in ["Jack","Queen","King"]:
            return 10
        elif self.rank == "Ace":
            return 11 #11 as standard, will be handled case by case in 'Hand' class.
        else:
            raise ValueError(f"Unexpected card rank: {self.rank}")
    
    def reveal(self):
        self.revealed = True

    def get_filename(self):
        """Returns the card's name as a string, e.g., "spades_ace"."""
        return f"{self.suit}_{self.rank}"
    
    def get_cardname(self):
        """
        Returns the card's representation for terminal output, using suit symbols.
        """
        suit_symbols = {
            "Hearts": "♥",
            "Diamonds": "♦",
            "Clubs": "♣",
            "Spades": "♠"
        }

        return f"{self.rank} {suit_symbols.get(self.suit, '?')}"
    
    def get_image(self, card_type="front"):
        """
        Returns the appropriate image for the card.
        Args:
            card_type (str): 'front' for the card face, 'back' for the card back.
        Returns:
            PhotoImage: The image to display.
        """
        if card_type == "front":
            file_path = f"assets/svg_playing_cards-fronts/{self.suit.lower()}_{self.rank.lower()}.svg"
        elif card_type == "back":
            file_path = "assets/svg_playing_cards-backs/abstract.svg"
        else:
            raise ValueError(f"Invalid card_type: {card_type}")

        # Convert SVG to PNG for tkinter using cairosvg
        png_data = svg2png(url=file_path)
        from io import BytesIO
        return PhotoImage(data=BytesIO(png_data).read())
    
class Deck:
    """
    Represents the state of a deck of a given number of shuffled decks of cards
    """
    def __init__(self,decks = 6):
        """
        Initialises a deck where every combination of rank and suit of cards is included for as many decks as there are.
        The resultant deck is then shuffled.
        """
        self.new_deck(decks = decks)

    def new_deck(self, decks = 1):
        print("New deck shuffled")
        self.suits = ["Hearts","Diamonds","Clubs","Spades"]
        self.ranks = [str(i) for i in range(2,11)] + ["Jack","Queen","King","Ace"]
        self.cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks] * decks

        for card in self.cards:
            card.revealed = True

        random.shuffle(self.cards)
        self.dealt_cards = 0
        self.should_shuffle_after_hand = False
    
    def deal_card(self):
        """
        Pulls a card from somewhere in the deck, removing it from the deck in the process.
        """
        if not self.cards:
            raise ValueError("No cards left in the deck")
        
        if self.dealt_cards >= 0.75 * len(self.cards):
            print("Cut card reached! Shuffle after this hand.")
            self.should_shuffle_after_hand = True
        
        self.dealt_cards += 1
        
        return self.cards.pop()    
    
    def should_shuffle(self):
        """
        Checks if the deck should be shuffled based on penetration level.
        Returns:
            bool: True if the deck should be shuffled, False otherwise.
        """
        return self.should_shuffle_after_hand

class Hand:
    """
    Represents the current hand of a player (or the dealer)
    """
    def __init__(self):
        """
        Initialises the hand as an empty set before cards are dealt.
        """
        self.cards = []
    
    def reset(self):
        """Resets the current hand to empty and ensures no card has unintended hidden status."""
        for card in self.cards:
            card.revealed = True
        self.cards.clear()

    def add_card(self,card):
        """
        Adds a given card to the current hand
        """
        self.cards.append(card)
    
    def hard_total(self):
        """
        Returns the 'hard total' of the hand
        This is the total where any aces are treated as 1's
        It is therefore the minimum value the hand can take.
        """
        total = 0
        for card in self.cards:
            if card.rank != "Ace":
                total += card.value()
            else:
                total += 1 #In a hard total, any aces are treated as a 1

        return total
    
    def soft_total(self):
        """
        Returns the 'soft total' of the hand
        This is the total where at most one ace is treated as an 11 (more than this and you'll always be bust)
        This is therefore the maximum sensible value the hand can take 
        """
        total = 0
        first_ace_down = False
        for card in self.cards:
            if card.rank != "Ace":
                total += card.value()
            elif not first_ace_down:
                total += 11 #Count only the first ace as 11 (as a second one counted as 11 would always bust your total)
                first_ace_down = True 
            else:
                total +=1 #Any subsequent aces to the first are always counted as 1's

        return total
    
    def total(self):
        """
        Returns the maximum possible total assuming the hand isn't bust.
        """
        hard = self.hard_total()
        soft = self.soft_total()

        if soft <= 21:
            return soft
        else:
            return hard
    
    def is_soft(self):
        """
        Returns true if the hard and soft totals are not the same (i.e. the hand is 'soft')
        This means there is at least one ace in the hand and it can be played as an 11 or 1 without going bust
        """
        return self.soft_total() != self.hard_total() and self.soft_total() <= 21
    
    def is_bust(self):
        """
        Returns true if the hard total is above 21 (i.e. the player has no way of making their hand below 21)
        """
        return self.hard_total() > 21
    
    def is_pair(self):
        """
        Returns true if there are exactly 2 cards in the hand and they have the same rank
        (Used for splitting logic in gameplay)
        """
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank
    
    def display_score_string(self, reveal_cards=True, standing=False):
        """
        Returns the score string for the hand.
        Args:
            reveal_cards (bool): Whether to reveal the current score or not.
            standing (bool): Whether the player or dealer is standing.
        Returns:
            str: The formatted score string.
        """
        if not reveal_cards:
            return "Hidden"

        if standing and self.is_soft() and not self.is_bust():
            # If standing and the hand is soft, return only the soft total
            return f"{self.soft_total()}"
    
        hard_total = self.hard_total()
        if self.is_soft():
            soft_total = self.soft_total()
            return f"{hard_total}/{soft_total}"
        else:
            return f"{hard_total}"
    
    def get_deckstring(self, reveal_cards=True):
        """
        Returns a string listing the current cards in the hand.
        Args:
            reveal_cards (bool): If False, hidden cards will be represented as '-'.
        """
        card_strings = []
        for card in self.cards:
            if card.revealed or reveal_cards:
                card_strings.append(card.get_cardname())
            else:
                card_strings.append("-")

        return ", ".join(card_strings)
    
    