"""Regression and performance tests for reverb plugin processor."""

import time

import numpy as np

from backend.voice.effects.reverb import ReverbConfig, ReverbEffect
from plugins.reverb.processor import apply_reverb


def test_reverb_matches_reference_effect():
    sample_rate = 44100
    t = np.linspace(0, 1, sample_rate, endpoint=False, dtype=np.float32)
    samples = (0.25 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

    plugin_out = apply_reverb(samples, sample_rate, room_size=0.5, damping=0.5)

    reference = ReverbEffect(ReverbConfig(room_size=0.5, damping=0.5))
    reference_out = reference.process(samples, sample_rate)

    np.testing.assert_allclose(plugin_out, reference_out.astype(np.float32), rtol=1e-6, atol=1e-6)


def test_reverb_processes_1s_audio_under_100ms():
    sample_rate = 44100
    rng = np.random.default_rng(5678)
    samples = rng.uniform(-0.2, 0.2, sample_rate).astype(np.float32)

    start = time.perf_counter()
    output = apply_reverb(samples, sample_rate)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert len(output) == len(samples)
    assert elapsed_ms < 100.0
