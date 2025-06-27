import tkinter as tk
from PIL import Image, ImageTk
import math

class HexBoard:
    def __init__(self, root, letters, target_letter, callback):
        self.root = root
        self.letters = letters
        self.target_letter = target_letter
        self.callback = callback  # Function to call when a hex is clicked

        self.canvas = tk.Canvas(root, width=500, height=500, bg='white', highlightthickness=0)
        self.canvas.pack()

        # Load and resize hex images
        self.hex_leaf_img = Image.open("hex_leaf.png").resize((300, 300), Image.LANCZOS)
        self.hex_center_img = Image.open("hex_center.png").resize((300, 300), Image.LANCZOS)
        self.tk_hex_leaf = ImageTk.PhotoImage(self.hex_leaf_img)
        self.tk_hex_center = ImageTk.PhotoImage(self.hex_center_img)

        self.hex_positions = self.get_hex_positions(100, center=(250, 250))
        self.hex_ids = []
        self.text_ids = []
        for i, (x, y) in enumerate(self.hex_positions):
            letter = self.target_letter if i == 0 else self.letters[i]
            img = self.tk_hex_center if i == 0 else self.tk_hex_leaf

            image_id = self.canvas.create_image(x, y, image=img)
            text_id = self.canvas.create_text(x, y, text=letter.upper(), font=('Helvetica', 20, 'bold'), fill='black')

            self.hex_ids.append((image_id, letter))
            self.text_ids.append(text_id)

        # Bind click
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def get_hex_positions(self, size, center=(250, 250)):
        cx, cy = center
        dx = size * 0.75
        dy = size * math.sqrt(3) / 2
        return [
            (cx, cy),  # center
            (cx, cy - dy),  # top
            (cx + dx, cy - dy / 2),  # top-right
            (cx + dx, cy + dy / 2),  # bottom-right
            (cx, cy + dy),  # bottom
            (cx - dx, cy + dy / 2),  # bottom-left
            (cx - dx, cy - dy / 2),  # top-left
        ]

    def on_canvas_click(self, event):
        for i, ((img_id, letter), (x, y)) in enumerate(zip(self.hex_ids, self.hex_positions)):
            if self.point_in_hex(event.x, event.y, x, y, 50):  # 50 is radius
                print(f"Hex {i+1} clicked! Letter: {letter}")
                self.callback(letter)
                break

    def point_in_hex(self, px, py, hx, hy, size):
        dx = abs(px - hx) / size
        dy = abs(py - hy) / size
        return dy <= math.sqrt(3) * min(0.5, 1 - dx)
root = tk.Tk()
HexBoard(root, letters=["S", "T", "R", "I", "K", "E", "R"], target_letter="I", callback=lambda l: print(f"You selected: {l}"))
root.mainloop()
