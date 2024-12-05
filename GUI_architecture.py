import tkinter as tk
from PIL import Image, ImageTk
from cairosvg import svg2png
from io import BytesIO

# File paths for card images and card back images
CARD_IMAGES_PATH = r"C:\\Users\\marcu\\OneDrive\\.EDUCATION MARCUS\\Blackjack\\Re-try\\assets\\svg_playing_cards-fronts\\"
CARD_BACK_IMAGE_PATH = r"C:\\Users\\marcu\\OneDrive\\.EDUCATION MARCUS\\Blackjack\\testing\\assets\\svg_playing_cards-backs\\abstract.svg"

class CardsWindow:
    """
    A utility class to create a standalone window to display cards with specified dimensions and coordinates.
    """

    def __init__(self, root, title, x_position, y_position, width=800, height=400):
        """
        Initializes the card display window.
        Args:
            root (Tk object): Root Tkinter window for creating child windows.
            title (str): Title of the window.
            x_position, y_position (int): Coordinates for the window on the screen.
            width, height (int): Dimensions of the window.
        """
        # Create a child window with a specified title
        self.window = tk.Toplevel(root)
        self.window.title(title)

        # Attributes to manage the display
        self.card_labels = []  # List to store card image labels for dynamic updates
        self.card_width = 300 # Standard width of cards 
        self.card_height = 450  # Standard height of cards 
        self.card_padding = 10  # Padding between cards
        self.border_padding = 20 #Padding between cards and the window borders
        self.total_width = width  # Default width of the window
        self.total_height = height  # Default height of the window

        # Set the window geometry using width, height, and coordinates
        self.window.geometry(f"{width}x{height}+{x_position}+{y_position}")

    def load_card_image(self, card_path):
        """
        Loads a card image from an SVG file, rescales it, and converts it to a PhotoImage for Tkinter.
        Args:
            card_path (str): File path of the card image.
        Returns:
            PhotoImage: The Tkinter-compatible image.
        """
        try:
            # Convert SVG to PNG data
            png_data = svg2png(url=card_path)

            # Open the PNG data and resize it
            image = Image.open(BytesIO(png_data))
            image = image.resize((self.card_width, self.card_height), Image.LANCZOS)

            # Convert to PhotoImage for Tkinter
            return ImageTk.PhotoImage(image)
            
        except Exception as e:
            print(f"Error loading card image: {e}")
            raise

    def display_cards(self, cards):
        """
        Displays a list of card images in the window, resizing it as needed.
        Args:
            card_names (list): List of card names (e.g., "spades_ace", "clubs_king").
            reveal_all (bool): If False, the second card isn't shown, instead being displayed as a card back.
        """
        # Clear all existing card labels in the window
        for label in self.card_labels:
            label.destroy()
        self.card_labels.clear()

        # Position to start displaying cards from the left of the window
        current_x = self.border_padding #Start a buffer length in from the left

        for card in cards:

            # Determine which card image to load (face or back)
            if not card.revealed:
                card_path = CARD_BACK_IMAGE_PATH  # Use the back image for unrevealed cards
            else:
                card_path = f"{CARD_IMAGES_PATH}{card.get_filename()}.svg"

            # Load the image and create a label widget to display it
            card_image = self.load_card_image(card_path)
            label = tk.Label(self.window, image=card_image)
            label.image = card_image  
            label.place(x = current_x, y = self.border_padding) 
            self.card_labels.append(label)

            # Update the position for the next card to be placed, add padding
            current_x += self.card_width + self.card_padding

        # Calculate the total size of the window based on the number of cards displayed
        total_width = current_x - self.card_padding + self.border_padding 
        total_height = self.card_height + 2* self.border_padding

        # Update the window geometry to fit the cards
        self.total_width = total_width
        self.total_height = total_height
        self.window.geometry(f"{total_width}x{total_height}")

class ControlWindow:
    """
    A utility class to create a control window with buttons to manage the game.
    """

    def __init__(self, root, ui, title, x_position, y_position, width=400, height=400):
        """
        Initializes the control window with buttons for gameplay actions.
        Args:
            root (Tk object): Root Tkinter window.
            ui (BlackjackUI): Reference to the Blackjack UI to access game methods.
        """
        self.ui = ui
        self.window = tk.Toplevel(root)
        self.window.title(title)

        self.width = width
        self.height = height

        # Set window position and size
        self.window.geometry(f"{width}x{height}+{x_position}+{y_position}")

        #Add a hit button
        self.hit_button = tk.Button(self.window, text="Hit", command=self.hit, font=("Arial", 14), width=10, height=2)
        self.hit_button.place(relx=0.3, rely=0.5, anchor="center")  # Position the hit button more to the left

        #Add a stand button
        self.stand_button = tk.Button(self.window, text="Stand", command=self.stand, font=("Arial", 14), width=10, height=2)
        self.stand_button.place(relx=0.7, rely=0.5, anchor="center")  # Position the stand button more to the right

        self.new_game_button = tk.Button(self.window, text="New Game", command=self.new_game, font=("Arial", 14), width=10, height=2)
        self.new_game_button.place(relx=0.3, rely=0.7, anchor="center")

        self.quit_button = tk.Button(self.window, text="Quit", command=self.quit_game, font=("Arial", 14), width=10, height=2)
        self.quit_button.place(relx=0.7, rely=0.7, anchor="center")

        
    def hit(self):
        """
        Handles the "Hit" action by calling the appropriate game logic to deal a card to the player.
        """
        if not self.ui.game.current_hand.player_turn_over:
            self.ui.game.current_hand.deal_card_to_player()
            self.ui.game.current_hand.check_bust()
            if self.ui.game.current_hand.player_turn_over:
                self.disable_buttons()

    def stand(self):
        """
        Handles the "Stand" action by ending the player's turn and starting the dealer's turn.
        """
        if not self.ui.game.current_hand.player_turn_over:
            self.ui.game.current_hand.player_stands()
            if self.ui.game.current_hand.hand_over:
                self.disable_buttons()

    def new_game(self):
        """
        Starts a new hand of the game.
        """
        self.ui.game.new_hand()
        self.enable_buttons()

    def quit_game(self):
        """
        Quits the game by destroying the main window.
        """
        self.ui.root.quit()

    def disable_buttons(self):
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)



class BlackjackUI:
    """
    Main UI class to create and manage the card display windows for the dealer and player.
    """

    def __init__(self,game):
        # Create root window and hide it since we only need child windows
        self.root = tk.Tk()
        self.root.withdraw()

        self.game = game

        # Calculate central point on the screen for the cards (1/2 in both directions used but could be anywhere)
        self.x_center_cards = self.root.winfo_screenwidth() // 2
        self.y_center_cards = self.root.winfo_screenheight() // 2
        self.window_padding = 100 #This is the gap between the two hand windows

        # Create separate windows for the dealer's hand and player's hand
        self.dealer_display = CardsWindow(self.root, "Dealer's Hand", 0, 0)
        self.player_display = CardsWindow(self.root, "Player's Hand", 0, 0)

        self.x_center_controls = self.root.winfo_screenwidth() // 4
        self.y_center_controls = self.root.winfo_screenheight() // 2
        self.control_window = ControlWindow(self.root, self,"Game Controls",0,0)

        self.center_windows()

    def center_windows(self):
        """
        Centers the dealer and player windows based on the current screen dimensions.
        The two hands + padding will be centred on the centre point defined earlier.
        """
        # Calculate positions for centering dealer and player windows with padding on the centre point
        y_d = self.y_center_cards - (self.dealer_display.total_height + self.window_padding + self.player_display.total_height) // 2
        x_d = self.x_center_cards - self.dealer_display.total_width // 2

        y_p = self.y_center_cards + (self.dealer_display.total_height + self.window_padding - self.player_display.total_height) // 2
        x_p = self.x_center_cards - self.player_display.total_width // 2

        # Set the position and dimensions for dealer and player windows
        self.dealer_display.window.geometry(f"{self.dealer_display.total_width}x{self.dealer_display.total_height}+{x_d}+{y_d}")
        self.player_display.window.geometry(f"{self.player_display.total_width}x{self.player_display.total_height}+{x_p}+{y_p}")

        x_c = min(self.x_center_controls - self.control_window.width // 2, x_d-self.window_padding-self.control_window.width)
        y_c = self.y_center_cards - (self.dealer_display.total_height + self.window_padding + self.control_window.height) // 2
        #y_c = self.y_center_controls - self.control_window.height // 2
        self.control_window.window.geometry(f"{self.control_window.width}x{self.control_window.height}+{x_c}+{y_c}")

    def update_dealer(self, cards):
        """
        Updates the dealer's card display window.
        Args:
            cards: Set of cards for the dealer's hand.
        """
        self.dealer_display.display_cards(cards)
        self.center_windows()  

    def update_player(self, cards):
        """
        Updates the player's card display window.
        Args:
            cards: Set of cards for the player's hand.
        """
        self.player_display.display_cards(cards)
        self.center_windows() 

    def mainloop(self):
        """
        Starts the Tkinter main event loop to keep the UI running.
        """
        self.root.mainloop()

