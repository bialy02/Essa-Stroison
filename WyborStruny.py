import tkinter as tk
from tkinter import ttk, messagebox
import sounddevice as sd
import numpy as np
from tons import frequency_to_cents
from yin import yin
import PokazNajblizsza

GUITAR_NOTES = {
    'E2': 82.41, 'A2': 110.00, 'D3': 146.83,
    'G3': 196.00, 'B3': 246.94, 'E4': 329.63
}

def match_to_target(freq, target_freq):
    diff = freq - target_freq
    if abs(diff) < 1:
        status = "Nastrojona"
    elif diff > 0:
        status = "Za wysoko"
    else:
        status = "Za nisko"
    return status, round(diff, 2)

class TunerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stroik do Gitary")
        self.root.geometry("400x380")
        self.root.minsize(380, 380)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind('<Left>', self.change_string_with_keys)
        self.root.bind('<Right>', self.change_string_with_keys)
        self.string_names = list(GUITAR_NOTES.keys())
        self.selected_string = tk.StringVar(value=self.string_names[0])
        self.tuning_mode = tk.StringVar(value="manual")
        self.sample_rate = 44100
        self.block_duration = 0.2
        self.block_size = int(self.sample_rate * self.block_duration)
        self.stream = None
        self.listening = False

        self.create_widgets()

    def change_string_with_keys(self, event):
        if self.tuning_mode.get() != "manual":
            return

        try:
            current_index = self.string_names.index(self.selected_string.get())
        except ValueError:
            return

        if event.keysym == 'Right':
            new_index = (current_index + 1) % len(self.string_names)
        elif event.keysym == 'Left':
            new_index = (current_index - 1 + len(self.string_names)) % len(self.string_names)
        else:
            return

        new_note = self.string_names[new_index]
        self.selected_string.set(new_note)

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(expand=True, fill="both")

        mode_frame = ttk.LabelFrame(main_frame, text="Tryb strojenia", padding=10)
        mode_frame.pack(fill=tk.X, pady=5)
        mode_radio_container = ttk.Frame(mode_frame)
        mode_radio_container.pack()
        ttk.Radiobutton(mode_radio_container, text="Automatyczny", variable=self.tuning_mode, value="auto", command=self.toggle_mode).pack(side=tk.LEFT, padx=15)
        ttk.Radiobutton(mode_radio_container, text="Manualny", variable=self.tuning_mode, value="manual", command=self.toggle_mode).pack(side=tk.LEFT, padx=15)

        self.manual_selection_frame = ttk.LabelFrame(main_frame, text="Wybierz strunę (użyj strzałek ⬅️➡️)", padding=10)
        self.manual_selection_frame.pack(fill=tk.X, pady=5)
        self.manual_selection_frame.columnconfigure((0, 1, 2), weight=1)
        for i, key in enumerate(self.string_names):
            row, col = divmod(i, 3)
            rb = ttk.Radiobutton(self.manual_selection_frame, text=key, variable=self.selected_string, value=key)
            rb.grid(row=row, column=col, padx=5, pady=2, sticky="ew")

        status_info_frame = ttk.LabelFrame(main_frame, text="Informacje o strojeniu", padding=10)
        status_info_frame.pack(fill=tk.BOTH, pady=5, expand=True)
        self.status_label = ttk.Label(status_info_frame, text="Wybierz tryb i kliknij Start", font=("Arial", 16), justify=tk.CENTER)
        self.status_label.pack(pady=10, expand=True)
        self.info_label = ttk.Label(status_info_frame, text="", font=("Arial", 12), justify=tk.CENTER)
        self.info_label.pack(pady=10, expand=True)

        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(10, 0), fill=tk.X)
        btn_frame.columnconfigure((0, 1), weight=1)
        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start_listening)
        self.start_btn.grid(row=0, column=0, padx=5, sticky="ew")
        self.stop_btn = ttk.Button(btn_frame, text="Stop", command=self.stop, state=tk.DISABLED)
        self.stop_btn.grid(row=0, column=1, padx=5, sticky="ew")

        self.toggle_mode()

    def toggle_mode(self):
        is_manual = self.tuning_mode.get() == "manual"
        state = tk.NORMAL if is_manual else tk.DISABLED
        for child in self.manual_selection_frame.winfo_children():
            child.configure(state=state)
        self.stop()

    def audio_callback(self, indata, frames, time_info, status):
        signal = indata[:, 0]
        freq = yin(signal, self.sample_rate)
        if not self.listening or freq <= 0:
            return

        if self.tuning_mode.get() == "auto":
            note, status_note, diff, target_freq = PokazNajblizsza.match_guitar_note(freq)
            cents = frequency_to_cents(freq, target_freq)
            self.root.after(0, self.update_ui, note, status_note, f"{diff:+.2f} Hz", f"{cents:+.1f} centów")
        else:
            target_note = self.selected_string.get()
            target_freq = GUITAR_NOTES[target_note]
            status_text, diff = match_to_target(freq, target_freq)
            cents = frequency_to_cents(freq, target_freq)
            self.root.after(0, self.update_ui, target_note, status_text, f"{diff:+.2f} Hz", f"{cents:+.1f} centów")

    def update_ui(self, note, status, diff_hz, diff_cents):
        self.status_label.config(text=f"Struna: {note} - {status}")
        self.info_label.config(text=f"Różnica: {diff_hz} / {diff_cents}")

    def start_listening(self):
        if self.listening: return
        self.listening = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        if self.tuning_mode.get() == "manual":
             for child in self.manual_selection_frame.winfo_children():
                child.configure(state=tk.DISABLED)

        self.status_label.config(text="Słucham...")
        self.info_label.config(text="")
        try:
            self.stream = sd.InputStream(channels=1, callback=self.audio_callback, samplerate=self.sample_rate, blocksize=self.block_size)
            self.stream.start()
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można otworzyć mikrofonu: {e}")
            self.stop()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        self.listening = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

        if self.tuning_mode.get() == "manual":
            self.status_label.config(text="Wybierz strunę i kliknij Start")
            for child in self.manual_selection_frame.winfo_children():
                child.configure(state=tk.NORMAL)
        else:
            self.status_label.config(text="Tryb automatyczny: gotowy")

        self.info_label.config(text="")

    def on_closing(self):
        self.stop()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TunerApp(root)
    root.mainloop()