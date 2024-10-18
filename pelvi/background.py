# Prüfen, ob Pillow installiert ist
try:
    from PIL import Image, ImageTk
except ImportError:
    print("Pillow ist nicht installiert. Bitte installieren Sie es mit 'pip install Pillow'.")
    Image = None

def load_image_to_canvas(canvas, image_path, width, height):
    if Image:
        try:
            img = Image.open(image_path)
            img = img.resize((width, height))
            bg = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, image=bg, anchor='nw')
            canvas.image = bg  # Keep a reference to avoid garbage collection
        except Exception as e:
            print(f"Konnte das Imgae {image_path} nicht laden: {e}")
    else:
        print("Pillow ist nicht installiert. Kein Hintergundbild für die Leinwand möglich.")
