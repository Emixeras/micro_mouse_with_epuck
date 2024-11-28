import serial
import time

# Replace with the correct port and baud rate for your e-puck
SERIAL_PORT = "/dev/rfcomm0"  # Replace with your port (e.g., COM3 or /dev/ttyUSB0)
BAUD_RATE = 115200  # Standard baud rate for e-puck communication


def connect_to_epuck():
    try:
        # Open the serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected to e-puck at", SERIAL_PORT)
        return ser
    except Exception as e:
        print("Failed to connect:", e)
        return None


def send_command(ser, command):
    try:
        # Send a command to the e-puck (e.g., move, stop, etc.)
        ser.write(command.encode())  # Encode string to bytes
        print("Command sent:", command)
    except Exception as e:
        print("Failed to send command:", e)


def read_response(ser):
    try:
        # Read the response from the e-puck
        response = ser.readline().decode().strip()  # Decode bytes to string
        return response
    except Exception as e:
        print("Failed to read response:", e)
        return None


if __name__ == "__main__":
    ser = connect_to_epuck()
    if ser:
        try:
            # Example: send a command to move the motors
            send_command(ser, "D,500,500")  # 'D' for direct motor control: left, right
            time.sleep(1)  # Wait for e-puck to process the command

            # Read a response if the e-puck sends any data
            response = read_response(ser)
            if response:
                print("Response from e-puck:", response)
        finally:
            # Close the connection
            ser.close()
            print("Connection closed.")
