"""Tests for PitchShiftEffect in backend.voice.effects.pitch.

GAP-TC-004: Test stubs for untested effects module.
"""

import numpy as np
import pytest

from backend.voice.effects.pitch import PitchShiftConfig, PitchShiftEffect


class TestPitchShiftConfig:
    """Tests for PitchShiftConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PitchShiftConfig()
        assert config.semitones == 0.0
        assert config.formant_preserve is True
        assert config.quality == "balanced"

    def test_custom_config(self):
        """Test custom configuration values."""
        config = PitchShiftConfig(semitones=5.0, quality="high")
        assert config.semitones == 5.0
        assert config.quality == "high"


class TestPitchShiftEffect:
    """Tests for PitchShiftEffect class."""

    def test_initialization_default_config(self):
        """Test pitch shifter initializes with default config."""
        effect = PitchShiftEffect()
        assert effect.enabled
        assert effect._config.semitones == 0.0

    def test_initialization_custom_config(self):
        """Test pitch shifter initializes with custom config."""
        config = PitchShiftConfig(semitones=-3.0)
        effect = PitchShiftEffect(config)
        assert effect._config.semitones == -3.0

    def test_process_preserves_shape(self):
        """Test that process preserves audio shape."""
        effect = PitchShiftEffect(PitchShiftConfig(semitones=2.0))
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        assert result.shape == audio.shape

    def test_zero_semitones_passthrough(self):
        """Test that zero semitones passes audio through unchanged."""
        effect = PitchShiftEffect()  # Default 0 semitones
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        np.testing.assert_array_equal(result, audio)

    def test_disabled_effect_passthrough(self):
        """Test that disabled effect passes audio through unchanged."""
        effect = PitchShiftEffect(PitchShiftConfig(semitones=5.0))
        effect.enabled = False
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        np.testing.assert_array_equal(result, audio)

    def test_set_semitones_clamps_range(self):
        """Test that set_semitones clamps to valid range."""
        effect = PitchShiftEffect()
        effect.set_semitones(20.0)
        assert effect._config.semitones == 12.0
        effect.set_semitones(-20.0)
        assert effect._config.semitones == -12.0

    def test_reset_clears_state(self):
        """Test that reset clears internal state."""
        effect = PitchShiftEffect()
        effect._last_phase = np.array([1, 2, 3])
        effect.reset()
        assert effect._last_phase is None

    def test_get_config_returns_dict(self):
        """Test that get_config returns configuration dictionary."""
        config = PitchShiftConfig(semitones=4.0)
        effect = PitchShiftEffect(config)
        config_dict = effect.get_config()
        assert isinstance(config_dict, dict)
        assert config_dict["semitones"] == 4.0
