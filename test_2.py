from GUI_architecture_old import BlackjackUI

def main():
    ui = BlackjackUI()

    # Example card paths
    dealer_cards = [
        r"C:\Users\marcu\OneDrive\.EDUCATION MARCUS\Blackjack\Re-try\assets\svg_playing_cards-fronts\spades_ace.svg",
        r"C:\Users\marcu\OneDrive\.EDUCATION MARCUS\Blackjack\Re-try\assets\svg_playing_cards-fronts\clubs_king.svg"
    ]

    player_cards = [
        r"C:\Users\marcu\OneDrive\.EDUCATION MARCUS\Blackjack\Re-try\assets\svg_playing_cards-fronts\hearts_7.svg",
        r"C:\Users\marcu\OneDrive\.EDUCATION MARCUS\Blackjack\Re-try\assets\svg_playing_cards-fronts\diamonds_3.svg",
        r"C:\Users\marcu\OneDrive\.EDUCATION MARCUS\Blackjack\Re-try\assets\svg_playing_cards-fronts\diamonds_4.svg",
        r"C:\Users\marcu\OneDrive\.EDUCATION MARCUS\Blackjack\Re-try\assets\svg_playing_cards-fronts\diamonds_5.svg",
        r"C:\Users\marcu\OneDrive\.EDUCATION MARCUS\Blackjack\Re-try\assets\svg_playing_cards-fronts\diamonds_6.svg"
    ]

    # Display cards
    ui.update_dealer(dealer_cards)
    ui.update_player(player_cards)

    ui.mainloop()


if __name__ == "__main__":
    main()
