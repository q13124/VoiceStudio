"""
Phase 6: Export System
Task 6.6: Audio export with multiple formats.
"""

from __future__ import annotations

import asyncio
import logging
import struct
import wave
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class AudioFormat(Enum):
    """Supported audio formats."""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    AAC = "aac"
    M4A = "m4a"
    OPUS = "opus"


class SampleRate(Enum):
    """Common sample rates."""

    SR_8000 = 8000
    SR_16000 = 16000
    SR_22050 = 22050
    SR_44100 = 44100
    SR_48000 = 48000
    SR_96000 = 96000


class BitDepth(Enum):
    """Common bit depths."""

    BIT_8 = 8
    BIT_16 = 16
    BIT_24 = 24
    BIT_32 = 32


@dataclass
class ExportSettings:
    """Audio export settings."""

    format: AudioFormat = AudioFormat.WAV
    sample_rate: int = 44100
    bit_depth: int = 16
    channels: int = 2
    bitrate: int | None = None  # For lossy formats (kbps)
    normalize: bool = False
    normalize_level: float = -3.0  # dB
    trim_silence: bool = False
    fade_in: float = 0.0  # seconds
    fade_out: float = 0.0  # seconds
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class ExportResult:
    """Result of an export operation."""

    success: bool
    output_path: Path | None = None
    file_size: int = 0
    duration: float = 0.0
    format: AudioFormat | None = None
    error: str | None = None


class AudioExporter:
    """Exporter for audio files."""

    def __init__(self):
        self._ffmpeg_path: Path | None = None

    async def export(
        self, input_path: Path, output_path: Path, settings: ExportSettings
    ) -> ExportResult:
        """Export audio file with specified settings."""
        try:
            if not input_path.exists():
                return ExportResult(success=False, error=f"Input file not found: {input_path}")

            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Process based on format
            if settings.format == AudioFormat.WAV:
                return await self._export_wav(input_path, output_path, settings)
            else:
                return await self._export_with_ffmpeg(input_path, output_path, settings)

        except Exception as e:
            logger.error(f"Export error: {e}")
            return ExportResult(success=False, error=str(e))

    async def _export_wav(
        self, input_path: Path, output_path: Path, settings: ExportSettings
    ) -> ExportResult:
        """Export to WAV format."""
        try:
            # Read input
            with wave.open(str(input_path), "rb") as wav_in:
                n_channels = wav_in.getnchannels()
                sample_width = wav_in.getsampwidth()
                frame_rate = wav_in.getframerate()
                n_frames = wav_in.getnframes()
                audio_data = wav_in.readframes(n_frames)

            # Apply processing if needed
            if settings.normalize:
                audio_data = self._normalize_audio(
                    audio_data, sample_width, settings.normalize_level
                )

            # Write output
            output_path = output_path.with_suffix(".wav")

            with wave.open(str(output_path), "wb") as wav_out:
                wav_out.setnchannels(settings.channels or n_channels)
                wav_out.setsampwidth(settings.bit_depth // 8)
                wav_out.setframerate(settings.sample_rate or frame_rate)
                wav_out.writeframes(audio_data)

            duration = n_frames / frame_rate

            return ExportResult(
                success=True,
                output_path=output_path,
                file_size=output_path.stat().st_size,
                duration=duration,
                format=AudioFormat.WAV,
            )

        except Exception as e:
            return ExportResult(success=False, error=str(e))

    async def _export_with_ffmpeg(
        self, input_path: Path, output_path: Path, settings: ExportSettings
    ) -> ExportResult:
        """Export using FFmpeg."""
        try:
            # Build FFmpeg command
            cmd = ["ffmpeg", "-y", "-i", str(input_path)]

            # Audio settings
            cmd.extend(["-ar", str(settings.sample_rate)])
            cmd.extend(["-ac", str(settings.channels)])

            # Format-specific settings
            if settings.format == AudioFormat.MP3:
                output_path = output_path.with_suffix(".mp3")
                cmd.extend(["-c:a", "libmp3lame"])
                if settings.bitrate:
                    cmd.extend(["-b:a", f"{settings.bitrate}k"])

            elif settings.format == AudioFormat.FLAC:
                output_path = output_path.with_suffix(".flac")
                cmd.extend(["-c:a", "flac"])

            elif settings.format == AudioFormat.OGG:
                output_path = output_path.with_suffix(".ogg")
                cmd.extend(["-c:a", "libvorbis"])
                if settings.bitrate:
                    cmd.extend(["-b:a", f"{settings.bitrate}k"])

            elif settings.format == AudioFormat.AAC:
                output_path = output_path.with_suffix(".aac")
                cmd.extend(["-c:a", "aac"])
                if settings.bitrate:
                    cmd.extend(["-b:a", f"{settings.bitrate}k"])

            elif settings.format == AudioFormat.OPUS:
                output_path = output_path.with_suffix(".opus")
                cmd.extend(["-c:a", "libopus"])
                if settings.bitrate:
                    cmd.extend(["-b:a", f"{settings.bitrate}k"])

            # Filters
            filters = []

            if settings.normalize:
                filters.append(f"loudnorm=I={settings.normalize_level}")

            if settings.fade_in > 0:
                filters.append(f"afade=t=in:st=0:d={settings.fade_in}")

            if settings.fade_out > 0:
                filters.append(f"afade=t=out:st=0:d={settings.fade_out}")

            if filters:
                cmd.extend(["-af", ",".join(filters)])

            # Metadata
            for key, value in settings.metadata.items():
                cmd.extend(["-metadata", f"{key}={value}"])

            cmd.append(str(output_path))

            # Execute
            process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            _stdout, stderr = await process.communicate()

            if process.returncode != 0:
                return ExportResult(
                    success=False, error=stderr.decode() if stderr else "FFmpeg error"
                )

            return ExportResult(
                success=True,
                output_path=output_path,
                file_size=output_path.stat().st_size if output_path.exists() else 0,
                format=settings.format,
            )

        except FileNotFoundError:
            return ExportResult(success=False, error="FFmpeg not found. Please install FFmpeg.")
        except Exception as e:
            return ExportResult(success=False, error=str(e))

    def _normalize_audio(self, audio_data: bytes, sample_width: int, target_db: float) -> bytes:
        """Normalize audio to target level."""
        # Convert to samples
        if sample_width == 2:
            fmt = f"<{len(audio_data) // 2}h"
            samples = list(struct.unpack(fmt, audio_data))
        else:
            return audio_data

        # Find peak
        peak = max(abs(min(samples)), abs(max(samples)))
        if peak == 0:
            return audio_data

        # Calculate gain
        target_peak = int(32767 * (10 ** (target_db / 20)))
        gain = target_peak / peak

        # Apply gain
        normalized = [int(s * gain) for s in samples]

        # Clip
        normalized = [max(-32768, min(32767, s)) for s in normalized]

        # Pack back
        return struct.pack(fmt, *normalized)

    def get_supported_formats(self) -> list[AudioFormat]:
        """Get list of supported export formats."""
        return list(AudioFormat)

    def get_format_info(self, format: AudioFormat) -> dict[str, Any]:
        """Get information about a format."""
        info = {
            AudioFormat.WAV: {
                "name": "WAV",
                "extension": ".wav",
                "lossy": False,
                "supports_metadata": False,
            },
            AudioFormat.MP3: {
                "name": "MP3",
                "extension": ".mp3",
                "lossy": True,
                "supports_metadata": True,
                "default_bitrate": 192,
            },
            AudioFormat.FLAC: {
                "name": "FLAC",
                "extension": ".flac",
                "lossy": False,
                "supports_metadata": True,
            },
            AudioFormat.OGG: {
                "name": "OGG Vorbis",
                "extension": ".ogg",
                "lossy": True,
                "supports_metadata": True,
                "default_bitrate": 192,
            },
            AudioFormat.AAC: {
                "name": "AAC",
                "extension": ".aac",
                "lossy": True,
                "supports_metadata": True,
                "default_bitrate": 192,
            },
            AudioFormat.OPUS: {
                "name": "Opus",
                "extension": ".opus",
                "lossy": True,
                "supports_metadata": True,
                "default_bitrate": 128,
            },
        }

        return info.get(format, {})
