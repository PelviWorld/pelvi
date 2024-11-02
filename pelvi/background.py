from PIL import Image, ImageTk

def load_image_to_canvas(canvas, image_path, width, height):
    img = Image.open(image_path)
    img = img.resize((width, height))
    bg = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=bg, anchor='nw')
    canvas.image = bg  # Keep a reference to avoid garbage collection
