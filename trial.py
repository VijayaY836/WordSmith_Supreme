from tkinter import Tk, Button, PhotoImage
import math

def button_click():
    print("Hexagon button clicked!")

root = Tk()
root.title("Hexagon Button Example")

# Load the hexagonal image (ensure the background is transparent or matches your desired button color)
try:
    image = PhotoImage(file="hexagon_button.png")  # Replace with your image file
except:
    print("Error loading image. Make sure the file exists and is a valid image format.")
    exit()


# Create the button with the image
button = Button(root, image=image, borderwidth=0, highlightthickness=0, command=button_click)
button.pack()

root.mainloop()