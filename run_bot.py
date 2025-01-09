from time import sleep

from ePuck_Communication import connect_to_epuck, read_accelerometer
from ePuck_Steuerung import *
from micro_mouse_with_epuck.floodfill import Floodfill, Cell
from micro_mouse_with_epuck.objects.sensor_information import SensorInformation

LABYRINTH_SIZE = 7
GOAL_X = 3
GOAL_Y = 4

def move_labyrinth(ser):
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    turn90degree(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    turn90degree(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    turn90degree(ser, False)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    turn90degree(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    turn90degree(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    turn90degree(ser)
    sleep(0.1)
    move_one_cell_straight(ser)

def move_labyrinth_backwards(ser):
    move_one_cell_straight(ser)
    sleep(0.1)
    turn90degree(ser, False)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    turn90degree(ser, False)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    turn90degree(ser, False)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    turn90degree(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    turn90degree(ser, False)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    turn90degree(ser, False)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)
    sleep(0.1)
    move_one_cell_straight(ser)


if __name__ == "__main__":

    ser = connect_to_epuck()
    if ser:
        try:
            targetCell1 = Cell(2,2)
            targetCell2 = Cell(3,2)
            targetCell3 = Cell(2,3)
            targetCell4 = Cell(3,3)
            floodfillAlg = Floodfill(ser,6,6, [targetCell1, targetCell2, targetCell3, targetCell4])
            floodfillAlg.trainMaze()
            floodfillAlg.runMaze()

        finally:
            # Close the connection
            ser.close()
            #print(time_elapsed)
            print("Connection closed.")

