import tkinter as tk
from PIL import Image, ImageTk
from cairosvg import svg2png
from io import BytesIO

CARD_IMAGES_PATH = r"C:\\Users\\marcu\\OneDrive\\.EDUCATION MARCUS\\Blackjack\\Re-try\\assets\\svg_playing_cards-fronts\\"
CARD_BACK_IMAGE_PATH = r"C:\\Users\\marcu\\OneDrive\\.EDUCATION MARCUS\\Blackjack\\testing\\assets\\svg_playing_cards-backs\\abstract.svg"

class WindowDisplay:
    """
    A utility class to create a standalone window with specified coordinates and dimensions.
    """
    def __init__(self, root, title, x_position, y_position, width=800, height=400):
        """
        Initializes the card display window.
        """
        self.window = tk.Toplevel(root)  # Creates a new separate child window
        self.window.title(title)  # Sets the window title
        self.card_labels = []  # Store card image labels for dynamic updates
        self.card_width = 2*150  # Increased card width for better visibility
        self.card_height = 2*225  # Increased card height for better visibility
        self.padding = 10  # Padding between cards
        self.total_width = width  # Default width
        self.total_height = height  # Default height
        self.window.geometry(f"{width}x{height}+{x_position}+{y_position}")

    def load_card_image(self, card_path):
        """
        Loads a card image from an SVG file, rescales it, and converts it to a PhotoImage.
        """
        try:
            png_data = svg2png(url=card_path)
            image = Image.open(BytesIO(png_data))

            # Rescale image to standard dimensions
            image = image.resize((self.card_width, self.card_height), Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading card image: {e}")
            raise

    def display_cards(self, card_names, reveal_all=True):
        """
        Dynamically displays the given cards in the window and resizes the window to fit them.
        Args:
            card_names (list): List of card names (e.g., "spades_ace", "clubs_king").
            reveal_first_only (bool): If True, only the first card is revealed, others are shown as back of the cards.
        """
        # Remove existing card labels
        for label in self.card_labels:
            label.destroy()
        self.card_labels.clear()

        # Display new cards with rescaled dimensions using place() for exact positioning
        current_x = 0
        for index, card_name in enumerate(card_names):
            if not reveal_all and index == 1:
                card_path = CARD_BACK_IMAGE_PATH
            else:
                card_path = f"{CARD_IMAGES_PATH}{card_name}.svg"

            card_image = self.load_card_image(card_path)
            label = tk.Label(self.window, image=card_image)
            label.image = card_image  # Prevent garbage collection
            label.place(x=current_x, y=10)  # Reduced vertical offset to better fit cards vertically
            self.card_labels.append(label)

            # Update the current x-coordinate for the next card, adding padding
            current_x += self.card_width + self.padding

        # Calculate the dimensions needed for the window including padding
        buffer = 20  # Smaller buffer to avoid unnecessary extra space
        total_width = current_x + buffer
        total_height = self.card_height + buffer  # Accounting for both vertical offsets with a minimal buffer

        # Set the window geometry and force an update
        self.total_width = total_width
        self.total_height = total_height
        self.window.geometry(f"{total_width}x{total_height}")


class BlackjackUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

        self.x_center = self.root.winfo_screenwidth() // 2
        self.y_center = self.root.winfo_screenheight() // 2
        self.padding = 100

        # Create windows for dealer and player
        self.dealer_display = WindowDisplay(self.root, "Dealer's Hand", 0, 0)
        self.player_display = WindowDisplay(self.root, "Player's Hand", 0, 0)

        # Update default dimensions for centering
        self.update_dimensions()

    def update_dimensions(self):
        """
        Ensures the windows have correct dimensions for initial positioning.
        """
        self.dealer_display.total_width = self.dealer_display.total_width or 800
        self.dealer_display.total_height = self.dealer_display.total_height or 400
        self.player_display.total_width = self.player_display.total_width or 800
        self.player_display.total_height = self.player_display.total_height or 400
        self.center_windows()

    def center_windows(self):
        """
        Re-centres the dealer and player windows based on their dimensions.
        """
        y_d = self.y_center - (self.dealer_display.total_height + self.padding + self.player_display.total_height) // 2
        x_d = self.x_center - self.dealer_display.total_width // 2

        y_p = self.y_center + (self.dealer_display.total_height + self.padding - self.player_display.total_height) // 2
        x_p = self.x_center - self.player_display.total_width // 2

        self.dealer_display.window.geometry(f"{self.dealer_display.total_width}x{self.dealer_display.total_height}+{x_d}+{y_d}")
        self.player_display.window.geometry(f"{self.player_display.total_width}x{self.player_display.total_height}+{x_p}+{y_p}")

    def update_dealer(self, card_names, reveal_all = False):
        """
        Updates the dealer's card display.
        Args:
            card_names (list): List of card names (e.g., "spades_ace", "clubs_king") for the dealer's cards.
            reveal_first_only (bool): If True, only the first card is revealed, others are shown as back of the cards.
        """
        self.dealer_display.display_cards(card_names, reveal_all)
        self.center_windows()

    def update_player(self, card_names):
        """
        Updates the player's card display.
        Args:
            card_names (list): List of card names (e.g., "hearts_7", "diamonds_3") for the player's cards.
        """
        self.player_display.display_cards(card_names)
        self.center_windows()


    def mainloop(self):
        self.root.mainloop()
