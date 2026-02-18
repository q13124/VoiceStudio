"""Tests for CompressorEffect in backend.voice.effects.compressor.

GAP-TC-004: Test stubs for untested effects module.
"""

import numpy as np
import pytest

from backend.voice.effects.compressor import CompressorConfig, CompressorEffect


class TestCompressorConfig:
    """Tests for CompressorConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CompressorConfig()
        assert config.threshold_db == -20.0
        assert config.ratio == 4.0
        assert config.attack_ms == 10.0
        assert config.release_ms == 100.0
        assert config.knee_db == 6.0
        assert config.makeup_gain_db == 0.0

    def test_custom_config(self):
        """Test custom configuration values."""
        config = CompressorConfig(
            threshold_db=-15.0,
            ratio=2.0,
            attack_ms=5.0,
            release_ms=50.0,
        )
        assert config.threshold_db == -15.0
        assert config.ratio == 2.0


class TestCompressorEffect:
    """Tests for CompressorEffect class."""

    def test_initialization_default_config(self):
        """Test compressor initializes with default config."""
        effect = CompressorEffect()
        assert effect.enabled

    def test_initialization_custom_config(self):
        """Test compressor initializes with custom config."""
        config = CompressorConfig(threshold_db=-10.0, ratio=8.0)
        effect = CompressorEffect(config)
        assert effect._config.threshold_db == -10.0
        assert effect._config.ratio == 8.0

    def test_process_preserves_shape(self):
        """Test that process preserves audio shape."""
        effect = CompressorEffect()
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        assert result.shape == audio.shape

    def test_process_silent_audio(self):
        """Test processing silent audio."""
        effect = CompressorEffect()
        audio = np.zeros(1000, dtype=np.float32)
        result = effect.process(audio, sample_rate=24000)
        np.testing.assert_array_equal(result, audio)

    def test_disabled_effect_passthrough(self):
        """Test that disabled effect passes audio through unchanged."""
        effect = CompressorEffect()
        effect.enabled = False
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        np.testing.assert_array_equal(result, audio)

    def test_reset_clears_envelope(self):
        """Test that reset clears the envelope state."""
        effect = CompressorEffect()
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        effect.process(audio, sample_rate=24000)
        effect.reset()
        assert effect._envelope == 0.0

    def test_get_config_returns_dict(self):
        """Test that get_config returns configuration dictionary."""
        config = CompressorConfig(threshold_db=-25.0)
        effect = CompressorEffect(config)
        config_dict = effect.get_config()
        assert isinstance(config_dict, dict)
        assert config_dict["threshold_db"] == -25.0
