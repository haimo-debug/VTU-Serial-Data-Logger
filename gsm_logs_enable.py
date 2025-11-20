import serial
import time
import sys

# --- Serial Port Configuration ---
# For the specified Linux port 'ttyUSB0'
PORT_NAME = '/dev/ttyUSB0'
BAUD_RATE = 115200
TIMEOUT = 1  # Read/write timeout in seconds

# --- Data to Transmit ---
# The string to be sent over the serial port.
# '\r\n' represents a Carriage Return and Line Feed (New Line),
DATA_TO_SEND = "!yde\r\n"


def send_serial_data(port, baud, data):
    """
    Initializes the serial port and transmits the given data.
    """
    print(f"Attempting to open serial port: {port} at {baud} baud...")

    try:
        # Open the serial port
        ser = serial.Serial(
            port=port,
            baudrate=baud,
            timeout=TIMEOUT
        )
        print("Serial port opened successfully.")

        # Give a small delay to ensure the port is ready (optional but recommended)
        time.sleep(2)

        # Encode the string to bytes, as serial ports transmit bytes
        data_bytes = data.encode('ascii')

        print(f"Sending data: '{data.strip()}'")

        # Write the data to the serial port
        bytes_sent = ser.write(data_bytes)

        print(f"Successfully sent {bytes_sent} bytes.")

        # Wait a moment for the transmission to complete
        time.sleep(0.1)

        # Close the serial port
        ser.close()
        print("Serial port closed.")

    except serial.SerialException as e:
        print(f"❌ Error communicating with serial port {port}: {e}")
        print(
            "Please ensure the device is connected, the port name is correct, and you have the necessary permissions .")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    send_serial_data(PORT_NAME, BAUD_RATE, DATA_TO_SEND)