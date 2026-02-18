"""Micro-benchmark smoke test for template processing path."""

import time

import numpy as np
from parameters import EffectParameters
from processor import process_samples


def test_process_1s_audio_under_100ms():
    sample_rate = 44100
    samples = np.random.uniform(-0.2, 0.2, sample_rate).astype(np.float32)
    params = EffectParameters(gain_db=0.0, normalize_output=True)

    start = time.perf_counter()
    result = process_samples(samples, params)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert len(result) == len(samples)
    assert elapsed_ms < 100.0
