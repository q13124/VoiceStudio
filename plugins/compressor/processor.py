"""Compressor effect processing logic."""

from __future__ import annotations

import numpy as np

from backend.voice.effects.compressor import CompressorConfig, CompressorEffect


def compress_samples(
    samples: np.ndarray,
    sample_rate: int,
    threshold_db: float = -20.0,
    ratio: float = 4.0,
    attack_ms: float = 10.0,
    release_ms: float = 100.0,
    knee_db: float = 6.0,
    makeup_gain_db: float = 0.0,
) -> np.ndarray:
    config = CompressorConfig(
        threshold_db=threshold_db,
        ratio=ratio,
        attack_ms=attack_ms,
        release_ms=release_ms,
        knee_db=knee_db,
        makeup_gain_db=makeup_gain_db,
    )
    effect = CompressorEffect(config=config)
    return effect.process(samples.astype(np.float32), sample_rate).astype(np.float32)
