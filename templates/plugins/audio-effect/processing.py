"""Audio effect processing - pure functions."""

import numpy as np


def apply_gain(audio_array: np.ndarray, gain_db: float) -> np.ndarray:
    """Apply gain to audio."""
    if gain_db == 0:
        return audio_array.copy()
    gain_linear = 10 ** (gain_db / 20)
    processed = audio_array * gain_linear
    return np.clip(processed, -1.0, 1.0)

def normalize(audio_array: np.ndarray) -> np.ndarray:
    """Normalize audio to -1..1 range."""
    max_val = np.max(np.abs(audio_array))
    if max_val > 0:
        return audio_array / max_val
    return audio_array
