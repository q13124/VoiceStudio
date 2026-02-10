"""
Equalizer Effect.

Task 4.5.2: Parametric EQ for voice shaping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from backend.voice.effects.chain import AudioEffect, EffectConfig


@dataclass
class EQBand:
    """A single EQ band."""
    frequency: float  # Hz
    gain: float = 0.0  # dB (-12 to +12)
    q: float = 1.0  # Q factor
    band_type: str = "peak"  # peak, lowshelf, highshelf, lowpass, highpass


@dataclass
class EqualizerConfig(EffectConfig):
    """Equalizer configuration."""
    
    bands: List[EQBand] = field(default_factory=lambda: [
        EQBand(frequency=80, gain=0, band_type="lowshelf"),
        EQBand(frequency=250, gain=0, band_type="peak"),
        EQBand(frequency=1000, gain=0, band_type="peak"),
        EQBand(frequency=4000, gain=0, band_type="peak"),
        EQBand(frequency=12000, gain=0, band_type="highshelf"),
    ])


# Voice-optimized presets
EQ_PRESETS: Dict[str, List[EQBand]] = {
    "flat": [
        EQBand(80, 0, 1.0, "lowshelf"),
        EQBand(250, 0, 1.0, "peak"),
        EQBand(1000, 0, 1.0, "peak"),
        EQBand(4000, 0, 1.0, "peak"),
        EQBand(12000, 0, 1.0, "highshelf"),
    ],
    "warmth": [
        EQBand(80, 3, 0.7, "lowshelf"),
        EQBand(200, 2, 1.0, "peak"),
        EQBand(3000, -2, 1.0, "peak"),
        EQBand(8000, -1, 1.0, "highshelf"),
    ],
    "presence": [
        EQBand(100, -2, 0.7, "lowshelf"),
        EQBand(250, 0, 1.0, "peak"),
        EQBand(3000, 3, 1.2, "peak"),
        EQBand(5000, 2, 1.0, "peak"),
        EQBand(10000, 1, 1.0, "highshelf"),
    ],
    "radio": [
        EQBand(80, -6, 0.7, "highpass"),
        EQBand(300, 2, 1.0, "peak"),
        EQBand(3000, 4, 1.0, "peak"),
        EQBand(8000, -3, 0.7, "lowpass"),
    ],
    "telephone": [
        EQBand(300, 0, 1.0, "highpass"),
        EQBand(1000, 3, 0.5, "peak"),
        EQBand(3400, 0, 1.0, "lowpass"),
    ],
}


class EqualizerEffect(AudioEffect):
    """
    Parametric equalizer effect.
    """
    
    def __init__(self, config: Optional[EqualizerConfig] = None):
        """
        Initialize equalizer.
        
        Args:
            config: EQ configuration
        """
        super().__init__(config or EqualizerConfig())
        self._config: EqualizerConfig = self._config
        
        # Filter states
        self._filter_states = []
    
    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """Apply EQ to audio."""
        if not self.enabled:
            return audio
        
        output = audio.copy()
        
        for band in self._config.bands:
            if band.gain == 0 and band.band_type == "peak":
                continue
            
            output = self._apply_band(output, sample_rate, band)
        
        return output
    
    def _apply_band(
        self,
        audio: np.ndarray,
        sample_rate: int,
        band: EQBand,
    ) -> np.ndarray:
        """Apply a single EQ band."""
        # Calculate biquad coefficients
        coeffs = self._calculate_coefficients(sample_rate, band)
        
        if coeffs is None:
            return audio
        
        b0, b1, b2, a0, a1, a2 = coeffs
        
        # Normalize coefficients
        b0 /= a0
        b1 /= a0
        b2 /= a0
        a1 /= a0
        a2 /= a0
        
        # Apply biquad filter
        output = np.zeros_like(audio)
        x1, x2, y1, y2 = 0, 0, 0, 0
        
        for i, x in enumerate(audio):
            y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
            output[i] = y
            x2, x1 = x1, x
            y2, y1 = y1, y
        
        return output
    
    def _calculate_coefficients(
        self,
        sample_rate: int,
        band: EQBand,
    ) -> Optional[tuple]:
        """Calculate biquad filter coefficients."""
        omega = 2 * np.pi * band.frequency / sample_rate
        sin_omega = np.sin(omega)
        cos_omega = np.cos(omega)
        alpha = sin_omega / (2 * band.q)
        
        A = 10 ** (band.gain / 40)
        
        if band.band_type == "peak":
            b0 = 1 + alpha * A
            b1 = -2 * cos_omega
            b2 = 1 - alpha * A
            a0 = 1 + alpha / A
            a1 = -2 * cos_omega
            a2 = 1 - alpha / A
            
        elif band.band_type == "lowshelf":
            b0 = A * ((A + 1) - (A - 1) * cos_omega + 2 * np.sqrt(A) * alpha)
            b1 = 2 * A * ((A - 1) - (A + 1) * cos_omega)
            b2 = A * ((A + 1) - (A - 1) * cos_omega - 2 * np.sqrt(A) * alpha)
            a0 = (A + 1) + (A - 1) * cos_omega + 2 * np.sqrt(A) * alpha
            a1 = -2 * ((A - 1) + (A + 1) * cos_omega)
            a2 = (A + 1) + (A - 1) * cos_omega - 2 * np.sqrt(A) * alpha
            
        elif band.band_type == "highshelf":
            b0 = A * ((A + 1) + (A - 1) * cos_omega + 2 * np.sqrt(A) * alpha)
            b1 = -2 * A * ((A - 1) + (A + 1) * cos_omega)
            b2 = A * ((A + 1) + (A - 1) * cos_omega - 2 * np.sqrt(A) * alpha)
            a0 = (A + 1) - (A - 1) * cos_omega + 2 * np.sqrt(A) * alpha
            a1 = 2 * ((A - 1) - (A + 1) * cos_omega)
            a2 = (A + 1) - (A - 1) * cos_omega - 2 * np.sqrt(A) * alpha
            
        else:
            return None
        
        return b0, b1, b2, a0, a1, a2
    
    def apply_preset(self, preset_name: str) -> bool:
        """Apply a preset EQ setting."""
        if preset_name in EQ_PRESETS:
            self._config.bands = EQ_PRESETS[preset_name].copy()
            return True
        return False
    
    def list_presets(self) -> List[str]:
        """List available presets."""
        return list(EQ_PRESETS.keys())
    
    def set_band(
        self,
        index: int,
        frequency: Optional[float] = None,
        gain: Optional[float] = None,
        q: Optional[float] = None,
    ) -> None:
        """Modify a single band."""
        if 0 <= index < len(self._config.bands):
            band = self._config.bands[index]
            if frequency is not None:
                band.frequency = frequency
            if gain is not None:
                band.gain = max(-12, min(12, gain))
            if q is not None:
                band.q = max(0.1, min(10, q))
    
    def get_config(self) -> dict:
        return {
            **super().get_config(),
            "bands": [
                {
                    "frequency": b.frequency,
                    "gain": b.gain,
                    "q": b.q,
                    "type": b.band_type,
                }
                for b in self._config.bands
            ],
        }
