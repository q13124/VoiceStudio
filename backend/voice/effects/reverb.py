"""
Reverb Effect.

Task 4.5.1: Reverb/room simulation effect.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np

from backend.voice.effects.chain import AudioEffect, EffectConfig


@dataclass
class ReverbConfig(EffectConfig):
    """Reverb configuration."""
    
    room_size: float = 0.5  # 0-1
    damping: float = 0.5    # 0-1
    stereo_width: float = 1.0  # 0-1
    pre_delay_ms: float = 20.0
    decay_time: float = 2.0  # seconds


class ReverbEffect(AudioEffect):
    """
    Reverb effect using algorithmic reverb.
    """
    
    def __init__(self, config: Optional[ReverbConfig] = None):
        """
        Initialize reverb effect.
        
        Args:
            config: Reverb configuration
        """
        super().__init__(config or ReverbConfig())
        self._config: ReverbConfig = self._config
        
        # Delay lines for Schroeder reverb
        self._delays = []
        self._allpass = []
    
    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """Apply reverb to audio."""
        if not self.enabled:
            return audio
        
        # Initialize delay lines if needed
        if not self._delays:
            self._init_delay_lines(sample_rate)
        
        output = audio.copy()
        
        # Simple reverb implementation
        # In production, use proper Schroeder or convolution reverb
        
        # Pre-delay
        pre_delay_samples = int(self._config.pre_delay_ms * sample_rate / 1000)
        if pre_delay_samples > 0:
            output = np.concatenate([
                np.zeros(pre_delay_samples),
                audio[:-pre_delay_samples] if len(audio) > pre_delay_samples else audio,
            ])[:len(audio)]
        
        # Apply simple feedback delay for reverb tail
        decay = self._config.room_size * 0.5
        delay_samples = int(self._config.decay_time * sample_rate / 4)
        
        if delay_samples > 0 and delay_samples < len(output):
            for i in range(delay_samples, len(output)):
                output[i] += output[i - delay_samples] * decay
        
        # Apply damping (simple low-pass filter)
        if self._config.damping > 0:
            damping = self._config.damping * 0.9
            for i in range(1, len(output)):
                output[i] = output[i] * (1 - damping) + output[i-1] * damping
        
        return output
    
    def _init_delay_lines(self, sample_rate: int) -> None:
        """Initialize delay lines for reverb algorithm."""
        # Schroeder reverb delay times (in samples)
        base_delays = [1557, 1617, 1491, 1422, 1277, 1356, 1188, 1116]
        
        self._delays = [
            int(d * sample_rate / 44100)
            for d in base_delays
        ]
    
    def reset(self) -> None:
        """Reset reverb state."""
        self._delays = []
        self._allpass = []
    
    def get_config(self) -> dict:
        return {
            **super().get_config(),
            "room_size": self._config.room_size,
            "damping": self._config.damping,
            "stereo_width": self._config.stereo_width,
            "pre_delay_ms": self._config.pre_delay_ms,
            "decay_time": self._config.decay_time,
        }
