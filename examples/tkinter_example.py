"""
An example of using WinGrab with tkinter.

This example is a simple window with a button. When the button is clicked, the PID of the window under the cursor will be
displayed in the window.

Note that the PID of the window under the cursor will be displayed as "Loading..." before the PID is obtained.

This example is only for demonstration purposes. It is not recommended to use this example directly in your project.

@Author: Jianzhang Chen
"""

import threading
import tkinter as tk
import time

# If you import wingrab in another thread, you will get an error!
# You can import wingrab in the main thread and use it in another thread.
import wingrab


class ExampleWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WinGrab Example Window")
        self.geometry("600x400")

        self._pid_label = tk.Label(self, text="PID: ", font=("TkDefaultFont", 18))
        self._pid_label.pack(pady=10)

        self._grab_button = tk.Button(self, text="Grab", height=2, command=self.start_grab, width=10)
        self._grab_button.pack(pady=10)

        self._is_grab_finished = False

    def start_grab(self):
        self._is_grab_finished = False  # mark the grab is not finished
        self.set_loading_text()

        thread = threading.Thread(target=self.grab)
        thread.start()

    def grab(self):
        pid = wingrab.grab()

        self._is_grab_finished = True  # mark the grab is finished
        self._pid_label.config(text=f"PID: {pid}")

    def set_loading_text(self):
        if not self._is_grab_finished:
            self._pid_label.config(text=f"PID: Loading... (Current Time: {time.strftime('%H:%M:%S')})")
            self.after(1000, self.set_loading_text)


if __name__ == '__main__':
    window = ExampleWindow()
    window.mainloop()
