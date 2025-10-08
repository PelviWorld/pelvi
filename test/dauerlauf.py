import sys
sys.path.append('..')
from pelvi.arduino import Arduino
from pelvi.pelvi import Pelvi

import configparser
import time
import json

# Read configuration
config = configparser.ConfigParser()
config.read('../.config')

arduino_port: str = config['Arduino'].get('port')
arduino_baudrate: int = config['Arduino'].getint('baudrate')
testing: bool = config['General'].getboolean('testing', False) if config.has_section('General') else False

axes = ["X1", "Y1", "X2", "Y2", "Y3"]
axis_map = {axis: 0 for axis in axes}
axes_status = {axis: False for axis in axes}
homing_done = False

with open('move_commands.json', 'r') as f:
    move_commands = json.load(f)

def check_movement():
    while all(axes_status[axis] for axis in axes):
        time.sleep(0.2)

def move_axis(arduino, axis, position):
    print("Fahre Achse {axis} zu Position {position}".format(axis=axis, position=position))
    set_axis_moving(axis)
    arduino.send_coordinates(axis, position)

def set_axis_position(axis, position):
    print("Axis {axis} erreicht Position {position}".format(axis=axis, position=position))
    axis_map[axis] = position

def set_axis_moving(axis):
    print("Achse {} startet".format(axis))
    axes_status[axis] = True

def set_axis_finished(axis):
    print("Achse {} ist angekommen".format(axis))
    axes_status[axis] = False

def parse_axis_message(line):
    # Erwartetes Format: "Axis X moved to 123"
    parts = line.split()
    if len(parts) >= 5 and parts[0] == "Axis" and parts[2] == "moved" and parts[3] == "to":
        axis = parts[1]
        try:
            position = int(parts[4])
            return axis, position
        except ValueError:
            print(f"Ungültige Positionsangabe: {parts[4]}")
    return None, None

def check_serial_message(line):
    global homing_done
    if line.startswith("Achse steht auf Endschalter"):
        print(f"Warnung {line}.")
    elif line.startswith("Axis"):
        axis, position = parse_axis_message(line)
        if axis is not None and position is not None:
            set_axis_position(axis, position)
            set_axis_finished(axis)
            print(f"Achse {axis} ist auf Position {position} angekommen.")
        else:
            print(f"Unbekanntes Format: {line}")
    elif line.startswith("Homing"):
        homing_done = True

if __name__ == '__main__':
    pelvi = Pelvi()
    arduino = Arduino(arduino_port, arduino_baudrate, check_serial_message)
    arduino.send_command('INIT')
    arduino.send_command('HOMING')
    while not homing_done:
        pass
    print("Homing abgeschlossen. Starting next steps.")

    for axis in axes:
        set_axis_moving(axis)
    while not all(arduino.get_axis_max_value(axis) > 0 for axis in axes):
        pass
    axes_max_correct = True
    for axis in axes:
        if not pelvi.set_axis_max_value(axis, arduino.get_axis_max_value(axis)):
            axes_max_correct = False
            print(f"Axis max value {axis} changed")
        else:
            print(f"Axis max value {axis} not changed")

    if not axes_max_correct:
        pelvi.update_all_axis_max_values()
        print("Axis max values changed. Need to write it to db. Restart the application if somethings looks weird.")

    print("Arduino connected and send max axis values.")

    for moves in move_commands:
        print(f"nächste/r Bewegungsbefehl/e: {moves}")
        for axis, position in moves:
            move_axis(arduino, axis, position)
        check_movement()

    check_movement()
    print("Tests sind abgeschlossen.")