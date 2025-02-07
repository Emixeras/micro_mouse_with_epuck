# Setup

The code is developed and tested under Python 3.11 but other versions should also work.
The package needed is pyserial. 
This can be done with the command **python -m pip install pyserial** or 
**conda install pyserial**.

# Run
1. Connect the e-Puck to the PC. To do this, start the e-Puck, set the programme selection
to 3 and connect to the e-Puck via Bluetooth (the serial number is the pin).
2. Set the appropriate COM port. Find out with which port the e-Puck can be reached.
Enter the appropriate COM port in the SERIAL_PORT variable in ePuck_Communications.py.
3. Adjust the Labyrinth parameters in the following code in the main method of run_bot.py. The targetCell is the target of the labyrinth and WIDTH and HEIGHT indicate the size of the labyrinth. The program can work with an arbitrary number of target cells.
```py
    ser = connect_to_epuck()
    if ser:
        try:
            targetCell1 = Cell(<ROW>,<COLUMN>)
            targetCell2 = Cell(3,2)
            floodfillAlg = Floodfill(ser,<WIDTH>, <HEIGHT>, [targetCell1, targetCell2])
            floodfillAlg.trainMaze()
            floodfillAlg.runMaze()

        finally:
            ser.close()
```
4. Place the e-puck in the labyrinth. Make sure that it is in the top left corner and the front is facing to the right.
5. Start the program in run_bot.py.

# Common errors

- The program runs very unreliably resulting in the e-Puck crashing into walls. 
The program cannot free the e-Puck from such a situation.
- It can happen that the program terminates with the error message about semaphores.
In this case, simply restart the programme.