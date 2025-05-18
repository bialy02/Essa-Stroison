import numpy as np
import librosa

GUITAR_NOTES = {
    'E2': 82.41,
    'A2': 110.00,
    'D3': 146.83,
    'G3': 196.00,
    'B3': 246.94,
    'E4': 329.63
}

def detect_pitch_yin(file_path):
    y, sr = librosa.load(file_path)
    f0 = librosa.yin(y, fmin=70, fmax=350, sr=sr)
    f0 = f0[~np.isnan(f0)]
    if len(f0) == 0:
        return None
    return np.median(f0)

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
    freq = detect_pitch_yin(file_path)
    if freq is None:
        print("Nie udało się wykryć częstotliwości.")
    else:
        note, status, diff = match_guitar_note(freq)
        print(f"Dominująca częstotliwość: {freq:.2f} Hz")
        print(f"Najbliższy dźwięk gitarowy: {note}")
        print(f"Struna jest {status} ({diff} Hz różnicy)")
