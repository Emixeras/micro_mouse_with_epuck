from time import sleep

from ePuck_Communication import connect_to_epuck, read_accelerometer
from ePuck_Steuerung import *
from micro_mouse_with_epuck.objects.sensor_information import SensorInformation

LABYRINTH_SIZE = 7
GOAL_X = 3
GOAL_Y = 4

def move_labyrinth(ser):
    move_one_cell_straight(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    move_one_cell_straight(ser)
    turn90degree(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    turn90degree(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    turn90degree(ser, False)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    turn90degree(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    turn90degree(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    move_one_cell_straight(ser)
    sleep(1)
    turn90degree(ser)
    sleep(1)
    move_one_cell_straight(ser)

if __name__ == "__main__":
    ser = connect_to_epuck()
    if ser:
        try:
            # time_elapsed=0
            # moving_straight=False
            # currently_measuring=False
            # time_start=0
            # while True:
            #     moving_straight = move_straight(ser)
            #     if moving_straight and not currently_measuring:
            #         time_start = time.time()
            #         currently_measuring = True
            #     if not moving_straight and currently_measuring:
            #         time_end = time.time()
            #         time_elapsed += time_end - time_start
            #         currently_measuring = False
            #     walls = read_walls(ser)
            #     if walls.front:
            #         set_motor_speed(ser, "0", "0")
            #         break
            #       #  set_motor_speed(ser, "200", "200")

            #while True:
                #print(sensors)
                #move_one_cell_straight(ser)
                #turn90degree(ser)
            #move_one_cell_straight(ser)
            move_labyrinth(ser)
        finally:
            # Close the connection
            ser.close()
            #print(time_elapsed)
            print("Connection closed.")

