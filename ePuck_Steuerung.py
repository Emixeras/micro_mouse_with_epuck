import math

from ePuck_Communication import read_sensors, set_motor_position, read_motor_position, set_motor_speed
from objects.wall_information import read_walls
from objects.sensor_information import SensorInformation

FRONT_GOAL = 3000

TOLERANCE_FRONT_DISTANCE = 200

THRESHHOLD_FRONT_DISTANCE = 100

THRESHOLD_DYNAMIC_SPEED = 100

TOLERANCE_STEPS_DISTANCE = 1

SERIAL_PORT = "COM8"  # Replace with your port (e.g., COM3 or /dev/ttyUSB0)
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


def turn_left(ser, speed):
    set_motor_speed(ser, -speed, speed)

def turn_right(ser, speed):
    set_motor_speed(ser, speed, -speed)

def stop_motor(ser):
    set_motor_speed(ser, 0, 0)

def turn90degree(ser, clockwise=True):
    set_motor_position(ser, 0, 0)
    left, right = read_motor_position(ser)
    threshhold_dynamic_speed = 100
    tolerance = 1
    if clockwise:
        remaining_steps_left = NEEDED_STEPS_FOR_90_DEGREE - float(left)
        while remaining_steps_left > threshhold_dynamic_speed:
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
        while remaining_steps_right > threshhold_dynamic_speed:
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
    set_motor_position(ser, 0, 0)

def move_one_cell_straight(ser):
    needed_stepps = NEEDED_STEPS_FOR_MOVING_ONE_CELL

    wall_change = False

    walls, sensors = read_walls(ser)
    set_motor_position(ser, 0, 0)

    while(True):
        new_walls, sensors = read_walls(ser)
        # Frage Nach Wall Change
            # setze Needet Steps neu
        if not wall_change:
            if new_walls.left != walls.left or new_walls.right != walls.right:
                wall_change = True
            if wall_change:
                set_motor_position(ser, 0, 0)
                needed_stepps = NEEDED_STEPS_FOR_MOVING_ONE_CELL/2

        # Frage nach needet Stepps
        pos_left, pos_right = read_motor_position(ser)
        steps_to_go = needed_stepps - (int(pos_left)+int(pos_right))/2

        if have_moved_necessary_steps(steps_to_go) or close_enough_to_wall(sensors):
            break

        dynamic_speed = get_dynamic_speed(sensors, steps_to_go)

        move_accordingly_to_sensor_information(dynamic_speed, sensors, ser)
    # we are done so we stop the motors
    set_motor_speed(ser, 0, 0)


def move_accordingly_to_sensor_information(dynamic_speed, sensors, ser):
    if sensors.front_side_right > 500 and sensors.front_side_left > 500:
        wall_on_left_and_right(ser, sensors.front_side_left, sensors.front_side_right, dynamic_speed)
    if sensors.front_side_right > 500 and sensors.front_side_left < 500:
        wall_on_right(ser, sensors.front_side_right, dynamic_speed)
    elif sensors.front_side_left > 500 and sensors.front_side_right < 500:
        wall_on_left(ser, sensors.front_side_left, dynamic_speed)
    else:
        wall_none(ser, dynamic_speed)


def close_enough_to_wall(sensors):
    return abs(sensors.front_right - FRONT_GOAL) < TOLERANCE_FRONT_DISTANCE


def have_moved_necessary_steps(steps_to_go):
    return abs(steps_to_go) < TOLERANCE_STEPS_DISTANCE


def get_dynamic_speed(sensors, steps_to_go):
    dynamic_speed = V_BASE
    if abs(steps_to_go) < THRESHOLD_DYNAMIC_SPEED:
        # ändere speed für Needed Steps (v_base)
        dynamic_speed = min(10 * steps_to_go, V_BASE)
    # Fragee Nach frontwall
    if sensors.front_right > THRESHHOLD_FRONT_DISTANCE:
        # gehe in Modus für wand annäherung
        dynamic_speed = min((FRONT_GOAL - sensors.front_right) / 20, V_BASE)
        # TODO gucken ob es probleme mit der Seitenwand gibt.
    return dynamic_speed

#todo check if still necessary or can remove
def move_straight(ser):
    sensors = SensorInformation(read_sensors(ser))
    difference_between_sensors = sensors.front_side_right - sensors.front_side_left
    print(difference_between_sensors)
    threshhold = 500
    if abs(difference_between_sensors) > threshhold:
        if difference_between_sensors > threshhold: # Linkskurve
            set_motor_speed(ser, 0, 200)
        elif difference_between_sensors < -threshhold: # Rechtskurve
            set_motor_speed(ser, 200, 0)
        return False
    if abs(difference_between_sensors) < threshhold:
        set_motor_speed(ser, 400, 400)
        return True


def move(ser):
    walls, sensors = read_walls(ser)

    difference_between_sensors = sensors.front_side_right - sensors.front_side_left
    if walls.left and walls.right:
        handle_left_and_right(difference_between_sensors, ser)
    if sensors.front_side_right > 500 and sensors.front_side_left < 500:
        wall_on_right(ser, sensors.front_side_right)
    elif sensors.front_side_left > 500 and sensors.front_side_right < 500:
        wall_on_left(ser, sensors.front_side_left)
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
        sensors = SensorInformation(read_sensors(ser))

        difference_between_sensors = sensors.front_side_right - sensors.front_side_left
    set_motor_speed(ser, 200, 200)

def wall_on_right(ser, front_side_right_sensor, v_base = V_BASE):
    correction = 0
    if front_side_right_sensor > 1000:
        correction = v_base * 0.07
    if front_side_right_sensor < 1000:
        correction = -v_base * 0.07
    if front_side_right_sensor > 1200:
        correction = v_base * 0.2
    if front_side_right_sensor > 1500:
        correction = v_base * 0.8
    if front_side_right_sensor < 900:
        correction = -v_base * 0.2
    v_right = v_base + correction
    v_left = v_base - correction
    set_motor_speed(ser, int(v_left), int(v_right))

def wall_on_left(ser, front_side_left_sensor, v_base = V_BASE):
    correction = 0
    if front_side_left_sensor > 1000:
        correction = v_base * 0.07
    if front_side_left_sensor < 1000:
        correction = -v_base * 0.07
    if front_side_left_sensor > 1200:
        correction = v_base * 0.2
    if front_side_left_sensor > 1500:
        correction = v_base * 0.8
    if front_side_left_sensor < 900:
        correction = -v_base * 0.2
    v_right = v_base - correction
    v_left = v_base + correction
    set_motor_speed(ser, int(v_left), int(v_right))

def wall_on_left_and_right(ser, front_side_left_sensor, front_side_right_sensor, v_base = V_BASE):
    correction = 0
    diff_sensors = front_side_right_sensor - front_side_left_sensor
    if diff_sensors > 0:
        correction = v_base * 0.07
    if diff_sensors < 0:
        correction = -v_base * 0.07
    if diff_sensors > 500:
        correction = v_base * 0.20
    if diff_sensors < -500:
        correction = -v_base * 0.20
    if diff_sensors > 1200:
        correction = v_base * 0.8
    if correction < -1200:
        correction = -v_base * 0.8
    v_right = v_base + correction
    v_left = v_base - correction
    set_motor_speed(ser, int(v_left), int(v_right))

def wall_none(ser, v_base = V_BASE):
    set_motor_speed(ser, int(v_base), int(v_base))



