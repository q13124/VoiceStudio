"""Pure DSP processing logic for the audio effect processor template."""

from __future__ import annotations

import numpy as np
from dsp_utils import apply_gain, normalize_peak
from parameters import EffectParameters


def process_samples(samples: np.ndarray, params: EffectParameters) -> np.ndarray:
    """Apply gain and optional normalization to float32 sample array."""
    processed = apply_gain(samples, params.gain_db)
    if params.normalize_output:
        processed = normalize_peak(processed, target_peak=params.target_peak)
    return processed.astype(np.float32)
