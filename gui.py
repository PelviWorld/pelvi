import tkinter as tk
from tkinter import ttk
from pelvi.pelvi import Pelvi
from pelvi.arduino import Arduino
from pelvi.canvasarea import CanvasArea

# Konfiguration
arduino_port = 'COM7'
arduino_baudrate = 115200

def move_to_xy(x, y):
    if is_inside_rectangle(x, y):
        print("Bewegung in den roten Bereich ist nicht erlaubt.")
        return False
    pelvi.move_axis_to("X", x)
    pelvi.move_axis_to("Y", y)
    arduino.send_coordinates('XY', pelvi.get_axis_value("X"), pelvi.get_axis_value("Y"))
    canvas_xy.update_point()
    return True

def click_canvas_xy(event):
    x = event.x
    y = event.y

    # Check if the clicked position is within the canvas boundaries
    if x < 0 or x > canvas_width_xy or y < 0 or y > canvas_height_xy:
        print("Klick außerhalb der Leinwand")
        return
    move_to_xy(x, y)

def is_inside_rectangle(x_mm, y_mm):
    return ((pelvi.get_blocked_area("X")[0] <= x_mm <= pelvi.get_blocked_area("X")[1])
            and (pelvi.get_blocked_area("Y")[0] <= y_mm <= pelvi.get_blocked_area("Y")[1]))

def move_to_ze0(z, e0):
    pelvi.move_axis_to("Z", z)
    pelvi.move_axis_to("E0", e0)
    arduino.send_coordinates('ZE0', pelvi.get_axis_value("Z"), pelvi.get_axis_value("E0"))
    canvas_ze0.update_point()

def click_canvas_ze0(event):
    move_to_ze0(event.x, event.y)

def move_to_e1(e1):
    pelvi.move_axis_to("E1", e1)
    arduino.send_coordinates('E1', pelvi.get_axis_value("E1"))
    canvas_e1.update_point()

def click_canvas_e1(event):
    move_to_e1(event.y)

def is_point_inside_rectangle(left, top, right, bottom):
    points = [(pelvi.get_axis_value("X"), pelvi.get_axis_value("Y"))]
    for x, y in points:
        if left <= x <= right and top <= y <= bottom:
            return True
    return False

def adjust_blocked_position(dx=0, dy=0):
    # Get current rectangle coordinates from pelvi
    rectangle_left, rectangle_right = pelvi.get_blocked_area("X")
    rectangle_top, rectangle_bottom = pelvi.get_blocked_area("Y")

    # Calculate new positions
    new_left = rectangle_left + dx
    new_top = rectangle_top + dy
    new_right = rectangle_right + dx
    new_bottom = rectangle_bottom + dy

    # Ensure the rectangle stays within the canvas boundaries
    if new_left < 0:
        new_left = 0
        new_right = rectangle_right - rectangle_left
    if new_top < 0:
        new_top = 0
        new_bottom = rectangle_bottom - rectangle_top
    if new_right > pelvi.get_axis_range("X"):
        new_right = pelvi.get_axis_range("X")
        new_left = pelvi.get_axis_range("X") - (rectangle_right - rectangle_left)
    if new_bottom > pelvi.get_axis_range("Y"):
        new_bottom = pelvi.get_axis_range("Y")
        new_top = pelvi.get_axis_range("Y") - (rectangle_bottom - rectangle_top)

    # Check if any point is within the new rectangle coordinates
    if is_point_inside_rectangle(new_left, new_top, new_right, new_bottom):
        print("Blockierte Position kann nicht auf den aktuellen Punkt verschoben werden.")
        return

    # Update pelvi blocked area data
    pelvi.update_blocked_area("X", new_left, new_right)
    pelvi.update_blocked_area("Y", new_top, new_bottom)

    canvas_xy.update_red_rectangle()

def move_by(axis, value):
    pelvi.move_axis_by(axis, value)
    if axis == 'X' or axis == 'Y':
        if move_to_xy(pelvi.get_axis_value("X"), pelvi.get_axis_value("Y")) is False:
            pelvi.move_axis_by(axis, -value)
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

def create_dc_motor_gui(canvas_frame):
    frame_motor = ttk.Frame(canvas_frame)
    frame_motor.grid(row=3, column=0, pady=10)
    label_motor = ttk.Label(frame_motor, text="DC-Motor-Steuerung")
    label_motor.grid(row=3, column=0, columnspan=3)
    btn_motor_reverse = ttk.Button(frame_motor, text="Motor Vorwärts", command=lambda: motor_command('MOTOR FORWARD'))
    btn_motor_reverse.grid(row=4, column=0, padx=3)
    btn_motor_stop = ttk.Button(frame_motor, text="Motor Stop", command=lambda: motor_command('MOTOR STOP'))
    btn_motor_stop.grid(row=5, column=0, columnspan=2, pady=4, padx=3)
    btn_motor_forward = ttk.Button(frame_motor, text="Motor Rückwärts", command=lambda: motor_command('MOTOR REVERSE'))
    btn_motor_forward.grid(row=4, column=1, padx=3)

def create_save_button_gui(canvas_frame):
    btn_save = ttk.Button(canvas_frame, text="Save", command=save_data)
    btn_save.grid(row=3, column=2, padx=3, pady=5)

def create_e1_frame(_canvas_e1, _canvas_frame):
    frame_e1 = ttk.Frame(_canvas_frame)
    frame_e1.grid(row=1, column= 2, padx=10, pady=10)
    button_frame_e1 = ttk.Frame(frame_e1)
    button_frame_e1.grid(pady=5)

    btn_e1_negative = ttk.Button(button_frame_e1, text='↓', command=lambda: move_by("E1", 10), width=3)
    btn_e1_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_e1_positive = ttk.Button(button_frame_e1, text='↑', command=lambda: move_by("E1", -10), width=3)
    btn_e1_positive.grid(row=1, column=0, padx=2, pady=2)
    return _canvas_e1

def create_ze0_frame(_canvas_ze0, _canvas_frame):
    frame_ze0 = ttk.Frame(_canvas_frame)
    frame_ze0.grid(row=1, column=1, padx=10, pady=10)
    button_frame_ze0 = ttk.Frame(frame_ze0)
    button_frame_ze0.grid(pady=5)

    btn_z_negative = ttk.Button(button_frame_ze0, text='←', command=lambda: move_by("Z", -10), width=3)
    btn_z_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_z_positive = ttk.Button(button_frame_ze0, text='→', command=lambda: move_by("Z", 10), width=3)
    btn_z_positive.grid(row=0, column=1, padx=2, pady=2)
    btn_e0_negative = ttk.Button(button_frame_ze0, text='↓', command=lambda: move_by("E0", 10), width=3)
    btn_e0_negative.grid(row=1, column=0, padx=2, pady=2)
    btn_e0_positive = ttk.Button(button_frame_ze0, text='↑', command=lambda: move_by("E0", -10), width=3)
    btn_e0_positive.grid(row=1, column=1, padx=2, pady=2)
    return _canvas_ze0

def create_xy_frame(_canvas_xy, _canvas_frame):
    frame_xy = ttk.Frame(_canvas_frame)
    frame_xy.grid(row=1, column=0, padx=4, pady=5)
    button_frame_xy = ttk.Frame(frame_xy)
    button_frame_xy.grid(pady=5)

    btn_x_negative = ttk.Button(button_frame_xy, text='←', command=lambda: move_by("X", -10), width=3)
    btn_x_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_x_positive = ttk.Button(button_frame_xy, text='→', command=lambda: move_by("X", 10), width=3)
    btn_x_positive.grid(row=0, column=1, padx=2, pady=2)
    btn_y_positive = ttk.Button(button_frame_xy, text='↓', command=lambda: move_by("Y", 10), width=3)
    btn_y_positive.grid(row=1, column=0, padx=2, pady=2)
    btn_y_negative = ttk.Button(button_frame_xy, text='↑', command=lambda: move_by("Y", -10), width=3)
    btn_y_negative.grid(row=1, column=1, padx=2, pady=2)

    # Zeichnen des roten Rechtecks
    canvas_xy.update_red_rectangle()

    # Steuerung für das rote Rechteck
    frame_rectangle = ttk.Frame(frame_xy)
    frame_rectangle.grid(pady=3)
    label_rectangle = ttk.Label(frame_rectangle, text="Rotes Rechteck bewegen")
    label_rectangle.grid(row=0, column=0, columnspan=2)

    button_frame_rectangle = ttk.Frame(frame_rectangle)
    button_frame_rectangle.grid(row=1, column=0, columnspan=2)

    btn_rectangle_x_negative = ttk.Button(button_frame_rectangle, text='←',
                                          command=lambda: adjust_blocked_position(-10, 0), width=3)
    btn_rectangle_x_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_rectangle_x_positive = ttk.Button(button_frame_rectangle, text='→',
                                          command=lambda: adjust_blocked_position(10, 0), width=3)
    btn_rectangle_x_positive.grid(row=0, column=1, padx=2, pady=2)
    btn_rectangle_y_positive = ttk.Button(button_frame_rectangle, text='↓',
                                          command=lambda: adjust_blocked_position(0, 10), width=3)
    btn_rectangle_y_positive.grid(row=1, column=0, padx=2, pady=2)
    btn_rectangle_y_negative = ttk.Button(button_frame_rectangle, text='↑',
                                          command=lambda: adjust_blocked_position(0, -10), width=3)
    btn_rectangle_y_negative.grid(row=1, column=1, padx=2, pady=2)

    return _canvas_xy

def create_canvas_frame(_root):
    _canvas_frame = ttk.Frame(_root)
    _canvas_frame.pack(side=tk.TOP, padx=4, pady=5)
    return _canvas_frame

def create_canvas_areas():
    global canvas_xy, canvas_ze0, canvas_e1

    canvas_frame = ttk.Frame(root)
    canvas_frame.grid(row=0, column=0, padx=4, pady=5)

    canvas_xy = CanvasArea(
        canvas_frame, pelvi, "X", "Y", canvas_width_xy, canvas_height_xy,
        'background_xy.png', click_canvas_xy
    )
    canvas_xy.create_axes_lines(0, 0)
    canvas_xy.canvas.grid(row=0, column=0, padx=4, pady=5)
    create_xy_frame(canvas_xy, canvas_frame)

    canvas_ze0 = CanvasArea(
        canvas_frame, pelvi, "Z", "E0", canvas_width_ze0, canvas_height_ze0,
        'background_ze0.png', click_canvas_ze0
    )
    canvas_ze0.create_axes_lines(0, 0)
    canvas_ze0.canvas.grid(row=0, column=1, padx=4, pady=5)
    create_ze0_frame(canvas_ze0, canvas_frame)

    canvas_e1 = CanvasArea(
        canvas_frame, pelvi,"E1", "E1", canvas_width_e1, canvas_height_e1,
        'background_e1.png', click_canvas_e1
    )
    canvas_e1.create_axes_lines(50, 0)
    canvas_e1.canvas.grid(row=0, column=2, padx=4, pady=5)
    create_e1_frame(canvas_e1, canvas_frame)

    create_dc_motor_gui(canvas_frame)

    create_save_button_gui(canvas_frame)

def create_main_window():
    _root = tk.Tk()
    _root.title("Koordinatensteuerung")
    style = ttk.Style()
    style.theme_use('clam')
    return _root

if __name__ == '__main__':
    global canvas_xy, canvas_ze0, canvas_e1
    pelvi = Pelvi()
    arduino = Arduino(arduino_port, arduino_baudrate)

    root = create_main_window()

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
    create_canvas_areas()


    arduino.send_coordinates('XY', pelvi.get_axis_value("X"), pelvi.get_axis_value("Y"))
    arduino.send_coordinates('ZE0', pelvi.get_axis_value("Z"), pelvi.get_axis_value("E0"))
    arduino.send_coordinates('E1', pelvi.get_axis_value("E1"))
    canvas_xy.update_point()
    canvas_ze0.update_point()
    canvas_e1.update_point()

    # Hauptschleife starten
    root.mainloop()
