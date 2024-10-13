import tkinter as tk
from tkinter import ttk
from pelvi.pelvi import Pelvi
from pelvi.arduino import Arduino

# Konfiguration
arduino_port = 'COM7'
arduino_baudrate = 115200

# Prüfen, ob Pillow installiert ist
try:
    from PIL import Image, ImageTk
except ImportError:
    print("Pillow ist nicht installiert. Bitte installieren Sie es mit 'pip install Pillow'.")
    Image = None

def move_to_xy(x, y):
    if is_inside_circle(x, y):
        print("Bewegung in den roten Kreis ist nicht erlaubt.")
        return
    pelvi.move_axis_to("X", x)
    pelvi.move_axis_to("Y", y)
    arduino.send_coordinates('XY', pelvi.get_axis_value("X"), pelvi.get_axis_value("Y"))
    update_point_xy()

def click_canvas_xy(event):
    x_mm = event.x
    y_mm = event.y
    if is_inside_circle(x_mm, y_mm):
        print("Klick innerhalb des roten Kreises. Keine Aktion.")
        return
    move_to_xy(x_mm, y_mm)

def update_point_xy():
    global point_xy
    x_pixel = pelvi.get_axis_value("X")
    y_pixel = pelvi.get_axis_value("Y")
    if point_xy:
        canvas_xy.delete(point_xy)
    point_xy = canvas_xy.create_oval(x_pixel - 5, y_pixel - 5, x_pixel + 5, y_pixel + 5, fill='blue')

def is_inside_circle(x_mm, y_mm):
    dx = x_mm - circle_center_x_mm
    dy = y_mm - circle_center_y_mm
    distance_squared = dx**2 + dy**2
    return distance_squared < circle_radius_mm**2

def move_to_ze0(z, e0):
    pelvi.move_axis_to("Z", z)
    pelvi.move_axis_to("E0", e0)
    arduino.send_coordinates('ZE0', pelvi.get_axis_value("Z"), pelvi.get_axis_value("E0"))
    update_point_ze0()

def click_canvas_ze0(event):
    z_mm = event.x
    e0_mm = event.y
    move_to_ze0(z_mm, e0_mm)

def update_point_ze0():
    global point_ze0
    z_pixel = pelvi.get_axis_value("Z")
    e0_pixel = pelvi.get_axis_value("E0")
    if point_ze0:
        canvas_ze0.delete(point_ze0)
    point_ze0 = canvas_ze0.create_oval(z_pixel - 5, e0_pixel - 5, z_pixel + 5, e0_pixel + 5, fill='blue')

def move_to_e1(e1):
    pelvi.move_axis_to("E1", e1)
    arduino.send_coordinates('E1', pelvi.get_axis_value("E1"))
    update_point_e1()

def click_canvas_e1(event):
    e1_mm = event.y
    move_to_e1(e1_mm)

def update_point_e1():
    global point_e1
    e1_pixel = pelvi.get_axis_value("E1")
    if point_e1:
        canvas_e1.delete(point_e1)
    point_e1 = canvas_e1.create_oval(45, e1_pixel - 5, 55, e1_pixel + 5, fill='blue')

def adjust_circle_position(dx=0, dy=0):
    global circle_center_x_mm, circle_center_y_mm

    circle_center_x_mm = max(0, min(pelvi.get_axis_range("X"), circle_center_x_mm + dx))
    circle_center_y_mm = max(0, min(pelvi.get_axis_value("Y"), circle_center_y_mm + dy))
    update_red_circle()

def update_red_circle():
    global circle_center_x_mm, circle_center_y_mm, circle_radius_mm

    canvas_xy.delete('red_circle')

    canvas_xy.create_oval(
        circle_center_x_mm - circle_radius_mm,
        circle_center_y_mm - circle_radius_mm,
        circle_center_x_mm + circle_radius_mm,
        circle_center_y_mm + circle_radius_mm,
        fill='red',
        outline='',
        tags='red_circle'
    )

def move_by(axis, value):
    pelvi.move_axis_by(axis, value)
    if axis == 'X' or axis == 'Y':
        if is_inside_circle(pelvi.get_axis_value("X"), pelvi.get_axis_value("Y")):
            pelvi.move_axis_by(axis, -value)
            print("Bewegung in den roten Kreis ist nicht erlaubt.")
            return
        move_to_xy(pelvi.get_axis_value("X"), pelvi.get_axis_value("Y"))
    elif axis == 'Z' or axis == 'E0':
        move_to_ze0(pelvi.get_axis_value("Z"), pelvi.get_axis_value("E0"))
    elif axis == 'E1':
        move_to_e1(pelvi.get_axis_value("E1"))

def motor_command(command):
    arduino.send_coordinates('MOTOR', command)
    print(f"DC Motor-Befehl: {command}")

def save_data():
    pelvi.save_user_data()
    print("Data saved")

def create_dc_motor_gui():
    frame_motor = ttk.Frame(root)
    frame_motor.pack(pady=10)
    label_motor = ttk.Label(frame_motor, text="DC-Motor-Steuerung")
    label_motor.pack()
    btn_motor_forward = ttk.Button(frame_motor, text="Motor Rückwärts", command=lambda: motor_command('MOTOR FORWARD'))
    btn_motor_forward.pack(side=tk.LEFT, padx=5)
    btn_motor_reverse = ttk.Button(frame_motor, text="Motor Vorwärts", command=lambda: motor_command('MOTOR REVERSE'))
    btn_motor_reverse.pack(side=tk.LEFT, padx=5)
    btn_motor_stop = ttk.Button(frame_motor, text="Motor Stop", command=lambda: motor_command('MOTOR STOP'))
    btn_motor_stop.pack(side=tk.LEFT, padx=5)

def create_save_button_gui():
    btn_save = ttk.Button(root, text="Save", command=save_data)
    btn_save.pack(pady=10)

def create_e1_frame(_canvas_frame):
    frame_e1 = ttk.Frame(_canvas_frame)
    frame_e1.grid(row=0, column=2, padx=10)
    _canvas_e1 = tk.Canvas(frame_e1, width=canvas_width_e1, height=canvas_height_e1)
    _canvas_e1.pack()

    # Hintergrundbild für E1
    if Image:
        try:
            img_e1 = Image.open('background_e1.png')
            img_e1 = img_e1.resize((canvas_width_e1, canvas_height_e1))
            bg_e1 = ImageTk.PhotoImage(img_e1)
            _canvas_e1.create_image(0, 0, image=bg_e1, anchor='nw')
        except:
            print("Konnte Hintergrundbild für E1 nicht laden.")
    else:
        print("Pillow nicht installiert. Kein Hintergrundbild für E1.")
    _canvas_e1.create_line(50, 0, 50, canvas_height_e1, fill="black")  # E1-Achse
    _canvas_e1.bind("<Button-1>", click_canvas_e1)
    button_frame_e1 = ttk.Frame(frame_e1)
    button_frame_e1.pack(pady=5)
    btn_e1_negative = ttk.Button(button_frame_e1, text='↓', command=lambda: move_by("E1", 10), width=3)
    btn_e1_negative.pack()

    btn_e1_positive = ttk.Button(button_frame_e1, text='↑', command=lambda: move_by("E1", -10), width=3)
    btn_e1_positive.pack()
    return _canvas_e1

def create_ze0_frame(_canvas_frame):
    frame_ze0 = ttk.Frame(_canvas_frame)
    frame_ze0.grid(row=0, column=1, padx=10)
    _canvas_ze0 = tk.Canvas(frame_ze0, width=canvas_width_ze0, height=canvas_height_ze0)
    _canvas_ze0.pack()

    # Hintergrundbild für ZE0
    if Image:
        try:
            img_ze0 = Image.open('background_ze0.png')
            img_ze0 = img_ze0.resize((canvas_width_ze0, canvas_height_ze0))
            bg_ze0 = ImageTk.PhotoImage(img_ze0)
            _canvas_ze0.create_image(0, 0, image=bg_ze0, anchor='nw')
        except:
            print("Konnte Hintergrundbild für ZE0 nicht laden.")
    else:
        print("Pillow nicht installiert. Kein Hintergrundbild für ZE0.")
    _canvas_ze0.create_line(0, 0, 0, canvas_height_ze0, fill="black")  # E0-Achse
    _canvas_ze0.create_line(0, 0, canvas_width_ze0, 0, fill="black")  # Z-Achse
    _canvas_ze0.bind("<Button-1>", click_canvas_ze0)
    button_frame_ze0 = ttk.Frame(frame_ze0)
    button_frame_ze0.pack(pady=5)
    btn_z_negative = ttk.Button(button_frame_ze0, text='←', command=lambda: move_by("Z", -10), width=3)
    btn_z_negative.grid(row=0, column=0, padx=2)
    btn_z_positive = ttk.Button(button_frame_ze0, text='→', command=lambda: move_by("Z", 10), width=3)
    btn_z_positive.grid(row=0, column=1, padx=2)
    btn_e0_negative = ttk.Button(button_frame_ze0, text='↓', command=lambda: move_by("E0", 10), width=3)
    btn_e0_negative.grid(row=1, column=0, padx=2)
    btn_e0_positive = ttk.Button(button_frame_ze0, text='↑', command=lambda: move_by("E0", -10), width=3)
    btn_e0_positive.grid(row=1, column=1, padx=2)
    return _canvas_ze0

def create_xy_frame(_canvas_frame):
    frame_xy = ttk.Frame(_canvas_frame)
    frame_xy.grid(row=0, column=0, padx=10)
    _canvas_xy = tk.Canvas(frame_xy, width=canvas_width_xy, height=canvas_height_xy)
    _canvas_xy.pack()

    # Hintergrundbild für XY
    if Image:
        try:
            img_xy = Image.open('background_xy.png')
            img_xy = img_xy.resize((canvas_width_xy, canvas_height_xy))
            bg_xy = ImageTk.PhotoImage(img_xy)
            _canvas_xy.create_image(0, 0, image=bg_xy, anchor='nw')
        except:
            print("Konnte Hintergrundbild für XY nicht laden.")
    else:
        print("Pillow nicht installiert. Kein Hintergrundbild für XY.")

    # Zeichnen des roten Kreises
    _canvas_xy.create_oval(
        circle_center_x_mm - circle_radius_mm,
        circle_center_y_mm - circle_radius_mm,
        circle_center_x_mm + circle_radius_mm,
        circle_center_y_mm + circle_radius_mm,
        fill='red',
        outline='',
        tags='red_circle'  # Hinzugefügtes Tag für späteres Löschen
    )
    _canvas_xy.create_line(0, 0, 0, canvas_height_xy, fill="black")  # Y-Achse
    _canvas_xy.create_line(0, 0, canvas_width_xy, 0, fill="black")  # X-Achse
    _canvas_xy.bind("<Button-1>", click_canvas_xy)
    button_frame_xy = ttk.Frame(frame_xy)
    button_frame_xy.pack(pady=5)
    btn_x_negative = ttk.Button(button_frame_xy, text='←', command=lambda: move_by("X", -10), width=3)
    btn_x_negative.grid(row=0, column=0, padx=2)
    btn_x_positive = ttk.Button(button_frame_xy, text='→', command=lambda: move_by("X", 10), width=3)
    btn_x_positive.grid(row=0, column=1, padx=2)
    btn_y_positive = ttk.Button(button_frame_xy, text='↓', command=lambda: move_by("Y", 10), width=3)
    btn_y_positive.grid(row=1, column=0, padx=2)
    btn_y_negative = ttk.Button(button_frame_xy, text='↑', command=lambda: move_by("Y", -10), width=3)
    btn_y_negative.grid(row=1, column=1, padx=2)

    # Steuerung für den roten Kreis
    frame_circle = ttk.Frame(frame_xy)
    frame_circle.pack(pady=5)
    label_circle = ttk.Label(frame_circle, text="Roter Punkt bewegen")
    label_circle.grid(row=0, column=0, columnspan=2)
    btn_circle_x_negative = ttk.Button(frame_circle, text='←', command=lambda: adjust_circle_position(-10,0), width=3)
    btn_circle_x_negative.grid(row=1, column=0, padx=2)
    btn_circle_x_positive = ttk.Button(frame_circle, text='→', command=lambda: adjust_circle_position(10,0), width=3)
    btn_circle_x_positive.grid(row=1, column=1, padx=2)
    btn_circle_y_positive = ttk.Button(frame_circle, text='↓', command=lambda: adjust_circle_position(0,10), width=3)
    btn_circle_y_positive.grid(row=2, column=0, padx=2)
    btn_circle_y_negative = ttk.Button(frame_circle, text='↑', command=lambda: adjust_circle_position(0,-10), width=3)
    btn_circle_y_negative.grid(row=2, column=1, padx=2)
    return _canvas_xy

def create_canvas_frame(_root):
    _canvas_frame = ttk.Frame(_root)
    _canvas_frame.pack(side=tk.TOP, padx=10, pady=10)
    return _canvas_frame

def create_main_window():
    _root = tk.Tk()
    _root.title("Koordinatensteuerung")
    style = ttk.Style()
    style.theme_use('clam')
    return _root

if __name__ == '__main__':
    pelvi = Pelvi()
    arduino = Arduino(arduino_port, arduino_baudrate)

    root = create_main_window()
    canvas_frame = create_canvas_frame(root)

    # IDs der Punkte auf den Canvas
    point_xy = None
    point_ze0 = None
    point_e1 = None

    # Canvas-Größen from pelvi db
    canvas_width_xy = pelvi.get_axis_range("X")
    canvas_height_xy = pelvi.get_axis_range("Y")
    canvas_width_ze0 = pelvi.get_axis_range("Z")
    canvas_height_ze0 = pelvi.get_axis_range("E0")
    canvas_height_e1 = pelvi.get_axis_range("E1")

    # Set global variables to values
    canvas_width_e1 = 100
    circle_center_x_mm = 200.0
    circle_center_y_mm = 120.0
    circle_radius_mm = 60.0

    canvas_xy = create_xy_frame(canvas_frame)
    canvas_ze0 = create_ze0_frame(canvas_frame)
    canvas_e1 = create_e1_frame(canvas_frame)
    create_dc_motor_gui()
    create_save_button_gui()

    arduino.send_coordinates('XY', pelvi.get_axis_value("X"), pelvi.get_axis_value("Y"))
    arduino.send_coordinates('ZE0', pelvi.get_axis_value("Z"), pelvi.get_axis_value("E0"))
    arduino.send_coordinates('E1', pelvi.get_axis_value("E1"))
    update_point_xy()
    update_point_ze0()
    update_point_e1()

    # Hauptschleife starten
    root.mainloop()
