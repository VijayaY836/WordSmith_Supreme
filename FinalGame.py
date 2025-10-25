import tkinter as tk
from tkinter import messagebox
import random
import json
import os
import nltk
from nltk.corpus import words
from PIL import Image, ImageTk
from playsound3 import playsound
import threading
import pygame
import time
import smtplib
from email.message import EmailMessage

def play_sound(file):
    try:
        playsound(file)
    except Exception as e:
        print(f"Sound playback failed: {e}")



word_list = set(word.lower() for word in words.words() if word.isalpha() and len(word) >= 3)

class PlayerTracker:
    def __init__(self):
        self.words_entered = set()
        self.score = 0
        self.congrats_shown=False

    def add_word(self, word):
        if word not in self.words_entered:
            self.words_entered.add(word)
            self.score += 5
       
    def get_score(self):
        return self.score

    def get_words(self):
        return list(self.words_entered)

    def reset(self):
        self.words_entered.clear()
        self.score = 0


class WordGame:
    def set_background(self, image_name):
        self.bg_image = Image.open(image_name)
        self.bg_image = self.bg_image.resize((1000, 800))
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = tk.Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    def __init__(self, root):
        self.root = root
        self.root.title("WordSmith Supreme")
        self.root.geometry("1000x800")
        self.name = ""
        self.letters = []
        self.target_letter = ""
        self.valid_words = set()
        self.remaining_time = 60
        self.tracker = PlayerTracker()
        self.leaderboard_file = "leaderboard.json"
        self.load_leaderboard()
        self.quit_early = False
        self.music_playing = False
        self.music_thread = None
        self.music_muted = False
        self.timer_paused = False
        self.button_sound_on = True

        # Load images ONCE and keep as instance variables
        PETAL_SIZE = 120
        CENTER_SIZE = 120
        self.hex_leaf_img = ImageTk.PhotoImage(Image.open("hex_leaf.png").resize((PETAL_SIZE, PETAL_SIZE), Image.LANCZOS))
        self.hex_center_img = ImageTk.PhotoImage(Image.open("hex_center.png").resize((CENTER_SIZE, CENTER_SIZE), Image.LANCZOS))

        self.play_music()

        # Load word data from JSON
        with open("word_data.json", "r") as f:
            self.word_data = json.load(f)

        self.show_welcome_screen()

        self.completed_levels = set()
        self.total_levels = 5
        self.levels_unlocked = False  # Set to True if all levels completed once

        self.level_bonus_word = {
            1: "meadows",
            2: "orbital",
            3: "genomic",
            4: "citadel",
            5: "poetics"
        }

        self.level_labels = {
            1: "Whispers of the Wildwood",
            2: "Echoes in the Infinite",
            3: "The Clockwork Crucible",
            4: "Thrones of the Forgotten Time",
            5: "Talespinners' End"
        }
        self.level_themes = {
            1: "Nature",
            2: "Space",
            3: "Science and Tech",
            4: "History",
            5: "Literature and Books"
        }
        self.level_bg_map = {
            1: "nature.png",
            2: "space.png",
            3: "Science.png",
            4: "History.png",
            5: "Book.png"
        }
        self.honey_bg_map = {
            1: "#b6e7a6",  # Nature - light green
            2: "#b6d7e7",  # Space - light blue
            3: "#e7e6b6",  # Science & Tech - light yellow
            4: "#e7c6b6",  # History - light tan
            5: "#d1b6e7",  # Literature - light purple
        }

    def load_leaderboard(self):
        if os.path.exists(self.leaderboard_file):
            with open(self.leaderboard_file, 'r') as f:
                self.leaderboard = json.load(f)
        else:
            self.leaderboard = {}

    

    def save_leaderboard(self):
        with open(self.leaderboard_file, 'w') as f:
            json.dump(self.leaderboard, f, indent=2)
        print("Saved leaderboard:", self.leaderboard)

    def play_button_sound(self):
        if self.button_sound_on:
            threading.Thread(target=lambda: playsound("button.wav", block=False), daemon=True).start()

    def toggle_button_sound(self):
        self.button_sound_on = not self.button_sound_on
        if hasattr(self, "button_sound_btn"):
            self.button_sound_btn.config(
                text="Off button sound" if self.button_sound_on else "On button sound"
            )

    def show_welcome_screen(self):
        self.clear_screen()

        self.set_background("Bg.png")
        self.music_btn = tk.Button(self.root, text="Mute" if not self.music_muted else "Unmute", command=self.toggle_music, font=('Helvetica', 12), bg="#cccccc")
        self.music_btn.place(x=10, y=10)
        self.button_sound_btn = tk.Button(
            self.root,
            text="Off button sound" if self.button_sound_on else "On button sound",
            command=lambda: [self.play_button_sound(), self.toggle_button_sound()],
            font=('Helvetica', 12), bg="#cccccc"
        )
        self.button_sound_btn.place(x=120, y=10)
        welcome_label = tk.Label(
            self.root,
            text="Welcome warrior! Ready to jump in?",
            font=('Helvetica', 32, "bold"),
            bg="#f7f7f7"
        )
        welcome_label.place(relx=0.5, rely=0.35, anchor="center")

        start_btn = tk.Button(
            self.root,
            text="You bet!",
            font=('Helvetica', 24, "bold"),
            bg="#f0e68c",
            command=self.create_start_screen
        )
        start_btn.place(relx=0.5, rely=0.55, anchor="center")
        instr_btn = tk.Button(
            self.root,
            text="Instructions",
            font=('Helvetica', 16, "bold"),
            bg="#add8e6",
            command=self.show_instructions
        )
        instr_btn.place(relx=0.5, rely=0.65, anchor="center")
        

    def show_instructions(self):
        instructions = (
            "Instructions:\n"
            "- Choose a level and form words using the honeycomb letters.\n"
            "- Each word must include the target letter.\n"
            "- Guess at least 5 valid words to win the round.\n"
            "- Use the menu buttons to navigate between screens.\n"
            "- Have fun and challenge yourself!"
        )
        messagebox.showinfo("Instructions", instructions)

    def quit_to_levels(self):
        self.show_levels_screen()

    def create_start_screen(self):
        self.clear_screen()
        self.set_background("bg1.png")
        tk.Label(self.root, text="WELCOME!", font=('Helvetica', 16),bg="#e7e7e7").pack(pady=10)
        tk.Label(self.root, text="Enter Your Name:", font=('Helvetica', 16),bg="#69e3f5").pack(pady=20)
        self.name_entry = tk.Entry(self.root, font=('Helvetica', 14))
        self.name_entry.pack()

        tk.Button(self.root, text="Start Game", command=self.show_levels_screen, font=('Helvetica', 14), bg="#90ee90").pack(pady=10)
        tk.Button(self.root, text="Leaderboard", command=self.show_leaderboard, font=('Helvetica', 14), bg="#add8e6").pack(pady=10)
        tk.Button(self.root, text="Back", command=self.show_welcome_screen, font=('Helvetica', 12), bg="#f0e68c").pack(pady=10)
        self.music_btn = tk.Button(self.root, text="Mute" if not self.music_muted else "Unmute", command=self.toggle_music, font=('Helvetica', 12), bg="#cccccc")
        self.music_btn.place(x=10, y=10)
        self.button_sound_btn = tk.Button(
            self.root,
            text="Off button sound" if self.button_sound_on else "On button sound",
            command=lambda: [self.play_button_sound(), self.toggle_button_sound()],
            font=('Helvetica', 12), bg="#cccccc"
        )
        self.button_sound_btn.place(x=120, y=10)
        self.update_music_button()


    def start_game(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter your name.")
            return
        self.name = name
        self.tracker.reset()
        self.tracker.congrats_shown = False
        self.quit_early = False
        self.timer_paused = False 

        while True:
            self.main_word = random.choice(list(self.word_data.keys()))
            # Get unique letters in order of appearance
            unique_letters = []
            for ch in self.main_word.upper():
                if ch not in unique_letters:
                    unique_letters.append(ch)
            if len(unique_letters) != 7:
                continue  # Only use words with exactly 7 unique letters
            self.letters = unique_letters  # This will be ['S', 'T', 'A', 'P', 'L', 'E', 'R'] for STAPLER
            all_subwords = set(self.word_data[self.main_word]["subwords"])
            possible_targets = []
            for letter in self.letters:
                valid = {w for w in all_subwords if letter.lower() in w}
                if len(valid) >= 5:  # Lowered from 7 to 5
                    possible_targets.append((letter, valid))
            if possible_targets:
                self.target_letter, self.valid_words = random.choice(possible_targets)
                self.target_letter = self.target_letter.lower()
                break

        self.remaining_time = 60
        self.create_game_screen()


    def create_game_screen(self):
        self.clear_screen()
        self.set_background(self.level_bg_map.get(self.selected_level, "Bg.png"))
        tk.Label(self.root, text=f"Form words using the honeycomb!", font=('Helvetica', 16)).pack(pady=10)
        tk.Label(self.root, text=f"Target Letter: {self.target_letter.upper()}", font=('Helvetica', 16, "bold")).pack(pady=5)
        tk.Label(self.root, text=f"Guess any 5 words using the letter: {self.target_letter.upper()}", font=('Helvetica', 14), fg="blue").pack(pady=5)

        # --- Honeycomb Hexagon Grid ---
        HONEY_BG = self.honey_bg_map.get(self.selected_level, "#efbce7")
        self.hex_frame = tk.Frame(self.root, bg="", width=320, height=220)
        self.hex_frame.pack(pady=10)
        self.hex_frame.pack_propagate(False)

        PETAL_SIZE = 120
        CENTER_SIZE = 120
        

        positions = [
            (80, 10),    # top-left
            (200, 10),   # top-right
            (20, 100),   # left
            (260, 100),  # right
            (80, 190),   # bottom-left
            (200, 190),  # bottom-right
        ]
        center_pos = (140, 100)  # center

        self.selected_word = ""
        self.letter_buttons = []

        # Remove only one occurrence of the target letter for petals
        petal_letters = []
        target_used = False
        for l in self.letters:
            if l.lower() == self.target_letter and not target_used:
                target_used = True
                continue
            petal_letters.append(l)
        # Now petal_letters has 6 letters, target letter is in center

        # Place petals
        for i, (x, y) in enumerate(positions):
            letter = petal_letters[i]
            btn = tk.Button(
                self.hex_frame,
                image=self.hex_leaf_img,
                text=letter,
                compound="center",
                font=('Helvetica', 22, "bold"),
                fg="black",
                bd=0,
                highlightthickness=0,
                bg=HONEY_BG,
                activebackground=HONEY_BG,
                command=lambda l=letter: self.add_letter(l)
            )
            btn.place(x=x, y=y, width=PETAL_SIZE, height=PETAL_SIZE)
            self.letter_buttons.append(btn)

        # Center button (target letter)
        center_btn = tk.Button(
            self.hex_frame,
            image=self.hex_center_img,
            text=self.target_letter.upper(),
            compound="center",
            font=('Helvetica', 26, "bold"),
            fg="red",
            bd=0,
            highlightthickness=0,
            bg=HONEY_BG,
            activebackground=HONEY_BG,
            command=lambda: self.add_letter(self.target_letter.upper())
        )
        center_btn.place(x=center_pos[0], y=center_pos[1], width=CENTER_SIZE, height=CENTER_SIZE)

        self.hex_frame.config(width=360, height=300)
        side_btn_frame = tk.Frame(self.root, bg="")
        side_btn_frame.place(x=720,y=150)

        # Display current word
        self.word_label = tk.Label(self.root, text="", font=('Helvetica', 18, "bold"), fg="purple")
        self.word_label.pack(pady=5)

        # Submit and Clear buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Submit", command=self.submit_word, font=('Helvetica', 14), bg="#f0e57e").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_word, font=('Helvetica', 14), bg="#ffe4b5").pack(side="left", padx=5)

        self.timer_label = tk.Label(self.root, text=f"Time Left: {self.remaining_time}", font=('Helvetica', 14))
        self.timer_label.pack()

        self.guessed_label = tk.Label(self.root, text="Words Guessed: ", font=('Helvetica', 14))
        self.guessed_label.pack()

        self.feedback_label = tk.Label(self.root, text="", font=('Helvetica', 12), fg='red')
        self.feedback_label.pack()


        tk.Button(self.root, text="Back to Levels", command=self.show_levels_screen, font=('Helvetica', 12), bg="#ffb347").pack(pady=5)

        # Score label
        self.score_label = tk.Label(self.root, text=f"Score: {self.tracker.get_score()}", font=('Helvetica', 16, "bold"), fg="darkgreen", bg="#f0f0f0")
        self.score_label.place(x=820, y=50)  # Adjust x, y as needed for your layout

        # Back to Menu button with save functionality
        def back_to_menu_and_save():
            if self.name and (self.name not in self.leaderboard or self.tracker.get_score() > self.leaderboard[self.name]):
                self.leaderboard[self.name] = self.tracker.get_score()
                self.save_leaderboard()
            self.create_start_screen()

        tk.Button(self.root, text="Back to Menu", command=back_to_menu_and_save, font=('Helvetica', 12), bg="#f0e68c").pack(pady=10)
        self.pause_btn = tk.Button(self.root, text="Pause Timer", command=self.toggle_timer_pause, font=('Helvetica', 12), bg="#ffe066")
        self.pause_btn.pack(pady=10)

        # Music button
        self.music_btn = tk.Button(self.root, text="Mute" if not self.music_muted else "Unmute", command=self.toggle_music, font=('Helvetica', 12), bg="#cccccc")
        self.music_btn.place(x=10, y=10)
        self.button_sound_btn = tk.Button(
            self.root,
            text="Off button sound" if self.button_sound_on else "On button sound",
            command=lambda: [self.play_button_sound(), self.toggle_button_sound()],
            font=('Helvetica', 12), bg="#cccccc"
        )
        self.button_sound_btn.place(x=120, y=10)
        self.update_music_button()

        self.done_btn = tk.Button(side_btn_frame, text="Done", font=('Helvetica', 14), bg="#90ee90", command=lambda: self.end_game(True))
        self.done_btn.pack(pady=5)
        self.done_btn.config(state="disabled")  # Only enabled after 5 words guessed and user chooses to continue

        # Level name and theme label
        level_name = self.level_labels.get(self.selected_level, f"Level {self.selected_level}")
        level_theme = self.level_themes.get(self.selected_level, "")
        tk.Label(
            self.root,
            text=f"{level_name}  |  {level_theme}",
            font=('Helvetica', 18, "bold"),
            bg="#e7e7e7"
        ).pack(pady=15)

        self.update_timer()

    def toggle_timer_pause(self):
        self.timer_paused = not self.timer_paused
        if self.timer_paused:
            self.pause_btn.config(text="Resume Timer")
        else:
            self.pause_btn.config(text="Pause Timer")
            self.update_timer()

    def add_letter(self, letter):
        self.selected_word += letter.lower()
        self.word_label.config(text=self.selected_word)

    def show_continue_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Continue?")
        popup_width = 400
        popup_height = 150

        self.root.update_idletasks()  # Ensure the root window is fully rendered
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        x = root_x + (root_width // 2) - (popup_width // 2)
        y = root_y + (root_height // 2) - (popup_height // 2)

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        popup.configure(bg="#222244")
        
        tk.Label(
            popup,
            text="You've guessed 5 words!\nDo you want to continue guessing for a higher score?",
            font=('Helvetica', 12),
            bg="#222244",         # Label background
            fg="#f7e96b"          # Label text color
        ).pack(pady=20)

        btn_frame = tk.Frame(popup, bg="#222244")
        btn_frame.pack(pady=10)

        def yes_action():
            popup.destroy()
            self.timer_paused = True  # Stop the timer
            self.done_btn.config(state="normal")  # Enable the Done button

        def no_action():
            popup.destroy()
            self.end_game(True)

        tk.Button(btn_frame, text="Yes", width=10, command=yes_action, bg="#4caf50",).pack(side="left", padx=10)
        tk.Button(btn_frame, text="No", width=10, command=no_action, bg="#f44336").pack(side="right", padx=10)

    def clear_word(self):
        self.selected_word = ""
        self.word_label.config(text="")

    def submit_word(self):
        #if self.tracker.congrats_shown:
            #return
        word = self.selected_word.lower().strip()
        self.clear_word()
        if word in self.tracker.get_words():
            self.feedback_label.config(text="Repeated!", fg="red")
        elif word in self.valid_words and self.target_letter in word:
            # Check for bonus word
            bonus_word = self.level_bonus_word.get(self.selected_level, "")
            if word == bonus_word:
                self.tracker.add_word(word)
                self.tracker.score += 10  # Add 10 more for a total of 15
                self.update_score_label()  # <-- update here
                self.update_labels()
                if len(self.tracker.get_words()) == 5 and not self.tracker.congrats_shown:
                    self.tracker.congrats_shown = True
                    self.feedback_label.config(text="🎉 Congratulations! You've guessed 5 correct words! 🎉", fg="blue")
                    self.update_labels()
                    if not self.music_muted:
                        self.play_music()
                    self.show_continue_popup()
                    return
                else:
                    self.feedback_label.config(text="Accepted! Hidden word guessed! +15 score!", fg="green")
            else:
                self.tracker.add_word(word)
                self.update_score_label()  # <-- update here
                self.update_labels()
                if len(self.tracker.get_words()) == 5 and not self.tracker.congrats_shown:
                    self.tracker.congrats_shown = True
                    self.feedback_label.config(text="🎉 Congratulations! You've guessed 5 correct words! 🎉", fg="blue")
                    self.update_labels()
                    self.show_continue_popup()
                    return
                else:
                    self.feedback_label.config(text="Accepted! +5 score!", fg="green")
        else:
            self.feedback_label.config(text="Invalid Word!", fg="red")

    def update_labels(self):
        
        self.guessed_label.config(text=f"Words Guessed: {', '.join(self.tracker.get_words())}")

    def update_timer(self):
        if self.timer_paused:
            return
        if self.remaining_time > 0:
            self.timer_label.config(text=f"Time Left: {self.remaining_time}")
            self.remaining_time -= 1
            self.root.after(1000, self.update_timer)
        else:
            threading.Thread(target=play_sound).start()
            self.root.after(1000, self.end_game, False) 

    def end_game(self, won):
        self.clear_screen()
        self.set_background("Bg.png")
        tk.Label(self.root, text="Game Over", font=('Helvetica', 18, 'bold')).pack(pady=10)
        tk.Label(self.root, text=f"Score: {self.tracker.get_score()}", font=('Helvetica', 14)).pack(pady=5)
        tk.Label(self.root, text=f"Guessed Words: {', '.join(self.tracker.get_words())}", font=('Helvetica', 12)).pack(pady=5)
        missed = self.valid_words - set(self.tracker.get_words())
        tk.Label(self.root, text=f"Missed Words: {', '.join(missed)}", font=('Helvetica', 12), fg="gray").pack(pady=5)
        tk.Label(self.root, text="Suggest a word you think should be accepted, Level and target letter will be included!:", font=('Helvetica', 12)).pack(pady=(10, 2))
        self.suggestion_entry = tk.Entry(self.root, font=('Helvetica', 12), width=20)
        self.suggestion_entry.pack()
        tk.Button(self.root, text="Submit Suggestion", command=self.submit_suggestion, font=('Helvetica', 12), bg="#add8e6").pack(pady=5)

        if won:
            msg = "Onward and upward! March forth, word warrior!"
        else:
            msg = "Nice try! Refine your arsenal next time."
        tk.Label(self.root, text=msg, font=('Helvetica', 14, "italic")).pack(pady=10)

        # Only update if new score is higher
        if self.name not in self.leaderboard or self.tracker.get_score() > self.leaderboard[self.name]:
            self.leaderboard[self.name] = self.tracker.get_score()
        self.save_leaderboard()

        tk.Button(self.root, text="Back to Menu", command=self.create_start_screen, font=('Helvetica', 12), bg="#f0e68c").pack(pady=10)
        self.music_btn = tk.Button(self.root, text="Mute" if not self.music_muted else "Unmute", command=self.toggle_music, font=('Helvetica', 12), bg="#cccccc")
        self.music_btn.place(x=10, y=10)
        self.button_sound_btn = tk.Button(
            self.root,
            text="Off button sound" if self.button_sound_on else "On button sound",
            command=lambda: [self.play_button_sound(), self.toggle_button_sound()],
            font=('Helvetica', 12), bg="#cccccc"
        )
        self.button_sound_btn.place(x=120, y=10)
        self.update_music_button()
        # ...existing code in end_game()...

        tk.Button(self.root, text="Back to Levels", command=self.show_levels_screen, font=('Helvetica', 12), bg="#ffb347").pack(pady=5)

        # --- MUSIC CONTROL FOR VICTORY ---
        if won and self.music_playing and not self.music_muted:
            # Only play victory.wav if NOT a grand victory
            is_grand_victory = (
                hasattr(self, "selected_level")
                and len(self.completed_levels | {self.selected_level}) == self.total_levels
            )
            if not is_grand_victory:
                self.stop_music()
                def play_victory_and_resume():
                    try:
                        pygame.mixer.init()
                        victory = pygame.mixer.Sound("victory.wav")
                        victory.play()
                        time.sleep(victory.get_length())
                    except Exception as e:
                        print("Victory sound error:", e)
                    # Resume background music if not muted
                    if not self.music_muted:
                        self.play_music()
                threading.Thread(target=play_victory_and_resume, daemon=True).start()

        if won and hasattr(self, "selected_level"):
            self.completed_levels.add(self.selected_level)
            # If all levels completed, unlock all for replay
            # Special case: if dev and just finished level 5, show grand victory immediately
            if (
                (self.name.lower() == "dev" and self.selected_level == self.total_levels)
                or len(self.completed_levels) == self.total_levels
            ):
                self.levels_unlocked = True
                self.show_grand_victory()
                return

        # Show Next button if not last level and won
        if won and hasattr(self, "selected_level") and self.selected_level < self.total_levels:
            tk.Button(self.root, text="Next", command=lambda: self.start_level(self.selected_level + 1),
                      font=('Helvetica', 12), bg="#90ee90").pack(pady=10)

    def quit_game(self):
        self.quit_early = True
        self.create_start_screen()

    def show_leaderboard(self):
        self.clear_screen()
        self.set_background("Leaderboard.png")
        tk.Label(self.root, text="Leaderboard- Top 10", font=('Helvetica', 18, 'bold')).pack(pady=10)
        sorted_leaderboard = sorted(self.leaderboard.items(), key=lambda x: x[1], reverse=True)
        for i, (player, score) in enumerate(sorted_leaderboard[:10], 1):
            tk.Label(self.root, text=f"{i}. {player} - {score} pts", font=('Helvetica', 12)).pack()

        tk.Button(self.root, text="Clear Leaderboard", command=self.clear_leaderboard, font=('Helvetica', 12), bg="#ffcccb").pack(pady=10)
        tk.Button(self.root, text="Back", command=self.create_start_screen, font=('Helvetica', 12), bg="#add8e6").pack(pady=10)
        self.music_btn = tk.Button(self.root, text="Mute" if not self.music_muted else "Unmute", command=self.toggle_music, font=('Helvetica', 12), bg="#cccccc")
        self.music_btn.place(x=10, y=10)
        self.button_sound_btn = tk.Button(
            self.root,
            text="Off button sound" if self.button_sound_on else "On button sound",
            command=lambda: [self.play_button_sound(), self.toggle_button_sound()],
            font=('Helvetica', 12), bg="#cccccc"
        )
        self.button_sound_btn.place(x=120, y=10)
        self.update_music_button()
    
    def clear_leaderboard(self):
        self.leaderboard = {}
        self.save_leaderboard()
        messagebox.showinfo("Reset", "Leaderboard cleared.")
        self.show_leaderboard()

    def clear_screen(self):
        
        for widget in self.root.winfo_children():
            widget.destroy()

    def play_music(self):
        if not hasattr(self, "music_initialized"):
            pygame.mixer.init()
            self.music_initialized = True
        if not self.music_muted:
            pygame.mixer.music.load("Audio.wav")
            pygame.mixer.music.play(-1)  # Loop forever
            self.music_playing = True
            self.update_music_button("Mute")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False
        self.update_music_button("Unmute")

    def toggle_music(self):
        if self.music_playing and not self.music_muted:
            self.music_muted = True
            self.stop_music()
        else:
            self.music_muted = False
            self.play_music()

    def update_music_button(self, text=None):
        if hasattr(self, "music_btn"):
            if text:
                self.music_btn.config(text=text)
            else:
                self.music_btn.config(text="Mute" if self.music_playing and not self.music_muted else "Unmute")


    def show_levels_screen(self):
    # Only check for name if name_entry exists AND is still a valid widget
        if hasattr(self, "name_entry") and self.name_entry.winfo_exists():
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showwarning("Input Error", "Please enter your name.")
                return
            self.name = name
        # Unlock all levels for dev
            if self.name.lower() == "dev":
                self.levels_unlocked = True
            else:
                self.levels_unlocked = False
    # ...rest of your code (do not change anything else)...
        self.clear_screen()
    # Load and display background
        bg_image = Image.open("image.png").resize((1000, 800))
        self.levels_bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self.root, image=self.levels_bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Level-to-word mapping
        self.level_word_map = {
            1: "MEADOWS",
            2: "ORBITAL",
            3: "GENOMIC",
            4: "CITADEL",
            5: "POETICS",
        }

        # Relative positions for buttons (x%, y%)
        button_rel_positions = [
            (0.45, 0.63),  # Level 1
            (0.48, 0.53),  # Level 2
            (0.51, 0.43),  # Level 3
            (0.54, 0.33),  # Level 4
            (0.57, 0.23)   # Level 5
        ]

        # Create level buttons
        for i, (rel_x, rel_y) in zip(range(1, 6), button_rel_positions):
            btn = tk.Button(
                self.root,
                text=f"Level {i}",
                bg="lightblue",
                font=("Arial", 14, "bold"),
                command=lambda level=i: (
                    self.start_level(level)
                    if self.levels_unlocked or level == 1 or all(l in self.completed_levels for l in range(1, level))
                    else messagebox.showinfo("Locked", "Slow down champ! Clear previous levels!")
                )
            )
            btn.place(relx=rel_x, rely=rel_y, anchor="center", width=100, height=50)
            # Add label beside the button
            tk.Label(
                self.root,
                text=self.level_labels[i],
                font=("Helvetica", 10, "italic"),
                bg="#e7e7e7"
            ).place(relx=rel_x + 0.09, rely=rel_y, anchor="w")

        # Music button
        self.music_btn = tk.Button(self.root, text="Mute" if not self.music_muted else "Unmute",
                                   command=self.toggle_music, font=('Helvetica', 12), bg="#cccccc")
        self.music_btn.place(x=10, y=10)
        self.button_sound_btn = tk.Button(
            self.root,
            text="Off button sound" if self.button_sound_on else "On button sound",
            command=lambda: [self.play_button_sound(), self.toggle_button_sound()],
            font=('Helvetica', 12), bg="#cccccc"
        )
        self.button_sound_btn.place(x=120, y=10)
        self.update_music_button()

        tk.Button(self.root, text="Back", command=self.create_start_screen, font=('Helvetica', 12), bg="#f0e68c").place(x=900, y=20)

    def start_level(self, level):
        self.selected_level = level
        self.main_word = self.level_word_map[level]
        unique_letters = []
        for ch in self.main_word.upper():
            if ch not in unique_letters:
                unique_letters.append(ch)
        self.letters = unique_letters
        all_subwords = set(self.word_data[self.main_word]["subwords"])
        possible_targets = []
        for letter in self.letters:
            valid = {w for w in all_subwords if letter.lower() in w}
            if len(valid) >= 5:  # Lowered threshold for smaller sets
                possible_targets.append((letter, valid))
        if possible_targets:
            self.target_letter, self.valid_words = random.choice(possible_targets)
            self.target_letter = self.target_letter.lower()
        else:
            # fallback: pick the letter with the most subwords
            best_letter = max(self.letters, key=lambda l: sum(l.lower() in w for w in all_subwords))
            valid = {w for w in all_subwords if best_letter.lower() in w}
            self.target_letter = best_letter.lower()
            self.valid_words = valid
        level_times = {1: 70, 2: 65, 3: 60, 4: 55, 5: 50}
        self.remaining_time = level_times.get(level, 60)
        self.tracker.reset()
        self.tracker.congrats_shown = False
        self.timer_paused = False
        self.create_game_screen()
        

    def show_grand_victory(self):
        self.clear_screen()
        self.set_background("Ultimate.png")
        tk.Label(self.root, text="GRAND VICTORY, WORDSMITH SUPREME!", font=('Helvetica', 32, "bold"), fg="#dbce59").pack(pady=40)
        tk.Label(self.root, text="You have conquered all levels! Thou art worthy of thy title!", font=('Helvetica', 18)).pack(pady=20)
        tk.Button(self.root, text="Back to Menu", command=self.create_start_screen, font=('Helvetica', 14), bg="#f0e68c").pack(pady=20)

        # Play UVictory.wav
        def play_ultimate_victory():
            try:
                pygame.mixer.init()
                ultimate = pygame.mixer.Sound("UVictory.wav")
                ultimate.play()
                time.sleep(ultimate.get_length())
            except Exception as e:
                print("Ultimate victory sound error:", e)
            # Resume background music if not mut
            if not self.music_muted:
                self.play_music()
        threading.Thread(target=play_ultimate_victory, daemon=True).start()

    def send_suggestion_email(self, player_name, suggested_word):
        try:
            email_sender = 'vijayayeditha8537@gmail.com'
            email_password = 'vsyw vipa huph rqcz' 
            email_receiver = 'vijayayeditha8537@gmail.com'

            subject = 'New Word Suggestion from WordSmith Game'
            level = getattr(self, "selected_level", "N/A")
            target_letter = getattr(self, "target_letter", "N/A")
            body = (
                f"Player: {player_name}\n"
                f"Suggested Word: {suggested_word}\n"
                f"Level: {level}\n"
                f"Target Letter: {target_letter.upper() if target_letter else 'N/A'}"
            )

            em = EmailMessage()
            em['From'] = email_sender
            em['To'] = email_receiver
            em['Subject'] = subject
            em.set_content(body)

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(email_sender, email_password)
                smtp.send_message(em)

        except Exception as e:
            print(f"Failed to send suggestion email: {e}")

    def submit_suggestion(self):
        suggested_word = self.suggestion_entry.get().strip().lower()
        if not suggested_word or not suggested_word.isalpha():
            messagebox.showwarning("Invalid Input", "Please enter a valid word.")
            return
        try:
            self.send_suggestion_email(self.name, suggested_word)
        except Exception as e:
            print(f"Suggestion email failed: {e}")
        # Always show this, even if email fails
        messagebox.showinfo("Suggestion Sent", "Thank you! Your suggestion has been sent.")
        self.suggestion_entry.delete(0, 'end')

    def update_score_label(self):
        if hasattr(self, "score_label"):
            self.score_label.config(text=f"Score: {self.tracker.get_score()}")

    

if __name__=="__main__":
    root = tk.Tk()
    app = WordGame(root)

    root.mainloop()