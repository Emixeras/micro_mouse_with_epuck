# Setup

The code is tested under Python 3.11 but other versions should also work.
The package needed is pyserial. 
This can be done with the command **python -m pip install pyserial** or 
**conda install pyserial**.

# Run
1. connect the e-Puck to the PC. To do this, start the e-Puck, set the programme selection
to 3 and connect to the e-Puck via Bluetooth (the serial number is the pin).
2. set the appropriate COM port. Find out with which port the e-Puck can be reached.
Enter the appropriate COM port in the SERIAL_PORT variable in ePuck_Communications.py.
3. adjust the Labyrinth parameters. Call the following code in the main method of run_bot.py.
```py

Translated with DeepL.com (free version)
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
The targetCell is the target of the labyrinth and WIDTH and HIGHT indicate the size of the labyrinth.
4. place the e-puck in the labyrinth. Make sure that it is in the top left corner and the front is facing to the right.
5. start the programme.

# Common errors

- The programme runs very unreliably resulting in the e-Puck crashing into walls. 
The programme cannot free the e-Puck from such a situation.
- It can happen that the programme terminates with the error message about semaphores.
In this case, simply restart the programme.