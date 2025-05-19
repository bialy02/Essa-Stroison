import numpy as np
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
    return nsdf, w

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


def nsdf_pitch_detection(signal, fs, W=None):
    if W is None or W > len(signal):
        W = len(signal)

    signal = signal[:W]
    signal = signal / np.max(np.abs(signal))  # normalizacja

    nsdf, _ = compute_nsdf(signal, W)
    pitch = pick_pitch_from_nsdf(nsdf, fs)
    return pitch

