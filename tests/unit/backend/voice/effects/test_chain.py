"""Tests for EffectsChain in backend.voice.effects.chain.

GAP-TC-004: Test stubs for untested effects module.
"""

import numpy as np
import pytest

from backend.voice.effects.chain import AudioEffect, EffectConfig, EffectsChain


class SimpleTestEffect(AudioEffect):
    """Simple effect for testing purposes."""
    
    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply simple gain."""
        return audio * 0.5


class GainEffect(AudioEffect):
    """Gain effect for testing."""
    
    def __init__(self, gain: float = 1.0):
        super().__init__()
        self.gain = gain
    
    def process(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply gain."""
        if not self.enabled:
            return audio
        return audio * self.gain


class TestEffectConfig:
    """Tests for EffectConfig dataclass."""

    def test_default_config(self):
        """Test default configuration values."""
        config = EffectConfig()
        assert config.enabled is True
        assert config.wet_mix == 1.0

    def test_custom_config(self):
        """Test custom configuration values."""
        config = EffectConfig(enabled=False, wet_mix=0.5)
        assert config.enabled is False
        assert config.wet_mix == 0.5


class TestAudioEffect:
    """Tests for AudioEffect base class."""

    def test_effect_name(self):
        """Test that effect has correct name."""
        effect = SimpleTestEffect()
        assert effect.name == "SimpleTestEffect"

    def test_effect_enabled_by_default(self):
        """Test effect is enabled by default."""
        effect = SimpleTestEffect()
        assert effect.enabled is True

    def test_effect_disable_enable(self):
        """Test enabling/disabling effect."""
        effect = SimpleTestEffect()
        effect.enabled = False
        assert effect.enabled is False
        effect.enabled = True
        assert effect.enabled is True

    def test_get_config(self):
        """Test getting effect configuration."""
        effect = SimpleTestEffect()
        config = effect.get_config()
        assert isinstance(config, dict)
        assert "enabled" in config
        assert "wet_mix" in config

    def test_set_config(self):
        """Test setting effect configuration."""
        effect = SimpleTestEffect()
        effect.set_config(enabled=False, wet_mix=0.3)
        assert effect.enabled is False


class TestEffectsChain:
    """Tests for EffectsChain class."""

    def test_empty_chain_initialization(self):
        """Test chain initializes empty."""
        chain = EffectsChain()
        assert len(chain.list_effects()) == 0
        assert not chain.bypassed

    def test_add_effect(self):
        """Test adding an effect."""
        chain = EffectsChain()
        effect = SimpleTestEffect()
        chain.add_effect(effect)
        assert len(chain.list_effects()) == 1
        assert "SimpleTestEffect" in chain.list_effects()

    def test_remove_effect(self):
        """Test removing an effect."""
        chain = EffectsChain()
        effect = SimpleTestEffect()
        chain.add_effect(effect)
        result = chain.remove_effect(effect)
        assert result is True
        assert len(chain.list_effects()) == 0

    def test_remove_effect_by_name(self):
        """Test removing effect by name."""
        chain = EffectsChain()
        chain.add_effect(SimpleTestEffect())
        result = chain.remove_effect_by_name("SimpleTestEffect")
        assert result is True
        assert len(chain.list_effects()) == 0

    def test_clear_effects(self):
        """Test clearing all effects."""
        chain = EffectsChain()
        chain.add_effect(SimpleTestEffect())
        chain.add_effect(GainEffect())
        chain.clear()
        assert len(chain.list_effects()) == 0

    def test_get_effect_by_name(self):
        """Test getting effect by name."""
        chain = EffectsChain()
        effect = SimpleTestEffect()
        chain.add_effect(effect)
        found = chain.get_effect("SimpleTestEffect")
        assert found is effect

    def test_get_nonexistent_effect(self):
        """Test getting nonexistent effect returns None."""
        chain = EffectsChain()
        found = chain.get_effect("NonExistent")
        assert found is None

    def test_move_effect(self):
        """Test moving effect position."""
        chain = EffectsChain()
        chain.add_effect(SimpleTestEffect())
        chain.add_effect(GainEffect())
        chain.move_effect("GainEffect", 0)
        effects = chain.list_effects()
        assert effects[0] == "GainEffect"

    def test_chain_bypass(self):
        """Test chain bypass."""
        chain = EffectsChain()
        chain.add_effect(GainEffect(gain=0.5))
        chain.bypassed = True
        
        audio = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        result = chain.process(audio, sample_rate=24000)
        np.testing.assert_array_equal(result, audio)

    def test_chain_process_sequential(self):
        """Test chain processes effects sequentially."""
        chain = EffectsChain()
        chain.add_effect(GainEffect(gain=0.5))
        chain.add_effect(GainEffect(gain=0.5))
        
        audio = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        result = chain.process(audio, sample_rate=24000)
        # Two 0.5 gains = 0.25 final
        expected = np.array([0.25, 0.25, 0.25], dtype=np.float32)
        np.testing.assert_array_almost_equal(result, expected)
