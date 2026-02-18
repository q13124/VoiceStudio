"""Tests for ReverbEffect in backend.voice.effects.reverb.

GAP-TC-004: Test stubs for untested effects module.
"""

import numpy as np
import pytest

from backend.voice.effects.reverb import ReverbConfig, ReverbEffect


class TestReverbConfig:
    """Tests for ReverbConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ReverbConfig()
        assert config.room_size == 0.5
        assert config.damping == 0.5
        assert config.stereo_width == 1.0
        assert config.pre_delay_ms == 20.0
        assert config.decay_time == 2.0

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ReverbConfig(room_size=0.8, decay_time=3.5)
        assert config.room_size == 0.8
        assert config.decay_time == 3.5


class TestReverbEffect:
    """Tests for ReverbEffect class."""

    def test_initialization_default_config(self):
        """Test reverb initializes with default config."""
        effect = ReverbEffect()
        assert effect.enabled

    def test_initialization_custom_config(self):
        """Test reverb initializes with custom config."""
        config = ReverbConfig(room_size=0.9, damping=0.3)
        effect = ReverbEffect(config)
        assert effect._config.room_size == 0.9
        assert effect._config.damping == 0.3

    def test_process_preserves_shape(self):
        """Test that process preserves audio shape."""
        effect = ReverbEffect()
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        assert result.shape == audio.shape

    def test_process_silent_audio(self):
        """Test processing silent audio."""
        effect = ReverbEffect()
        audio = np.zeros(1000, dtype=np.float32)
        result = effect.process(audio, sample_rate=24000)
        # Silent audio should produce minimal reverb tail
        assert result.shape == audio.shape

    def test_disabled_effect_passthrough(self):
        """Test that disabled effect passes audio through unchanged."""
        effect = ReverbEffect()
        effect.enabled = False
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        np.testing.assert_array_equal(result, audio)

    def test_get_config_returns_dict(self):
        """Test that get_config returns configuration dictionary."""
        config = ReverbConfig(room_size=0.7)
        effect = ReverbEffect(config)
        config_dict = effect.get_config()
        assert isinstance(config_dict, dict)
        assert config_dict["room_size"] == 0.7
