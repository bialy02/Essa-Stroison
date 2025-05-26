import numpy as np
import sounddevice as sd
import time
import tkinter as tk
from tkinter import ttk, messagebox
from yin import yin  # zakładamy, że to funkcja

GUITAR_NOTES = {
    'E2': 82.41,
    'A2': 110.00,
    'D3': 146.83,
    'G3': 196.00,
    'B3': 246.94,
    'E4': 329.63
}

def match_to_target(freq, target_freq):
    diff = freq - target_freq
    if abs(diff) < 1:
        status = "in tune"
    elif diff > 0:
        status = "too high"
    else:
        status = "too low"
    return status, round(diff, 2)

class TunerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Guitar Tuner")

        self.selected_string = tk.StringVar(value='E2')
        self.sample_rate = 44100
        self.block_duration = 0.1
        self.block_size = int(self.sample_rate * self.block_duration)
        self.stream = None
        self.listening = False

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack()

        ttk.Label(frame, text="Wybierz strunę do strojenia:").pack(pady=5)

        self.combo = ttk.Combobox(frame, values=list(GUITAR_NOTES.keys()), textvariable=self.selected_string, state='readonly')
        self.combo.pack(pady=5)

        # Nowy przycisk "Start" i "Stop"
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_listening)
        self.start_btn.grid(row=0, column=0, padx=5)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5)

        self.status_label = ttk.Label(frame, text="", font=("Arial", 14))
        self.status_label.pack(pady=10)

    def audio_callback(self, indata, frames, time_info, status):
        signal = indata[:, 0]
        freq = yin(signal, self.sample_rate)

        if freq > 0:
            target_freq = GUITAR_NOTES[self.selected_string.get()]
            status_text, diff = match_to_target(freq, target_freq)
            self.update_status(f"Częstotliwość: {freq:.2f} Hz\nStatus: {status_text} ({diff} Hz)")

    def update_status(self, text):
        self.root.after(0, lambda: self.status_label.config(text=text))

    def start_listening(self):
        if self.listening:
            messagebox.showinfo("Info", "Nasłuch już działa!")
            return

        self.listening = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.combo.config(state=tk.DISABLED)
        self.status_label.config(text="Nasłuch... zagraj na gitarze!")

        self.stream = sd.InputStream(
            channels=1,
            callback=self.audio_callback,
            samplerate=self.sample_rate,
            blocksize=self.block_size
        )

        self.stream.start()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self.listening = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.combo.config(state='readonly')
        self.status_label.config(text="Wybierz strunę i kliknij Start")

if __name__ == "__main__":
    root = tk.Tk()
    app = TunerApp(root)

    def on_closing():
        app.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
