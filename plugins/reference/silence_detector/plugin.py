"""
Silence Detector Plugin for VoiceStudio.

Reference plugin demonstrating audio analysis capabilities.
Uses librosa for silence detection with configurable thresholds.
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


class SilenceDetectorPlugin:
    """Detects and reports silence regions in audio files."""

    PLUGIN_ID = "com.voicestudio.silence_detector"
    PLUGIN_VERSION = "1.0.0"

    def __init__(self) -> None:
        self._config: dict[str, Any] = {
            "silence_threshold_db": -40,
            "min_silence_duration": 0.3,
            "frame_length": 2048,
            "hop_length": 512,
        }

    async def activate(self) -> bool:
        if not LIBROSA_AVAILABLE:
            logger.error("librosa library not installed")
            return False
        if not SOUNDFILE_AVAILABLE:
            logger.error("soundfile library not installed")
            return False
        logger.info("SilenceDetectorPlugin activated")
        return True

    async def deactivate(self) -> None:
        logger.info("SilenceDetectorPlugin deactivated")

    def configure(self, settings: dict[str, Any]) -> None:
        for key in self._config:
            if key in settings:
                self._config[key] = settings[key]

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze audio for silence regions.

        Args:
            input_data: Dict with 'audio_path' (str).

        Returns:
            Dict with silence analysis results.
        """
        audio_path = Path(input_data["audio_path"])
        if not audio_path.exists():
            return {"error": f"Input file not found: {audio_path}"}

        audio_data, sample_rate = sf.read(str(audio_path))
        if audio_data.ndim > 1:
            audio_data = np.mean(audio_data, axis=1)

        total_duration = len(audio_data) / sample_rate

        intervals = librosa.effects.split(
            audio_data,
            top_db=abs(self._config["silence_threshold_db"]),
            frame_length=self._config["frame_length"],
            hop_length=self._config["hop_length"],
        )

        silence_regions = []
        prev_end = 0
        for start_sample, end_sample in intervals:
            gap_start = prev_end / sample_rate
            gap_end = start_sample / sample_rate
            gap_duration = gap_end - gap_start
            if gap_duration >= self._config["min_silence_duration"]:
                silence_regions.append({
                    "start_time": round(gap_start, 3),
                    "end_time": round(gap_end, 3),
                    "duration": round(gap_duration, 3),
                })
            prev_end = end_sample

        trailing_gap = total_duration - (prev_end / sample_rate)
        if trailing_gap >= self._config["min_silence_duration"]:
            silence_regions.append({
                "start_time": round(prev_end / sample_rate, 3),
                "end_time": round(total_duration, 3),
                "duration": round(trailing_gap, 3),
            })

        total_silence = sum(r["duration"] for r in silence_regions)

        return {
            "audio_path": str(audio_path),
            "total_duration": round(total_duration, 3),
            "silence_regions": silence_regions,
            "silence_count": len(silence_regions),
            "total_silence_duration": round(total_silence, 3),
            "silence_percentage": round((total_silence / total_duration) * 100, 1) if total_duration > 0 else 0,
            "speech_duration": round(total_duration - total_silence, 3),
        }

    def get_info(self) -> dict[str, Any]:
        return {
            "id": self.PLUGIN_ID,
            "version": self.PLUGIN_VERSION,
            "config": self._config,
            "librosa_available": LIBROSA_AVAILABLE,
        }
