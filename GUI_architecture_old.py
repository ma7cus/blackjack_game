import tkinter as tk
from PIL import Image, ImageTk
from cairosvg import svg2png
from io import BytesIO

class WindowDisplay:
    """
    A utility class to create a standalone window with specified coordinates and dimensions.
    """
    def __init__(self, root, title, x_position, y_position, width=600, height=300):
        """
        Initializes the card display window.
        """
        self.window = tk.Toplevel(root)  # Creates a new separate child window
        self.window.title(title)  # Sets the window title
        self.card_labels = []  # Store card image labels for dynamic updates
        self.card_width = 0
        self.card_height = 0
        self.padding = 10  # Padding between cards
        self.total_width = width  # Default width
        self.total_height = height  # Default height
        self.window.geometry(f"{width}x{height}+{x_position}+{y_position}") 

    def load_card_image(self, card_path):
        """
        Loads a card image from an SVG file and converts it to a PhotoImage.
        """
        try:
            png_data = svg2png(url=card_path)
            image = Image.open(BytesIO(png_data))

            if not self.card_width or not self.card_height:
                self.card_width, self.card_height = image.size
                print(f"Card dimensions set: width={self.card_width}, height={self.card_height}")

            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading card image: {e}")
            raise

    def display_cards(self, card_paths):
        """
        Dynamically displays the given cards in the window and resizes the window to fit them.
        """
        for label in self.card_labels:
            label.destroy()
        self.card_labels.clear()

        for card_path in card_paths:
            card_image = self.load_card_image(card_path)
            label = tk.Label(self.window, image=card_image)
            label.image = card_image  # Prevent garbage collection
            label.pack(side=tk.LEFT, padx=(0, self.padding))
            self.card_labels.append(label)

        self.window.update_idletasks()

        total_width = len(card_paths) * self.card_width + (len(card_paths) - 1) * self.padding
        total_height = self.card_height

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
        self.dealer_display.total_width = self.dealer_display.total_width or 600
        self.dealer_display.total_height = self.dealer_display.total_height or 300
        self.player_display.total_width = self.player_display.total_width or 600
        self.player_display.total_height = self.player_display.total_height or 300
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

    def update_dealer(self, card_paths):
        self.dealer_display.display_cards(card_paths)
        self.center_windows()

    def update_player(self, card_paths):
        self.player_display.display_cards(card_paths)
        self.center_windows()

    def mainloop(self):
        self.root.mainloop()
