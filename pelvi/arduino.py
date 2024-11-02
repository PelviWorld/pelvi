import time
import serial
import threading

class ArduinoMock:
    def __init__(self):
        self.buffer = []

    def write(self, data):
        command = data.decode().strip()
        if command == 'HOMING':
            self.buffer.append(b'Homing complete\n')
        elif command.startswith('MOTOR '):
            self.buffer.append(f'Motor command received {command}\n'.encode())
        elif command.startswith('X '):
            self.buffer.append(b'X axis moved\n')
        elif command.startswith('Y '):
            self.buffer.append(b'Y axis moved\n')
        elif command.startswith('Z '):
            self.buffer.append(b'Z axis moved\n')
        elif command.startswith('E0 '):
            self.buffer.append(b'E0 axis moved\n')
        elif command.startswith('E1 '):
            self.buffer.append(b'E1 axis moved\n')

    @staticmethod
    def close():
        print("Mock-Serial-Verbindung geschlossen.")

    @property
    def in_waiting(self):
        return len(self.buffer)

    def readline(self):
        if self.buffer:
            return self.buffer.pop(0)
        return b''

class Arduino:
    def __init__(self, port, baudrate=115200):
        self.__port = port
        self.__baudrate = baudrate
        self.__serial = None
        self.__serial_connection_timeout = 2
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

    def send_coordinates(self, axis, value):
        if self.__serial:
            command = f"{axis} {value}\n"
            self.__serial.write(command.encode())
            print(f"Gesendet: {command.strip()}")
        else:
            print("Arduino ist nicht verbunden.")

    def __start_serial_thread(self):
        self.__serial_thread = threading.Thread(target=self.__read_from_serial)
        self.__serial_thread.daemon = True
        self.__serial_thread.start()

    def __read_from_serial(self):
        while True:
            if self.__serial.in_waiting > 0:
                line = self.__serial.readline().decode('utf-8').rstrip()
                print(line)
            time.sleep(0.1)  # Small delay to prevent high CPU usage
