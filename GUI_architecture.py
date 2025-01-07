import tkinter as tk
from PIL import Image, ImageTk
from cairosvg import svg2png
from io import BytesIO

# File paths for card images and card back images
CARD_IMAGES_PATH = r"C:\\Users\\marcu\\OneDrive\\.EDUCATION MARCUS\\Blackjack\\Re-try\\assets\\svg_playing_cards-fronts\\"
CARD_BACK_IMAGE_PATH = r"C:\\Users\\marcu\\OneDrive\\.EDUCATION MARCUS\\Blackjack\\testing\\assets\\svg_playing_cards-backs\\abstract.svg"

class CardsWindowBase:
    def __init__(self, root, title, x_position, y_position, width=800, height=400):
        # Initialize the window
        self.window = tk.Toplevel(root)
        self.window.title(title)
        self.window.geometry(f"{width}x{height}+{x_position}+{y_position}")

        # Attributes for card display
        self.card_labels = []
        self.card_width = 300
        self.card_height = 450
        self.card_padding = 10
        self.border_padding = 20

        # Set default total width and height to the initial window size
        self.default_width = width
        self.default_height = height
        self.total_width = width  # Default width of the window
        self.total_height = height  # Default height of the window

    def load_card_image(self, card_path):
        """ Loads a card image from an SVG file and resizes it for Tkinter. """
        try:
            png_data = svg2png(url=card_path)
            image = Image.open(BytesIO(png_data))
            image = image.resize((self.card_width, self.card_height), Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Error loading card image: {e}")
            raise

    def display_cards(self, cards, y_offset=None):
        """ Displays the cards in the window. """
        # Clear all existing card labels
        for label in self.card_labels:
            label.destroy()
        self.card_labels.clear()

        # Position to start displaying cards from the left of the window
        current_x = self.border_padding

        # Loop through each card and display it
        for card in cards:
            card_path = f"assets/svg_playing_cards-fronts/{card.get_filename()}.svg" if card.revealed else "assets/svg_playing_cards-backs/abstract.svg"
            card_image = self.load_card_image(card_path)
            label = tk.Label(self.window, image=card_image)
            label.image = card_image  # Keep a reference to avoid garbage collection
            label.place(x=current_x, y=self.border_padding)
            self.card_labels.append(label)
            current_x += self.card_width + self.card_padding
        
        # Calculate the total size of the window based on the number of cards displayed
        total_width = current_x - self.card_padding + self.border_padding 
        total_height = self.card_height + 2* self.border_padding

        # Update the window geometry to fit the cards
        self.total_width = total_width
        self.total_height = total_height
        self.window.geometry(f"{total_width}x{total_height}")

class PlayerHandWindow(CardsWindowBase):
    def __init__(self, root, title, x_position, y_position, width=800, height=600):
        # Call the base class constructor
        super().__init__(root, title, x_position, y_position, width, height)

        # Add labels for player and dealer hand totals 
        self.player_hand_value_label = tk.Label(self.window, text="Player Hand: 0", font=("Arial", 20))
        self.dealer_hand_value_label = tk.Label(self.window, text="Dealer Hand: Hidden", font=("Arial", 20))

        # Add 'Hit' and 'Stand' buttons
        self.hit_button = tk.Button(self.window, text="Hit", command=self.hit, font=("Arial", 20),width = 15,height=2)
        self.stand_button = tk.Button(self.window, text="Stand", command=self.stand, font=("Arial", 20),width = 15,height=2)

        # Placeholders for card labels and game reference
        self.ui = None

    def display_cards(self, cards):
        # Clear all existing card labels
        for label in self.card_labels:
            label.destroy()
        self.card_labels.clear()

        # Calculate the total width of the cards section based on number of cards
        current_x = self.border_padding
        for card in cards:
            current_x += self.card_width + self.card_padding
        total_width = current_x - self.card_padding + self.border_padding
        self.total_width = total_width  # Update the width attribute

        # Place labels initially to get their requested height
        label_y_position = self.border_padding
        self.player_hand_value_label.place(x=self.total_width * 0.25, y=label_y_position, anchor="n")
        self.dealer_hand_value_label.place(x=self.total_width * 0.75, y=label_y_position, anchor="n")

        # Get the height of the labels after they are placed
        label_height = max(self.player_hand_value_label.winfo_reqheight(), self.dealer_hand_value_label.winfo_reqheight())
        
        # Calculate card section position
        card_y_position = label_y_position + label_height + self.border_padding
        current_x = self.border_padding

        # Display the cards using place and collect their heights
        for card in cards:
            card_path = f"{CARD_IMAGES_PATH}{card.get_filename()}.svg" if card.revealed else CARD_BACK_IMAGE_PATH
            card_image = self.load_card_image(card_path)
            label = tk.Label(self.window, image=card_image)
            label.image = card_image  # Keep a reference to avoid garbage collection
            label.place(x=current_x, y=card_y_position)
            self.card_labels.append(label)
            current_x += self.card_width + self.card_padding
        
        # Place buttons and calculate their position
        button_y_position = card_y_position + self.card_height + self.border_padding
        self.hit_button.place(x=total_width * 0.25, y=button_y_position, anchor='n')
        self.stand_button.place(x=total_width * 0.75, y=button_y_position, anchor='n')

        # Get button height (assuming both buttons have the same height)
        button_height = self.hit_button.winfo_reqheight()

        # Calculate the total height required for the window
        total_height = button_y_position + button_height + self.border_padding
        self.total_height = total_height  # Update the height attribute

        # Update the window geometry to fit all elements
        self.window.geometry(f"{total_width}x{total_height}")


    def set_game_reference(self, ui):
        """ Connect the player hand window to the game controller. """
        self.ui = ui

    def hit(self):
        if self.ui:
            self.ui.game.current_hand.deal_card_to_player()
            self.ui.game.current_hand.check_bust()
            if self.ui.game.current_hand.player_turn_over:
                self.disable_buttons()

    def stand(self):
        if self.ui:
            self.ui.game.current_hand.player_stands()
            if self.ui.game.current_hand.round_over:
                self.disable_buttons()
    
    def update_hand_values(self, player_total, dealer_total, dealer_revealed):
        """
        Updates the displayed values of the player and dealer hands.
        Args:
            player_total (int): The current total value of the player's hand.
            dealer_total (int): The current total value of the dealer's hand.
            dealer_revealed (bool): Whether the dealer's total should be revealed.
        """
        self.player_hand_value_label.config(text=f"Player Hand: {player_total}")

        if dealer_revealed:
            self.dealer_hand_value_label.config(text=f"Dealer Hand: {dealer_total}")
        else:
            self.dealer_hand_value_label.config(text=f"Dealer Hand: Hidden")

    def disable_buttons(self):
        self.hit_button.config(state=tk.DISABLED)
        self.stand_button.config(state=tk.DISABLED)

    def enable_buttons(self):
        self.hit_button.config(state=tk.NORMAL)
        self.stand_button.config(state=tk.NORMAL)


class DealerHandWindow(CardsWindowBase):
    def __init__(self, root, title, x_position, y_position, width=800, height=400):
        # Call the base class constructor
        super().__init__(root, title, x_position, y_position, width, height)
        

class ControlWindow:
    """
    A utility class to create a control window with buttons to manage the game.
    """

    def __init__(self, root, ui, title, x_position, y_position):
        """
        Initializes the control window with buttons for gameplay actions.
        Args:
            root (Tk object): Root Tkinter window.
            ui (BlackjackUI): Reference to the Blackjack UI to access game methods.
        """
        self.ui = ui
        self.window = tk.Toplevel(root)
        self.window.title(title)

        # Create 'New Game' and 'Quit' buttons with appropriate size based on text width
        self.new_game_button = tk.Button(self.window, text="New Game", command=self.new_game, font=("Arial", 20), width=10)
        self.quit_button = tk.Button(self.window, text="Quit", command=self.quit_game, font=("Arial", 20), width=10)

        # Calculate button height and padding
        button_padding = 20  # Padding around buttons in pixels
        button_height = max(self.new_game_button.winfo_reqheight(), self.quit_button.winfo_reqheight())

        # Calculate total width and height for the control window based on button dimensions
        self.width = 2 * self.new_game_button.winfo_reqwidth() + 3 * button_padding
        self.height = button_height + 2 * button_padding

        # Set window position and size
        self.window.geometry(f"{self.width}x{self.height}+{x_position}+{y_position}")

        # Place buttons evenly spaced within the window
        self.new_game_button.place(x=button_padding, y=button_padding, anchor="nw")
        self.quit_button.place(x=2 * button_padding + self.new_game_button.winfo_reqwidth(), y=button_padding, anchor="nw")

    def new_game(self):
        """
        Starts a new hand of the game.
        """
        self.ui.game.new_hand()

    def quit_game(self):
        """
        Quits the game by destroying the main window.
        """
        self.ui.root.quit()


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
        self.dealer_display = DealerHandWindow(self.root, "Dealer's Hand", 0, 0)
        self.player_display = PlayerHandWindow(self.root, "Player's Hand", 0, 0)

        # Set the game reference for player actions
        self.player_display.set_game_reference(self)


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
    
    def update_hand_values(self, player_total, dealer_total, dealer_revealed):
        """
        Updates the hand values in the control window.
        Args:
            player_total (int): The player's current hand value.
            dealer_total (int): The dealer's current hand value.
            dealer_revealed (bool): Whether the dealer's total should be revealed.
        """
        self.player_display.update_hand_values(player_total, dealer_total, dealer_revealed)

    def mainloop(self):
        """
        Starts the Tkinter main event loop to keep the UI running.
        """
        self.root.mainloop()

