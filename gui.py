import tkinter as tk
from tkinter import ttk
import serial
import time
import sys
import os

# Prüfen, ob Pillow installiert ist
try:
    from PIL import Image, ImageTk
except ImportError:
    print("Pillow ist nicht installiert. Bitte installieren Sie es mit 'pip install Pillow'.")
    Image = None

# Funktion, um zu prüfen, ob der Arduino verbunden ist
def is_arduino_connected(port):
    try:
        ser = serial.Serial('COM7', 115200)
        ser.close()
        return True
    except:
        return False

# Konfiguration der seriellen Verbindung
arduino_port = 'COM7'  # Passen Sie den Port an
arduino_connected = is_arduino_connected(arduino_port)

if arduino_connected:
    arduino = serial.Serial(arduino_port, 115200)
    time.sleep(2)  # Warten, bis die Verbindung hergestellt ist
else:
    # Mock-Serial-Klasse
    class MockSerial:
        def write(self, data):
            print(f"Gesendet (Mock): {data.decode().strip()}")

        def close(self):
            print("Mock-Serial-Verbindung geschlossen.")

    arduino = MockSerial()
    print("Arduino nicht verbunden. Verwende Mock-Serial-Klasse.")

# Maximale Achsenpositionen
X_MAX_POS = 300.0
Y_MAX_POS = 470.0
Z_MAX_POS = 290.0
E0_MAX_POS = 180.0
E1_MAX_POS = 180.0

# Aktuelle Positionen
current_x = 0
current_y = 0
current_z = 0
current_e0 = 0
current_e1 = 0

# IDs der Punkte auf den Canvas
point_xy = None
point_ze0 = None
point_e1 = None

# Hauptfenster erstellen
root = tk.Tk()
root.title("Koordinatensteuerung")

# Style für ttk Widgets festlegen
style = ttk.Style()
style.theme_use('clam')

# Größe des Koordinatensystems festlegen
canvas_width_xy = 300
canvas_height_xy = 470

scale_x = canvas_width_xy / X_MAX_POS
scale_y = canvas_height_xy / Y_MAX_POS

# Für ZE0 Canvas
canvas_width_ze0 = 290
canvas_height_ze0 = 180

scale_z = canvas_width_ze0 / Z_MAX_POS
scale_e0 = canvas_height_ze0 / E0_MAX_POS

# Für E1 Canvas
canvas_width_e1 = 100
canvas_height_e1 = E1_MAX_POS

scale_e1 = canvas_height_e1 / E1_MAX_POS

# Roter Kreis im XY-Feld
circle_center_x_mm = 200.0
circle_center_y_mm = 120.0
circle_radius_mm = 60.0  # Durchmesser 120 mm, also Radius 60 mm

# Berechnung der Pixelkoordinaten des roten Kreises
circle_center_x_px = circle_center_x_mm * scale_x
circle_center_y_px = circle_center_y_mm * scale_y
circle_radius_px = circle_radius_mm * scale_x  # Annahme: scale_x und scale_y sind gleich

# Funktion zum Senden der Koordinaten
def send_coordinates(axis, *args):
    if arduino:
        if axis == 'XY':
            x_mm, y_mm = args
            command = f"XY {x_mm},{y_mm}\n"
            arduino.write(command.encode())
            print(f"Gesendet: {command.strip()}")
        elif axis == 'ZE0':
            z_mm, e0_mm = args
            command = f"ZE0 {z_mm},{e0_mm}\n"
            arduino.write(command.encode())
            print(f"Gesendet: {command.strip()}")
        elif axis == 'E1':
            e1_mm = args[0]
            command = f"E1 {e1_mm}\n"
            arduino.write(command.encode())
            print(f"Gesendet: {command.strip()}")
        elif axis == 'MOTOR':
            command = f"{args[0]}\n"
            arduino.write(command.encode())
            print(f"Gesendet: {command.strip()}")
    else:
        print("Arduino ist nicht verbunden.")

# Funktionen zum Bewegen und Aktualisieren der Positionen
def move_to_xy(x, y):
    global current_x, current_y
    # Überprüfung, ob die Zielposition innerhalb des roten Kreises liegt
    if is_inside_circle(x, y):
        print("Bewegung in den roten Kreis ist nicht erlaubt.")
        return
    current_x = max(0, min(X_MAX_POS, x))
    current_y = max(0, min(Y_MAX_POS, y))
    send_coordinates('XY', current_x, current_y)
    update_point_xy()

def update_point_xy():
    global point_xy
    x_pixel = current_x * scale_x
    y_pixel = current_y * scale_y
    if point_xy:
        canvas_xy.delete(point_xy)
    point_xy = canvas_xy.create_oval(x_pixel - 5, y_pixel -5, x_pixel +5, y_pixel +5, fill='blue')

def is_inside_circle(x_mm, y_mm):
    dx = x_mm - circle_center_x_mm
    dy = y_mm - circle_center_y_mm
    distance_squared = dx**2 + dy**2
    return distance_squared < circle_radius_mm**2

def move_to_ze0(z, e0):
    global current_z, current_e0
    current_z = max(0, min(Z_MAX_POS, z))
    current_e0 = max(0, min(E0_MAX_POS, e0))
    send_coordinates('ZE0', current_z, current_e0)
    update_point_ze0()

def update_point_ze0():
    global point_ze0
    z_pixel = current_z * scale_z
    e0_pixel = current_e0 * scale_e0
    if point_ze0:
        canvas_ze0.delete(point_ze0)
    point_ze0 = canvas_ze0.create_oval(z_pixel - 5, e0_pixel -5, z_pixel +5, e0_pixel +5, fill='blue')

def move_to_e1(e1):
    global current_e1
    current_e1 = max(0, min(E1_MAX_POS, e1))
    send_coordinates('E1', current_e1)
    update_point_e1()

def update_point_e1():
    global point_e1
    e1_pixel = current_e1 * scale_e1
    if point_e1:
        canvas_e1.delete(point_e1)
    point_e1 = canvas_e1.create_oval(45, e1_pixel -5, 55, e1_pixel +5, fill='blue')

# Funktionen zum Bewegen des roten Kreises
def move_circle_x_positive():
    adjust_circle_position(dx=10, dy=0)

def move_circle_x_negative():
    adjust_circle_position(dx=-10, dy=0)

def move_circle_y_positive():
    adjust_circle_position(dx=0, dy=-10)

def move_circle_y_negative():
    adjust_circle_position(dx=0, dy=10)

def adjust_circle_position(dx=0, dy=0):
    global circle_center_x_mm, circle_center_y_mm
    circle_center_x_mm = max(0, min(X_MAX_POS, circle_center_x_mm + dx))
    circle_center_y_mm = max(0, min(Y_MAX_POS, circle_center_y_mm + dy))
    update_red_circle()

def update_red_circle():
    global circle_center_x_px, circle_center_y_px, circle_radius_px
    # Aktualisieren der Pixelkoordinaten
    circle_center_x_px = circle_center_x_mm * scale_x
    circle_center_y_px = circle_center_y_mm * scale_y
    # Alten Kreis löschen und neuen zeichnen
    canvas_xy.delete('red_circle')
    canvas_xy.create_oval(
        circle_center_x_px - circle_radius_px,
        circle_center_y_px - circle_radius_px,
        circle_center_x_px + circle_radius_px,
        circle_center_y_px + circle_radius_px,
        fill='red',
        outline='',
        tags='red_circle'
    )

# Funktionen für die Buttons
def move_x_positive():
    move_to_xy(current_x + 10, current_y)

def move_x_negative():
    move_to_xy(current_x - 10, current_y)

def move_y_positive():
    move_to_xy(current_x, current_y + 10)

def move_y_negative():
    move_to_xy(current_x, current_y - 10)

def move_z_positive():
    move_to_ze0(current_z + 10, current_e0)

def move_z_negative():
    move_to_ze0(current_z - 10, current_e0)

def move_e0_positive():
    move_to_ze0(current_z, current_e0 + 10)

def move_e0_negative():
    move_to_ze0(current_z, current_e0 - 10)

def move_e1_positive():
    move_to_e1(current_e1 + 10)

def move_e1_negative():
    move_to_e1(current_e1 - 10)

# Funktionen für den DC-Motor
def motor_forward():
    send_coordinates('MOTOR', 'MOTOR FORWARD')
    print("Motor läuft rückwärts.")

def motor_reverse():
    send_coordinates('MOTOR', 'MOTOR REVERSE')
    print("Motor läuft vorwärts.")

def motor_stop():
    send_coordinates('MOTOR', 'MOTOR STOP')
    print("Motor gestoppt.")

# Frame für die Canvas und Buttons
canvas_frame = ttk.Frame(root)
canvas_frame.pack(side=tk.TOP, padx=10, pady=10)

# -------------------- XY Achsen --------------------
frame_xy = ttk.Frame(canvas_frame)
frame_xy.grid(row=0, column=0, padx=10)

canvas_xy = tk.Canvas(frame_xy, width=canvas_width_xy, height=canvas_height_xy)
canvas_xy.pack()

# Hintergrundbild für XY
if Image:
    try:
        img_xy = Image.open('background_xy.png')
        img_xy = img_xy.resize((canvas_width_xy, canvas_height_xy))
        bg_xy = ImageTk.PhotoImage(img_xy)
        canvas_xy.create_image(0, 0, image=bg_xy, anchor='nw')
    except:
        print("Konnte Hintergrundbild für XY nicht laden.")
else:
    print("Pillow nicht installiert. Kein Hintergrundbild für XY.")

# Zeichnen des roten Kreises
canvas_xy.create_oval(
    circle_center_x_px - circle_radius_px,
    circle_center_y_px - circle_radius_px,
    circle_center_x_px + circle_radius_px,
    circle_center_y_px + circle_radius_px,
    fill='red',
    outline='',
    tags='red_circle'  # Hinzugefügtes Tag für späteres Löschen
)

canvas_xy.create_line(0, 0, 0, canvas_height_xy, fill="black")  # Y-Achse
canvas_xy.create_line(0, 0, canvas_width_xy, 0, fill="black")  # X-Achse

def click_canvas_xy(event):
    x_mm = event.x / scale_x
    y_mm = event.y / scale_y
    if is_inside_circle(x_mm, y_mm):
        print("Klick innerhalb des roten Kreises. Keine Aktion.")
        return
    move_to_xy(x_mm, y_mm)

canvas_xy.bind("<Button-1>", click_canvas_xy)

button_frame_xy = ttk.Frame(frame_xy)
button_frame_xy.pack(pady=5)

btn_x_negative = ttk.Button(button_frame_xy, text='←', command=move_x_negative, width=3)
btn_x_negative.grid(row=0, column=0, padx=2)

btn_x_positive = ttk.Button(button_frame_xy, text='→', command=move_x_positive, width=3)
btn_x_positive.grid(row=0, column=1, padx=2)

btn_y_negative = ttk.Button(button_frame_xy, text='↓', command=move_y_negative, width=3)
btn_y_negative.grid(row=1, column=0, padx=2)

btn_y_positive = ttk.Button(button_frame_xy, text='↑', command=move_y_positive, width=3)
btn_y_positive.grid(row=1, column=1, padx=2)

# Steuerung für den roten Kreis
frame_circle = ttk.Frame(frame_xy)
frame_circle.pack(pady=5)

label_circle = ttk.Label(frame_circle, text="Roter Punkt bewegen")
label_circle.grid(row=0, column=0, columnspan=2)

btn_circle_x_negative = ttk.Button(frame_circle, text='←', command=move_circle_x_negative, width=3)
btn_circle_x_negative.grid(row=1, column=0, padx=2)

btn_circle_x_positive = ttk.Button(frame_circle, text='→', command=move_circle_x_positive, width=3)
btn_circle_x_positive.grid(row=1, column=1, padx=2)

btn_circle_y_negative = ttk.Button(frame_circle, text='↓', command=move_circle_y_negative, width=3)
btn_circle_y_negative.grid(row=2, column=0, padx=2)

btn_circle_y_positive = ttk.Button(frame_circle, text='↑', command=move_circle_y_positive, width=3)
btn_circle_y_positive.grid(row=2, column=1, padx=2)

# -------------------- ZE0 Achsen --------------------
frame_ze0 = ttk.Frame(canvas_frame)
frame_ze0.grid(row=0, column=1, padx=10)

canvas_ze0 = tk.Canvas(frame_ze0, width=canvas_width_ze0, height=canvas_height_ze0)
canvas_ze0.pack()

# Hintergrundbild für ZE0
if Image:
    try:
        img_ze0 = Image.open('background_ze0.png')
        img_ze0 = img_ze0.resize((canvas_width_ze0, canvas_height_ze0))
        bg_ze0 = ImageTk.PhotoImage(img_ze0)
        canvas_ze0.create_image(0, 0, image=bg_ze0, anchor='nw')
    except:
        print("Konnte Hintergrundbild für ZE0 nicht laden.")
else:
    print("Pillow nicht installiert. Kein Hintergrundbild für ZE0.")

canvas_ze0.create_line(0, 0, 0, canvas_height_ze0, fill="black")  # E0-Achse
canvas_ze0.create_line(0, 0, canvas_width_ze0, 0, fill="black")  # Z-Achse

def click_canvas_ze0(event):
    z_mm = event.x / scale_z
    e0_mm = event.y / scale_e0
    move_to_ze0(z_mm, e0_mm)

canvas_ze0.bind("<Button-1>", click_canvas_ze0)

button_frame_ze0 = ttk.Frame(frame_ze0)
button_frame_ze0.pack(pady=5)

btn_z_negative = ttk.Button(button_frame_ze0, text='←', command=move_z_negative, width=3)
btn_z_negative.grid(row=0, column=0, padx=2)

btn_z_positive = ttk.Button(button_frame_ze0, text='→', command=move_z_positive, width=3)
btn_z_positive.grid(row=0, column=1, padx=2)

btn_e0_negative = ttk.Button(button_frame_ze0, text='↓', command=move_e0_negative, width=3)
btn_e0_negative.grid(row=1, column=0, padx=2)

btn_e0_positive = ttk.Button(button_frame_ze0, text='↑', command=move_e0_positive, width=3)
btn_e0_positive.grid(row=1, column=1, padx=2)

# -------------------- E1 Achse --------------------
frame_e1 = ttk.Frame(canvas_frame)
frame_e1.grid(row=0, column=2, padx=10)

canvas_e1 = tk.Canvas(frame_e1, width=canvas_width_e1, height=canvas_height_e1)
canvas_e1.pack()

# Hintergrundbild für E1
if Image:
    try:
        img_e1 = Image.open('background_e1.png')
        img_e1 = img_e1.resize((canvas_width_e1, canvas_height_e1))
        bg_e1 = ImageTk.PhotoImage(img_e1)
        canvas_e1.create_image(0, 0, image=bg_e1, anchor='nw')
    except:
        print("Konnte Hintergrundbild für E1 nicht laden.")
else:
    print("Pillow nicht installiert. Kein Hintergrundbild für E1.")

canvas_e1.create_line(50, 0, 50, canvas_height_e1, fill="black")  # E1-Achse

def click_canvas_e1(event):
    e1_mm = event.y / scale_e1
    move_to_e1(e1_mm)

canvas_e1.bind("<Button-1>", click_canvas_e1)

button_frame_e1 = ttk.Frame(frame_e1)
button_frame_e1.pack(pady=5)

btn_e1_negative = ttk.Button(button_frame_e1, text='↓', command=move_e1_negative, width=3)
btn_e1_negative.pack()

btn_e1_positive = ttk.Button(button_frame_e1, text='↑', command=move_e1_positive, width=3)
btn_e1_positive.pack()

# -------------------- DC-Motor-Steuerung --------------------
frame_motor = ttk.Frame(root)
frame_motor.pack(pady=10)

label_motor = ttk.Label(frame_motor, text="DC-Motor-Steuerung")
label_motor.pack()

btn_motor_forward = ttk.Button(frame_motor, text="Motor Rückwärts", command=motor_forward)
btn_motor_forward.pack(side=tk.LEFT, padx=5)

btn_motor_reverse = ttk.Button(frame_motor, text="Motor Vorwärts", command=motor_reverse)
btn_motor_reverse.pack(side=tk.LEFT, padx=5)

btn_motor_stop = ttk.Button(frame_motor, text="Motor Stop", command=motor_stop)
btn_motor_stop.pack(side=tk.LEFT, padx=5)

# Hauptschleife starten
root.mainloop()

# Schließe die serielle Verbindung, wenn das Fenster geschlossen wird
if arduino_connected:
    arduino.close()
