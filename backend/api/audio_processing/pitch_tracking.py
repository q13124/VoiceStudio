"""
Pitch Tracking Integration
Integrates crepe and pyin libraries for pitch estimation.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

# Try importing crepe
HAS_CREPE = False
try:
    import crepe

    HAS_CREPE = True
except ImportError:
    logger.warning("crepe not available. Pitch tracking will be limited.")

# Try importing pyin (via librosa)
HAS_PYIN = False
try:
    import librosa

    HAS_PYIN = True
except ImportError:
    logger.warning("librosa not available. PYIN pitch tracking unavailable.")


class PitchTracker:
    """
    Pitch tracking using crepe and pyin libraries.
    """

    def __init__(self):
        """Initialize pitch tracker."""
        self.crepe_available = HAS_CREPE
        self.pyin_available = HAS_PYIN

    def track_pitch_crepe(
        self,
        audio: np.ndarray,
        sample_rate: int,
        model_capacity: str = "full",
        viterbi: bool = True,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Track pitch using crepe library.

        Args:
            audio: Audio signal (mono)
            sample_rate: Sample rate in Hz
            model_capacity: Model capacity ('tiny', 'small', 'medium', 'large', 'full')
            viterbi: Use Viterbi smoothing

        Returns:
            Tuple of (time, frequency) arrays
        """
        if not self.crepe_available:
            raise ImportError("crepe library not available")

        try:
            time, frequency, _confidence, _activation = crepe.predict(
                audio,
                sample_rate,
                model_capacity=model_capacity,
                viterbi=viterbi,
                step_size=10,  # 10ms steps
            )
            return time, frequency
        except Exception as e:
            logger.error(f"Error in crepe pitch tracking: {e}", exc_info=True)
            raise

    def track_pitch_pyin(
        self,
        audio: np.ndarray,
        sample_rate: int,
        fmin: float = 80.0,
        fmax: float = 400.0,
        frame_length: int = 2048,
        hop_length: int | None = None,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Track pitch using librosa's PYIN algorithm.

        Args:
            audio: Audio signal (mono)
            sample_rate: Sample rate in Hz
            fmin: Minimum frequency in Hz
            fmax: Maximum frequency in Hz
            frame_length: Frame length for analysis
            hop_length: Hop length (default: frame_length // 4)

        Returns:
            Tuple of (f0, voiced_flag, voiced_prob) arrays
        """
        if not self.pyin_available:
            raise ImportError("librosa not available for PYIN")

        try:
            if hop_length is None:
                hop_length = frame_length // 4

            f0, voiced_flag, voiced_prob = librosa.pyin(
                audio,
                fmin=fmin,
                fmax=fmax,
                frame_length=frame_length,
                hop_length=hop_length,
                sr=sample_rate,
            )
            return f0, voiced_flag, voiced_prob
        except Exception as e:
            logger.error(f"Error in PYIN pitch tracking: {e}", exc_info=True)
            raise

    def get_pitch_statistics(
        self,
        frequencies: np.ndarray,
        times: np.ndarray | None = None,
    ) -> dict:
        """
        Calculate pitch statistics from frequency array.

        Args:
            frequencies: Array of pitch frequencies (Hz)
            times: Optional time array for temporal analysis

        Returns:
            Dictionary of pitch statistics
        """
        # Filter out invalid frequencies (NaN, inf, zero)
        valid_freqs = frequencies[np.isfinite(frequencies) & (frequencies > 0)]

        if len(valid_freqs) == 0:
            return {
                "mean": 0.0,
                "std": 0.0,
                "min": 0.0,
                "max": 0.0,
                "median": 0.0,
                "stability": 0.0,
            }

        stats = {
            "mean": float(np.mean(valid_freqs)),
            "std": float(np.std(valid_freqs)),
            "min": float(np.min(valid_freqs)),
            "max": float(np.max(valid_freqs)),
            "median": float(np.median(valid_freqs)),
            "stability": float(
                1.0 / (1.0 + np.std(valid_freqs) / np.mean(valid_freqs))
            ),
        }

        # Add temporal statistics if times provided
        if times is not None and len(times) == len(frequencies):
            valid_times = times[np.isfinite(frequencies) & (frequencies > 0)]
            if len(valid_times) > 1:
                stats["duration"] = float(valid_times[-1] - valid_times[0])
                stats["pitch_range"] = float(stats["max"] - stats["min"])

        return stats
