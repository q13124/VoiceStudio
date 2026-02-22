"""
LUFS Meter Module for VoiceStudio
Real-time loudness measurement and monitoring using LUFS (Loudness Units relative to Full Scale)

Compatible with:
- Python 3.10+
- numpy>=1.26.0
- pyloudnorm>=0.1.1
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

try:
    import pyloudnorm as pyln

    HAS_PYLOUDNORM = True
except ImportError:
    HAS_PYLOUDNORM = False
    logger.warning("pyloudnorm not installed. Install with: pip install pyloudnorm")


class LUFSMeter:
    """
    LUFS Meter for real-time loudness measurement and monitoring.

    Supports:
    - Integrated LUFS measurement
    - Momentary LUFS (400ms blocks)
    - Short-term LUFS (3s blocks)
    - Peak LUFS
    - Real-time monitoring
    - Time-series LUFS data
    """

    def __init__(self, sample_rate: int = 24000, block_size: float = 0.400):
        """
        Initialize LUFS Meter.

        Args:
            sample_rate: Sample rate for processing
            block_size: Block size in seconds for LUFS measurement (default 0.400s)
        """
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.meter = None

        if HAS_PYLOUDNORM:
            try:
                self.meter = pyln.Meter(sample_rate, block_size=block_size)
            except Exception as e:
                logger.warning(f"Failed to initialize pyloudnorm meter: {e}")

    def measure_integrated_lufs(self, audio: np.ndarray, sample_rate: int | None = None) -> float:
        """
        Measure integrated LUFS (overall loudness).

        Args:
            audio: Input audio array (mono or stereo)
            sample_rate: Sample rate (uses instance default if None)

        Returns:
            Integrated LUFS value in dB
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if not HAS_PYLOUDNORM:
            return self._estimate_lufs_from_rms(audio)

        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        try:
            # Create meter if needed or sample rate changed
            if self.meter is None or sample_rate != self.sample_rate:
                self.meter = pyln.Meter(sample_rate, block_size=self.block_size)
                self.sample_rate = sample_rate

            loudness = self.meter.integrated_loudness(audio)

            if np.isnan(loudness) or np.isinf(loudness):
                return self._estimate_lufs_from_rms(audio)

            return float(loudness)
        except Exception as e:
            logger.warning(f"Integrated LUFS measurement failed: {e}")
            return self._estimate_lufs_from_rms(audio)

    def measure_momentary_lufs(self, audio: np.ndarray, sample_rate: int | None = None) -> float:
        """
        Measure momentary LUFS (400ms blocks).

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)

        Returns:
            Momentary LUFS value in dB
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if not HAS_PYLOUDNORM:
            return self._estimate_lufs_from_rms(audio)

        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        try:
            # Create meter if needed
            if self.meter is None or sample_rate != self.sample_rate:
                self.meter = pyln.Meter(sample_rate, block_size=0.400)
                self.sample_rate = sample_rate

            # Use last 400ms block
            block_samples = int(sample_rate * 0.400)
            if len(audio) < block_samples:
                return self.measure_integrated_lufs(audio, sample_rate)

            block_audio = audio[-block_samples:]
            loudness = self.meter.integrated_loudness(block_audio)

            if np.isnan(loudness) or np.isinf(loudness):
                return self._estimate_lufs_from_rms(block_audio)

            return float(loudness)
        except Exception as e:
            logger.warning(f"Momentary LUFS measurement failed: {e}")
            return self._estimate_lufs_from_rms(audio)

    def measure_short_term_lufs(self, audio: np.ndarray, sample_rate: int | None = None) -> float:
        """
        Measure short-term LUFS (3s blocks).

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)

        Returns:
            Short-term LUFS value in dB
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if not HAS_PYLOUDNORM:
            return self._estimate_lufs_from_rms(audio)

        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        try:
            # Create meter with 3s block size
            meter_3s = pyln.Meter(sample_rate, block_size=3.0)

            # Use last 3s block
            block_samples = int(sample_rate * 3.0)
            if len(audio) < block_samples:
                return self.measure_integrated_lufs(audio, sample_rate)

            block_audio = audio[-block_samples:]
            loudness = meter_3s.integrated_loudness(block_audio)

            if np.isnan(loudness) or np.isinf(loudness):
                return self._estimate_lufs_from_rms(block_audio)

            return float(loudness)
        except Exception as e:
            logger.warning(f"Short-term LUFS measurement failed: {e}")
            return self._estimate_lufs_from_rms(audio)

    def measure_peak_lufs(self, audio: np.ndarray, sample_rate: int | None = None) -> float:
        """
        Measure peak LUFS (true peak).

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)

        Returns:
            Peak LUFS value in dB
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if not HAS_PYLOUDNORM:
            # Estimate from peak
            peak = np.max(np.abs(audio))
            if peak > 0:
                return float(20.0 * np.log10(peak))
            return -70.0

        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        try:
            # Create meter if needed
            if self.meter is None or sample_rate != self.sample_rate:
                self.meter = pyln.Meter(sample_rate, block_size=self.block_size)
                self.sample_rate = sample_rate

            peak = self.meter.peak(audio)

            if np.isnan(peak) or np.isinf(peak):
                peak_val = np.max(np.abs(audio))
                if peak_val > 0:
                    return float(20.0 * np.log10(peak_val))
                return -70.0

            return float(peak)
        except Exception as e:
            logger.warning(f"Peak LUFS measurement failed: {e}")
            peak_val = np.max(np.abs(audio))
            if peak_val > 0:
                return float(20.0 * np.log10(peak_val))
            return -70.0

    def measure_time_series(
        self,
        audio: np.ndarray,
        sample_rate: int | None = None,
        window_size: float = 0.400,
        hop_size: float | None = None,
    ) -> tuple[list[float], list[float]]:
        """
        Measure LUFS over time (time-series data).

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)
            window_size: Window size in seconds for each measurement
            hop_size: Hop size in seconds (default: window_size / 4 for 75% overlap)

        Returns:
            Tuple of (times, lufs_values) lists
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        if hop_size is None:
            hop_size = window_size / 4.0  # 75% overlap

        times = []
        lufs_values = []

        # Convert to mono if stereo
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)

        window_samples = int(sample_rate * window_size)
        hop_samples = int(sample_rate * hop_size)

        if window_samples <= 0 or hop_samples <= 0:
            return times, lufs_values

        if HAS_PYLOUDNORM:
            try:
                meter = pyln.Meter(sample_rate, block_size=window_size)

                for i in range(0, len(audio) - window_samples, hop_samples):
                    block_audio = audio[i : i + window_samples]

                    try:
                        loudness = meter.integrated_loudness(block_audio)
                        if np.isnan(loudness) or np.isinf(loudness):
                            loudness = self._estimate_lufs_from_rms(block_audio)
                    except Exception:
                        loudness = self._estimate_lufs_from_rms(block_audio)

                    time_pos = i / sample_rate
                    times.append(time_pos)
                    lufs_values.append(float(loudness))
            except Exception as e:
                logger.warning(f"Time-series LUFS measurement failed: {e}")
                # Fallback to RMS estimation
                for i in range(0, len(audio) - window_samples, hop_samples):
                    block_audio = audio[i : i + window_samples]
                    loudness = self._estimate_lufs_from_rms(block_audio)
                    time_pos = i / sample_rate
                    times.append(time_pos)
                    lufs_values.append(float(loudness))
        else:
            # Fallback: estimate from RMS
            for i in range(0, len(audio) - window_samples, hop_samples):
                block_audio = audio[i : i + window_samples]
                loudness = self._estimate_lufs_from_rms(block_audio)
                time_pos = i / sample_rate
                times.append(time_pos)
                lufs_values.append(float(loudness))

        return times, lufs_values

    def measure_all(self, audio: np.ndarray, sample_rate: int | None = None) -> dict[str, float]:
        """
        Measure all LUFS metrics at once.

        Args:
            audio: Input audio array
            sample_rate: Sample rate (uses instance default if None)

        Returns:
            Dictionary with all LUFS measurements:
                - integrated: Integrated LUFS
                - momentary: Momentary LUFS
                - short_term: Short-term LUFS
                - peak: Peak LUFS
        """
        if sample_rate is None:
            sample_rate = self.sample_rate

        return {
            "integrated": self.measure_integrated_lufs(audio, sample_rate),
            "momentary": self.measure_momentary_lufs(audio, sample_rate),
            "short_term": self.measure_short_term_lufs(audio, sample_rate),
            "peak": self.measure_peak_lufs(audio, sample_rate),
        }

    def _estimate_lufs_from_rms(self, audio: np.ndarray) -> float:
        """Estimate LUFS from RMS (fallback when pyloudnorm unavailable)."""
        if audio.size == 0:
            return -70.0

        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            # Rough approximation: RMS to LUFS
            # This is not accurate but provides a reasonable estimate
            lufs = 20.0 * np.log10(rms)
            # Adjust for typical voice range
            lufs = lufs - 10.0  # Rough calibration
            return float(max(-70.0, min(0.0, lufs)))

        return -70.0


def create_lufs_meter(sample_rate: int = 24000, block_size: float = 0.400) -> LUFSMeter:
    """
    Factory function to create a LUFS Meter instance.

    Args:
        sample_rate: Sample rate for processing
        block_size: Block size in seconds for LUFS measurement

    Returns:
        Initialized LUFSMeter instance
    """
    return LUFSMeter(sample_rate=sample_rate, block_size=block_size)


def measure_lufs(
    audio: np.ndarray,
    sample_rate: int = 24000,
    metric: str = "integrated",
    **kwargs,
) -> float:
    """
    Convenience function to measure LUFS.

    Args:
        audio: Input audio array
        sample_rate: Sample rate
        metric: Metric to measure ('integrated', 'momentary', 'short_term', 'peak')
        **kwargs: Additional options

    Returns:
        LUFS value in dB
    """
    meter = LUFSMeter(sample_rate=sample_rate)

    if metric == "integrated":
        return meter.measure_integrated_lufs(audio, sample_rate)
    elif metric == "momentary":
        return meter.measure_momentary_lufs(audio, sample_rate)
    elif metric == "short_term":
        return meter.measure_short_term_lufs(audio, sample_rate)
    elif metric == "peak":
        return meter.measure_peak_lufs(audio, sample_rate)
    else:
        logger.warning(f"Unknown metric: {metric}, using integrated")
        return meter.measure_integrated_lufs(audio, sample_rate)
