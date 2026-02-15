"""
Audio Effects Chain.

Task 4.5: Professional audio effects processing.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EffectConfig:
    """Base configuration for effects."""
    enabled: bool = True
    wet_mix: float = 1.0  # 0-1, wet/dry mix


class AudioEffect(ABC):
    """
    Base class for audio effects.
    """

    def __init__(self, config: EffectConfig | None = None):
        """
        Initialize effect.

        Args:
            config: Effect configuration
        """
        self._config = config or EffectConfig()
        self._name = self.__class__.__name__

    @property
    def name(self) -> str:
        """Get effect name."""
        return self._name

    @property
    def enabled(self) -> bool:
        """Check if effect is enabled."""
        return self._config.enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable/disable effect."""
        self._config.enabled = value

    @abstractmethod
    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """
        Process audio through the effect.

        Args:
            audio: Input audio samples
            sample_rate: Sample rate

        Returns:
            Processed audio
        """
        pass

    def reset(self) -> None:
        """Reset effect state (for stateful effects)."""
        pass

    def get_config(self) -> dict[str, Any]:
        """Get effect configuration."""
        return {"enabled": self._config.enabled, "wet_mix": self._config.wet_mix}

    def set_config(self, **kwargs) -> None:
        """Set effect configuration."""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)


class EffectsChain:
    """
    Chain of audio effects for sequential processing.

    Features:
    - Add/remove effects
    - Enable/disable individual effects
    - Bypass entire chain
    - Wet/dry mixing
    """

    def __init__(self):
        """Initialize effects chain."""
        self._effects: list[AudioEffect] = []
        self._bypassed = False

    def add_effect(self, effect: AudioEffect) -> None:
        """Add an effect to the chain."""
        self._effects.append(effect)
        logger.debug(f"Added effect: {effect.name}")

    def remove_effect(self, effect: AudioEffect) -> bool:
        """Remove an effect from the chain."""
        if effect in self._effects:
            self._effects.remove(effect)
            return True
        return False

    def remove_effect_by_name(self, name: str) -> bool:
        """Remove an effect by name."""
        for effect in self._effects:
            if effect.name == name:
                self._effects.remove(effect)
                return True
        return False

    def clear(self) -> None:
        """Remove all effects."""
        self._effects.clear()

    def get_effect(self, name: str) -> AudioEffect | None:
        """Get an effect by name."""
        for effect in self._effects:
            if effect.name == name:
                return effect
        return None

    def list_effects(self) -> list[str]:
        """List effect names in order."""
        return [e.name for e in self._effects]

    def move_effect(self, name: str, new_index: int) -> bool:
        """Move an effect to a new position."""
        effect = self.get_effect(name)
        if effect:
            self._effects.remove(effect)
            self._effects.insert(new_index, effect)
            return True
        return False

    @property
    def bypassed(self) -> bool:
        """Check if chain is bypassed."""
        return self._bypassed

    @bypassed.setter
    def bypassed(self, value: bool) -> None:
        """Set bypass state."""
        self._bypassed = value

    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """
        Process audio through the effects chain.

        Args:
            audio: Input audio
            sample_rate: Sample rate

        Returns:
            Processed audio
        """
        if self._bypassed or not self._effects:
            return audio

        result = audio.copy()

        for effect in self._effects:
            if effect.enabled:
                try:
                    processed = effect.process(result, sample_rate)

                    # Apply wet/dry mix
                    wet = effect._config.wet_mix
                    result = result * (1 - wet) + processed * wet if wet < 1.0 else processed

                except Exception as e:
                    logger.error(f"Effect {effect.name} error: {e}")

        return result

    def reset(self) -> None:
        """Reset all effects."""
        for effect in self._effects:
            effect.reset()

    def get_chain_config(self) -> dict[str, Any]:
        """Get configuration for entire chain."""
        return {
            "bypassed": self._bypassed,
            "effects": [
                {"name": e.name, **e.get_config()}
                for e in self._effects
            ],
        }
