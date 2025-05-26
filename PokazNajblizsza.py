import numpy as np
import sounddevice as sd
import time
from yin import yin


GUITAR_NOTES = {
    'E2': 82.41,
    'A2': 110.00,
    'D3': 146.83,
    'G3': 196.00,
    'B3': 246.94,
    'E4': 329.63
}


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


def audio_callback(indata, frames, time_info, status):
    signal = indata[:, 0]

    freq = yin(signal, sample_rate)
    if freq > 0:
        note, status_note, diff = match_guitar_note(freq)
        print(f"Detected frequency: {freq:.2f} Hz - Note: {note}, Status: {status_note} ({diff} Hz)")


if __name__ == "__main__":
    sample_rate = 44100
    block_duration = 0.1
    block_size = int(sample_rate * block_duration)

    print("Starting real-time pitch detection. Play guitar note...")

    with sd.InputStream(channels=1, callback=audio_callback, samplerate=sample_rate, blocksize=block_size):
        print("Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Stopped")
