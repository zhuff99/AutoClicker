# Auto Clicker

An advanced auto-clicker application built with Python and Tkinter. This tool simulates mouse clicks at random intervals to mimic human behavior, with features like multiple interval sets, random pauses, burst clicking, and more. It's designed for tasks requiring automated clicking while avoiding detection as a bot by varying click patterns.

## Features

- **Multiple Interval Sets**: Add up to 3 sets of min/max click intervals (in ms). A random set is chosen each time auto-clicking is toggled on.
- **Toggle Control**: Start/stop clicking with a configurable keyboard key or mouse button (e.g., Mouse4 or Mouse5).
- **Random Pauses**: Configure a percentage chance for pauses between clicks, with customizable min/max pause duration.
- **Burst Clicking**: Add short bursts of faster clicks (e.g., 2-4 clicks at 30-50 ms intervals) with configurable chance and parameters to simulate human rapid clicking.
- **Logging**: Real-time log of click intervals, pauses, and bursts in the GUI.
- **Save/Load Settings**: Save and load configurations (intervals, toggle key, pauses, bursts) to/from JSON files.
- **Resizable GUI**: The interface scales when the window is resized.
- **Key/Mouse Detection**: Easily detect and set the toggle key or mouse button by pressing it.

## Installation

1. **Prerequisites**:
   - Python 3.6 or higher (tested on 3.12.3).
   - Install required libraries:
     ```
     pip install pynput
     ```
     Tkinter is included with Python; no additional installation needed.

2. **Download the Script**:
   - Copy the provided code into a file named `auto_clicker.py`.

## Usage

1. **Run the Application**:
   ```
   python auto_clicker.py
   ```

2. **Configure Settings**:
   - **Intervals**: Enter min/max values and click "Add Interval Set" (up to 3). Remove selected sets if needed.
   - **Pauses**: Set chance (%) and min/max duration (ms).
   - **Bursts**: Set chance (%), min/max clicks per burst, and min/max interval (ms) for burst clicks.
   - **Toggle Key**: Type a key (e.g., 'f') or use "Detect Key/Mouse" to press a key/mouse button. Supports Mouse4/Mouse5.
   - Click "Apply Settings and Start Listener" to activate.

3. **Start/Stop Clicking**:
   - Use the toggle key/button to start/stop auto-clicking.
   - Clicks occur at the current mouse position.
   - Monitor the log for intervals, pauses, and bursts.

4. **Save/Load**:
   - Use "Save Settings" and "Load Settings" to manage configurations.

5. **Reset**:
   - Click "Reset Settings" to stop listeners and clear the log.

## Dependencies

- **pynput**: For mouse/keyboard control and listening.
- **tkinter**: For the GUI (built-in with Python).
- **json**: For saving/loading settings (built-in).
- **threading, time, random**: Built-in Python modules.

## Notes

- **Human-Like Behavior**: Random intervals, pauses, and bursts help mimic natural clicking patterns.
- **Limitations**: Maximum 3 interval sets. Bursts and pauses are optional (default 0%).
- **Troubleshooting**: If intervals seem inconsistent, check system load (time.sleep accuracy varies). The log shows actual elapsed times.
- **Safety**: Use responsibly; auto-clickers may violate terms of service in games/apps.

## License

This project is open-source and available under the MIT License. Feel free to modify and distribute.
