import serial
import math


SERIAL_PORT = "COM8"  # Replace with your port (e.g., COM3 or /dev/ttyUSB0)
BAUD_RATE = 115200  # Standard baud rate for e-puck communication
MM_PRO_STEP = 0.13
ABSTAND_RAEDER_IN_MM = 53
VIERTEL_KREIS = 1/4 * math.pi * ABSTAND_RAEDER_IN_MM
NEEDED_STEPS_FOR_90_DEGREE = VIERTEL_KREIS / MM_PRO_STEP
SIZE_ONE_CELL_IN_MM = 1600
NEEDED_STEPS_FOR_MOVING_ONE_CELL = SIZE_ONE_CELL_IN_MM / MM_PRO_STEP


def connect_to_epuck():
    try:
        # Open the serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
        #needed as the first command always gives an error
        send_command(ser, b'b\r')
        print("Connected to e-puck at", SERIAL_PORT)
        return ser
    except Exception as e:
        print("Failed to connect:", e)
        return None

def set_motor_position(ser, left, right):
    send_command(ser, str.join(["P,", left, ",", right, "\r\n"]).encode("ascii"))

def read_motor_position(ser):
    response = send_command(ser, str.join(["Q\r\n"]).encode("ascii"))
    if response == "":
        read_motor_position(ser)
    response = str.split(response, ",")
    return response[1], response[2]

def set_motor_speed(ser, left, right):
    send_command(ser, str.join(["D,", left, ",", right, "\r\n"]).encode("ascii"))

def turn_left(ser, speed):
    set_motor_speed(ser, -speed, speed)

def turn_right(ser, speed):
    set_motor_speed(ser, -speed, speed)

def stop_motor(ser):
    set_motor_speed(ser, 0, 0)

def turn90degree(ser, speed=500, clockwise=True):
    set_motor_position(ser, 0, 0)
    left, right = read_motor_position(ser)
    while abs(float(left)) < (NEEDED_STEPS_FOR_90_DEGREE -70): # 70 ist weil der Roboter noch nachdreht nachdem ausgelesen wurde
        if clockwise:
            turn_right(ser, speed)
        else:
            turn_left(ser, speed)
        left, right = read_motor_position(ser)

    # reset
    stop_motor(ser)
    set_motor_position(ser, 0,0)

def moveOneCellStraight(ser, speed=1000):
    set_motor_position(ser, 0, 0)
    left, right = read_motor_position(ser)
    while abs(float(left)) < (NEEDED_STEPS_FOR_MOVING_ONE_CELL - 70):  # 70 ist weil der Roboter noch nachdreht nachdem ausgelesen wurde
        set_motor_speed(speed)
        left, right = read_motor_position(ser)

    # reset
    stop_motor(ser)
    set_motor_position(ser, 0, 0)

def send_command(ser, command, should_read_response):
    try:
        ser.write(command)
        print("Command sent:", command)
        if should_read_response:
            return ser.readline().decode()
    except Exception as e:
        print("Failed to send command:", e)