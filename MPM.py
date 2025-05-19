import numpy as np
import scipy.io.wavfile as wav
import matplotlib.pyplot as plt
from scipy.fft import fft, ifft

def compute_nsdf(signal, W):
    w = W // 2
    window = signal[:W]

    def autocorrelation_fft(x):
        x = np.pad(x, (0, w), 'constant')
        X = fft(x)
        S = X * np.conj(X)
        result = np.real(ifft(S))
        return result[:w]

    r_tau = autocorrelation_fft(window)
    x2 = window**2
    m_tau = np.array([np.sum(x2[:W - τ] + x2[τ:W]) for τ in range(w)])
    nsdf = 2 * r_tau / m_tau
    return nsdf

def pick_pitch_from_nsdf(nsdf, fs, k=0.9):
    nmax = np.max(nsdf[1:])
    key_maxima = []
    found_positive_slope = False

    for i in range(1, len(nsdf) - 1):
        if nsdf[i - 1] < 0 and nsdf[i] >= 0:
            found_positive_slope = True
            local_max = (i, nsdf[i])
        elif found_positive_slope and nsdf[i] > local_max[1]:
            local_max = (i, nsdf[i])
        elif found_positive_slope and nsdf[i] < 0:
            key_maxima.append(local_max)
            found_positive_slope = False

    for idx, value in key_maxima:
        if value >= k * nmax:
            if 1 < idx < len(nsdf) - 1:
                alpha = nsdf[idx - 1]
                beta = nsdf[idx]
                gamma = nsdf[idx + 1]
                p = 0.5 * (alpha - gamma) / (alpha - 2 * beta + gamma)
                idx = idx + p
            return fs / idx
    return 0

def detect_pitch_from_wav(file_path, window_size=8192, k=0.9):
    rate, data = wav.read(file_path)
    if data.ndim > 1:
        data = data[:, 0]
    data = data.astype(np.float64)

    start = len(data) // 3
    signal = data[start:start + window_size]
    nsdf = compute_nsdf(signal, window_size)
    pitch = pick_pitch_from_nsdf(nsdf, rate, k=k)

    return pitch
