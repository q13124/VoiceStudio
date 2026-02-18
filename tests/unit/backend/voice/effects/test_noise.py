"""Tests for NoiseReductionEffect in backend.voice.effects.noise.

GAP-TC-004: Test stubs for untested effects module.
"""

import numpy as np
import pytest

from backend.voice.effects.noise import NoiseReductionConfig, NoiseReductionEffect


class TestNoiseReductionConfig:
    """Tests for NoiseReductionConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = NoiseReductionConfig()
        assert config.reduction_amount == 0.5
        assert config.noise_floor_db == -40.0
        assert config.smoothing == 0.98
        assert config.use_spectral is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = NoiseReductionConfig(reduction_amount=0.8, use_spectral=False)
        assert config.reduction_amount == 0.8
        assert config.use_spectral is False


class TestNoiseReductionEffect:
    """Tests for NoiseReductionEffect class."""

    def test_initialization_default_config(self):
        """Test noise reduction initializes with default config."""
        effect = NoiseReductionEffect()
        assert effect.enabled
        assert effect._noise_profile is None

    def test_initialization_custom_config(self):
        """Test noise reduction initializes with custom config."""
        config = NoiseReductionConfig(reduction_amount=0.3)
        effect = NoiseReductionEffect(config)
        assert effect._config.reduction_amount == 0.3

    def test_process_preserves_shape(self):
        """Test that process preserves audio shape."""
        effect = NoiseReductionEffect()
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        assert result.shape == audio.shape

    def test_process_silent_audio(self):
        """Test processing silent audio."""
        effect = NoiseReductionEffect()
        audio = np.zeros(1000, dtype=np.float32)
        result = effect.process(audio, sample_rate=24000)
        np.testing.assert_array_equal(result, audio)

    def test_disabled_effect_passthrough(self):
        """Test that disabled effect passes audio through unchanged."""
        effect = NoiseReductionEffect()
        effect.enabled = False
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        np.testing.assert_array_equal(result, audio)

    def test_spectral_mode(self):
        """Test spectral noise reduction mode."""
        config = NoiseReductionConfig(use_spectral=True)
        effect = NoiseReductionEffect(config)
        audio = np.random.uniform(-0.1, 0.1, 2048).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        assert result.shape == audio.shape

    def test_simple_gate_mode(self):
        """Test simple gate noise reduction mode."""
        config = NoiseReductionConfig(use_spectral=False)
        effect = NoiseReductionEffect(config)
        audio = np.random.uniform(-0.1, 0.1, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        assert result.shape == audio.shape
