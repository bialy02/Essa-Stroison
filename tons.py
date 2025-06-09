import numpy as np

def frequency_to_cents(frequency, target_frequency):
    if frequency <= 0 or target_frequency <= 0:
        return 0.0
    return 1200 * np.log2(frequency / target_frequency)
