"""
EQ Module for VoiceStudio
Advanced parametric equalizer for precise frequency shaping

Compatible with:
- Python 3.10+
- numpy>=1.26.0
- scipy>=1.9.0
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

try:
    from scipy import signal

    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    logger.warning("scipy not installed. Install with: pip install scipy")


class EQBand:
    """Represents a single EQ band."""

    def __init__(
        self,
        frequency: float,
        gain_db: float = 0.0,
        q: float = 1.0,
        band_type: str = "peaking",
        enabled: bool = True,
    ):
        """
        Initialize EQ band.

        Args:
            frequency: Center frequency in Hz
            gain_db: Gain in dB (-24 to +24)
            q: Q factor (bandwidth control, 0.1 to 10.0)
            band_type: Band type ('peaking', 'low_shelf', 'high_shelf', 'lowpass', 'highpass', 'bandpass', 'notch')
            enabled: Whether band is enabled
        """
        self.frequency = frequency
        self.gain_db = gain_db
        self.q = q
        self.band_type = band_type
        self.enabled = enabled


class ParametricEQ:
    """
    Parametric Equalizer for precise frequency shaping.

    Supports:
    - Multiple parametric bands
    - Peaking, shelf, and filter types
    - Q control for bandwidth
    - Gain control per band
    - Band enable/disable
    - Preset EQ curves
    """

    def __init__(self, sample_rate: int = 24000, num_bands: int = 10):
        """
        Initialize Parametric EQ.

        Args:
            sample_rate: Default sample rate for processing
            num_bands: Maximum number of bands
        """
        self.sample_rate = sample_rate
        self.num_bands = num_bands
        self.bands: list[EQBand] = []

    def add_band(
        self,
        frequency: float,
        gain_db: float = 0.0,
        q: float = 1.0,
        band_type: str = "peaking",
        enabled: bool = True,
    ) -> EQBand | None:
        """
        Add an EQ band.

        Args:
            frequency: Center frequency in Hz
            gain_db: Gain in dB
            q: Q factor
            band_type: Band type
            enabled: Whether band is enabled

        Returns:
            Created EQBand instance
        """
        if len(self.bands) >= self.num_bands:
            logger.warning(f"Maximum number of bands ({self.num_bands}) reached")
            return None

        band = EQBand(frequency, gain_db, q, band_type, enabled)
        self.bands.append(band)
        return band

    def remove_band(self, index: int):
        """Remove an EQ band by index."""
        if 0 <= index < len(self.bands):
            del self.bands[index]

    def clear_bands(self):
        """Clear all EQ bands."""
        self.bands.clear()

    def process(
        self,
        audio: np.ndarray,
        sample_rate: int | None = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Process audio with parametric EQ.

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)
            **kwargs: Additional processing options

        Returns:
            Processed audio array
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if not HAS_SCIPY:
            logger.warning("scipy required for EQ processing")
            return audio

        if not self.bands:
            return audio

        # Process each channel
        if len(audio.shape) == 1:
            audio = audio.reshape(1, -1)
            was_mono = True
        else:
            was_mono = False

        processed_channels = []

        for channel in audio:
            processed = channel.copy()

            # Apply each band in sequence
            for band in self.bands:
                if not band.enabled:
                    continue

                processed = self._apply_band(processed, band, sample_rate)

            processed_channels.append(processed)

        result = np.array(processed_channels)
        if was_mono:
            result = result[0]

        # Normalize to prevent clipping
        max_val = np.max(np.abs(result))
        if max_val > 0.95:
            result = result / max_val * 0.95

        return result

    def _apply_band(self, audio: np.ndarray, band: EQBand, sample_rate: int) -> np.ndarray:
        """Apply a single EQ band to audio."""
        nyquist = sample_rate / 2.0
        normalized_freq = band.frequency / nyquist

        if normalized_freq >= 1.0:
            normalized_freq = 0.99
        if normalized_freq <= 0.0:
            normalized_freq = 0.01

        gain_linear = 10.0 ** (band.gain_db / 20.0)

        try:
            if band.band_type == "peaking":
                # Parametric peaking filter
                b, a = signal.iirpeak(normalized_freq, Q=band.q, fs=sample_rate)
                filtered = signal.filtfilt(b, a, audio)
                # Apply gain
                processed = audio + (filtered - audio) * (gain_linear - 1.0)

            elif band.band_type == "low_shelf":
                # Low shelf filter
                b, a = signal.iirfilter(
                    2,
                    normalized_freq,
                    btype="lowpass",
                    ftype="butter",
                    output="ba",
                )
                filtered = signal.filtfilt(b, a, audio)
                processed = audio + (filtered - audio) * (gain_linear - 1.0)

            elif band.band_type == "high_shelf":
                # High shelf filter
                b, a = signal.iirfilter(
                    2,
                    normalized_freq,
                    btype="highpass",
                    ftype="butter",
                    output="ba",
                )
                filtered = signal.filtfilt(b, a, audio)
                processed = audio + (filtered - audio) * (gain_linear - 1.0)

            elif band.band_type == "lowpass":
                # Lowpass filter
                b, a = signal.iirfilter(4, normalized_freq, btype="lowpass", ftype="butter")
                processed = signal.filtfilt(b, a, audio) * gain_linear

            elif band.band_type == "highpass":
                # Highpass filter
                b, a = signal.iirfilter(4, normalized_freq, btype="highpass", ftype="butter")
                processed = signal.filtfilt(b, a, audio) * gain_linear

            elif band.band_type == "bandpass":
                # Bandpass filter
                bandwidth = normalized_freq / band.q
                low = max(0.01, normalized_freq - bandwidth / 2)
                high = min(0.99, normalized_freq + bandwidth / 2)
                b, a = signal.iirfilter(4, [low, high], btype="bandpass", ftype="butter")
                filtered = signal.filtfilt(b, a, audio)
                processed = audio + (filtered - audio) * (gain_linear - 1.0)

            elif band.band_type == "notch":
                # Notch filter
                bandwidth = normalized_freq / band.q
                low = max(0.01, normalized_freq - bandwidth / 2)
                high = min(0.99, normalized_freq + bandwidth / 2)
                b, a = signal.iirfilter(4, [low, high], btype="bandstop", ftype="butter")
                processed = signal.filtfilt(b, a, audio) * gain_linear

            else:
                logger.warning(f"Unknown band type: {band.band_type}")
                processed = audio

        except Exception as e:
            logger.warning(f"EQ band processing failed: {e}")
            processed = audio

        return np.asarray(processed)

    def get_preset(self, preset_name: str) -> list[EQBand]:
        """Get EQ preset bands."""
        presets = {
            "vocal_enhance": [
                EQBand(80, -3.0, 1.0, "low_shelf"),
                EQBand(200, 2.0, 1.5, "peaking"),
                EQBand(2000, 3.0, 2.0, "peaking"),
                EQBand(5000, 2.0, 1.5, "peaking"),
                EQBand(12000, -2.0, 1.0, "high_shelf"),
            ],
            "bass_boost": [
                EQBand(60, 6.0, 1.0, "low_shelf"),
                EQBand(120, 4.0, 1.5, "peaking"),
            ],
            "treble_boost": [
                EQBand(8000, 4.0, 1.5, "peaking"),
                EQBand(12000, 6.0, 1.0, "high_shelf"),
            ],
            "presence": [
                EQBand(2000, 4.0, 2.0, "peaking"),
                EQBand(4000, 3.0, 2.0, "peaking"),
            ],
            "warmth": [
                EQBand(200, 3.0, 1.5, "peaking"),
                EQBand(500, 2.0, 1.5, "peaking"),
                EQBand(8000, -2.0, 1.5, "peaking"),
            ],
            "bright": [
                EQBand(5000, 4.0, 2.0, "peaking"),
                EQBand(10000, 5.0, 1.5, "peaking"),
            ],
            "flat": [],
        }

        return presets.get(preset_name.lower(), [])

    def load_preset(self, preset_name: str):
        """Load an EQ preset."""
        self.clear_bands()
        preset_bands = self.get_preset(preset_name)
        self.bands.extend(preset_bands)

    def get_frequency_response(
        self, frequencies: np.ndarray, sample_rate: int | None = None
    ) -> np.ndarray:
        """
        Calculate frequency response of EQ.

        Args:
            frequencies: Array of frequencies to evaluate (Hz)
            sample_rate: Sample rate

        Returns:
            Array of gain values in dB
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if not HAS_SCIPY:
            return np.zeros_like(frequencies)

        nyquist = sample_rate / 2.0
        response = np.ones_like(frequencies, dtype=float)

        for band in self.bands:
            if not band.enabled:
                continue

            gain_linear = 10.0 ** (band.gain_db / 20.0)
            normalized_freq = band.frequency / nyquist

            # Simplified frequency response calculation
            for i, freq in enumerate(frequencies):
                normalized_f = freq / nyquist
                if normalized_f >= 1.0:
                    continue

                if band.band_type == "peaking":
                    # Peaking filter response
                    q_factor = band.q
                    f_ratio = normalized_f / normalized_freq
                    if f_ratio > 0:
                        magnitude = 1.0 + (gain_linear - 1.0) / (
                            1.0 + q_factor * (f_ratio - 1.0 / f_ratio) ** 2
                        )
                        response[i] *= magnitude

                elif band.band_type == "low_shelf":
                    if normalized_f <= normalized_freq:
                        response[i] *= gain_linear
                    else:
                        # Transition
                        transition = 1.0 - (normalized_f - normalized_freq) / (
                            0.5 - normalized_freq
                        )
                        transition = max(0.0, min(1.0, transition))
                        response[i] *= 1.0 + (gain_linear - 1.0) * transition

                elif band.band_type == "high_shelf":
                    if normalized_f >= normalized_freq:
                        response[i] *= gain_linear
                    else:
                        # Transition
                        transition = normalized_f / normalized_freq
                        transition = max(0.0, min(1.0, transition))
                        response[i] *= 1.0 + (gain_linear - 1.0) * transition

        # Convert to dB
        response_db = 20.0 * np.log10(np.maximum(response, 1e-10))

        return np.asarray(response_db)


def create_parametric_eq(sample_rate: int = 24000, num_bands: int = 10) -> ParametricEQ:
    """
    Factory function to create a Parametric EQ instance.

    Args:
        sample_rate: Default sample rate for processing
        num_bands: Maximum number of bands

    Returns:
        Initialized ParametricEQ instance
    """
    return ParametricEQ(sample_rate=sample_rate, num_bands=num_bands)


def apply_eq(
    audio: np.ndarray,
    bands: list[dict],
    sample_rate: int = 24000,
    **kwargs,
) -> np.ndarray:
    """
    Convenience function to apply EQ to audio.

    Args:
        audio: Input audio array
        bands: List of band dictionaries with:
            - frequency: Center frequency (Hz)
            - gain_db: Gain in dB
            - q: Q factor
            - band_type: Band type
            - enabled: Whether enabled
        sample_rate: Sample rate
        **kwargs: Additional processing options

    Returns:
        Processed audio array
    """
    eq = ParametricEQ(sample_rate=sample_rate)
    for band_dict in bands:
        eq.add_band(
            frequency=band_dict.get("frequency", 1000.0),
            gain_db=band_dict.get("gain_db", 0.0),
            q=band_dict.get("q", 1.0),
            band_type=band_dict.get("band_type", "peaking"),
            enabled=band_dict.get("enabled", True),
        )
    return eq.process(audio, sample_rate, **kwargs)
