import tkinter as tk
import serial
import time

MAX_POINTS = 10
MARGE_ERREUR = 0.1 # prevents the gear from falling off of the steering rack
LENGTH_X = 19  # length of the X axis steering rack in cm
LENGTH_Y = 2.2 # length of the Y axis steering rack in cm
MAX_X_POSITION_ABS = round(LENGTH_X*(1 - MARGE_ERREUR)/2, 1)
MAX_Y_POSITION_ABS = round(LENGTH_Y*(1 - MARGE_ERREUR)/2, 1)
MIN_SPEED = 0.1 # minimum movement speed in cm/s
MAX_SPEED = 1.5 # maximum movement speed in cm/s

route_x = []
route_y = []
route_speed = []
route_loaded = False

# Auxiliary Functions

def send_command(command):
    ser.write((command + '\n').encode())

def write_message(msg):
    global message_box
    message_box.insert(tk.END, msg)
    message_box.see(tk.END)

# Button Activated Functions

def clear_log():
    global message_box
    message_box.delete('1.0', tk.END)

def add_point():
    global route_x, route_y, x_entry, y_entry, speed_entry, route_loaded
    route_loaded = False
    x_coord = x_entry.get()
    y_coord = y_entry.get()
    speed = speed_entry.get()
    if len(x_coord) <= 0 or len(y_coord) <= 0 or len(speed) <= 0:
        write_message("Error: please insert both X and Y coordinates plus a speed value for the displacement.\n")
    elif len(route_speed) >= MAX_POINTS:
        write_message(f"Warning: The robot's route can have a\nmaximum of {MAX_POINTS} middle points.\n")
    elif float(speed) <= 0:
        write_message(f"Error: speed of displacement must be strictly positive.\n")
    elif abs(float(x_coord)) > MAX_X_POSITION_ABS or abs(float(y_coord)) > MAX_Y_POSITION_ABS:
        write_message(f"Error: please pay attention to the limits of the X and Y coordinates.\n")
    elif abs(float(speed)) > MAX_SPEED:
        write_message(f"Error: please pay attention to the limits of the X and Y coordinates.\n")
    else:
        route_x.append(float(x_coord))
        route_y.append(float(y_coord))
        route_speed.append(float(speed))
        write_message(f"Point {float(x_coord), float(y_coord)} with speed {float(speed)} added.\n")
        route_loaded = False

def clear_route():
    global route_x, route_y, route_speed, route_loaded
    route_loaded = False
    route_x.clear()
    route_y.clear()
    route_speed.clear()
    write_message("Route Cleared.\n")

def show_route():
    global route_x, route_y, route_speed, route_loaded
    clear_log()
    len_x = len(route_x)
    len_y = len(route_y)
    len_s = len(route_speed)
    if len_x < 1 or len_y < 1 or len_s < 1:
        write_message("Route is empty.\n")
    else:
        if route_loaded:
            write_message("Route: Loaded\n  X  |  Y  | Speed\n------------------\n")
        else:
            write_message("Route: Not Loaded\n  X  |  Y  | Speed\n------------------\n")
        for i in range(len_x):
            coords = " " + str(route_x[i])
            coords += " | " + str(route_y[i]) + " |  " + str(route_speed[i]) + "\n"
            write_message(coords)

def load_route():
    global route_x, route_y, route_loaded
    len_x = len(route_x)
    len_y = len(route_y)
    len_s = len(route_speed)
    if len_x < 2 or len_y < 2:
        write_message("Error: route must have at least one start point and one end point.\n")
    else:
        command_x = "ROUTE X"
        command_y = "ROUTE Y"
        command_s = "ROUTE S"
        for i in range(len_x):
            command_x += " " + str(route_x[i])
            command_y += " " + str(route_y[i])
            command_s += " " + str(route_speed[i])
        send_command(f"{command_x}")
        send_command(f"{command_y}")
        send_command(f"{command_s}")
        write_message("Route Loaded.\n")
        route_loaded = True

def start_movement():
    if not route_loaded:
        write_message("Error: to start movement, first you must specify a route providing the coordinates and pressing \"Add\".\n")
    else:
        write_message("Movement Started.\n")
        send_command(f"START")

def stop_movement():
    write_message("Movement Stopped.\n")
    send_command(f"STOP")

def reset_position():
    write_message("Resetting Position.\n")
    send_command(f"RESET")

# Initialization Function
def initialize_gui():
    #  Create resizable window
    window = tk.Tk()
    window.title("Movement Control")
    window.rowconfigure([0, 1, 2, 3, 4, 5], weight=1)
    window.columnconfigure(0, weight=1)

    # Movement Control Buttons Frame
    control_frame = tk.Frame(window, padx=10, pady=10)
    control_frame.grid(row=0, column=0, sticky="nsew")
    control_frame.columnconfigure([0, 1, 2], weight=1)

    start_button = tk.Button(control_frame, text="Start", command=start_movement)
    start_button.grid(row=0, column=0, padx=5, sticky="nsew")

    stop_button = tk.Button(control_frame, text="Stop", command=stop_movement)
    stop_button.grid(row=0, column=1, padx=5, sticky="nsew")

    reset_button = tk.Button(control_frame, text="Reset", command=reset_position)
    reset_button.grid(row=0, column=2, padx=5, sticky="nsew")

    # Entry Frame
    entry_frame = tk.Frame(window, padx=10, pady=10)
    entry_frame.grid(row=1, column=0, sticky="nsew")
    entry_frame.columnconfigure([0, 1], weight=1)
    entry_frame.rowconfigure([0, 1, 2], weight=1)

    x_label = tk.Label(entry_frame, text=f"X Position (cm):\nMin: {-MAX_X_POSITION_ABS}, Max: {MAX_X_POSITION_ABS}")
    x_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    x_entry = tk.Entry(entry_frame, width=5)
    x_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    y_label = tk.Label(entry_frame, text=f"Y Position (cm):\nMin: {-MAX_Y_POSITION_ABS}, Max: {MAX_Y_POSITION_ABS}")
    y_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    y_entry = tk.Entry(entry_frame, width=5)
    y_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    speed_label = tk.Label(entry_frame, text=f"Speed (cm/s):\nMin: {MIN_SPEED}, Max: {MAX_SPEED}")
    speed_label.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

    speed_entry = tk.Entry(entry_frame, width=5)
    speed_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # Route Management Buttons Frame
    route_frame = tk.Frame(window, padx=10, pady=10)
    route_frame.grid(row=2, column=0, sticky="nsew")
    route_frame.columnconfigure([0, 1, 2], weight=1)

    add_button = tk.Button(route_frame, text="Add Point", command=add_point)
    add_button.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

    clear_button = tk.Button(route_frame, text="Clear Route", command=clear_route)
    clear_button.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
    
    show_button = tk.Button(route_frame, text="Show Route", command=show_route)
    show_button.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")

    load_button = tk.Button(route_frame, text="Load Route", command=load_route)
    load_button.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")

    # Message Box Frame
    message_frame = tk.Frame(window, padx=10, pady=10)
    message_frame.grid(row=3, column=0, sticky="nsew")
    message_frame.columnconfigure(0, weight=1)

    message_box = tk.Text(message_frame, height=10, width=50)
    message_box.grid(row=0, column=0, sticky="nsew")

    clear_log_button = tk.Button(message_frame, text="Clear Log", command=clear_log)
    clear_log_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    # Warning Frame
    warning_frame = tk.Frame(window, padx=10, pady=10)
    warning_frame.grid(row=4, column=0, sticky="nsew")

    warning_label = tk.Label(warning_frame, text=f"Warning: The robot's route can have a\nmaximum of {MAX_POINTS} middle points.")
    warning_label.grid(row=0, column=0, sticky="ew")

    return window, x_entry, y_entry, speed_entry, message_box

# Configure serial port - REPLACE 'COM4' BY YOUR PROPER PORT (see Device Manager)
ser = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)  # Await connection to the Arduino
window, x_entry, y_entry, speed_entry, message_box = initialize_gui()
window.mainloop()
ser.close()
