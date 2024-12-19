import time

import serial
import math
from time import sleep

from objects.wall_information import WallInformation

SERIAL_PORT = "COM7"  # Replace with your port (e.g., COM3 or /dev/ttyUSB0)
BAUD_RATE = 115200  # Standard baud rate for e-puck communication
MM_PRO_STEP = 0.13
ABSTAND_RAEDER_IN_MM = 52.7
VIERTEL_KREIS = 1/4 * math.pi * ABSTAND_RAEDER_IN_MM
NEEDED_STEPS_FOR_90_DEGREE = VIERTEL_KREIS / MM_PRO_STEP
SIZE_ONE_CELL_IN_MM = 90
NEEDED_STEPS_FOR_MOVING_ONE_CELL = SIZE_ONE_CELL_IN_MM / MM_PRO_STEP
WALL_THRESHHOLD = 2500
WALL_THRESHHOLD_BACK = 1500
time_start = 0
time_end = 0
V_BASE = 500    # Base velocity for motors

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

def set_motor_position(ser, left, right):
    send_command(ser, "".join(["P,", str(left), ",", str(right), "\r\n"]).encode("ascii"))

def read_motor_position(ser):
    response = []
    while len(response) != 3:
        response = send_command(ser, "".join(["Q\r\n"]).encode("ascii"))
        response = str.split(response, ",")
        sleep(0.01)
    return response[1], response[2]

def set_motor_speed(ser, left, right):
    send_command(ser, "".join(["D,", str(left), ",", str(right), "\r\n"]).encode("ascii"))

def turn_left(ser, speed):
    set_motor_speed(ser, -speed, speed)

def turn_right(ser, speed):
    set_motor_speed(ser, speed, -speed)

def stop_motor(ser):
    set_motor_speed(ser, 0, 0)

def turn90degree(ser, clockwise=True):
    set_motor_position(ser, 0, 0)
    left, right = read_motor_position(ser)
    theshhold_dynamic_speed = 100
    tolerance = 1
    if clockwise:
        remaining_steps_left = NEEDED_STEPS_FOR_90_DEGREE - float(left)
        while remaining_steps_left > theshhold_dynamic_speed:
            set_motor_speed(ser, V_BASE, -V_BASE)
            left, right = read_motor_position(ser)
            remaining_steps_left = NEEDED_STEPS_FOR_90_DEGREE - float(left)
        while abs(remaining_steps_left) > tolerance:
            dynamic_speed = min(10*remaining_steps_left,V_BASE)
            set_motor_speed(ser, int(dynamic_speed), -int(dynamic_speed))
            left, right = read_motor_position(ser)
            remaining_steps_left = NEEDED_STEPS_FOR_90_DEGREE - float(left)
        set_motor_position(ser, 0, 0)
    else:
        remaining_steps_right = NEEDED_STEPS_FOR_90_DEGREE - float(right)
        while remaining_steps_right > theshhold_dynamic_speed:
            set_motor_speed(ser, V_BASE, -V_BASE)
            left, right = read_motor_position(ser)
            remaining_steps_right = NEEDED_STEPS_FOR_90_DEGREE - float(right)
        while abs(remaining_steps_right) > tolerance:
            dynamic_speed = min(10*remaining_steps_right,V_BASE)
            set_motor_speed(ser, int(dynamic_speed), -int(dynamic_speed))
            left, right = read_motor_position(ser)
            remaining_steps_right = NEEDED_STEPS_FOR_90_DEGREE - float(right)
        set_motor_position(ser, 0, 0)
    
    
    # reset
    stop_motor(ser)
    set_motor_position(ser, 0,0)

def move_one_cell_straight(ser, speed=1000):
    set_motor_position(ser, 0, 0)
    left, right = read_motor_position(ser)
    while abs(float(left)) < (NEEDED_STEPS_FOR_MOVING_ONE_CELL - 70):  # 70 ist weil der Roboter noch nachdreht nachdem ausgelesen wurde
        set_motor_speed(speed)
        left, right = read_motor_position(ser)

    # reset
    stop_motor(ser)
    set_motor_position(ser, 0, 0)

def read_sensors(ser):
    sensors = []
    while len(sensors) !=9:
        sensors = send_command(ser, "".join(["N\r\n"]).encode("ascii"))
        sensors = sensors.split(",")
        sleep(0.01)
    sensors[8] = sensors[8].replace('\r\n',"")
    return sensors[1:]

def read_accelerometer(ser):
    accelerometer = send_command(ser, "A".encode("ascii"))
    print(accelerometer)

def read_walls(ser):
    sensors = read_sensors(ser)
    front = left = right = back = False
    if int(sensors[0]) > WALL_THRESHHOLD and int(sensors[7]) > WALL_THRESHHOLD:
        front = True
    if int(sensors[5]) > WALL_THRESHHOLD:
        left = True
    if int(sensors[2]) > WALL_THRESHHOLD:
        right = True
    if int(sensors[4]) > WALL_THRESHHOLD_BACK and int(sensors[3]) > WALL_THRESHHOLD_BACK:
        back = True
    return WallInformation(front, back, left, right), sensors

def move_straight(ser):
    sensors = read_sensors(ser)
    right_sensor = sensors[1]
    left_sensor = sensors[6]
    difference_between_sensors = int(right_sensor) - int(left_sensor)
    print(difference_between_sensors)
    threshhold = 500
    if abs(difference_between_sensors) > threshhold:
        if difference_between_sensors > threshhold: # Linkskurve
            set_motor_speed(ser, 0, 200)
        elif difference_between_sensors < -threshhold: # Rechtskurve
            set_motor_speed(ser, 200,0)
        return False
    if abs(difference_between_sensors) < threshhold:
        set_motor_speed(ser, 400,400)
        return True


def move(ser):
    walls, sensors = read_walls(ser)
    right_sensor = sensors[1]
    left_sensor = sensors[6]
    difference_between_sensors = int(right_sensor) - int(left_sensor)
    if walls.left and walls.right:
        handle_left_and_right(difference_between_sensors, ser)
    if int(right_sensor) > 500 and int(left_sensor) < 500:
        wall_on_right(ser, int(right_sensor))
    elif int(left_sensor) > 500 and int(right_sensor) < 500:
        wall_on_left(ser, int(left_sensor))
    else:
        wall_none(ser)

def handle_left_and_right(difference_between_sensors, ser):
    threshhold = 1000
    while abs(difference_between_sensors) > threshhold:
        if difference_between_sensors > threshhold:  # Linkskurve
            set_motor_speed(ser, -20, 20)
        elif difference_between_sensors < -threshhold:  # Rechtskurve
            set_motor_speed(ser, 20, -20)
        print(difference_between_sensors)
        sensors = read_sensors(ser)
        right_sensor = sensors[1]
        left_sensor = sensors[6]
        difference_between_sensors = int(right_sensor) - int(left_sensor)
    set_motor_speed(ser, 200, 200)

def wall_on_right(ser, right_sensor, v_base = V_BASE):
    correction = 0
    if(int(right_sensor) > 1000):
        correction = v_base * 0.07
    if(int(right_sensor) < 1000):
        correction = -v_base * 0.07
    if(int(right_sensor) > 1200):
        correction = v_base * 0.2
    if(int(right_sensor) > 1500):
        correction = v_base * 0.8
    if(int(right_sensor) < 900):
        correction = -v_base * 0.2
    v_right = v_base + correction
    v_left = v_base - correction
    set_motor_speed(ser, int(v_left), int(v_right))

def wall_on_left(ser, left_sensor, v_base = V_BASE):
    correction = 0
    if(int(left_sensor) > 1000):
        correction = v_base * 0.07
    if(int(left_sensor) < 1000):
        correction = -v_base * 0.07
    if(int(left_sensor) > 1200):
        correction = v_base * 0.2
    if(int(left_sensor) > 1500):
        correction = v_base * 0.8
    if(int(left_sensor) < 900):
        correction = -v_base * 0.2
    v_right = v_base - correction
    v_left = v_base + correction
    set_motor_speed(ser, int(v_left), int(v_right))

def wall_on_left_and_right(ser, left_sensor, right_sensor, v_base = V_BASE):
    correction = 0
    diff_sensors = int(right_sensor) - int(left_sensor)
    if(diff_sensors > 0):
        correction = v_base * 0.07
    if(diff_sensors < 0):
        correction = -v_base * 0.07
    if(diff_sensors > 500):
        correction = v_base * 0.20
    if(diff_sensors < -500):
        correction = -v_base * 0.20
    if(diff_sensors > 1200):
        correction = v_base * 0.8
    if(correction < -1200):
        correction = -v_base * 0.8
    v_right = v_base + correction
    v_left = v_base - correction
    set_motor_speed(ser, int(v_left), int(v_right))

def wall_none(ser, v_base = V_BASE):
    set_motor_speed(ser, int(v_base), int(v_base))



def send_command(ser, command, should_read_response = True):
    try:
        ser.write(command)
        print("Command sent:", command)
        if should_read_response:
            return ser.readline().decode()
    except Exception as e:
        print("Failed to send command:", e)