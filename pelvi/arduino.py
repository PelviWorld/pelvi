import time
import serial

class ArduinoMock:
    @staticmethod
    def write(data):
        print(f"Gesendet (Mock): {data.decode().strip()}")

    @staticmethod
    def close():
        print("Mock-Serial-Verbindung geschlossen.")

class Arduino:
    def __init__(self, port, baudrate=115200):
        self.__port = port
        self.__baudrate = baudrate
        self.__serial = None
        self.__serial_connection_timeout = 2
        self.__connect()

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

    def send_coordinates(self, axis, value):
        if self.__serial:
            command = f"{axis} {value}\n"
            self.__serial.write(command.encode())
            print(f"Gesendet: {command.strip()}")
        else:
            print("Arduino ist nicht verbunden.")
