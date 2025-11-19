🌟 WordSmith Supreme
The Ultimate Hexagonal Word-Crafting Challenge

WordSmith Supreme is a fast-paced, theme-based, hexagonal word-building game designed to sharpen vocabulary, reflexes, pattern-recognition, and linguistic creativity.
Built with Python, Tkinter, custom-designed honeycomb interfaces, and a structured JSON word-engine, this project combines gameplay, UI design, and algorithmic logic into a polished, dynamic experience.

🔷 Game Concept

Form as many valid English words as you can using the 7-letter hexagonal flower board.
Each round gives you a central letter + six surrounding ones, and your challenge is to discover every possible subword — from 3-letter basics to full 7-letter bangers.

Different difficulty modes tune the challenge, scoring, and allowed word lengths.

🎮 Key Features
⬣ Hexagonal Honeycomb Board

A fully functional, custom-built 7-hex flower arrangement:

Center tile + six leaf tiles

Built using Canvas + PhotoImage

Custom PNGs: hex_center.png, hex_leaf.png

Every tile is clickable & correctly mapped

Pressing a hex selects only that letter, no overlap or ghost-click issues

🧠 Difficulty Levels

Each difficulty defines what word lengths are allowed:

Level	Allowed Word Lengths	Notes
Easy	3 letters & above	For warm-up rounds
Medium	4 letters & above	Removes trivial words
Hard	5 letters & above	Pure sweat mode

All levels award bonus points for 7-letter words.
📚 Custom Word List Engine

No NLTK.
No external libraries.
No unpredictable dictionaries.

The game reads from a curated word_list.json that contains:

Root 7-letter word

All its valid subwords

Optional hints

Example:

"CAPTURE": {
  "subwords": ["cap", "cape", "care", "crate", "recap", "rapture", "capture"],
  "hints": ["Leave this for user to add"]
}

🖼️ Dynamic Background Themes

Every screen uses unique background art:

Welcome Screen

Start / Mode Select

Game Screen (5 themes: nature, space, tech, mythology, abstract)

End Screen

Ultimate Victory Screen

Images sit in /assets/, loaded via PhotoImage.

🎯 Game Flow

Player enters the welcome screen

Chooses difficulty

Hex-board loads with assigned letters

Player clicks tiles → word forms → checks against JSON

Score updates in real time

All-found → victory screen

Missed some → end screen

🗂️ Project Structure
/
│
├── venture.py              # Main game
├── word_list.json          # All root words, subwords, hints
├── hex_center.png          # Center tile graphics
├── hex_leaf.png            # Leaf tile graphics
├── assets/
│   ├── welcome_bg.png
│   ├── start_bg.png
│   ├── game_bg_1.png
│   ├── game_bg_2.png
│   ├── game_bg_3.png
│   ├── game_bg_4.png
│   ├── game_bg_5.png
│   ├── end_bg.png
│   ├── victory_bg.png
│
└── README.md               # (This file)

🛠️ Tech Stack

Python 3.10+

Tkinter (UI engine)

PIL / Pillow (image processing)

JSON (word database)

🚀 How to Run

Install dependencies:

pip install pillow


Place all PNGs in the working directory.

Run:

python venture.py

🌈 Future Enhancements

Timer mode

Daily puzzle mode

Global leaderboard (API-based)

Sound effects & animations

Multiplayer “Word Duel”

👑 Created By

Team WordSmith Supreme
Powered by logic, imagination, and a heroic amount of caffeine.
