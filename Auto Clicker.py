import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import threading
import time
import random
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
import json

# Global variables
clicking = False
thread = None
current_min_interval = 0
current_max_interval = 1000
interval_sets = []
toggle_key = 'f'
is_mouse_toggle = False
mouse_toggle_button = None
mouse_controller = Controller()
keyboard_listener = None
mouse_listener = None
last_click_time = None
temp_keyboard_listener = None
temp_mouse_listener = None
detect_status_label = None
current_interval_label = None
pause_chance = 0
min_pause = 0
max_pause = 0
burst_chance = 0
min_burst_clicks = 2
max_burst_clicks = 4
min_burst_interval = 30
max_burst_interval = 50

def interruptible_sleep(duration):
    start = time.time()
    while time.time() - start < duration:
        if not clicking:
            return
        time.sleep(0.001)

def click_loop():
    global clicking, last_click_time
    while clicking:
        if last_click_time is not None:
            interval = random.uniform(current_min_interval, current_max_interval) / 1000.0
            interruptible_sleep(interval)
            if not clicking:
                return
        
        # Random pause
        if random.random() * 100 < pause_chance:
            pause_duration = random.uniform(min_pause, max_pause) / 1000.0
            root.after(0, lambda pd=int(pause_duration * 1000): insert_to_list(f"Pause: {pd} ms"))
            interruptible_sleep(pause_duration)
            if not clicking:
                return
        
        # Determine if burst
        num_clicks = 1
        if random.random() * 100 < burst_chance:
            num_clicks = random.randint(min_burst_clicks, max_burst_clicks)
        
        for i in range(num_clicks):
            mouse_controller.click(Button.left)
            current_time = time.time()
            if last_click_time is None:
                msg = "0 ms (initial)"
            else:
                elapsed = int((current_time - last_click_time) * 1000)
                if i == 0:
                    msg = f"{elapsed} ms"
                else:
                    msg = f"{elapsed} ms (burst)"
            root.after(0, lambda m=msg: insert_to_list(m))
            last_click_time = current_time
            if i < num_clicks - 1:
                burst_interval = random.uniform(min_burst_interval, max_burst_interval) / 1000.0
                interruptible_sleep(burst_interval)
                if not clicking:
                    return

def insert_to_list(msg):
    click_list.insert(tk.END, msg)
    click_list.see(tk.END)

def toggle_clicking():
    global clicking, thread, last_click_time, current_min_interval, current_max_interval
    clicking = not clicking
    if clicking:
        if not interval_sets:
            messagebox.showerror("Error", "No interval sets added.")
            clicking = False
            return
        chosen = random.choice(interval_sets)
        current_min_interval, current_max_interval = chosen
        last_click_time = None
        click_list.delete(0, tk.END)
        thread = threading.Thread(target=click_loop, daemon=True)
        thread.start()
        status_label.config(text="Auto-clicking: ON")
        current_interval_label.config(text=f"Current Interval Set: Min: {current_min_interval} Max: {current_max_interval}")
    else:
        status_label.config(text="Auto-clicking: OFF")
        current_interval_label.config(text="Current Interval Set: None")

def on_keyboard_press(key):
    if hasattr(key, 'char') and key.char and key.char.lower() == toggle_key.lower():
        toggle_clicking()

def on_mouse_click(x, y, button, pressed):
    if pressed and button == mouse_toggle_button:
        toggle_clicking()

def start_listeners():
    global keyboard_listener, mouse_listener
    if is_mouse_toggle:
        mouse_listener = MouseListener(on_click=on_mouse_click)
        mouse_listener.start()
    else:
        keyboard_listener = KeyboardListener(on_press=on_keyboard_press)
        keyboard_listener.start()

def apply_settings():
    global toggle_key, is_mouse_toggle, mouse_toggle_button, pause_chance, min_pause, max_pause, burst_chance, min_burst_clicks, max_burst_clicks, min_burst_interval, max_burst_interval
    toggle_key_input = key_entry.get().strip().lower()
    if toggle_key_input in ['mouse4', 'mouse 4']:
        is_mouse_toggle = True
        mouse_toggle_button = Button.x1
    elif toggle_key_input in ['mouse5', 'mouse 5']:
        is_mouse_toggle = True
        mouse_toggle_button = Button.x2
    elif len(toggle_key_input) == 1:
        is_mouse_toggle = False
        toggle_key = toggle_key_input
    else:
        messagebox.showerror("Invalid key", "Please enter a single character or 'mouse4'/'mouse5' (or 'mouse 4'/'mouse 5') for the toggle key.")
        return

    try:
        pause_chance = float(pause_chance_entry.get())
        if not 0 <= pause_chance <= 100:
            raise ValueError("Pause chance must be between 0 and 100.")
        min_pause = int(min_pause_entry.get())
        max_pause = int(max_pause_entry.get())
        if min_pause > max_pause or min_pause < 0 or max_pause < 0:
            raise ValueError("Invalid pause range")
        
        burst_chance = float(burst_chance_entry.get())
        if not 0 <= burst_chance <= 100:
            raise ValueError("Burst chance must be between 0 and 100.")
        min_burst_clicks = int(min_burst_clicks_entry.get())
        max_burst_clicks = int(max_burst_clicks_entry.get())
        if min_burst_clicks > max_burst_clicks or min_burst_clicks < 1 or max_burst_clicks < 1:
            raise ValueError("Invalid burst clicks range")
        min_burst_interval = int(min_burst_interval_entry.get())
        max_burst_interval = int(max_burst_interval_entry.get())
        if min_burst_interval > max_burst_interval or min_burst_interval < 0 or max_burst_interval < 0:
            raise ValueError("Invalid burst interval range")
    except ValueError as e:
        messagebox.showerror("Invalid input", str(e))
        return

    start_listeners()
    apply_button.config(state='disabled')
    reset_button.config(state='normal')

def reset_settings():
    global clicking, thread, keyboard_listener, mouse_listener
    clicking = False
    if thread is not None:
        thread.join(timeout=1.0)
        thread = None
    if keyboard_listener is not None:
        keyboard_listener.stop()
        keyboard_listener = None
    if mouse_listener is not None:
        mouse_listener.stop()
        mouse_listener = None
    apply_button.config(state='normal')
    reset_button.config(state='disabled')
    status_label.config(text="Auto-clicking: OFF")
    click_list.delete(0, tk.END)
    current_interval_label.config(text="Current Interval Set: None")

# Temporary listeners for detecting toggle key
def on_temp_keyboard_press(key):
    global toggle_key, is_mouse_toggle
    if hasattr(key, 'char') and key.char:
        toggle_key = key.char.lower()
        is_mouse_toggle = False
        root.after(0, lambda: key_entry.delete(0, tk.END))
        root.after(0, lambda: key_entry.insert(0, toggle_key))
        stop_temp_listeners()
        return False  # Stop listener

def on_temp_mouse_click(x, y, button, pressed):
    global is_mouse_toggle, mouse_toggle_button
    if pressed:
        if button == Button.x1:
            is_mouse_toggle = True
            mouse_toggle_button = Button.x1
            root.after(0, lambda: key_entry.delete(0, tk.END))
            root.after(0, lambda: key_entry.insert(0, "mouse4"))
            stop_temp_listeners()
            return False
        elif button == Button.x2:
            is_mouse_toggle = True
            mouse_toggle_button = Button.x2
            root.after(0, lambda: key_entry.delete(0, tk.END))
            root.after(0, lambda: key_entry.insert(0, "mouse5"))
            stop_temp_listeners()
            return False

def start_temp_listeners():
    global temp_keyboard_listener, temp_mouse_listener
    detect_status_label.config(text="Press a key or mouse button (mouse4/mouse5)...")
    temp_keyboard_listener = KeyboardListener(on_press=on_temp_keyboard_press)
    temp_keyboard_listener.start()
    temp_mouse_listener = MouseListener(on_click=on_temp_mouse_click)
    temp_mouse_listener.start()

def stop_temp_listeners():
    global temp_keyboard_listener, temp_mouse_listener
    if temp_keyboard_listener is not None:
        temp_keyboard_listener.stop()
        temp_keyboard_listener = None
    if temp_mouse_listener is not None:
        temp_mouse_listener.stop()
        temp_mouse_listener = None
    detect_status_label.config(text="")

def add_interval():
    global interval_sets
    try:
        minv = int(min_entry.get())
        maxv = int(max_entry.get())
        if minv > maxv or minv < 0 or maxv < 0:
            raise ValueError("Invalid range")
        if len(interval_sets) >= 3:
            messagebox.showerror("Limit reached", "Maximum of 3 interval sets allowed.")
            return
        interval_sets.append((minv, maxv))
        interval_list.insert(tk.END, f"Min: {minv} Max: {maxv}")
    except ValueError:
        messagebox.showerror("Invalid input", "Please enter valid non-negative integers for milliseconds, with min <= max.")

def remove_interval():
    sel = interval_list.curselection()
    if sel:
        idx = sel[0]
        del interval_sets[idx]
        interval_list.delete(idx)

def save_settings():
    file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file:
        data = {
            "intervals": [list(i) for i in interval_sets],
            "toggle": key_entry.get(),
            "pause_chance": pause_chance_entry.get(),
            "min_pause": min_pause_entry.get(),
            "max_pause": max_pause_entry.get(),
            "burst_chance": burst_chance_entry.get(),
            "min_burst_clicks": min_burst_clicks_entry.get(),
            "max_burst_clicks": max_burst_clicks_entry.get(),
            "min_burst_interval": min_burst_interval_entry.get(),
            "max_burst_interval": max_burst_interval_entry.get()
        }
        with open(file, 'w') as f:
            json.dump(data, f)

def load_settings():
    file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
            global interval_sets
            interval_sets = []
            for i in data.get("intervals", []):
                minv = int(i[0])
                maxv = int(i[1])
                if minv > maxv or minv < 0 or maxv < 0:
                    raise ValueError("Invalid interval in loaded file")
                interval_sets.append((minv, maxv))
            interval_list.delete(0, tk.END)
            for minv, maxv in interval_sets:
                interval_list.insert(tk.END, f"Min: {minv} Max: {maxv}")
            key_entry.delete(0, tk.END)
            key_entry.insert(0, data.get("toggle", "f"))
            pause_chance_entry.delete(0, tk.END)
            pause_chance_entry.insert(0, data.get("pause_chance", "0"))
            min_pause_entry.delete(0, tk.END)
            min_pause_entry.insert(0, data.get("min_pause", "0"))
            max_pause_entry.delete(0, tk.END)
            max_pause_entry.insert(0, data.get("max_pause", "0"))
            burst_chance_entry.delete(0, tk.END)
            burst_chance_entry.insert(0, data.get("burst_chance", "0"))
            min_burst_clicks_entry.delete(0, tk.END)
            min_burst_clicks_entry.insert(0, data.get("min_burst_clicks", "2"))
            max_burst_clicks_entry.delete(0, tk.END)
            max_burst_clicks_entry.insert(0, data.get("max_burst_clicks", "4"))
            min_burst_interval_entry.delete(0, tk.END)
            min_burst_interval_entry.insert(0, data.get("min_burst_interval", "30"))
            max_burst_interval_entry.delete(0, tk.END)
            max_burst_interval_entry.insert(0, data.get("max_burst_interval", "50"))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load: {e}")

def on_closing():
    global clicking, keyboard_listener, mouse_listener, temp_keyboard_listener, temp_mouse_listener
    clicking = False
    if thread is not None:
        thread.join(timeout=1.0)
    if keyboard_listener is not None:
        keyboard_listener.stop()
    if mouse_listener is not None:
        mouse_listener.stop()
    if temp_keyboard_listener is not None:
        temp_keyboard_listener.stop()
    if temp_mouse_listener is not None:
        temp_mouse_listener.stop()
    root.destroy()

# GUI setup
root = tk.Tk()
root.title("Auto Clicker")
root.protocol("WM_DELETE_WINDOW", on_closing)
root.resizable(True, True)
root.configure(bg='#f0f0f0')  # Light gray background

# Style setup
style = ttk.Style()
style.theme_use('clam')  # Use 'clam' theme for a modern look
style.configure('TLabel', background='#f0f0f0', foreground='#333333', font=('Arial', 10))
style.configure('TEntry', fieldbackground='#ffffff', foreground='#000000', font=('Arial', 10))
style.configure('TButton', background='#4CAF50', foreground='#ffffff', font=('Arial', 10, 'bold'), padding=6)
style.map('TButton', background=[('active', '#45a049')])
style.configure('TRed.TButton', background='#f44336', foreground='#ffffff', font=('Arial', 10, 'bold'), padding=6)
style.map('TRed.TButton', background=[('active', '#e53935')])
style.configure('TListbox', background='#ffffff', foreground='#333333', font=('Arial', 10))
style.configure('Bold.TLabel', background='#f0f0f0', foreground='#333333', font=('Arial', 12, 'bold'))
style.configure('Status.TLabel', background='#f0f0f0', foreground='#4CAF50', font=('Arial', 12, 'bold'))

# Configure root grid weights
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=1)
root.rowconfigure(3, weight=1)
root.rowconfigure(4, weight=1)
root.rowconfigure(5, weight=3)
root.rowconfigure(6, weight=1)

# Interval Frame
interval_frame = ttk.Frame(root)
interval_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=5)
interval_frame.columnconfigure(0, weight=1)
interval_frame.columnconfigure(1, weight=1)
interval_frame.columnconfigure(2, weight=1)
interval_frame.rowconfigure(4, weight=1)

ttk.Label(interval_frame, text="Interval Settings", style='Bold.TLabel').grid(row=0, column=0, columnspan=3, pady=5, sticky='n')

ttk.Label(interval_frame, text="New Min interval (ms):").grid(row=1, column=0, padx=10, pady=5, sticky='e')
min_entry = ttk.Entry(interval_frame)
min_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
min_entry.insert(0, "0")

ttk.Label(interval_frame, text="New Max interval (ms):").grid(row=2, column=0, padx=10, pady=5, sticky='e')
max_entry = ttk.Entry(interval_frame)
max_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
max_entry.insert(0, "1000")

add_button = ttk.Button(interval_frame, text="Add Interval Set", command=add_interval)
add_button.grid(row=2, column=2, padx=10, pady=5, sticky='w')

ttk.Label(interval_frame, text="Added Interval Sets:").grid(row=3, column=0, columnspan=3, pady=5, sticky='n')
interval_list = tk.Listbox(interval_frame, height=3)
interval_list.grid(row=4, column=0, columnspan=3, pady=5, sticky='nsew')

remove_button = ttk.Button(interval_frame, text="Remove Selected", command=remove_interval, style='TRed.TButton')
remove_button.grid(row=5, column=0, columnspan=3, pady=5, sticky='n')

# Pause Frame
pause_frame = ttk.Frame(root)
pause_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
pause_frame.columnconfigure(0, weight=1)
pause_frame.columnconfigure(1, weight=1)

ttk.Label(pause_frame, text="Pause Settings", style='Bold.TLabel').grid(row=0, column=0, columnspan=2, pady=5, sticky='n')

ttk.Label(pause_frame, text="Pause Chance (%):").grid(row=1, column=0, padx=10, pady=5, sticky='e')
pause_chance_entry = ttk.Entry(pause_frame)
pause_chance_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
pause_chance_entry.insert(0, "0")

ttk.Label(pause_frame, text="Min Pause (ms):").grid(row=2, column=0, padx=10, pady=5, sticky='e')
min_pause_entry = ttk.Entry(pause_frame)
min_pause_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
min_pause_entry.insert(0, "0")

ttk.Label(pause_frame, text="Max Pause (ms):").grid(row=3, column=0, padx=10, pady=5, sticky='e')
max_pause_entry = ttk.Entry(pause_frame)
max_pause_entry.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
max_pause_entry.insert(0, "0")

# Burst Frame
burst_frame = ttk.Frame(root)
burst_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=5)
burst_frame.columnconfigure(0, weight=1)
burst_frame.columnconfigure(1, weight=1)

ttk.Label(burst_frame, text="Burst Settings", style='Bold.TLabel').grid(row=0, column=0, columnspan=2, pady=5, sticky='n')

ttk.Label(burst_frame, text="Burst Chance (%):").grid(row=1, column=0, padx=10, pady=5, sticky='e')
burst_chance_entry = ttk.Entry(burst_frame)
burst_chance_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
burst_chance_entry.insert(0, "0")

ttk.Label(burst_frame, text="Min Burst Clicks:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
min_burst_clicks_entry = ttk.Entry(burst_frame)
min_burst_clicks_entry.grid(row=2, column=1, padx=10, pady=5, sticky='ew')
min_burst_clicks_entry.insert(0, "2")

ttk.Label(burst_frame, text="Max Burst Clicks:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
max_burst_clicks_entry = ttk.Entry(burst_frame)
max_burst_clicks_entry.grid(row=3, column=1, padx=10, pady=5, sticky='ew')
max_burst_clicks_entry.insert(0, "4")

ttk.Label(burst_frame, text="Min Burst Interval (ms):").grid(row=4, column=0, padx=10, pady=5, sticky='e')
min_burst_interval_entry = ttk.Entry(burst_frame)
min_burst_interval_entry.grid(row=4, column=1, padx=10, pady=5, sticky='ew')
min_burst_interval_entry.insert(0, "30")

ttk.Label(burst_frame, text="Max Burst Interval (ms):").grid(row=5, column=0, padx=10, pady=5, sticky='e')
max_burst_interval_entry = ttk.Entry(burst_frame)
max_burst_interval_entry.grid(row=5, column=1, padx=10, pady=5, sticky='ew')
max_burst_interval_entry.insert(0, "50")

# Toggle Frame
toggle_frame = ttk.Frame(root)
toggle_frame.grid(row=3, column=0, sticky='nsew', padx=10, pady=5)
toggle_frame.columnconfigure(0, weight=1)
toggle_frame.columnconfigure(1, weight=1)
toggle_frame.columnconfigure(2, weight=1)

ttk.Label(toggle_frame, text="Toggle Settings", style='Bold.TLabel').grid(row=0, column=0, columnspan=3, pady=5, sticky='n')

ttk.Label(toggle_frame, text="Toggle key:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
key_entry = ttk.Entry(toggle_frame)
key_entry.grid(row=1, column=1, padx=10, pady=5, sticky='ew')
key_entry.insert(0, "f")

detect_button = ttk.Button(toggle_frame, text="Detect Key/Mouse", command=start_temp_listeners)
detect_button.grid(row=1, column=2, padx=10, pady=5, sticky='w')

detect_status_label = ttk.Label(toggle_frame, text="")
detect_status_label.grid(row=2, column=0, columnspan=3, pady=5, sticky='n')

# Controls Frame
controls_frame = ttk.Frame(root)
controls_frame.grid(row=4, column=0, sticky='nsew', padx=10, pady=5)
controls_frame.columnconfigure(0, weight=1)
controls_frame.columnconfigure(1, weight=1)
controls_frame.columnconfigure(2, weight=1)

apply_button = ttk.Button(controls_frame, text="Apply Settings and Start Listener", command=apply_settings)
apply_button.grid(row=0, column=0, columnspan=2, pady=10, sticky='ew')

reset_button = ttk.Button(controls_frame, text="Reset Settings", command=reset_settings, state='disabled', style='TRed.TButton')
reset_button.grid(row=0, column=2, pady=10, sticky='ew')

status_label = ttk.Label(controls_frame, text="Auto-clicking: OFF", style='Status.TLabel')
status_label.grid(row=1, column=0, columnspan=3, pady=5, sticky='n')

instructions_label = ttk.Label(controls_frame, text="Instructions: Use 'Detect' to set toggle by pressing, or type manually.\nAfter applying, use toggle to start/stop clicking.\nClicks at current mouse position.\nUse 'Reset' to change settings.", wraplength=500, justify='left')
instructions_label.grid(row=2, column=0, columnspan=3, pady=5, sticky='n')

# Status and Log Frame
log_frame = ttk.Frame(root)
log_frame.grid(row=5, column=0, sticky='nsew', padx=10, pady=5)
log_frame.columnconfigure(0, weight=1)
log_frame.rowconfigure(3, weight=1)

ttk.Label(log_frame, text="Click Log", style='Bold.TLabel').grid(row=0, column=0, pady=5, sticky='n')

current_interval_label = ttk.Label(log_frame, text="Current Interval Set: None")
current_interval_label.grid(row=1, column=0, pady=5, sticky='n')

ttk.Label(log_frame, text="Intervals between clicks (ms):").grid(row=2, column=0, pady=5, sticky='n')
click_list = tk.Listbox(log_frame, height=10)
click_list.grid(row=3, column=0, pady=5, sticky='nsew')

# Save/Load Frame
saveload_frame = ttk.Frame(root)
saveload_frame.grid(row=6, column=0, sticky='nsew', padx=10, pady=5)
saveload_frame.columnconfigure(0, weight=1)
saveload_frame.columnconfigure(1, weight=1)

save_button = ttk.Button(saveload_frame, text="Save Settings", command=save_settings)
save_button.grid(row=0, column=0, pady=10, sticky='ew')

load_button = ttk.Button(saveload_frame, text="Load Settings", command=load_settings)
load_button.grid(row=0, column=1, pady=10, sticky='ew')

root.mainloop()