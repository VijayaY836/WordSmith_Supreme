from tkinter import Tk, Button, PhotoImage
import math

root = Tk()
root.title("Honeycomb Hex Button Grid")

# Load the hexagonal image
image = PhotoImage(file="hexagon_button.png")  # Ensure transparent background

hex_buttons = []
button_size = 70  # Adjust based on your image
x_spacing = button_size * 3/4
y_spacing = button_size * math.sqrt(3)/2

# Coordinates for a 2D hexagon honeycomb grid
rows = 3
cols = 3
for row in range(rows):
    for col in range(cols):
        # Offset every other row to create the honeycomb effect
        x_offset = col * x_spacing
        y_offset = row * y_spacing

        if row % 2 == 1:
            x_offset += x_spacing / 2

        def make_callback(r=row, c=col):
            return lambda: print(f"Hexagon at ({r}, {c}) clicked!")

        button = Button(root, image=image, borderwidth=0, highlightthickness=0, command=make_callback())
        button.place(x=x_offset, y=y_offset)
        hex_buttons.append(button)

root.geometry("400x400")
root.mainloop()

