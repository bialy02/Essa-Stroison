import numpy as np

def autocorrelation_pitch(signal, sr, fmin=70, fmax=350):
    corr = np.correlate(signal, signal, mode='full')
    corr = corr[len(corr)//2:]

    min_lag = int(sr / fmax)
    max_lag = int(sr / fmin)

    peak = np.argmax(corr[min_lag:max_lag]) + min_lag

    pitch = sr / peak
    return pitch