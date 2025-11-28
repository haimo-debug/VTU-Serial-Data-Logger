import tkinter as tk
from tkinter import messagebox
import serial
import time
import threading
from datetime import datetime

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/ttyUSB0'  #  migrated to config.ini next ver.
BAUD_RATE = 115200            #  migrated to config.ini next ver.

# Mapping modes to their specific Start/Stop serial commands
# migrated to config.ini next ver.
COMMAND_MAP = {
    "Xirgo_GPS":  {"start": "!yde\r\n", "stop": "!ydd\r\n"},
    "Xirgo_GSM":  {"start": "!gde\r\n", "stop": "!gdd\r\n"},   # Placeholder commands
    "Xirgo_VBUS": {"start": "!vde\r\n", "stop": "!vdd\r\n"}, # Placeholder commands
}

class XirgoControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial logs reader")
        
        # 1. Setup Geometry for 3.5 inch Display
        self.root.geometry("480x320")
        self.root.configure(bg="#1e1e1e") # Dark background from mockup
        
        # State Variables
        self.current_mode = "Xirgo_GPS" # Default selection
        self.is_running = False
        
        # --- UI LAYOUT ---
        self.setup_ui()
        self.update_clock()

    def setup_ui(self):
        # --- Top Bar (Time & Status) ---
        top_frame = tk.Frame(self.root, bg="#2d2d2d", height=40)
        top_frame.pack(side="top", fill="x")
        
        self.time_label = tk.Label(top_frame, text="00:00:00", font=("Arial", 12, "bold"), fg="white", bg="#2d2d2d")
        self.time_label.pack(side="left", padx=10, pady=5)
        # "CONNECTED" label is a placeholder, requires logic do be added --> detected battery level  :  0 v = "DISCONNECTED"  , > 10 v = "CONNECTED"
        self.status_label = tk.Label(top_frame, text="● CONNECTED", font=("Arial", 10, "bold"), fg="#4CAF50", bg="#2d2d2d")
        self.status_label.pack(side="right", padx=10)

        # --- Log Console (Middle) ---
        # Mimicking the black console in your mockup
        self.log_frame = tk.Frame(self.root, bg="black")
        self.log_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)
        
        self.log_list = tk.Listbox(self.log_frame, bg="black", fg="#00ff00", font=("Consolas", 9), borderwidth=0, highlightthickness=0)
        self.log_list.pack(side="left", fill="both", expand=True)
        
        # Add scrollbar for the log
        scrollbar = tk.Scrollbar(self.log_frame, command=self.log_list.yview, bg="#333333")
        scrollbar.pack(side="right", fill="y")
        self.log_list.config(yscrollcommand=scrollbar.set)
        
        self.log_message(f"System initialized...", "white")
        self.log_message(f"Target Port: {SERIAL_PORT}", "gray")

        # --- Bottom Bar (Buttons) ---
        bottom_frame = tk.Frame(self.root, bg="#1e1e1e", height=80)
        bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)

        # MENU Button (Left)
        self.btn_menu = tk.Button(bottom_frame, text="☰ MENU", font=("Arial", 14, "bold"), 
                                  bg="#3a3a3a", fg="white", activebackground="#555", 
                                  width=10, height=2, command=self.open_menu_selection)
        self.btn_menu.pack(side="left", padx=5)

        # STOP/START Button (Right - Dynamic)
        self.btn_action = tk.Button(bottom_frame, text="▶ START", font=("Arial", 16, "bold"), 
                                    bg="#d32f2f", fg="white", activebackground="#b71c1c", 
                                    width=15, height=2, command=self.toggle_start_stop)
        self.btn_action.pack(side="right", padx=5)

        # Label to show what is currently selected
        self.selection_label = tk.Label(self.root, text=f"SELECTED: {self.current_mode}", 
                                        bg="#1e1e1e", fg="#aaaaaa", font=("Arial", 8))
        self.selection_label.place(x=15, y=235) # Place just above buttons

    # --- LOGIC HANDLERS ---

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def log_message(self, msg, color="white"):
        """Adds a message to the console area with a timestamp"""
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        full_msg = f"{timestamp} {msg}"
        self.log_list.insert(tk.END, full_msg)
        self.log_list.itemconfig(tk.END, fg=color)
        self.log_list.yview(tk.END) # Auto-scroll to bottom

    def open_menu_selection(self):
        """Creates a popup window to act as the scrolling menu"""
        if self.is_running:
            messagebox.showwarning("Busy", "Please STOP the current process before changing modes.")
            return

        # Create a popup window (Toplevel)
        menu_win = tk.Toplevel(self.root)
        menu_win.title("Select Mode")
        menu_win.geometry("200x200")
        # Center it roughly
        x = self.root.winfo_x() + 140
        y = self.root.winfo_y() + 60
        menu_win.geometry(f"+{x}+{y}")
        menu_win.transient(self.root) # Keep on top
        
        lbl = tk.Label(menu_win, text="Select Operation:", font=("Arial", 10, "bold"))
        lbl.pack(pady=5)

        # Listbox for selection
        modes = list(COMMAND_MAP.keys())
        listbox = tk.Listbox(menu_win, font=("Arial", 12), height=5)
        for mode in modes:
            listbox.insert(tk.END, mode)
        listbox.pack(fill="both", expand=True, padx=10, pady=5)

        def confirm_selection():
            selection_idx = listbox.curselection()
            if selection_idx:
                selected = listbox.get(selection_idx)
                self.current_mode = selected
                self.selection_label.config(text=f"SELECTED: {self.current_mode}")
                self.log_message(f"Mode changed to: {self.current_mode}", "cyan")
                menu_win.destroy()
        
        btn_confirm = tk.Button(menu_win, text="Confirm", command=confirm_selection, bg="#4CAF50", fg="white")
        btn_confirm.pack(fill="x", padx=10, pady=10)

    def toggle_start_stop(self):
        """Handles the main logic for switching scripts"""
        
        # Get the specific commands for the currently selected mode
        commands = COMMAND_MAP[self.current_mode]

        if not self.is_running:
            # LOGIC: User clicked START
            self.is_running = True
            self.btn_action.config(text="■ STOP", bg="#4CAF50") #   Stop=Red, Start=Green.

            
            self.log_message(f"Starting {self.current_mode}...", "orange")
            
            # Run the serial logic in a separate thread to not freeze UI
            threading.Thread(target=self.send_serial_command, args=(commands['start'],), daemon=True).start()
            
        else:
            # LOGIC: User clicked STOP
            self.is_running = False
            self.btn_action.config(text="▶ START", bg="#d32f2f")
            
            self.log_message(f"Stopping {self.current_mode}...", "orange")
            
            # Run the serial logic
            threading.Thread(target=self.send_serial_command, args=(commands['stop'],), daemon=True).start()

    def send_serial_command(self, data_str):
        """
        Adapted from already tested working 'xirgo_gps_start.py' script.
        Opens port, waits, sends data, closes.
        """
        try:
            self.log_message(f"Opening {SERIAL_PORT}...", "gray")
            
            # Simulation mode for testing without hardware (Remove this block on real device if needed)
            # if True: 
            #     time.sleep(1)
            #     self.log_message(f"SENT: {data_str.strip()}", "#00ff00")
            #     return

            # --- REAL HARDWARE LOGIC ---
            ser = serial.Serial(PORT_NAME=SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
            time.sleep(2) # Wait for connection stability
            
            data_bytes = data_str.encode('ascii')
            ser.write(data_bytes)
            
            self.log_message(f"Data sent: {data_str.strip()}", "#00ff00")
            
            time.sleep(0.1)
            ser.close()
            # ---------------------------

        except serial.SerialException as e:
            self.log_message(f"Serial Error: {e}", "red")
            # If error, reset the button state to allow trying again
            if self.is_running: 
                self.is_running = False
                self.root.after(0, lambda: self.btn_action.config(text="▶ START", bg="#d32f2f"))

        except Exception as e:
            self.log_message(f"Error: {e}", "red")

if __name__ == "__main__":
    root = tk.Tk()
    # Optional: Fullscreen for the 3.5 inch display
    # root.attributes('-fullscreen', True) 
    app = XirgoControlPanel(root)
    root.mainloop()