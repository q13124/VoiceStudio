"""
Silence Trimmer Plugin for VoiceStudio.

Reference plugin for trimming leading and trailing silence.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


class SilenceTrimmerPlugin:
    """Trims leading and trailing silence from audio."""

    PLUGIN_ID = "com.voicestudio.silence_trimmer"
    PLUGIN_VERSION = "1.0.0"

    def __init__(self) -> None:
        self._config: dict[str, Any] = {
            "threshold_db": -40.0,
            "padding_ms": 50.0,
        }

    async def activate(self) -> bool:
        if not SOUNDFILE_AVAILABLE:
            logger.error("soundfile library not installed")
            return False
        logger.info("SilenceTrimmerPlugin activated")
        return True

    async def deactivate(self) -> None:
        logger.info("SilenceTrimmerPlugin deactivated")

    def configure(self, settings: dict[str, Any]) -> None:
        for key in ("threshold_db", "padding_ms"):
            if key in settings:
                self._config[key] = settings[key]

    def _find_non_silent(self, audio: np.ndarray, sample_rate: int) -> tuple[int, int]:
        """Find start and end indices of non-silent regions."""
        threshold_linear = 10 ** (self._config["threshold_db"] / 20.0)
        padding_samples = int(
            self._config["padding_ms"] / 1000.0 * sample_rate
        )
        if audio.ndim > 1:
            mono = np.abs(audio).max(axis=1)
        else:
            mono = np.abs(audio)
        above = mono > threshold_linear
        indices = np.where(above)[0]
        if len(indices) == 0:
            return 0, len(audio)
        start = max(0, indices[0] - padding_samples)
        end = min(len(audio), indices[-1] + 1 + padding_samples)
        return start, end

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process audio to trim silence.

        Args:
            input_data: Dict with 'audio_path' (str) pointing to input audio file.

        Returns:
            Dict with 'audio_path' (str) pointing to processed output file.
        """
        audio_path = Path(input_data["audio_path"])
        if not audio_path.exists():
            return {"error": f"Input file not found: {audio_path}"}

        audio_data, sample_rate = sf.read(str(audio_path))
        start, end = self._find_non_silent(audio_data, sample_rate)
        trimmed = audio_data[start:end]

        output_path = audio_path.parent / f"{audio_path.stem}_trimmed{audio_path.suffix}"
        sf.write(str(output_path), trimmed, sample_rate)

        return {
            "audio_path": str(output_path),
            "sample_rate": sample_rate,
            "duration_seconds": len(trimmed) / sample_rate,
            "trimmed_samples": (start, end),
            "original_duration_seconds": len(audio_data) / sample_rate,
        }

    def get_info(self) -> dict[str, Any]:
        return {
            "id": self.PLUGIN_ID,
            "version": self.PLUGIN_VERSION,
            "config": self._config,
        }
