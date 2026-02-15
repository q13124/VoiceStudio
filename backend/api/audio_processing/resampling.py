"""
High-Quality Resampling Integration
Integrates soxr library for high-quality audio resampling.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)

# Try importing soxr
HAS_SOXR = False
try:
    import soxr

    HAS_SOXR = True
except ImportError:
    logger.warning("soxr not available. Using librosa for resampling.")


class HighQualityResampler:
    """
    High-quality audio resampling using soxr library.
    """

    def __init__(self):
        """Initialize resampler."""
        self.soxr_available = HAS_SOXR

    def resample(
        self,
        audio: np.ndarray,
        orig_sr: int,
        target_sr: int,
        quality: str = "HQ",
        num_channels: int | None = None,
    ) -> np.ndarray:
        """
        Resample audio using soxr (high quality) or librosa fallback.

        Args:
            audio: Audio signal
            orig_sr: Original sample rate
            target_sr: Target sample rate
            quality: Resampling quality ('VHQ', 'HQ', 'MQ', 'LQ', 'QQ')
            num_channels: Number of channels (auto-detect if None)

        Returns:
            Resampled audio signal
        """
        if orig_sr == target_sr:
            return audio

        if self.soxr_available:
            try:
                # Determine number of channels
                if num_channels is None:
                    num_channels = 1 if len(audio.shape) == 1 else audio.shape[1]

                # Resample using soxr
                resampled = soxr.resample(
                    audio,
                    orig_sr,
                    target_sr,
                    quality=quality,
                    num_channels=num_channels,
                )
                return resampled
            except Exception as e:
                logger.warning(
                    f"soxr resampling failed, falling back to librosa: {e}"
                )
                # Fall through to librosa fallback

        # Fallback to librosa
        try:
            import librosa

            resampled = librosa.resample(
                audio, orig_sr=orig_sr, target_sr=target_sr
            )
            return resampled
        except ImportError:
            raise ImportError(
                "Neither soxr nor librosa available for resampling"
            )
        except Exception as e:
            logger.error(f"Error in librosa resampling: {e}", exc_info=True)
            raise

    def get_supported_qualities(self) -> list:
        """
        Get list of supported resampling qualities.

        Returns:
            List of quality strings
        """
        if self.soxr_available:
            return ["VHQ", "HQ", "MQ", "LQ", "QQ"]
        else:
            return ["standard"]  # librosa default

