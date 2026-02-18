"""Unit tests for processor logic."""

import numpy as np
from parameters import EffectParameters
from processor import process_samples


def test_process_samples_preserves_shape():
    samples = np.array([0.1, -0.2, 0.05, 0.0], dtype=np.float32)
    params = EffectParameters(gain_db=0.0, normalize_output=False)
    result = process_samples(samples, params)
    assert result.shape == samples.shape


def test_process_samples_applies_gain():
    samples = np.array([0.1, -0.1], dtype=np.float32)
    params = EffectParameters(gain_db=6.0, normalize_output=False)
    result = process_samples(samples, params)
    assert abs(result[0]) > abs(samples[0])


def test_process_samples_normalizes_peak():
    samples = np.array([0.95, -0.95], dtype=np.float32)
    params = EffectParameters(gain_db=6.0, normalize_output=True, target_peak=0.9)
    result = process_samples(samples, params)
    assert np.max(np.abs(result)) <= 0.9 + 1e-5
