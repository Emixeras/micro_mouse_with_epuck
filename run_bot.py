
from ePuck_Steuerung import *

LABYRINTH_SIZE = 7
GOAL_X = 3
GOAL_Y = 4


if __name__ == "__main__":
    ser = connect_to_epuck()
    if ser:
        try:
            turn90degree(ser)
        finally:
            # Close the connection
            ser.close()
            print("Connection closed.")
