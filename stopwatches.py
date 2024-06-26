import tkinter as tk
from tkinter import ttk, simpledialog
import time
import keyboard

class Stopwatch:
    def __init__(self, parent, start_key, pause_key, reset_key, _app):
        self.start_time = None
        self.parent = parent
        self.running = False
        self.time_elapsed = 0
        self.app = _app
        self.destroyed = False

        self.start_key = start_key
        self.pause_key = pause_key
        self.reset_key = reset_key

        self.title_var = tk.StringVar(value="Stopwatch")
        self.title_label = ttk.Entry(parent, textvariable=self.title_var, font=("Helvetica", 16), justify='center')
        self.title_label.grid(row=0, column=0, columnspan=5, pady=5, sticky="ew")

        self.stopwatch_label = ttk.Label(parent, text="00:00:00:000", font=("Helvetica", 24), anchor='center')
        self.stopwatch_label.grid(row=1, column=0, columnspan=5, pady=5, sticky="ew")

        self.play_button = ttk.Button(parent, text=f"Play ({start_key})", command=self.start, width=10, style='TButton')
        self.play_button.grid(row=2, column=0, padx=2, pady=2, sticky="ew")

        self.pause_button = ttk.Button(parent, text=f"Pause ({pause_key})", command=self.pause, width=10, style='TButton')
        self.pause_button.grid(row=2, column=1, padx=2, pady=2, sticky="ew")

        self.reset_button = ttk.Button(parent, text=f"Reset ({reset_key})", command=self.reset, width=10, style='TButton')
        self.reset_button.grid(row=2, column=2, padx=2, pady=2, sticky="ew")

        self.settings_button = ttk.Button(parent, text="⚙️", command=self.open_settings, width=2, style='TButton')
        self.settings_button.grid(row=2, column=3, padx=2, pady=2, sticky="ew")

        self.remove_button = ttk.Button(parent, text="X", command=self.request_remove, width=2, style='TButton')
        self.remove_button.grid(row=2, column=4, padx=2, pady=2, sticky="ew")

        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(2, weight=1)
        self.parent.grid_columnconfigure(3, weight=1)
        self.parent.grid_columnconfigure(4, weight=1)

        self.bind_keys()
        self.update_stopwatch()

    def bind_keys(self):
        keyboard.add_hotkey(self.start_key, self.start)
        keyboard.add_hotkey(self.pause_key, self.pause)
        keyboard.add_hotkey(self.reset_key, self.reset)

    def unbind_keys(self):
        try:
            keyboard.remove_hotkey(self.start_key)
            keyboard.remove_hotkey(self.pause_key)
            keyboard.remove_hotkey(self.reset_key)
        except KeyError:
            pass

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time() - self.time_elapsed
            self.update_stopwatch()

    def pause(self):
        if self.running:
            self.running = False

    def reset(self):
        if self.destroyed:
            return
        self.running = False
        self.time_elapsed = 0
        self.stopwatch_label.config(text="00:00:00:000")

    def request_remove(self):
        self.app.remove_stopwatch(self)

    def update_stopwatch(self):
        if self.destroyed:
            return
        if self.running:
            self.time_elapsed = time.time() - self.start_time
            minutes, seconds = divmod(self.time_elapsed, 60)
            hours, minutes = divmod(minutes, 60)
            milliseconds = int((self.time_elapsed - int(self.time_elapsed)) * 1000)
            self.stopwatch_label.config(text=f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}:{milliseconds:03}")
        self.stopwatch_label.after(10, self.update_stopwatch)

    def open_settings(self):
        self.unbind_keys()

        start_key = simpledialog.askstring("Input", "Enter new start key:", parent=self.parent)
        if start_key:
            # Update the hotkey map in stopwatchApp
            if self.start_key in self.app.hotkey_map:
                self.app.hotkey_map[self.start_key].remove(self.start)
                if not self.app.hotkey_map[self.start_key]:
                    del self.app.hotkey_map[self.start_key]
            self.start_key = start_key
            self.app.hotkey_map[start_key] = self.app.hotkey_map.get(start_key, []) + [self.start]

        pause_key = simpledialog.askstring("Input", "Enter new pause key:", parent=self.parent)
        if pause_key:
            # Update the hotkey map in stopwatchApp
            if self.pause_key in self.app.hotkey_map:
                self.app.hotkey_map[self.pause_key].remove(self.pause)
                if not self.app.hotkey_map[self.pause_key]:
                    del self.app.hotkey_map[self.pause_key]
            self.pause_key = pause_key
            self.app.hotkey_map[pause_key] = self.app.hotkey_map.get(pause_key, []) + [self.pause]

        reset_key = simpledialog.askstring("Input", "Enter new reset key:", parent=self.parent)
        if reset_key:
            # Update the hotkey map in stopwatchApp
            if self.reset_key in self.app.hotkey_map:
                self.app.hotkey_map[self.reset_key].remove(self.reset)
                if not self.app.hotkey_map[self.reset_key]:
                    del self.app.hotkey_map[self.reset_key]
            self.reset_key = reset_key
            self.app.hotkey_map[reset_key] = self.app.hotkey_map.get(reset_key, []) + [self.reset]

        self.play_button.config(text=f"Play ({self.start_key})")
        self.pause_button.config(text=f"Pause ({self.pause_key})")
        self.reset_button.config(text=f"Reset ({self.reset_key})")

        self.bind_keys()

    def remove_stopwatch(self):
        self.destroyed = True
        self.parent.destroy()


# noinspection PyUnusedLocal
class StopwatchApp:
    def __init__(self, _root):
        self.root = _root
        self.root.title("Stopwatches")
        self.root.geometry("530x230")
        self.root.resizable(False, True)  # Only allow vertical resizing
        self.root.minsize(530, 230)  # Set minimum size for vertical resizing

        self.style = ttk.Style()
        self.style.configure('TButton', font=("Helvetica", 16))

        self.main_frame = ttk.Frame(_root)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        self.second_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((50, 0), window=self.second_frame, anchor="nw")

        self.stopwatches = []
        self.hotkey_map = {}
        self.add_stopwatch()  # Initialize with one stopwatch

        # Bind the mouse wheel to the canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_wheel)

        # Bind resizing event
        self.root.bind('<Configure>', self.on_root_resize)
        self.add_stopwatch_button = ttk.Button(self.second_frame, text="Add stopwatch", command=self.add_stopwatch, style='TButton')
        self.add_stopwatch_button.pack(side=tk.BOTTOM, pady=10)

    def on_canvas_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_mouse_wheel(self, event):
        if self.canvas.bbox("all")[3] > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def on_root_resize(self, event):
        self.center_stopwatches()

    def add_stopwatch(self):
        stopwatch_frame = ttk.Frame(self.second_frame)
        stopwatch_frame.pack(pady=10, padx=10, fill=tk.X)

        # Center the stopwatch frame
        stopwatch_frame.grid_columnconfigure(0, weight=1)
        stopwatch_frame.grid_columnconfigure(1, weight=1)
        stopwatch_frame.grid_columnconfigure(2, weight=1)
        stopwatch_frame.grid_columnconfigure(3, weight=1)
        stopwatch_frame.grid_columnconfigure(4, weight=1)
        stopwatch_frame.grid_columnconfigure(5, weight=1)

        # Define default hotkeys
        start_key = 'F1'
        pause_key = 'F2'
        reset_key = 'F3'

        stopwatch = Stopwatch(stopwatch_frame, start_key, pause_key, reset_key, self)
        self.stopwatches.append(stopwatch)

        # Add hotkeys to the map
        self.hotkey_map[start_key] = self.hotkey_map.get(start_key, []) + [stopwatch.start]
        self.hotkey_map[pause_key] = self.hotkey_map.get(pause_key, []) + [stopwatch.pause]
        self.hotkey_map[reset_key] = self.hotkey_map.get(reset_key, []) + [stopwatch.reset]

        # Bind the hotkeys
        self.bind_hotkeys(start_key)
        self.bind_hotkeys(pause_key)
        self.bind_hotkeys(reset_key)

        # Update the scroll region
        self.canvas.update_idletasks()
        self.on_canvas_configure(None)
        self.on_root_resize(None)

    def bind_hotkeys(self, key):
        if key in self.hotkey_map:
            keyboard.add_hotkey(key, self.run_hotkeys, args=(key,))

    def run_hotkeys(self, key):
        if key in self.hotkey_map:
            for func in self.hotkey_map[key]:
                func()

    def remove_stopwatch(self, stopwatch):
        if len(self.stopwatches) > 1:
            self.stopwatches.remove(stopwatch)
            stopwatch.unbind_keys()
            stopwatch.remove_stopwatch()

            # Remove hotkeys from the map
            if stopwatch.start_key in self.hotkey_map:
                self.hotkey_map[stopwatch.start_key].remove(stopwatch.start)
                if not self.hotkey_map[stopwatch.start_key]:
                    del self.hotkey_map[stopwatch.start_key]
                    try:
                        keyboard.remove_hotkey(stopwatch.start_key)
                    except KeyError:
                        pass

            if stopwatch.pause_key in self.hotkey_map:
                self.hotkey_map[stopwatch.pause_key].remove(stopwatch.pause)
                if not self.hotkey_map[stopwatch.pause_key]:
                    del self.hotkey_map[stopwatch.pause_key]
                    try:
                        keyboard.remove_hotkey(stopwatch.pause_key)
                    except KeyError:
                        pass

            if stopwatch.reset_key in self.hotkey_map:
                self.hotkey_map[stopwatch.reset_key].remove(stopwatch.reset)
                if not self.hotkey_map[stopwatch.reset_key]:
                    del self.hotkey_map[stopwatch.reset_key]
                    try:
                        keyboard.remove_hotkey(stopwatch.reset_key)
                    except KeyError:
                        pass

            # Update the scroll region
            self.canvas.update_idletasks()
            self.on_canvas_configure(None)
            self.center_stopwatches()

    def center_stopwatches(self):
        self.second_frame.update_idletasks()  # Update the frame to get the correct dimensions
        frame_width = self.second_frame.winfo_width()
        canvas_width = self.canvas.winfo_width()

        if canvas_width > frame_width:
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
            self.canvas.coords(self.canvas_window, (canvas_width / 2 - frame_width / 2, 0))
        elif canvas_width < frame_width:
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
            self.canvas.coords(self.canvas_window, (canvas_width / 2 - frame_width / 2, 0))
        else:
            self.canvas.itemconfig(self.canvas_window, width=frame_width)
            self.canvas.coords(self.canvas_window, (0, 0))

if __name__ == "__main__":
    root = tk.Tk()
    app = StopwatchApp(root)
    root.mainloop()
