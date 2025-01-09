# Blackjack Game

## Overview
This is a Python-based Blackjack game that includes a graphical user interface (GUI) built with `tkinter`. 
The game supports standard Blackjack rules, including splitting. 
It is designed for single-player gameplay against a dealer.

## Features
- **Interactive GUI**:
  - Play Blackjack with visual card representations.
  - Buttons for actions: Hit, Stand, and Split.
- **Rules Implementation**:
  - Splitting and resplitting up to 4 hands.
  - Only one more card is dealt after splitting aces.
  - Dealer logic follows standard rules (e.g., hits until above 17 or soft 17).
- **Dynamic Layout**:
  - Windows adjust dynamically based on the number of player hands.
- **Configurable Settings**:
  - Change the number of decks, maximum splits, and ace-specific rules via a `config.py` file.

## Installation

### Prerequisites
- Python 3.x
- Required libraries:
  - `tkinter` (should already be installed with python)
  - `cairosvg` 

### Steps
1. Clone this repository:
   ```bash
   git clone https://github.com/ma7cus/blackjack-game.git
