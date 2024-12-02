import tkinter as tk
from game_architecture import Blackjack_Game


def main():
    def start_new_round():
        """
        Starts a new round by resetting the game state and UI.
        """
        global game
        # Destroy old UI windows
        if hasattr(game, 'ui') and game.ui.root.winfo_exists():
            game.ui.root.destroy()

        # Reinitialize the game and UI
        initialize_game()

    def initialize_game():
        """
        Initializes the game and sets up the player controls for the current round.
        """
        global game
        game = Blackjack_Game()

        def update_player_score():
            """
            Calculates and displays the player's current score.
            """
            hand = game.player_hand
            hard_total = hand.hard_total()
            soft_total = hand.soft_total()

            # Determine the score display (handle soft hands)
            if hand.is_bust():
                score_text = f"Bust! Score: {hard_total}"
            elif hand.is_soft():
                score_text = f"Score: {soft_total} (Soft)"
            else:
                score_text = f"Score: {hard_total}"

            score_label.config(text=score_text)

        def player_hit():
            """
            Adds a card to the player's hand and updates the display and score.
            """
            game.player_hand.add_card(game.deck.deal_card())
            game.update_ui(reveal_dealer=False)
            update_player_score()

            # Check for bust
            if game.player_hand.is_bust():
                result_label.config(text="Bust! You Lose.")
                hit_button.config(state=tk.DISABLED)
                stick_button.config(state=tk.DISABLED)

        def player_stick():
            """
            Finalises the player's turn and disables further input.
            """
            result_label.config(text="Player Sticks!")
            hit_button.config(state=tk.DISABLED)
            stick_button.config(state=tk.DISABLED)

        # Create a control window
        control_window = tk.Toplevel(game.ui.root)
        control_window.title("Player Controls")

        # Set fixed position for Player Controls
        control_window.geometry("300x200+50+50")  # Width x Height + X Offset + Y Offset

        # Player's score display
        score_label = tk.Label(control_window, text="Score: 0", font=("Arial", 14))
        score_label.pack(pady=10)

        # Result display
        result_label = tk.Label(control_window, text="", font=("Arial", 14))
        result_label.pack(pady=10)

        # Buttons for Hit, Stick, and Redeal
        hit_button = tk.Button(control_window, text="Hit", command=player_hit)
        hit_button.pack(side=tk.LEFT, padx=10, pady=20)

        stick_button = tk.Button(control_window, text="Stick", command=player_stick)
        stick_button.pack(side=tk.LEFT, padx=10, pady=20)

        tk.Button(control_window, text="Redeal", command=start_new_round).pack(side=tk.RIGHT, padx=10, pady=20)

        # Start the game by dealing initial hands
        game.deal_initial_hands()
        update_player_score()

        # Start the Tkinter main loop
        game.ui.root.mainloop()

    # Initialize the first round
    initialize_game()


if __name__ == "__main__":
    main()
