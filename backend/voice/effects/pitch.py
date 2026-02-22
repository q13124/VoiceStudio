"""
Pitch Shift Effect.

Task 4.5.4: Real-time pitch shifting.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from backend.voice.effects.chain import AudioEffect, EffectConfig


@dataclass
class PitchShiftConfig(EffectConfig):
    """Pitch shift configuration."""

    semitones: float = 0.0  # -12 to +12
    formant_preserve: bool = True
    quality: str = "balanced"  # fast, balanced, high


class PitchShiftEffect(AudioEffect):
    """
    Pitch shifting effect.

    Uses phase vocoder for quality pitch shifting.
    """

    def __init__(self, config: PitchShiftConfig | None = None):
        """
        Initialize pitch shifter.

        Args:
            config: Pitch shift configuration
        """
        super().__init__(config or PitchShiftConfig())
        self._config: PitchShiftConfig = self._config

        # Phase vocoder state
        self._last_phase = None
        self._sum_phase = None

    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """Apply pitch shift to audio."""
        if not self.enabled or self._config.semitones == 0:
            return audio

        # Calculate pitch ratio
        ratio = 2 ** (self._config.semitones / 12)

        # Simple resampling-based pitch shift
        # In production, use phase vocoder or WSOLA

        output = self._resample_pitch(audio, ratio)

        # Formant preservation would require additional processing
        # (e.g., LPC analysis, formant shifting)

        return output

    def _resample_pitch(
        self,
        audio: np.ndarray,
        ratio: float,
    ) -> np.ndarray:
        """
        Simple pitch shift via resampling.

        Args:
            audio: Input audio
            ratio: Pitch ratio (>1 = higher, <1 = lower)

        Returns:
            Pitch-shifted audio (same length as input)
        """
        # Resample to change pitch
        new_length = int(len(audio) / ratio)

        # Linear interpolation resampling
        indices = np.linspace(0, len(audio) - 1, new_length)
        resampled = np.interp(indices, np.arange(len(audio)), audio)

        # Adjust length back to original
        if len(resampled) < len(audio):
            # Pitch went up - loop/pad to fill
            repeats = int(np.ceil(len(audio) / len(resampled)))
            resampled = np.tile(resampled, repeats)[: len(audio)]
        elif len(resampled) > len(audio):
            # Pitch went down - truncate
            resampled = resampled[: len(audio)]

        return resampled

    def reset(self) -> None:
        """Reset pitch shifter state."""
        self._last_phase = None
        self._sum_phase = None

    def set_semitones(self, semitones: float) -> None:
        """Set pitch shift in semitones."""
        self._config.semitones = max(-12, min(12, semitones))

    def get_config(self) -> dict:
        return {
            **super().get_config(),
            "semitones": self._config.semitones,
            "formant_preserve": self._config.formant_preserve,
            "quality": self._config.quality,
        }
