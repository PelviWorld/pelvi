import tkinter as tk
from tkinter import ttk
from pelvi.pelvi import Pelvi
from pelvi.arduino import Arduino
from pelvi.canvasarea import CanvasArea
from pelvi.buttoncreator import create_canvas_xy, create_canvas_ze0_buttons, create_canvas_e1_buttons, create_canvas_dc_motor_buttons, create_canvas_save_button

# Konfiguration
arduino_port = 'COM7'
arduino_baudrate = 115200

def create_canvas_areas():
    root_canvas = ttk.Frame(root)
    root_canvas.grid(row=0, column=0, padx=4, pady=5)

    create_canvas_xy(CanvasArea.create_canvas_area(
        root_canvas, pelvi, "X", "Y", pelvi.get_axis_range("X"), pelvi.get_axis_range("Y"),
        'background_xy.png', 0, 0
    ), root_canvas)

    create_canvas_ze0_buttons(CanvasArea.create_canvas_area(
        root_canvas, pelvi, "Z", "E0", pelvi.get_axis_range("Z"), pelvi.get_axis_range("E0"),
        'background_ze0.png', 0, 1
    ), root_canvas)

    create_canvas_e1_buttons(CanvasArea.create_canvas_area(
        root_canvas, pelvi, "E1", "E1", 100, pelvi.get_axis_range("E1"),
        'background_e1.png', 0, 2
    ), root_canvas)

    create_canvas_dc_motor_buttons(root_canvas, arduino)
    create_canvas_save_button(root_canvas, pelvi)

def create_main_window():
    _root = tk.Tk()
    _root.title("Koordinatensteuerung")
    ttk.Style().theme_use('clam')
    return _root

if __name__ == '__main__':
    pelvi = Pelvi()
    arduino = Arduino(arduino_port, arduino_baudrate)
    root = create_main_window()
    create_canvas_areas()

    # Startpositionen setzen
    arduino.send_coordinates('XY', pelvi.get_axis_value("X"), pelvi.get_axis_value("Y"))
    arduino.send_coordinates('ZE0', pelvi.get_axis_value("Z"), pelvi.get_axis_value("E0"))
    arduino.send_coordinates('E1', pelvi.get_axis_value("E1"))

    # Hauptschleife starten
    root.mainloop()
