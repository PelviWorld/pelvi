import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from screeninfo import get_monitors

from pelvi.pelvi import Pelvi
from pelvi.arduino import Arduino
from pelvi.canvasarea import CanvasArea
from pelvi.buttoncreator import create_canvas_back, create_canvas_seat, create_canvas_leg, \
    create_canvas_dc_motor_buttons, create_canvas_save_button, create_canvas_home_button
import configparser

# Read configuration
config = configparser.ConfigParser()
config.read('.config')

arduino_port: str = config['Arduino'].get('port')
arduino_baudrate: int = config['Arduino'].getint('baudrate')
testing: bool = config['General'].getboolean('testing', False) if config.has_section('General') else False

def create_canvas_areas(_pelvi,_arduino):
    root_canvas = ttk.Frame(root)
    root_canvas.grid(row=0, column=0, padx=4, pady=5)

    # Get the primary monitor's dimensions
    monitor = get_monitors()[0]
    monitor_height = monitor.height - 270

    # Calculate the ratio between the monitor and the pelvi
    pelvi_height = _pelvi.get_axis_range("Y1") + _pelvi.get_axis_range("Y2") + _pelvi.get_axis_range("Y3")
    scale = monitor_height / pelvi_height

    stop_button = tk.Button(
        root_canvas,
        text="STOP",
        bg="red",
        fg="white",
        font=("Arial", 32, "bold"),
        height=2,
        command=lambda: arduino.send_command("EMERGENCY_STOP")
    )
    stop_button.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

    canvas_back = create_canvas_back(CanvasArea.create_canvas_area(
        root_canvas, _pelvi, _arduino, "X1", "Y1", pelvi.get_axis_range("X1"), pelvi.get_axis_range("Y1"),
        'ressources/background_xy.png', 0, 0, scale
    ), root_canvas)

    canvas_seat = create_canvas_seat(CanvasArea.create_canvas_area(
        root_canvas, _pelvi, _arduino, "X2", "Y2", pelvi.get_axis_range("X2"), pelvi.get_axis_range("Y2"),
        'ressources/background_ze0.png', 1, 0, scale
    ), root_canvas)

    canvas_leg = create_canvas_leg(CanvasArea.create_canvas_area(
        root_canvas, _pelvi, _arduino, "Y3", "Y3", 100, pelvi.get_axis_range("Y3"),
        'ressources/background_e1.png', 2, 0, scale
    ), root_canvas)

    create_canvas_dc_motor_buttons(root_canvas, arduino)
    create_canvas_home_button(root_canvas, arduino, canvas_back, canvas_seat, canvas_leg)
    create_canvas_save_button(root_canvas, pelvi)

def create_main_window():
    _root = tk.Tk()
    _root.title("Koordinatensteuerung")
    _root.attributes('-zoomed', 1)
    if not testing:
        _root.attributes('-fullscreen', True)
        _root.attributes('-topmost', True)
        _root.update()
        _root.attributes('-topmost', False)
    ttk.Style().theme_use('clam')
    return _root


def check_serial_message(line):
    if line.startswith("Achse steht auf Endschalter"):
        messagebox.showinfo("Warnung", line)

if __name__ == '__main__':
    pelvi = Pelvi()
    arduino = Arduino(arduino_port, arduino_baudrate, check_serial_message)
    arduino.send_command('INIT')
    while not all(arduino.get_axis_max_value(axis) > 0 for axis in ["X1", "Y1", "X2", "Y2", "Y3"]):
        pass
    axes_max_correct = True
    for axis in ["X1", "Y1", "X2", "Y2", "Y3"]:
        if not pelvi.set_axis_max_value(axis, arduino.get_axis_max_value(axis)):
            axes_max_correct = False
            print(f"Axis max value {axis} changed")
        else:
            print(f"Axis max value {axis} not changed")

    if not axes_max_correct:
        pelvi.update_all_axis_max_values()
        print("Axis max values changed. Need to write it to db. Restart the application if somethings looks weird.")

    print("Arduino connected and send max axis values.")
    root = create_main_window()
    create_canvas_areas(pelvi, arduino)

    # Startpositionen setzen
    arduino.send_coordinates('X1', pelvi.get_axis_value("X1"))
    arduino.send_coordinates('Y1', pelvi.get_axis_value("Y1"))
    arduino.send_coordinates('X2', pelvi.get_axis_value("X2"))
    arduino.send_coordinates('Y2', pelvi.get_axis_value("Y2"))
    arduino.send_coordinates('Y3', pelvi.get_axis_value("Y3"))

    # Hauptschleife starten
    root.mainloop()
