import serial
import time
import os

# --- CONFIGURATION ---
# 1. SERIAL PORT SETTINGS
SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 115200
TIMEOUT = 1  # Read timeout in seconds

# 2. FILE SYSTEM SETTINGS
# The folder where the log file will be stored
LOG_DIR = '/home/pi/serial_logs'
# The name of the log file will be generated with a timestamp
LOG_FILE_PREFIX = 'serial_data_'

# -------------------------

def setup_log_directory(directory):
    """Creates the log directory if it doesn't exist."""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            print(f"✅ Created log directory: {directory}")
        except OSError as e:
            print(f"❌ Error creating directory {directory}: {e}")
            exit(1)  # Exit if we can't create the necessary directory


def start_serial_logging():
    """Connects to the serial port, reads data, and saves it to a file."""

    setup_log_directory(LOG_DIR)

    # Generate a unique log file name with a timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(LOG_DIR, f"{LOG_FILE_PREFIX}{timestamp}.log")

    try:
        # 1. Establish the serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        print(f"✅ Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
        print(f"📝 Logging data to: {log_filename}")

        # Open the log file for appending ('a')
        with open(log_filename, 'a') as f:
            print("--- Starting Data Capture (Press Ctrl+C to Stop) ---")

            # 2. Main loop for reading and logging
            while True:
                # Read all available bytes from the serial buffer
                raw_data = ser.read_all()

                if raw_data:
                    # Decode the raw bytes into a string (assuming ASCII/UTF-8)
                    try:
                        data_line = raw_data.decode('utf-8')

                        # Write the data to the file
                        f.write(data_line)
                        f.flush()  # Force write to disk immediately

                        # Optionally print to console for monitoring
                        print(data_line.strip())

                    except UnicodeDecodeError:
                        print("⚠️ Received non-ASCII/UTF-8 data. Skipping logging of this chunk.")

                # Small delay to prevent high CPU usage
                time.sleep(0.01)

    except serial.SerialException as e:
        print(f"\n❌ Error connecting to or reading from serial port {SERIAL_PORT}: {e}")

    except KeyboardInterrupt:
        print("\n🛑 Logging stopped by user (Ctrl+C).")

    finally:
        # 3. Clean up and close the connection
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("🔌 Serial connection closed.")
        print("Script finished.")


if __name__ == '__main__':
    start_serial_logging()