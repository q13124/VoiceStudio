"""Reverb effect processing logic."""

from __future__ import annotations

import numpy as np

from backend.voice.effects.reverb import ReverbConfig, ReverbEffect


def apply_reverb(
    samples: np.ndarray,
    sample_rate: int,
    room_size: float = 0.5,
    damping: float = 0.5,
    wet_dry_mix: float = 1.0,
    pre_delay_ms: float = 20.0,
    stereo_width: float = 1.0,
    decay_time: float = 2.0,
) -> np.ndarray:
    config = ReverbConfig(
        room_size=room_size,
        damping=damping,
        wet_mix=wet_dry_mix,
        pre_delay_ms=pre_delay_ms,
        stereo_width=stereo_width,
        decay_time=decay_time,
    )
    effect = ReverbEffect(config=config)
    return effect.process(samples.astype(np.float32), sample_rate).astype(np.float32)
