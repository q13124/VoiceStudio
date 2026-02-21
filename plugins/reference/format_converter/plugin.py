"""
Audio Format Converter Plugin for VoiceStudio.

Reference plugin demonstrating format conversion via FFmpeg.
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {"wav", "mp3", "flac", "ogg", "aac"}

CODEC_MAP = {
    "wav": "pcm_s16le",
    "mp3": "libmp3lame",
    "flac": "flac",
    "ogg": "libvorbis",
    "aac": "aac",
}


def _find_ffmpeg() -> str | None:
    """Locate FFmpeg binary."""
    import os
    custom = os.environ.get("VOICESTUDIO_FFMPEG_PATH")
    if custom and Path(custom).exists():
        return custom
    return shutil.which("ffmpeg")


class FormatConverterPlugin:
    """Converts audio between formats using FFmpeg."""

    PLUGIN_ID = "com.voicestudio.format_converter"
    PLUGIN_VERSION = "1.0.0"

    def __init__(self) -> None:
        self._config: dict[str, Any] = {
            "default_format": "wav",
            "bitrate": "192k",
            "sample_rate": 44100,
            "channels": 1,
        }
        self._ffmpeg_path: str | None = None

    async def activate(self) -> bool:
        self._ffmpeg_path = _find_ffmpeg()
        if not self._ffmpeg_path:
            logger.error("FFmpeg not found. Install FFmpeg or set VOICESTUDIO_FFMPEG_PATH.")
            return False
        logger.info("FormatConverterPlugin activated (ffmpeg=%s)", self._ffmpeg_path)
        return True

    async def deactivate(self) -> None:
        logger.info("FormatConverterPlugin deactivated")

    def configure(self, settings: dict[str, Any]) -> None:
        for key in ("default_format", "bitrate", "sample_rate", "channels"):
            if key in settings:
                self._config[key] = settings[key]

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Convert audio to the target format.

        Args:
            input_data: Dict with 'audio_path' and optional 'target_format'.

        Returns:
            Dict with 'audio_path' to converted file.
        """
        audio_path = Path(input_data["audio_path"])
        if not audio_path.exists():
            return {"error": f"Input file not found: {audio_path}"}

        target_fmt = input_data.get("target_format", self._config["default_format"])
        if target_fmt not in SUPPORTED_FORMATS:
            return {"error": f"Unsupported format: {target_fmt}. Use: {SUPPORTED_FORMATS}"}

        output_path = audio_path.parent / f"{audio_path.stem}.{target_fmt}"
        codec = CODEC_MAP[target_fmt]

        cmd = [
            self._ffmpeg_path, "-y",
            "-i", str(audio_path),
            "-acodec", codec,
            "-ar", str(self._config["sample_rate"]),
            "-ac", str(self._config["channels"]),
        ]
        if target_fmt in ("mp3", "ogg", "aac"):
            cmd.extend(["-b:a", self._config["bitrate"]])
        cmd.append(str(output_path))

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120,
            )
            if result.returncode != 0:
                return {"error": f"FFmpeg failed: {result.stderr[:500]}"}
        except subprocess.TimeoutExpired:
            return {"error": "FFmpeg timed out after 120 seconds"}

        return {
            "audio_path": str(output_path),
            "format": target_fmt,
            "codec": codec,
            "sample_rate": self._config["sample_rate"],
            "channels": self._config["channels"],
        }

    def get_info(self) -> dict[str, Any]:
        return {
            "id": self.PLUGIN_ID,
            "version": self.PLUGIN_VERSION,
            "config": self._config,
            "ffmpeg_available": self._ffmpeg_path is not None,
            "supported_formats": list(SUPPORTED_FORMATS),
        }
