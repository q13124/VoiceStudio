"""Tests for audio processing functions"""
import numpy as np
import pytest
from processing import apply_gain, normalize


def test_apply_gain_zero_db():
    audio = np.array([0.5, -0.5, 0.0], dtype=np.float32)
    result = apply_gain(audio, 0)
    np.testing.assert_array_almost_equal(result, audio)

def test_apply_gain_positive():
    audio = np.array([0.1, -0.1], dtype=np.float32)
    result = apply_gain(audio, 6)  # 6dB ~= 2x
    assert result[0] > audio[0]

def test_apply_gain_clipping():
    audio = np.array([0.5, -0.5], dtype=np.float32)
    result = apply_gain(audio, 20)  # 20dB ~= 10x
    assert np.all(np.abs(result) <= 1.0)

def test_normalize_silent():
    audio = np.array([0.0, 0.0], dtype=np.float32)
    result = normalize(audio)
    np.testing.assert_array_equal(result, audio)

def test_normalize_scales():
    audio = np.array([0.25, -0.25], dtype=np.float32)
    result = normalize(audio)
    assert np.max(np.abs(result)) <= 1.0
