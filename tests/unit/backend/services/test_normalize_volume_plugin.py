"""Regression tests for normalize volume plugin processor.

GAP-TC-003: Expanded from 1 test to 5 tests for better coverage.
"""

import numpy as np
import pytest

from plugins.normalize_volume.processor import normalize_samples


def _reference_peak_normalize(samples: np.ndarray) -> np.ndarray:
    max_val = np.max(np.abs(samples))
    if max_val > 0:
        return (samples / max_val * 0.95).astype(np.float32)
    return samples.astype(np.float32)


class TestNormalizeVolume:
    """Tests for normalize volume plugin processor."""

    def test_normalize_volume_peak_matches_reference_logic(self):
        """Test peak normalization matches reference implementation."""
        rng = np.random.default_rng(1234)
        samples = rng.uniform(-0.4, 0.4, 24000).astype(np.float32)
        sample_rate = 24000

        plugin_out = normalize_samples(samples, sample_rate, mode="peak")
        reference_out = _reference_peak_normalize(samples)

        np.testing.assert_allclose(plugin_out, reference_out.astype(np.float32), rtol=1e-6, atol=1e-6)

    def test_normalize_volume_returns_float32(self):
        """Test that output is always float32."""
        samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        result = normalize_samples(samples, sample_rate=24000, mode="peak")
        assert result.dtype == np.float32

    def test_normalize_volume_silent_audio_unchanged(self):
        """Test that silent audio is returned unchanged."""
        samples = np.zeros(1000, dtype=np.float32)
        result = normalize_samples(samples, sample_rate=24000, mode="peak")
        np.testing.assert_array_equal(result, samples)

    def test_normalize_volume_peak_reaches_target(self):
        """Test that peak normalization reaches 0.95 target level."""
        samples = np.array([0.1, -0.2, 0.3, -0.15], dtype=np.float32)
        result = normalize_samples(samples, sample_rate=24000, mode="peak")
        # Peak should be at 0.95 after normalization
        assert np.max(np.abs(result)) == pytest.approx(0.95, rel=1e-6)

    def test_normalize_volume_lufs_not_implemented(self):
        """Test that LUFS mode raises NotImplementedError."""
        samples = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        with pytest.raises(NotImplementedError, match="LUFS normalization"):
            normalize_samples(samples, sample_rate=24000, mode="lufs")
