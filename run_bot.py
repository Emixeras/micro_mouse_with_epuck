from ePuck_Communication import connect_to_epuck, read_accelerometer
from ePuck_Steuerung import *

LABYRINTH_SIZE = 7
GOAL_X = 3
GOAL_Y = 4


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

            while True:
                move_straight(ser)
                read_accelerometer(ser)
        finally:
            # Close the connection
            ser.close()
            #print(time_elapsed)
            print("Connection closed.")
