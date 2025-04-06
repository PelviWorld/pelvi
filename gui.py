import tkinter as tk
from tkinter import ttk

from screeninfo import get_monitors

from pelvi.pelvi import Pelvi
from pelvi.arduino import Arduino
from pelvi.canvasarea import CanvasArea
from pelvi.buttoncreator import create_canvas_xy, create_canvas_ze0_buttons, \
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
    monitor_height = monitor.height - 450

    # Calculate the ratio between the monitor and the pelvi
    pelvi_height = _pelvi.get_axis_range("Y") + _pelvi.get_axis_range("E0")
    scale = monitor_height / pelvi_height

    canvas_xy = create_canvas_xy(CanvasArea.create_canvas_area(
        root_canvas, _pelvi, _arduino, "X", "Y", pelvi.get_axis_range("X"), pelvi.get_axis_range("Y"),
        'ressources/background_xy.png', 0, 0, scale
    ), root_canvas)

    canvas_ze0 = create_canvas_ze0_buttons(CanvasArea.create_canvas_area(
        root_canvas, _pelvi, _arduino, "Z", "E0", pelvi.get_axis_range("Z"), pelvi.get_axis_range("E0"),
        'ressources/background_ze0.png', 1, 0, scale
    ), root_canvas)

    create_canvas_dc_motor_buttons(root_canvas, arduino)
    create_canvas_home_button(root_canvas, arduino, canvas_xy, canvas_ze0)
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

if __name__ == '__main__':
    pelvi = Pelvi()
    arduino = Arduino(arduino_port, arduino_baudrate)
    arduino.send_command('INIT')
    while not all(arduino.get_axis_max_value(axis) > 0 for axis in ["X", "Y", "Z", "E0"]):
        pass
    axes_max_correct = True
    for axis in ["X", "Y", "Z", "E0"]:
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
    arduino.send_coordinates('X', pelvi.get_axis_value("X"))
    arduino.send_coordinates('Y', pelvi.get_axis_value("Y"))
    arduino.send_coordinates('Z', pelvi.get_axis_value("Z"))
    arduino.send_coordinates('E0', pelvi.get_axis_value("E0"))

    # Hauptschleife starten
    root.mainloop()
