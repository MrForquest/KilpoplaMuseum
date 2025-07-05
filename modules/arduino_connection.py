import sys
import serial
from serial.tools import list_ports


class ArduinoConnection:
    """
    class for creating a connection with the Arduino on the Serial port
    """

    def __init__(self, port, speed_connection=9600, timeout=0.080):
        """
        Parameters
        ----------
        port : str
            COM port to which the Arduino is connected
        speed_connection : int
            connection speed with Arduino
       """
        self.port = port
        self.ser = serial.Serial(port, speed_connection, timeout=timeout)

    def write(self, value):
        self.ser.write(bytearray(value, encoding='utf8'))

    def write_array(self, valuesOfBytes):
        self.ser.write(valuesOfBytes)

    def read(self, size=1):
        return self.ser.read(size=size)

    def readable(self):
        return self.ser.readable()


if __name__ == "__main__":
    port_name = "/dev/ttyUSB0"
    print("Доступные порты:")
    for port in list_ports.comports():
        print(port)
    print()

    ard_device = ArduinoConnection(port_name, 9600)
    while True:
        if ard_device.ser.readable():
            print(ard_device.read())
        # ch = input()
        # ard_device.write(ch)
