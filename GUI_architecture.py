import tkinter as tk
from PIL import Image, ImageTk
from cairosvg import svg2png
from io import BytesIO
from config import CARD_IMAGES_PATH, CARD_BACK_IMAGE_PATH, CARD_WIDTH, CARD_HEIGHT, CARD_PADDING, BORDER_PADDING, DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT, WINDOW_PADDING, BUTTON_ACTIVE_COLOUR, BUTTON_DISABLED_COLOUR, BUTTON_TEXT_COLOUR


class CardsWindowBase:
    """
    Base class for windows displaying cards (player or dealer)
    Handles loading in images and initialising the window
    """
    def __init__(self, root, title, x_position, y_position, width=800, height=400):
        """
        Initialize the window
        """
        self.window = tk.Toplevel(root) #Creates a new top level window
        self.window.title(title) #Sets the title of the window
        self.window.geometry(f"{width}x{height}+{x_position}+{y_position}") #Positions the window at the given coordinates

        # Attributes for card display
        self.card_labels = [] #Stores card labels for easy access/clearing
        self.card_width = CARD_WIDTH 
        self.card_height = CARD_HEIGHT
        self.card_padding = CARD_PADDING #Padding between cards
        self.border_padding = BORDER_PADDING #Padding between cards and window border

        self.total_width = DEFAULT_WINDOW_WIDTH  # Default width of the window
        self.total_height = DEFAULT_WINDOW_HEIGHT  # Default height of the window

    def load_card_image(self, card_path):
        """ 
        Loads a card image from an SVG file and resizes it for Tkinter. 
        
        Args:
            card_path (str): the path to the card image to load
        """
        try:
            #Converting the SVG to PNG
            png_data = svg2png(url=card_path)  # Converts SVG file to binary PNG data
            image = Image.open(BytesIO(png_data))  # Open binary data as a PIL image
            image = image.resize((self.card_width, self.card_height), Image.LANCZOS)  # Resize the image
            return ImageTk.PhotoImage(image)  # Convert to tkinter-compatible format
        except Exception as e:
            print(f"Error loading card image: {e}")
            raise

    def display_cards(self, cards):
        """ 
        Displays the cards in the window by removing all existing card images and adding new ones back in iteratively.
        """
        # Clear all existing card labels
        for label in self.card_labels:
            label.destroy()
        self.card_labels.clear()

        # Position to start displaying cards from the left of the window
        current_x = self.border_padding

        # Loop through each card and display it with correct spacing
        for card in cards:
            
            #Pull the correct card paths based on whether the card is revealed or not
            if card.revealed:
                card_path = f"{CARD_IMAGES_PATH}{card.get_filename()}.svg" 
            else:
                card_path = CARD_BACK_IMAGE_PATH

            card_image = self.load_card_image(card_path) #Load the card image

            label = tk.Label(self.window, image=card_image) #Label the loaded card image
            label.image = card_image  # Keep a reference to the image
            label.place(x=current_x, y=self.border_padding) #Place the card image in the window
            self.card_labels.append(label) #Add the label to the list of card labels

            current_x += self.card_width + self.card_padding #Update the next card's starting x position 
        
        # Calculate the total size of the window based on the number of cards displayed
        total_width = max(current_x - self.card_padding + self.border_padding,3*self.card_padding+2*self.card_width) #Calculates the width of the window as the last card plus padding (or the space for two cards and padding if there's only one card)
        total_height = self.card_height + 2* self.border_padding

        # Update the window geometry to fit the cards
        self.total_width = total_width
        self.total_height = total_height
        self.window.geometry(f"{total_width}x{total_height}")

class PlayerHandWindow(CardsWindowBase):
    """
    A specialised window for managing a player's hand.
    Includes buttons and labels for interaction, allowing players to perform actions.
    """

    def __init__(self, root, title, x_position, y_position, hand_index, width=800, height=600):
        """
        Initialises the player's hand window with buttons.

        Args:
            hand_index (int): Index of the player's hand (used when multiple hands needed after splitting).
        """
        super().__init__(root, title, x_position, y_position, width, height)

        self.hand_index = hand_index #Identifies the hand index for the window

        # Add labels for player and dealer hand totals 
        self.player_hand_value_label = tk.Label(self.window, text="Player Hand: 0", font=("Arial", 20))
        self.dealer_hand_value_label = tk.Label(self.window, text="Dealer Hand: Hidden", font=("Arial", 20))

        # Add 'Hit', 'Stand' and 'Split' buttons
        self.hit_button = tk.Button(self.window, text="Hit", command=self.hit, font=("Arial", 20),width = 10,height=2)
        self.stand_button = tk.Button(self.window, text="Stand", command=self.stand, font=("Arial", 20),width = 10,height=2)
        self.split_button = tk.Button(self.window, text="Split", command=self.split, font=("Arial", 20), width=10, height=2, state=tk.DISABLED)

        self.enable_hit_stand_buttons()

        # Placeholders for card labels and game reference
        self.ui = None

    def display_cards(self, cards):
        """
        Overwrites the based class method to include buttons and labels for player interaction.
        """

        # Clear all existing card labels
        for label in self.card_labels:
            label.destroy()
        self.card_labels.clear()

        # Calculate the total width of the cards section based on number of cards
        current_x = self.border_padding
        for card in cards:
            current_x += self.card_width + self.card_padding
        total_width = max(current_x - self.card_padding + self.border_padding,3*self.card_padding+2*self.card_width) 
        self.total_width = total_width  # Update the width 

        # Place score labels initially to get their actual height for spacing
        label_y_position = self.border_padding
        self.player_hand_value_label.place(x=self.total_width * 0.25, y=label_y_position, anchor="n") #Puts the player score label 1/4 of the window in from the left
        self.dealer_hand_value_label.place(x=self.total_width * 0.75, y=label_y_position, anchor="n") #Puts the dealer score label 1/4 of the window in from the right

        # Get the height of the labels after they are placed
        label_height = max(self.player_hand_value_label.winfo_reqheight(), self.dealer_hand_value_label.winfo_reqheight()) #Extracts the height of the biggest label
        
        # Calculate card section position based on label height
        card_y_position = label_y_position + label_height + self.border_padding
        current_x = self.border_padding

        # Display the cards correctly spaced as in the base window functionality
        for card in cards:
            card_path = f"{CARD_IMAGES_PATH}{card.get_filename()}.svg" if card.revealed else CARD_BACK_IMAGE_PATH
            card_image = self.load_card_image(card_path)
            label = tk.Label(self.window, image=card_image)
            label.image = card_image  
            label.place(x=current_x, y=card_y_position)
            self.card_labels.append(label)
            current_x += self.card_width + self.card_padding
        
        # Place hit and stand buttons 
        button_y_position = card_y_position + self.card_height + self.border_padding
        self.hit_button.place(x=total_width * 0.25, y=button_y_position, anchor='n') #Puts the hit button 1/4 of the window in from the left
        self.stand_button.place(x=total_width * 0.75, y=button_y_position, anchor='n') #Puts the stand button 1/4 of the window in from the right

        # Get button height (assuming both buttons have the same height)
        button_height = self.hit_button.winfo_reqheight()

        #Place the split button using spacing from the hit and stand buttons
        self.split_button.place(x=total_width * 0.25 , y=button_y_position + button_height + self.border_padding , anchor='n')

        # Calculate the total height required for the window
        total_height = button_y_position + 2* button_height + 3 * self.border_padding
        self.total_height = total_height  # Update the window height 

        # Update the window geometry to fit all elements
        self.window.geometry(f"{total_width}x{total_height}")

    def set_game_reference(self, ui):
        """ 
        Connect the player hand window to the game controller. 
        """
        self.ui = ui

    def hit(self):
        """
        Contains the logic for the player hitting (including checking for bust and disabling buttons when the player's turn is over).
        """
        if self.ui:
            
            #Try to deal card
            self.ui.game.current_hand.deal_card_to_player(self.hand_index)
            
            #Check if the player has busted
            self.ui.game.current_hand.check_bust(self.hand_index)
            
            #Check if the player's turn is over
            if self.ui.game.current_hand.player_hand_turn_over[self.hand_index]:
                self.disable_hit_stand_buttons()

    def stand(self):
        """
        Contains the logic for the player standing (including disabling buttons when the player's turn is over).
        """
        if self.ui:

            #Update stands flag
            self.ui.game.current_hand.player_stands(self.hand_index)
            
            #Disable buttons if the player's turn is over (it should be over by default but this is a safety check)
            if self.ui.game.current_hand.player_hand_turn_over[self.hand_index]:
                self.disable_hit_stand_buttons()
    
    def update_hand_value_labels(self, player_total, dealer_total, dealer_revealed):
        """
        Updates the displayed values of the player and dealer hands on their windows
        Args:
            player_total (int): The current total value of the player's hand.
            dealer_total (int): The current total value of the dealer's hand.
            dealer_revealed (bool): Whether the dealer's total should be revealed.
        """
        #Update player score label
        self.player_hand_value_label.config(text=f"Player Hand: {player_total}")

        #Update dealer score label
        if dealer_revealed:
            self.dealer_hand_value_label.config(text=f"Dealer Hand: {dealer_total}")
        else:
            self.dealer_hand_value_label.config(text=f"Dealer Hand: Hidden")

    def enable_hit_stand_buttons(self):
        """Enable the hit and stand buttons and update their visuals."""
        self.hit_button.config(state=tk.NORMAL, bg=BUTTON_ACTIVE_COLOUR, fg=BUTTON_TEXT_COLOUR)
        self.stand_button.config(state=tk.NORMAL, bg=BUTTON_ACTIVE_COLOUR, fg=BUTTON_TEXT_COLOUR)

    def disable_hit_stand_buttons(self):
        """Disable the hit and stand buttons and update their visuals."""
        self.hit_button.config(state=tk.DISABLED, bg=BUTTON_DISABLED_COLOUR, fg=BUTTON_TEXT_COLOUR)
        self.stand_button.config(state=tk.DISABLED, bg=BUTTON_DISABLED_COLOUR, fg=BUTTON_TEXT_COLOUR)

    def enable_split_button(self):
        """Enable the split button and update its visuals."""
        self.split_button.config(state=tk.NORMAL, bg=BUTTON_ACTIVE_COLOUR, fg=BUTTON_TEXT_COLOUR)

    def disable_split_button(self):
        """Disable the split button and update its visuals."""
        self.split_button.config(state=tk.DISABLED, bg=BUTTON_DISABLED_COLOUR, fg=BUTTON_TEXT_COLOUR)


    def split(self):
        """Perform a split on this hand."""
        if self.ui and self.ui.game.current_hand.can_split(self.hand_index): #Check if the hand can be split
            
            #Use the split_hand function in game_architecture to split the hand
            self.ui.game.current_hand.split_hand(self.hand_index)

            self.ui.update_player()

    def update_buttons(self):
        """Update the button states based on the current hand's state."""
        if self.ui and self.ui.game.current_hand.can_split(self.hand_index):
            self.enable_split_button()
        else:
            self.disable_split_button()

    def reset_window(self):
        """Reset the window for a new round."""
        self.enable_hit_stand_buttons()  # Re-enable hit and stand buttons for the new round
        self.disable_split_button()  # Disable split button initially
        self.display_cards([])  # Clear displayed cards
        self.update_hand_value_labels(0, 0, dealer_revealed=False)  # Reset hand values

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

        # Create 'New Game' and 'Quit' buttons
        self.new_game_button = tk.Button(self.window, text="New Game", command=self.new_game, font=("Arial", 20), width=10, bg='green', fg='white')
        self.quit_button = tk.Button(self.window, text="Quit", command=self.quit_game, font=("Arial", 20), width=10,bg='red', fg='white')

        # Calculate button height and define padding
        button_padding = 20  # Padding around buttons in pixels
        button_height = max(self.new_game_button.winfo_reqheight(), self.quit_button.winfo_reqheight())

        # Calculate total width and height for the control window based on button dimensions and padding
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
        self.ui.game.start_new_hand()

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
        """
        Initializes the BlackjackUI, creating all necessary windows and setting up their positions.

        Args:
            game (Blackjack_Game): The main game object that manages gameplay logic.
        """
        
        # Create root window and hide it since we only need child windows
        self.root = tk.Tk()
        self.root.withdraw()

        self.game = game

        # Calculate central point on the screen for the cards (1/2 in both directions used but could be anywhere)
        self.x_center_cards = self.root.winfo_screenwidth() // 2
        self.y_center_cards = self.root.winfo_screenheight() // 2
        self.window_padding = WINDOW_PADDING #This is the vertical gap between the dealer and player hand windows

        # Create window for the dealer's hand 
        self.dealer_display = DealerHandWindow(self.root, "Dealer's Hand", 0, 0)

        #Creates a list to store player windows
        self.player_displays = []

        #Creates initial player window
        player_window = PlayerHandWindow(self.root, f"Player's Hand {1}", 0, 0, 0)
        player_window.set_game_reference(self)
        self.player_displays.append(player_window)
        
        #Calculates central point for the control window
        self.x_center_controls = self.root.winfo_screenwidth() // 4
        self.y_center_controls = self.root.winfo_screenheight() // 2

        # Create control window
        self.control_window = ControlWindow(self.root, self,"Game Controls",0,0)

        #Centers the windows to place them spaced correctly in the middle of the screen
        self.center_windows()

    def add_player_window(self, hand_index):
        """
        Dynamically adds a new player hand window, typically after a split.

        Args:
            hand_index (int): The index of the new hand created after splitting.
        """

        player_window = PlayerHandWindow(self.root, f"Player's Hand {hand_index + 1}", 0, 0, hand_index)
        player_window.set_game_reference(self)
        self.player_displays.append(player_window)
        self.center_windows()

    def center_windows(self):
        """
        Centers the dealer and player windows dynamically based on screen size and current layout.

        Logic:
        - Dealer and player windows are spaced with the dealer window above the player windows so that the two window object is centered vertically.
        - Player windows are aligned horizontally with equal spacing and centred horizontally
        - Control window is positioned to the left of the dealer window.
        """
        #######################################################################################
        #Dealer positioning
        #######################################################################################

        # Calculate positions for dealer window
        y_d = self.y_center_cards - (self.dealer_display.total_height + self.window_padding + self.player_displays[0].total_height) // 2
        x_d = self.x_center_cards - self.dealer_display.total_width // 2

        # Set the position and dimensions for dealer windows
        self.dealer_display.window.geometry(f"{self.dealer_display.total_width}x{self.dealer_display.total_height}+{x_d}+{y_d}")

        #######################################################################################
        #Player positioning
        #######################################################################################

        #Calculate total width of all player windows for spacing
        total_player_width = 0
        for i in range(len(self.player_displays)):
            total_player_width += (self.player_displays[i].total_width + self.window_padding)
        
        #Place the first window to the left of the centre point so that there is enough space to space the rest of the windows centred on the middle
        players_start_x = self.x_center_cards - total_player_width // 2
        
        #Initialise the first player window position
        x_p = [players_start_x]

        #Calculate the x position of each player window based on the previous window's position and width
        for i in range(1,len(self.player_displays)):
            x_p.append(x_p[i-1] + self.player_displays[i-1].total_width + self.window_padding)

        #Place all player windows at the same vertical position so that this and the dealer window are centred vertically
        y_p = self.y_center_cards + (self.dealer_display.total_height + self.window_padding - self.player_displays[0].total_height) // 2

        #Place the player windows at the calculated positions
        for i in range(len(self.player_displays)):
            self.player_displays[i].window.geometry(f"{self.player_displays[i].total_width}x{self.player_displays[i].total_height}+{x_p[i]}+{y_p}")

        #######################################################################################
        #Control panel positioning
        #######################################################################################
        
        #Place the control window to the left of the dealer window with at least some padding
        x_c = min(self.x_center_controls - self.control_window.width // 2, x_d-self.window_padding-self.control_window.width)
        
        #Place the control window at the same vertical position as the dealer window
        y_c = self.y_center_cards - (self.dealer_display.total_height + self.window_padding + self.control_window.height) // 2
        
        #Place the control window in the calculated position
        self.control_window.window.geometry(f"{self.control_window.width}x{self.control_window.height}+{x_c}+{y_c}")

    def update_dealer(self):
        """
        Updates the dealer's card display window with current cards
        """
        self.dealer_display.display_cards(self.game.current_hand.dealer_card_set.cards)

        self.center_windows()  

    def update_player(self):
        """
        Updates the player's card display window.
        """
        # Update the player windows with the current hands
        for i, player_window in enumerate(self.player_displays):
            player_window.display_cards(self.game.current_hand.player_hands[i].cards)
            player_window.update_buttons()

        # Check if the split button should be enabled on each hand in play
        for i, hand in enumerate(self.game.current_hand.player_hands):
            if self.game.current_hand.can_split(i):
                self.player_displays[i].enable_split_button()
                break
        else:
            self.player_displays[i].disable_split_button()

        self.center_windows() 
    
    def update_all_hand_value_labels(self):
        """
        Updates the hand value labels for all player hands and checks on the dealer's hand reveal status.
        """
        #Check dealer total and reveal status
        dealer_total = self.game.current_hand.dealer_card_set.total()
        dealer_revealed = all(card.revealed for card in self.game.current_hand.dealer_card_set.cards)

        #Update player hand values
        for i, hand in enumerate(self.game.current_hand.player_hands):
            player_total = hand.total()  # Calculate the total for this hand
            self.player_displays[i].update_hand_value_labels(player_total, dealer_total, dealer_revealed)

    def mainloop(self):
        """
        Starts the Tkinter main event loop to keep the UI running.
        """
        self.root.mainloop()

    def reset_player_windows(self):
        """Reset the player windows to match a single hand."""
        
        # Destroy all current player windows
        for player_window in self.player_displays:
            player_window.window.destroy()
        self.player_displays.clear()

        # Create a single player window
        player_window = PlayerHandWindow(self.root, "Player's Hand 1", 0, 0, 0)
        player_window.set_game_reference(self)
        self.player_displays.append(player_window)

        self.center_windows()

