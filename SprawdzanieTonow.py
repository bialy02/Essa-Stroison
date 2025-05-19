import numpy as np
from scipy.io import wavfile
import yin
import MPM
import time
import autocorrelation
import matplotlib
matplotlib.use('TkAgg')


GUITAR_NOTES = {
    'E2': 82.41,
    'A2': 110.00,
    'D3': 146.83,
    'G3': 196.00,
    'B3': 246.94,
    'E4': 329.63
}

def read_wav(file_path):
    sr, data = wavfile.read(file_path)
    if len(data.shape) == 2:
        data = data.mean(axis=1)
    return sr, data



def match_guitar_note(freq):
    closest_note = min(GUITAR_NOTES, key=lambda note: abs(GUITAR_NOTES[note] - freq))
    diff = freq - GUITAR_NOTES[closest_note]
    if abs(diff) < 1:
        status = "in tune"
    elif diff > 0:
        status = "too high"
    else:
        status = "too low"
    return closest_note, status, round(diff, 2)



if __name__ == "__main__":
    file_path = "testE.wav"

    sr, data = read_wav(file_path)

    segment = data[:sr*2]

    start_auto = time.time()

    freq_auto = autocorrelation.autocorrelation_pitch(segment, sr)

    end_auto = time.time()

    start_yin = time.time()
    freq_yin = yin.yin(segment, sr)
    end_yin = time.time()

    start_mpm = time.time()
    freq_mpm = MPM.detect_pitch_from_wav()
    end_mpm = time.time()

    note, status, diff = match_guitar_note(freq_auto)

    print(f"Dominująca częstotliwość (autokorelacja): {freq_auto:.2f} Hz, czas wykonywania {end_auto - start_auto:.2f} sekund")
    print(f"Dominująca częstotliwość (yin): {freq_yin:.2f} Hz, czas wykonywania {end_yin - start_yin:.2f} sekund")
    print(f"Dominująca częstotliwość (MPM): {freq_mpm:.2f} Hz, czas wykonywania {end_mpm - start_mpm:.2f} sekund")
    print(f"Najbliższy dźwięk gitarowy: {note}")
    print(f"Struna jest {status} ({diff} Hz różnicy)")
