"""Normalize effect processing logic."""

from __future__ import annotations

import numpy as np


def normalize_samples(
    samples: np.ndarray,
    sample_rate: int,
    mode: str = "peak",
    target_lufs: float = -23.0,
) -> np.ndarray:
    # Mirrors app/core/audio/post_fx.py normalize behavior for peak mode.
    method = (mode or "peak").lower()
    audio = samples.astype(np.float32)
    if method == "lufs":
        raise NotImplementedError(
            "LUFS normalization requires pyloudnorm (or equivalent); "
            "use mode='peak' for peak normalization."
        )
    if method == "peak":
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            return (audio / max_val * 0.95).astype(np.float32)
    return audio.astype(np.float32)
