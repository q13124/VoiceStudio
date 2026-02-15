"""
Noise Reduction Effect.

Task 4.5.5: Noise reduction and voice enhancement.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from backend.voice.effects.chain import AudioEffect, EffectConfig


@dataclass
class NoiseReductionConfig(EffectConfig):
    """Noise reduction configuration."""

    reduction_amount: float = 0.5  # 0-1
    noise_floor_db: float = -40.0
    smoothing: float = 0.98
    use_spectral: bool = True  # Spectral vs. simple gate


class NoiseReductionEffect(AudioEffect):
    """
    Noise reduction effect.

    Uses spectral subtraction for noise removal.
    """

    def __init__(self, config: NoiseReductionConfig | None = None):
        """
        Initialize noise reduction.

        Args:
            config: Noise reduction configuration
        """
        super().__init__(config or NoiseReductionConfig())
        self._config: NoiseReductionConfig = self._config

        # Noise profile
        self._noise_profile = None
        self._noise_floor = None

    def process(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """Apply noise reduction to audio."""
        if not self.enabled:
            return audio

        if self._config.use_spectral:
            return self._spectral_reduction(audio, sample_rate)
        else:
            return self._simple_gate(audio, sample_rate)

    def _spectral_reduction(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """Spectral subtraction noise reduction."""
        # FFT parameters
        fft_size = 2048
        hop_size = fft_size // 4

        # Pad audio
        padded = np.pad(audio, (0, fft_size - len(audio) % fft_size))
        output = np.zeros_like(padded)

        # Window
        window = np.hanning(fft_size)

        # Estimate noise if not set
        if self._noise_floor is None:
            noise_threshold = 10 ** (self._config.noise_floor_db / 20)
            self._noise_floor = noise_threshold

        # Process frames
        for i in range(0, len(padded) - fft_size, hop_size):
            frame = padded[i:i + fft_size] * window

            # FFT
            spectrum = np.fft.rfft(frame)
            magnitude = np.abs(spectrum)
            phase = np.angle(spectrum)

            # Spectral subtraction
            reduction = self._config.reduction_amount
            noise_floor = self._noise_floor

            # Apply reduction to magnitudes below threshold
            reduced_mag = magnitude.copy()
            for j in range(len(magnitude)):
                if magnitude[j] < noise_floor * 10:
                    reduced_mag[j] *= (1 - reduction)

            # Reconstruct
            new_spectrum = reduced_mag * np.exp(1j * phase)
            new_frame = np.fft.irfft(new_spectrum)

            # Overlap-add
            output[i:i + fft_size] += new_frame * window

        # Normalize overlap-add
        output /= 2

        return output[:len(audio)]

    def _simple_gate(
        self,
        audio: np.ndarray,
        sample_rate: int,
    ) -> np.ndarray:
        """Simple noise gate."""
        threshold = 10 ** (self._config.noise_floor_db / 20)
        reduction = self._config.reduction_amount

        output = audio.copy()

        # Simple gating
        envelope = np.abs(audio)

        # Smooth envelope
        smoothing = self._config.smoothing
        for i in range(1, len(envelope)):
            envelope[i] = smoothing * envelope[i-1] + (1 - smoothing) * envelope[i]

        # Apply gate
        for i in range(len(output)):
            if envelope[i] < threshold:
                output[i] *= (1 - reduction)

        return output

    def learn_noise_profile(self, noise_audio: np.ndarray) -> None:
        """
        Learn noise profile from sample.

        Args:
            noise_audio: Sample of noise only
        """
        # Calculate average spectrum of noise
        fft_size = 2048

        spectra = []
        for i in range(0, len(noise_audio) - fft_size, fft_size // 2):
            frame = noise_audio[i:i + fft_size]
            spectrum = np.abs(np.fft.rfft(frame))
            spectra.append(spectrum)

        if spectra:
            self._noise_profile = np.mean(spectra, axis=0)
            self._noise_floor = np.mean(self._noise_profile)

    def reset(self) -> None:
        """Reset noise reduction state."""
        self._noise_profile = None
        self._noise_floor = None

    def get_config(self) -> dict:
        return {
            **super().get_config(),
            "reduction_amount": self._config.reduction_amount,
            "noise_floor_db": self._config.noise_floor_db,
            "smoothing": self._config.smoothing,
            "use_spectral": self._config.use_spectral,
            "has_noise_profile": self._noise_profile is not None,
        }
