import math

import serial
import time

SERIAL_PORT = "COM8"  # Replace with your port (e.g., COM3 or /dev/ttyUSB0)
BAUD_RATE = 115200  # Standard baud rate for e-puck communication
LABYRINTH_SIZE = 7
GOAL_X = 3
GOAL_Y = 4
ABSTAND_RAEDER_IN_MM = 53
VIERTEL_KREIS = 1/4 * math.pi * ABSTAND_RAEDER_IN_MM
MM_PRO_STEP = 0.13


def turn90clock(ser):
    needed_steps = VIERTEL_KREIS / MM_PRO_STEP
    # set motor position to 0
    send_command(ser, b"P,0,0\r\n")
    # read motor position
    send_command(ser, b"Q\r\n", False)
    response = ser.read_all().decode()
    print(response)
    response = str.split(response, ",")
    print(response)
    print(needed_steps)
    while float(response[1]) < needed_steps:
        print(response)
        send_command(ser, b"D,1000,-1000\r\n")
        send_command(ser, b"Q\r\n", False)
        response = ser.read_all().decode()
        print(response)
        response = str.split(response, ",")

    # reset
    send_command(ser, b"D,0,0\r\n")
    send_command(ser, b"P,0,0\r\n")

def turn90counterclock(ser):
    return
def moveOneCellStraight(ser):
    return

def connect_to_epuck():
    try:
        # Open the serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.02)
        #needed as the first command always gives an error
        send_command(ser, b'b\r')
        print("Connected to e-puck at", SERIAL_PORT)
        return ser
    except Exception as e:
        print("Failed to connect:", e)
        return None


def send_command(ser, command, should_read_response = True):
    try:
        # Send a command to the e-puck (e.g., move, stop, etc.)
        ser.write(command)  # Encode string to bytes
        print("Command sent:", command)
        if should_read_response:
            print(ser.read_all().decode().strip())
    except Exception as e:
        print("Failed to send command:", e)


def read_response(ser):
    try:
        # Read the response from the e-puck
        response = ser.read_all().decode().strip()  # Decode bytes to string
        return response
    except Exception as e:
        print("Failed to read response:", e)
        return None

def testCommand(ser, command):
    # Example: send a command to move the motors
    ser.write(command)
      # Wait for e-puck to process the command

    #ser.write('\x0d\x0a'.encode('ascii'))
    # ser.write(b'\x0a') # Encode string to bytes
    # send_command(ser, b'H\r\n')  # 'D' for direct motor control: left, right

    # Read a response if the e-puck sends any data
    #response = read_response(ser)
    #if response:
       # print("Response from e-puck:", response)


if __name__ == "__main__":
    ser = connect_to_epuck()
    if ser:
        try:
            turn90clock(ser)
        finally:
            # Close the connection
            ser.close()
            print("Connection closed.")
