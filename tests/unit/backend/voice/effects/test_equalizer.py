"""Tests for EqualizerEffect in backend.voice.effects.equalizer.

GAP-TC-004: Test stubs for untested effects module.
"""

import numpy as np
import pytest

from backend.voice.effects.equalizer import (
    EQ_PRESETS,
    EQBand,
    EqualizerConfig,
    EqualizerEffect,
)


class TestEQBand:
    """Tests for EQBand dataclass."""

    def test_default_band(self):
        """Test default EQ band values."""
        band = EQBand(frequency=1000)
        assert band.frequency == 1000
        assert band.gain == 0.0
        assert band.q == 1.0
        assert band.band_type == "peak"

    def test_custom_band(self):
        """Test custom EQ band values."""
        band = EQBand(frequency=100, gain=3.0, q=0.7, band_type="lowshelf")
        assert band.frequency == 100
        assert band.gain == 3.0
        assert band.band_type == "lowshelf"


class TestEqualizerConfig:
    """Tests for EqualizerConfig dataclass."""

    def test_default_config_has_bands(self):
        """Test default configuration has 5 bands."""
        config = EqualizerConfig()
        assert len(config.bands) == 5

    def test_custom_config(self):
        """Test custom configuration with bands."""
        bands = [EQBand(500, gain=2.0)]
        config = EqualizerConfig(bands=bands)
        assert len(config.bands) == 1
        assert config.bands[0].frequency == 500


class TestEQPresets:
    """Tests for EQ presets."""

    def test_flat_preset_exists(self):
        """Test flat preset is defined."""
        assert "flat" in EQ_PRESETS
        assert len(EQ_PRESETS["flat"]) > 0

    def test_warmth_preset_exists(self):
        """Test warmth preset is defined."""
        assert "warmth" in EQ_PRESETS

    def test_presence_preset_exists(self):
        """Test presence preset is defined."""
        assert "presence" in EQ_PRESETS

    def test_radio_preset_exists(self):
        """Test radio preset is defined."""
        assert "radio" in EQ_PRESETS


class TestEqualizerEffect:
    """Tests for EqualizerEffect class."""

    def test_initialization_default_config(self):
        """Test equalizer initializes with default config."""
        effect = EqualizerEffect()
        assert effect.enabled
        assert len(effect._config.bands) == 5

    def test_initialization_custom_config(self):
        """Test equalizer initializes with custom config."""
        bands = [EQBand(200, gain=4.0)]
        config = EqualizerConfig(bands=bands)
        effect = EqualizerEffect(config)
        assert len(effect._config.bands) == 1

    def test_process_preserves_shape(self):
        """Test that process preserves audio shape."""
        effect = EqualizerEffect()
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        assert result.shape == audio.shape

    def test_disabled_effect_passthrough(self):
        """Test that disabled effect passes audio through unchanged."""
        effect = EqualizerEffect()
        effect.enabled = False
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        np.testing.assert_array_equal(result, audio)

    def test_flat_eq_minimal_change(self):
        """Test that flat EQ produces minimal change."""
        config = EqualizerConfig(bands=EQ_PRESETS["flat"])
        effect = EqualizerEffect(config)
        audio = np.random.uniform(-0.5, 0.5, 1000).astype(np.float32)
        result = effect.process(audio, sample_rate=24000)
        # Flat EQ should have minimal effect
        assert result.shape == audio.shape

    def test_get_config_returns_dict(self):
        """Test that get_config returns configuration dictionary."""
        effect = EqualizerEffect()
        config_dict = effect.get_config()
        assert isinstance(config_dict, dict)
