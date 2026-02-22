"""
Compressor Effect.

Task 4.5.3: Dynamic range compression for voice.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from backend.voice.effects.chain import AudioEffect, EffectConfig


@dataclass
class CompressorConfig(EffectConfig):
    """Compressor configuration."""

    threshold_db: float = -20.0
    ratio: float = 4.0  # 4:1 compression
    attack_ms: float = 10.0
    release_ms: float = 100.0
    knee_db: float = 6.0  # Soft knee
    makeup_gain_db: float = 0.0


class CompressorEffect(AudioEffect):
    """
    Dynamic range compressor effect.
    """

    def __init__(self, config: CompressorConfig | None = None):
        """
        Initialize compressor.

        Args:
            config: Compressor configuration
        """
        super().__init__(config or CompressorConfig())
        self._config: CompressorConfig = self._config

        # Envelope follower state
        self._envelope = 0.0

    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """Apply compression to audio."""
        if not self.enabled:
            return audio

        output = audio.copy()

        # Calculate time constants
        attack = np.exp(-1.0 / (self._config.attack_ms * sample_rate / 1000))
        release = np.exp(-1.0 / (self._config.release_ms * sample_rate / 1000))

        threshold = 10 ** (self._config.threshold_db / 20)
        ratio = self._config.ratio
        10 ** (self._config.knee_db / 20)
        makeup = 10 ** (self._config.makeup_gain_db / 20)

        envelope = self._envelope

        for i in range(len(output)):
            # Get input level
            input_level = abs(audio[i])

            # Update envelope follower
            if input_level > envelope:
                envelope = attack * envelope + (1 - attack) * input_level
            else:
                envelope = release * envelope + (1 - release) * input_level

            # Calculate gain reduction
            if envelope > threshold:
                # Above threshold - compress
                overshoot = envelope / threshold
                gain = (1 / overshoot) ** (1 - 1 / ratio)
            else:
                gain = 1.0

            # Apply gain with makeup
            output[i] = audio[i] * gain * makeup

        self._envelope = envelope

        return output

    def reset(self) -> None:
        """Reset compressor state."""
        self._envelope = 0.0

    def get_config(self) -> dict:
        return {
            **super().get_config(),
            "threshold_db": self._config.threshold_db,
            "ratio": self._config.ratio,
            "attack_ms": self._config.attack_ms,
            "release_ms": self._config.release_ms,
            "knee_db": self._config.knee_db,
            "makeup_gain_db": self._config.makeup_gain_db,
        }
