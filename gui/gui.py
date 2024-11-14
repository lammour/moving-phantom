import tkinter as tk
import serial
import time

MAX_POINTS = 10

route_x = []
route_y = []
route_speed = []
route_loaded = False

# Configure serial port (REPLACE BY THE PROPER PORT (see Device Manager))
ser = serial.Serial('COM4', 9600, timeout=1)
time.sleep(2)  # Await connection to the Arduino

def write_message(msg):
    global message_box
    message_box.insert(tk.END, msg)
    message_box.see(tk.END)

def clear_log():
    global message_box
    message_box.delete('1.0', tk.END)

def send_command(command):
    ser.write((command + '\n').encode())

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
        print(f"Command: {command_x}")
        send_command(f"{command_x}")
        print(f"Command: {command_y}")
        send_command(f"{command_y}")
        print(f"Command: {command_s}")
        send_command(f"{command_s}")
        write_message("Route Loaded.\n")
        route_loaded = True

def start_movement():
    if not route_loaded:
        write_message("Error: to start movement, first you must specify a route providing the coordinates and pressing \"Add\".\n")
    else:
        write_message("Movement Started.\n")
        print("Command: START")
        send_command(f"START")

def stop_movement():
    write_message("Movement Stopped.\n")
    print("Command: STOP")
    send_command(f"STOP")

def reset_position():
    write_message("Resetting Position.\n")
    print("Comando: RESET")
    send_command(f"RESET")

def initialize_gui():
    window = tk.Tk()
    window.title("Movement Control")
    
    # Resizable window
    window.rowconfigure([0, 1, 2, 3, 4, 5], weight=1)
    window.columnconfigure(0, weight=1)

    # Control Frame for Start/Stop/Reset Buttons
    frame_controls = tk.Frame(window, padx=10, pady=10)
    frame_controls.grid(row=0, column=0, sticky="nsew")
    frame_controls.columnconfigure([0, 1, 2], weight=1)

    start_button = tk.Button(frame_controls, text="Start", command=start_movement)
    start_button.grid(row=0, column=0, padx=5, sticky="nsew")

    stop_button = tk.Button(frame_controls, text="Stop", command=stop_movement)
    stop_button.grid(row=0, column=1, padx=5, sticky="nsew")

    reset_button = tk.Button(frame_controls, text="Reset", command=reset_position)
    reset_button.grid(row=0, column=2, padx=5, sticky="nsew")

    # Speed, X and Y Entry Frame
    frame_entries = tk.Frame(window, padx=10, pady=10)
    frame_entries.grid(row=1, column=0, sticky="nsew")
    frame_entries.columnconfigure([0, 1], weight=1)
    frame_entries.rowconfigure([0, 1, 2], weight=1)

    x_label = tk.Label(frame_entries, text="X Position:")
    x_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    x_entry = tk.Entry(frame_entries, width=5)
    x_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    y_label = tk.Label(frame_entries, text="Y Position:")
    y_label.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    y_entry = tk.Entry(frame_entries, width=5)
    y_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    speed_label = tk.Label(frame_entries, text="Speed:")
    speed_label.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

    speed_entry = tk.Entry(frame_entries, width=5)
    speed_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # Add/Load/Clear Buttons Frame
    frame_buttons = tk.Frame(window, padx=10, pady=10)
    frame_buttons.grid(row=2, column=0, sticky="nsew")
    frame_buttons.columnconfigure([0, 1, 2], weight=1)

    add_button = tk.Button(frame_buttons, text="Add Point", command=add_point)
    add_button.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")

    clear_button = tk.Button(frame_buttons, text="Clear Route", command=clear_route)
    clear_button.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
    
    show_button = tk.Button(frame_buttons, text="Show Route", command=show_route)
    show_button.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")

    load_button = tk.Button(frame_buttons, text="Load Route", command=load_route)
    load_button.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")

    # Message Box Frame for Warnings
    message_frame = tk.Frame(window, padx=10, pady=10)
    message_frame.grid(row=3, column=0, sticky="nsew")
    message_frame.columnconfigure(0, weight=1)

    message_box = tk.Text(message_frame, height=10, width=50)
    message_box.grid(row=0, column=0, sticky="nsew")

    clear_log_button = tk.Button(message_frame, text="Clear Log", command=clear_log)
    clear_log_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

    # Position Status Frame
    status_frame = tk.Frame(window, padx=10, pady=10)
    status_frame.grid(row=4, column=0, sticky="nsew")
    
    status_label = tk.Label(status_frame, text="Status: Static")
    status_label.grid(row=0, column=0, sticky="ew")

    position_label = tk.Label(status_frame, text="Current Position: X: 0, Y: 0")
    position_label.grid(row=1, column=0, sticky="ew")

    warning_label = tk.Label(status_frame, text=f"Warning: The robot's route can have a\nmaximum of {MAX_POINTS} middle points.")
    warning_label.grid(row=0, column=1, sticky="ew")

    return window, x_entry, y_entry, speed_entry, message_box, status_label, position_label

# Update the robot status based on the feedback information received by the Arduino.
def update_status():
    pass
    """if ser.in_waiting > 0:
    lines = ser.readlines()
    # At least 4 lines received
    if len(lines) >= 4:
        try:
            # Decodes and strips unuseful chars
            line_x = lines[0].decode('utf-8').strip()
            line_y = lines[1].decode('utf-8').strip()
            line_vx = lines[2].decode('utf-8').strip()
            line_vy = lines[3].decode('utf-8').strip()

            # Extracts values
            current_x = int(line_x.split(": ")[1])
            current_y = int(line_y.split(": ")[1])
            current_vx = int(line_vx.split(": ")[1])
            current_vy = int(line_vy.split(": ")[1])

            # Updates GUI with new info
            position_label.config(text=f"Current Position: X: {current_x}, Y: {current_y}")
            status_label.config(text=f"Speeds - Vx: {current_vx}, Vy: {current_vy}")
        except (IndexError, ValueError) as e:
            print("Error reading serial data:", e)
    if running:
        status_label.config(text=f"Status: moving")
    else:
        status_label.config(text=f"Status: static")
    window.after(100, update_status)"""

window, x_entry, y_entry, speed_entry, message_box, status_label, position_label = initialize_gui()
# Iniciar a atualização do status
update_status()
# Rodar a GUI
window.mainloop()
# Fechar a porta serial ao fechar a GUI
ser.close()
