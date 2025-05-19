import numpy as np
import librosa
def generate_sine_wave(frequency=440, duration=2.0, sample_rate=44100, amplitude=0.5):

    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    signal = amplitude * np.sin(2 * np.pi * frequency * t)
    return signal, sample_rate

def difference_function(x, W, max_tau):

    x = np.append(x, np.zeros(W + max_tau))
    d = np.zeros(max_tau)
    for tau in range(1, max_tau):
        if tau + W <= len(x):
            d[tau] = np.sum((x[:W] - x[tau:tau+W]) ** 2)
    return d

def cumulative_mean_normalized_difference(d):

    cmndf = np.copy(d)
    cmndf[1:] = d[1:] * np.arange(1, len(d)) / np.cumsum(d[1:])
    cmndf[0] = 1
    return cmndf

def get_pitch_from_cmndf(cmndf, threshold=0.1):

    for tau in range(2, len(cmndf)):
        if cmndf[tau] < threshold:
            while tau + 1 < len(cmndf) and cmndf[tau + 1] < cmndf[tau]:
                tau += 1
            return tau
    return 0  # brak f0

def yin(signal, sr, W=None, max_freq=500, threshold=0.1):

    if W is None:
        W = len(signal)
    max_tau = int(sr / 50)  # dolna granica: 50 Hz
    d = difference_function(signal, W, max_tau)
    cmndf = cumulative_mean_normalized_difference(d)
    tau = get_pitch_from_cmndf(cmndf, threshold)
    if tau == 0:
        return 0
    return sr / tau




