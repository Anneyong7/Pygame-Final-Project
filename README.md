# Pygame-Final-Project
# 5-in-1 Pygame Arcade Collection

## Project Overview
This project is a collection of 5 classic arcade and puzzle games built entirely in Python using the Pygame library. The collection features a variety of gameplay styles, ranging from casual clickers to strategic puzzles. 

This entire project was developed as a collaborative effort by a group of 5 members, with each member contributing to the creation, design, and assembly of the individual games.

## Included Games
The arcade collection features the following 5 games:

1. **2048** — A sliding block puzzle game where the player merges tiles with matching numbers to reach the ultimate 2048 tile.
2. **Minesweeper** — A logic puzzle game where the player clears a grid of hidden mines without detonating any of them.
3. **Spelling Bee** — An educational word puzzle game where players test their vocabulary by finding and spelling words from a set of letters.
4. **Tic Tac Toe** — The classic two-player turn-based strategy game of aligning three marks in a grid.
5. **Coin Clicker / Idle Game** — A casual progression game where players click a coin to earn points and purchase upgrades to automate their income.

## System Requirements
* Python 3.12 (Recommended for optimal library stability)
* Pygame library

---

## Installation and Setup

Follow these steps to install and run the project on your local computer:

### 1. Install Python 3.12
Ensure Python 3.12 is installed on your device. During installation, make sure to check the box that says "Add python.exe to PATH".

### 2. Install Pygame Library
Open your terminal or command prompt and run the following command to download the required engine:
pip install pygame

### 3. Running the Entire Collection
To launch the main launcher interface and select any of the 5 games, run this command in the root folder:
python Main_Menu.py

---

## Specific Setup: Running the Coin Clicker Game Standalone

If you want to test or run the Coin Clicker game by itself without opening the Main Menu, follow these steps:

### 1. Check the Folder Requirements
Make sure your file directory looks exactly like this:
Pygame-Final-Project/
   Clicker/
      Main_Game.py
      assets/
         background.png
         coin.png
         ClickSound.mp3
         PurchaseSound.mp3
         bg_music.mp3
         PressStart2P-Regular.ttf

*Note: The audio, image, and font files must stay inside the lowercase assets folder, or the script will crash.*

### 2. Run the Game File Directly
Open your terminal, navigate inside the Clicker subfolder, and execute Main_Game.py:
cd Clicker
python Main_Game.py

---

## Project Directory Structure
* Main_Menu.py — The main launcher interface to select and play any of the 5 games.
* Clicker/ — Code files and assets for the Coin Clicker game.
* 2048/ — Code files and assets for the 2048 puzzle game.
* Minesweeper/ — Code files and assets for the Minesweeper game.
* Spelling_Bee/ — Code files and assets for the Spelling Bee game.
* Tic_Tac_Toe/ — Code files and assets for the Tic Tac Toe game.
