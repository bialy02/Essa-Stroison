import numpy as np
from scipy.io import wavfile

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

def autocorrelation_pitch(signal, sr, fmin=70, fmax=350):
    corr = np.correlate(signal, signal, mode='full')
    corr = corr[len(corr)//2:]

    min_lag = int(sr / fmax)
    max_lag = int(sr / fmin)

    peak = np.argmax(corr[min_lag:max_lag]) + min_lag

    pitch = sr / peak
    return pitch

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

    freq = autocorrelation_pitch(segment, sr)
    note, status, diff = match_guitar_note(freq)

    print(f"Dominująca częstotliwość (autokorelacja): {freq:.2f} Hz")
    print(f"Najbliższy dźwięk gitarowy: {note}")
    print(f"Struna jest {status} ({diff} Hz różnicy)")
