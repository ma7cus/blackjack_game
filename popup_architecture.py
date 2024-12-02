import tkinter as tk
from PIL import Image, ImageTk
from cairosvg import svg2png
from io import BytesIO
import os


class CardDisplay:
    """
    Handles the display of cards in a window for either the dealer or the player.
    Dynamically resizes and repositions the window based on the number of cards.
    """

    def __init__(self, root, title, y_position):
        """
        Initializes the card display window.
        Args:
            root (tk.Tk): The root Tkinter application window.
            title (str): Title of the window.
            y_position (int): Vertical position of the window on the screen.
        """
        self.window = tk.Toplevel(root)
        self.window.title(title)
        self.y_position = y_position
        self.card_labels = []
        self.card_width = 0
        self.card_height = 0
        self.padding = 10  # Padding around each card

    def load_card_image(self, card_path):
        """
        Loads a card image from an SVG file and converts it for Tkinter display.
        Args:
            card_path (str): Path to the card SVG file.
        Returns:
            ImageTk.PhotoImage: The converted card image for display.
        """
        try:
            # Convert SVG to PNG in memory
            png_data = svg2png(url=card_path)
            image = Image.open(BytesIO(png_data))

            # Set card dimensions if not already set
            if not self.card_width or not self.card_height:
                self.card_width, self.card_height = image.size
                print(f"Card dimensions set: width={self.card_width}, height={self.card_height}")

            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading SVG card image from {card_path}: {e}")
            raise

    def display_cards(self, card_paths):
        """
        Displays the given cards in the window, resizing the window to fit the cards.
        Args:
            card_paths (list): List of file paths for the card images.
        """
        # Clear existing card labels
        for label in self.card_labels:
            label.destroy()
        self.card_labels = []

        # Add new cards
        for idx, card_path in enumerate(card_paths):
            card_image = self.load_card_image(card_path)
            label = tk.Label(self.window, image=card_image)
            label.image = card_image  # Prevent garbage collection
            label.pack(side=tk.LEFT, padx=self.padding)
            self.card_labels.append(label)

        # Calculate window dimensions
        total_width = len(card_paths) * (self.card_width + 2 * self.padding) 
        total_height = self.card_height + 2 * self.padding

        # Center horizontally and position vertically based on y_position
        screen_width = self.window.winfo_screenwidth()
        x_position = (screen_width - total_width) // 2

        self.window.geometry(f"{total_width}x{total_height}+{x_position}+{self.y_position}")
        print(f"{self.window.title()} window resized to: {total_width}x{total_height} at position ({x_position}, {self.y_position})")


class BlackjackUI:
    """
    Handles the overall UI for the Blackjack game, including both the dealer's and player's card displays.
    """

    def __init__(self):
        """
        Initializes the root window and creates the dealer and player card displays.
        """
        self.root = tk.Tk()
        self.root.title("Blackjack Game")
        self.root.geometry("200x100")
        self.root.withdraw()  # Hide the root window

        # Paths to card assets
        self.card_assets_front_path = r"C:\Users\marcu\OneDrive\.EDUCATION MARCUS\Blackjack\Re-try\assets\svg_playing_cards-fronts"
        self.card_back_path = r"C:\Users\marcu\OneDrive\.EDUCATION MARCUS\Blackjack\Re-try\assets\svg_playing_cards-backs\abstract.svg"

        # Create separate displays for dealer and player
        self.dealer_display = CardDisplay(self.root, "Dealer's Hand", 100)
        self.player_display = CardDisplay(self.root, "Player's Hand", 500)

    def get_card_path(self, card_name):
        """
        Constructs the full path to a card image file.
        Args:
            card_name (str): The name of the card (e.g., "spades_ace.svg").
        Returns:
            str: The full path to the card image file.
        """
        return os.path.join(self.card_assets_front_path, card_name)

    def update_dealer(self, hand, reveal_all=False):
        """
        Updates the dealer's card display.
        Args:
            hand (Hand): Dealer's hand object.
            reveal_all (bool): Whether to reveal all cards (True) or only the first card (False).
        """
        card_paths = [self.get_card_path(f"{card.suit.lower()}_{card.rank.lower()}.svg") for card in hand.cards]
        if not reveal_all:
            # Hide all cards except the first one
            card_paths = [card_paths[0]] + [self.card_back_path] * (len(card_paths) - 1)
        self.dealer_display.display_cards(card_paths)


    def update_player(self, hand):
        """
        Updates the player's card display.
        Args:
            hand (Hand): Player's hand object.
        """
        # Extract card filenames from the Hand object
        card_paths = [self.get_card_path(f"{card.suit.lower()}_{card.rank.lower()}.svg") for card in hand.cards]
        self.player_display.display_cards(card_paths)


    def mainloop(self):
        """
        Starts the Tkinter event loop.
        """
        self.root.mainloop()
