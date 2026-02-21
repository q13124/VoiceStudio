"""
Pitch Shifter Plugin for VoiceStudio.

Reference plugin demonstrating pitch shifting using librosa.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False


class PitchShifterPlugin:
    """Shifts audio pitch by semitones without changing duration."""

    PLUGIN_ID = "com.voicestudio.pitch_shifter"
    PLUGIN_VERSION = "1.0.0"

    def __init__(self) -> None:
        self._config: dict[str, Any] = {
            "semitones": 0.0,
            "preserve_formants": False,
        }

    async def activate(self) -> bool:
        if not LIBROSA_AVAILABLE:
            logger.error("librosa library not installed")
            return False
        if not SOUNDFILE_AVAILABLE:
            logger.error("soundfile library not installed")
            return False
        logger.info("PitchShifterPlugin activated")
        return True

    async def deactivate(self) -> None:
        logger.info("PitchShifterPlugin deactivated")

    def configure(self, settings: dict[str, Any]) -> None:
        for key in ("semitones", "preserve_formants"):
            if key in settings:
                self._config[key] = settings[key]

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Process audio to shift pitch.

        Args:
            input_data: Dict with 'audio_path' (str) pointing to input audio file.

        Returns:
            Dict with 'audio_path' (str) pointing to processed output file.
        """
        audio_path = Path(input_data["audio_path"])
        if not audio_path.exists():
            return {"error": f"Input file not found: {audio_path}"}

        audio_data, sample_rate = sf.read(str(audio_path))
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)

        semitones = float(self._config.get("semitones", 0))
        if abs(semitones) < 0.01:
            return {
                "audio_path": str(audio_path),
                "sample_rate": sample_rate,
                "semitones": 0,
                "message": "No pitch shift applied",
            }

        shifted = librosa.effects.pitch_shift(
            audio_data,
            sr=sample_rate,
            n_steps=semitones,
            res_type="soxr_hq",
        )

        output_path = audio_path.parent / f"{audio_path.stem}_pitch{audio_path.suffix}"
        sf.write(str(output_path), shifted, sample_rate)

        return {
            "audio_path": str(output_path),
            "sample_rate": sample_rate,
            "semitones": semitones,
            "duration_seconds": len(shifted) / sample_rate,
        }

    def get_info(self) -> dict[str, Any]:
        return {
            "id": self.PLUGIN_ID,
            "version": self.PLUGIN_VERSION,
            "config": self._config,
            "librosa_available": LIBROSA_AVAILABLE,
        }
