import time
import serial
import threading


class ArduinoMock:
    def __init__(self):
        self.buffer = []

    def write(self, data):
        command = data.decode().strip()
        if command == "INIT":
            self.buffer.append(b"AXIS X MAX 300.00\n")
            self.buffer.append(b"AXIS Y MAX 475.00\n")
            self.buffer.append(b"AXIS Z MAX 290.00\n")
            self.buffer.append(b"AXIS E0 MAX 180.00\n")
        if command == "HOMING":
            self.buffer.append(b"Homing complete\n")
        elif command.startswith("MOTOR "):
            self.buffer.append(f"Motor command received {command}\n".encode())
        else:
            self.write_axis(command)

    def write_axis(self, command):
        parts = command.split()
        for i in range(0, len(parts) - 1, 2):
            axis, value = parts[i], parts[i + 1]
            self.buffer.append(f"Axis {axis} moved to {value}\n".encode())

    @staticmethod
    def close():
        print("Mock-Serial-Verbindung geschlossen.")

    @property
    def in_waiting(self):
        return len(self.buffer)

    def readline(self):
        if self.buffer:
            return self.buffer.pop(0)
        return b""


class Arduino:
    def __init__(self, port, baudrate=115200, line_callback=None):
        self.__port = port
        self.__baudrate = baudrate
        self.__serial = None
        self.__serial_connection_timeout = 2
        self.__axis_max_value = {}
        self.__line_callback = line_callback
        self.__connect()
        self.__start_serial_thread()

    def __del__(self):
        if self.__serial is not None:
            self.__serial.close()

    def __connect(self):
        try:
            self.__serial = serial.Serial(self.__port, self.__baudrate)
            print(f"Verbindung zu {self.__port} hergestellt.")
        except:
            self.__serial = ArduinoMock()
            print("Arduino nicht verbunden. Verwende Mock-Serial-Klasse.")

    def write(self, data):
        self.__serial.write(data)

    def send_command(self, command):
        if self.__serial:
            self.__serial.write(command.encode())
            print(f"Gesendet: {command.strip()}")
        else:
            print("Arduino ist nicht verbunden.")

    def send_coordinates_multi(self, axis1, value1, axis2, value2):
        if self.__serial:
            command = f"{axis1} {value1} {axis2} {value2}\n"
            self.__serial.write(command.encode())
            print(f"Gesendet: {command.strip()}")
        else:
            print("Arduino ist nicht verbunden.")

    def send_coordinates(self, axis, value):
        if self.__serial:
            command = f"{axis} {value}\n"
            self.__serial.write(command.encode())
            print(f"Gesendet: {command.strip()}")
        else:
            print("Arduino ist nicht verbunden.")

    def get_axis_max_value(self, axis):
        return self.__axis_max_value.get(axis, 0)

    def __start_serial_thread(self):
        self.__serial_thread = threading.Thread(target=self.__read_from_serial)
        self.__serial_thread.daemon = True
        self.__serial_thread.start()

    def __read_axis_max_value(self, line):
        try:
            parts = line.split()
            axis = parts[1]
            max_value = int(float(parts[3]))
            self.__axis_max_value[axis] = max_value
            print(f"Maximalwert für {axis}: {max_value}")
        except (IndexError, ValueError):
            print(f"Fehler beim Parsen der Zeile: {line}")
            return

    def __read_from_serial(self):
        while True:
            if self.__serial.in_waiting > 0:
                line = self.__serial.readline().decode("utf-8").rstrip()
                print(line)
                if line.startswith("AXIS"):
                    self.__read_axis_max_value(line)
                else:
                    if self.__line_callback:
                        self.__line_callback(line)
                    else:
                        print("no interpreter for responses installed.")

            time.sleep(0.1)  # Small delay to prevent high CPU usage
