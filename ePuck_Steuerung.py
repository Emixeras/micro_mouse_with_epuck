import math

from ePuck_Communication import read_sensors, send_command
from objects.wall_information import read_walls
from objects.sensor_information import SensorInformation

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
    set_motor_position(ser, 0,0)

def move_one_cell_straight(ser):
    needed_stepps = NEEDED_STEPS_FOR_MOVING_ONE_CELL
    tolerance_stepps_distance = 1
    threshhold_dynamic_speed = 100
    threshhold_front_distance = 100
    tolerance_front_distance = 200
    front_goal = 3000
    set_motor_position(ser, 0, 0)
    wall_left = False
    wall_right = False
    wall_change = False
    sensors = SensorInformation(read_sensors(ser))
    if sensors.left > 500:
        wall_left =True
    if sensors.right > 500:
        wall_right = True

    while(True):
        # Frage Nach Wall Change
            # setze Needet Steps neu
        if not wall_change:
            if (sensors.left > 500 and not wall_left) or (sensors.left < 500 and wall_left):
                wall_change = True
            if (sensors.right > 500 and not wall_right) or (sensors.right < 500 and wall_right):
                wall_change = True
            if wall_change:
                set_motor_position(ser, 0,0)
                needed_stepps = NEEDED_STEPS_FOR_MOVING_ONE_CELL/2

        # Frage nach needet Stepps
        pos_left, pos_right = read_motor_position(ser)
        steps_to_go = needed_stepps - (int(pos_left)+int(pos_right))/2
        #Brake wenn nötige Schritte gegangen sind
        if(abs(steps_to_go)<tolerance_stepps_distance):
            break

        #berechnungen für Speed
        dynamic_speed = V_BASE
        if abs(steps_to_go) < threshhold_dynamic_speed:
            #ändere speed für Needed Steps (v_base)
            dynamic_speed = min(10 * steps_to_go, V_BASE)
        # Fragee Nach frontwall
        if sensors.front_right > threshhold_front_distance:
            # gehe in Modus für wand annäherung
            dynamic_speed = min((front_goal - sensors.front_right)/20,V_BASE)
            #TODO gucken ob es probleme mit der Seitenwand gibt.
        #Brake falls nahe genung an der Wand
        if(abs(sensors.front_right-front_goal)<tolerance_front_distance):
            break

        #Rufe die Wall run Methoden auf mit Vbase
        if sensors.front_side_right > 500 and sensors.front_side_left > 500:
            wall_on_left_and_right(ser, sensors.front_side_left, sensors.front_side_right, dynamic_speed)
        if sensors.front_side_right > 500 and sensors.front_side_left < 500:
            wall_on_right(ser, sensors.front_side_right, dynamic_speed)
        elif sensors.front_side_left > 500 and sensors.front_side_right < 500:
            wall_on_left(ser, sensors.front_side_left, dynamic_speed)
        else:
            wall_none(ser,dynamic_speed)
    # set motor 0 0 return
    set_motor_speed(ser, 0, 0)


def move_straight(ser):
    sensors = SensorInformation(read_sensors(ser))
    difference_between_sensors = sensors.front_side_right - sensors.front_side_left
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



