"""Common DSP helpers for processor plugins."""

from __future__ import annotations

import numpy as np


def rms(samples: np.ndarray) -> float:
    if samples.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(samples, dtype=np.float32))))


def peak(samples: np.ndarray) -> float:
    if samples.size == 0:
        return 0.0
    return float(np.max(np.abs(samples)))


def apply_gain(samples: np.ndarray, gain_db: float) -> np.ndarray:
    gain_linear = float(10.0 ** (gain_db / 20.0))
    return np.asarray(samples * gain_linear, dtype=np.float32)


def normalize_peak(samples: np.ndarray, target_peak: float = 0.98) -> np.ndarray:
    current_peak = peak(samples)
    if current_peak <= 1e-9:
        return np.asarray(samples, dtype=np.float32)
    scale = target_peak / current_peak
    normalized = np.asarray(samples * scale, dtype=np.float32)
    return np.clip(normalized, -1.0, 1.0).astype(np.float32)
