from time import sleep

import serial

SERIAL_PORT = "COM8"  # Replace with your port (e.g., COM3 or /dev/ttyUSB0)
BAUD_RATE = 115200  # Standard baud rate for e-puck communication

def connect_to_epuck():
    try:
        print("Try to connect at", SERIAL_PORT)
        # Open the serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=None)
        #needed as the first command always gives an error
        send_command(ser, b'b\r')
        print("Connected to e-puck at", SERIAL_PORT)
        return ser
    except Exception as e:
        print("Failed to connect:", e)
        return None


def read_sensors(ser):
    sensors_string = []
    while len(sensors_string) !=9:
        sensors_string = send_command(ser, "".join(["N\r\n"]).encode("ascii"))
        sensors_string = sensors_string.split(",")
        sleep(0.01)
    sensors_string[8] = sensors_string[8].replace('\r\n',"")
    sensors_int = [int(sensor) for sensor in sensors_string[1:]]
    return sensors_int


def read_accelerometer(ser):
    accelerometer = send_command(ser, "A".encode("ascii"))
    print(accelerometer)


def send_command(ser, command, should_read_response = True):
    try:
        ser.write(command)
        print("Command sent:", command)
        if should_read_response:
            return ser.readline().decode()
    except Exception as e:
        print("Failed to send command:", e)


def set_motor_position(ser, left, right):
    send_command(ser, "".join(["P,", str(left), ",", str(right), "\r\n"]).encode("ascii"))


def read_motor_position(ser):
    response = []
    while len(response) != 3:
        response = send_command(ser, "".join(["Q\r\n"]).encode("ascii"))
        response = str.split(response, ",")
    return response[1], response[2]


def set_motor_speed(ser, left, right):
    send_command(ser, "".join(["D,", str(left), ",", str(right), "\r\n"]).encode("ascii"))
