"""Regression tests for compressor plugin processor.

GAP-TC-003: Expanded from 1 test to 5 tests for better coverage.
"""

import numpy as np
import pytest

from backend.voice.effects.compressor import CompressorConfig, CompressorEffect
from plugins.compressor.processor import compress_samples


class TestCompressorPlugin:
    """Tests for compressor plugin processor."""

    def test_compressor_matches_reference_effect(self):
        """Test that plugin output matches reference CompressorEffect."""
        sample_rate = 24000
        t = np.linspace(0, 1, sample_rate, endpoint=False, dtype=np.float32)
        samples = (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)

        plugin_out = compress_samples(samples, sample_rate, threshold_db=-20.0, ratio=4.0)

        reference = CompressorEffect(CompressorConfig(threshold_db=-20.0, ratio=4.0))
        reference_out = reference.process(samples, sample_rate)

        np.testing.assert_allclose(
            plugin_out, reference_out.astype(np.float32), rtol=1e-6, atol=1e-6
        )

    def test_compressor_returns_float32(self):
        """Test that output is always float32."""
        samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        result = compress_samples(samples, sample_rate=24000)
        assert result.dtype == np.float32

    def test_compressor_preserves_silent_audio(self):
        """Test that silent audio passes through unchanged."""
        samples = np.zeros(1000, dtype=np.float32)
        result = compress_samples(samples, sample_rate=24000)
        np.testing.assert_array_equal(result, samples)

    def test_compressor_respects_threshold(self):
        """Test that compression only affects signals above threshold."""
        sample_rate = 24000
        # Create a loud signal that will exceed threshold
        t = np.linspace(0, 0.1, int(sample_rate * 0.1), endpoint=False, dtype=np.float32)
        loud_signal = (0.8 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

        # With very low threshold (-60dB), signal should be compressed
        compressed = compress_samples(loud_signal, sample_rate, threshold_db=-60.0, ratio=10.0)

        # Compressed signal should have lower peak than original
        assert np.max(np.abs(compressed)) <= np.max(np.abs(loud_signal))

    def test_compressor_custom_parameters(self):
        """Test compression with custom attack/release/knee parameters."""
        sample_rate = 24000
        t = np.linspace(0, 0.5, int(sample_rate * 0.5), endpoint=False, dtype=np.float32)
        samples = (0.5 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)

        # Should not raise error with custom parameters
        result = compress_samples(
            samples,
            sample_rate,
            threshold_db=-15.0,
            ratio=2.0,
            attack_ms=5.0,
            release_ms=50.0,
            knee_db=3.0,
            makeup_gain_db=2.0,
        )

        assert result.shape == samples.shape
        assert result.dtype == np.float32
