"""
Audio Conversion Service

Provides audio format conversion using FFmpeg with centralized format handling.
Uses path_config.get_ffmpeg_path() for FFmpeg discovery and the audio format
catalog for codec/format mappings.

Features:
- Convert any supported format to WAV (canonical format for internal processing)
- Convert WAV to any supported export format
- Configurable sample rate, channels, bit depth, and bitrate
- Async subprocess execution with proper error handling
- Detailed error reporting including FFmpeg stderr
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from .formats import (
    STANDARD_AUDIO_FORMATS,
    AudioFormat,
    get_format_by_extension,
)

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    """Result of an audio conversion operation."""

    success: bool
    output_path: Path | None = None
    input_format: AudioFormat | None = None
    output_format: AudioFormat | None = None
    duration_seconds: float | None = None
    file_size_bytes: int = 0
    error: str | None = None
    ffmpeg_stderr: str | None = None


@dataclass
class ConversionSettings:
    """Settings for audio conversion."""

    # Target format
    format: AudioFormat = AudioFormat.WAV

    # Audio parameters
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: int = 16  # For PCM formats (WAV, AIFF)
    bitrate_kbps: int | None = None  # For lossy formats

    # Processing options
    normalize: bool = False
    normalize_lufs: float = -14.0  # Target LUFS for loudnorm

    # Metadata (for formats that support it)
    metadata: dict | None = None


class AudioConversionService:
    """
    Service for converting audio files between formats.

    Uses FFmpeg for all conversions with path discovery via path_config.
    Thread-safe for use in async contexts.

    Example:
        service = AudioConversionService()
        result = await service.convert_to_wav(
            input_path=Path("audio.mp3"),
            output_path=Path("audio.wav"),
        )
        if result.success:
            print(f"Converted to {result.output_path}")
    """

    def __init__(self, ffmpeg_path: Path | None = None):
        """
        Initialize the conversion service.

        Args:
            ffmpeg_path: Explicit FFmpeg path. If None, uses path_config discovery.
        """
        self._ffmpeg_path = ffmpeg_path
        self._ffmpeg_resolved: Path | None = None

    def _get_ffmpeg(self) -> Path:
        """
        Get the FFmpeg executable path.

        Returns:
            Path to FFmpeg executable

        Raises:
            RuntimeError: If FFmpeg not found
        """
        if self._ffmpeg_resolved is not None:
            return self._ffmpeg_resolved

        if self._ffmpeg_path is not None:
            self._ffmpeg_resolved = self._ffmpeg_path
            return self._ffmpeg_resolved

        # Use path_config for discovery
        try:
            from backend.config.path_config import get_ffmpeg_path

            self._ffmpeg_resolved = get_ffmpeg_path()
            return self._ffmpeg_resolved
        except ImportError:
            logger.warning("path_config not available, falling back to system PATH")
        except Exception as e:
            logger.warning(f"FFmpeg discovery failed: {e}, falling back to system PATH")

        # Fallback to system PATH
        import shutil

        which = shutil.which("ffmpeg")
        if which:
            self._ffmpeg_resolved = Path(which)
            return self._ffmpeg_resolved

        raise RuntimeError("FFmpeg not found. Install FFmpeg or set VOICESTUDIO_FFMPEG_PATH.")

    async def convert_to_wav(
        self,
        input_path: Path,
        output_path: Path | None = None,
        sample_rate: int = 44100,
        channels: int = 2,
        bit_depth: int = 16,
    ) -> ConversionResult:
        """
        Convert any supported audio file to WAV format.

        This is the primary method for normalizing uploads to the canonical
        WAV format used internally by VoiceStudio.

        Args:
            input_path: Path to input audio file
            output_path: Path for output WAV. If None, uses input_path with .wav extension
            sample_rate: Output sample rate in Hz (default: 44100)
            channels: Number of output channels (default: 2 for stereo)
            bit_depth: Bit depth for PCM (default: 16)

        Returns:
            ConversionResult with success status and output path
        """
        if output_path is None:
            output_path = input_path.with_suffix(".wav")

        settings = ConversionSettings(
            format=AudioFormat.WAV,
            sample_rate=sample_rate,
            channels=channels,
            bit_depth=bit_depth,
        )

        return await self.convert(input_path, output_path, settings)

    async def convert_to_format(
        self,
        input_path: Path,
        output_path: Path,
        target_format: AudioFormat,
        bitrate_kbps: int | None = None,
        sample_rate: int | None = None,
        channels: int | None = None,
        normalize: bool = False,
        metadata: dict | None = None,
    ) -> ConversionResult:
        """
        Convert audio to a specific format with custom settings.

        Args:
            input_path: Path to input audio file
            output_path: Path for output file (extension will be corrected)
            target_format: Target AudioFormat
            bitrate_kbps: Bitrate for lossy formats (uses default if not specified)
            sample_rate: Output sample rate (uses format default if not specified)
            channels: Output channels (uses format default if not specified)
            normalize: Apply loudness normalization
            metadata: Metadata dict to embed (for supported formats)

        Returns:
            ConversionResult with success status and output path
        """
        fmt_info = STANDARD_AUDIO_FORMATS[target_format]

        # Ensure correct extension
        correct_ext = f".{fmt_info.primary_extension}"
        if output_path.suffix.lower() != correct_ext:
            output_path = output_path.with_suffix(correct_ext)

        settings = ConversionSettings(
            format=target_format,
            sample_rate=sample_rate or fmt_info.default_sample_rate,
            channels=channels or fmt_info.default_channels,
            bit_depth=fmt_info.default_bit_depth,
            bitrate_kbps=bitrate_kbps or fmt_info.default_bitrate_kbps,
            normalize=normalize,
            metadata=metadata,
        )

        return await self.convert(input_path, output_path, settings)

    async def convert(
        self,
        input_path: Path,
        output_path: Path,
        settings: ConversionSettings,
    ) -> ConversionResult:
        """
        Convert audio file with specified settings.

        This is the main conversion method used by all other methods.

        Args:
            input_path: Path to input audio file
            output_path: Path for output file
            settings: Conversion settings

        Returns:
            ConversionResult with success status and details
        """
        # Validate input exists
        if not input_path.exists():
            return ConversionResult(
                success=False,
                error=f"Input file not found: {input_path}",
            )

        # Detect input format
        input_format = get_format_by_extension(input_path.suffix)

        try:
            ffmpeg = self._get_ffmpeg()
        except RuntimeError as e:
            return ConversionResult(
                success=False,
                error=str(e),
            )

        # Build FFmpeg command
        cmd = [str(ffmpeg), "-y", "-i", str(input_path)]

        # Add format-specific encoding arguments
        fmt_info = STANDARD_AUDIO_FORMATS[settings.format]

        # Codec
        cmd.extend(["-c:a", fmt_info.ffmpeg_codec])

        # Sample rate
        cmd.extend(["-ar", str(settings.sample_rate)])

        # Channels
        cmd.extend(["-ac", str(settings.channels)])

        # Bit depth for PCM formats
        if settings.format in (AudioFormat.WAV, AudioFormat.AIFF):
            # Determine PCM codec based on bit depth
            if settings.bit_depth == 8:
                pcm_codec = "pcm_u8"
            elif settings.bit_depth == 24:
                pcm_codec = "pcm_s24le" if settings.format == AudioFormat.WAV else "pcm_s24be"
            elif settings.bit_depth == 32:
                pcm_codec = "pcm_s32le" if settings.format == AudioFormat.WAV else "pcm_s32be"
            else:  # Default to 16-bit
                pcm_codec = "pcm_s16le" if settings.format == AudioFormat.WAV else "pcm_s16be"
            cmd[cmd.index("-c:a") + 1] = pcm_codec

        # Bitrate for lossy formats
        if fmt_info.is_lossy and settings.bitrate_kbps:
            cmd.extend(["-b:a", f"{settings.bitrate_kbps}k"])

        # Audio filters
        filters = []

        if settings.normalize:
            filters.append(f"loudnorm=I={settings.normalize_lufs}")

        if filters:
            cmd.extend(["-af", ",".join(filters)])

        # Metadata
        if settings.metadata and fmt_info.supports_metadata:
            for key, value in settings.metadata.items():
                cmd.extend(["-metadata", f"{key}={value}"])

        # Output format if needed
        if fmt_info.ffmpeg_format:
            cmd.extend(["-f", fmt_info.ffmpeg_format])

        # Output path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd.append(str(output_path))

        logger.debug(f"FFmpeg command: {' '.join(cmd)}")

        # Execute FFmpeg
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            _stdout, stderr = await process.communicate()
            stderr_text = stderr.decode("utf-8", errors="replace") if stderr else ""

            if process.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {stderr_text}")
                return ConversionResult(
                    success=False,
                    input_format=input_format,
                    output_format=settings.format,
                    error=f"FFmpeg exited with code {process.returncode}",
                    ffmpeg_stderr=stderr_text,
                )

            # Get output file info
            file_size = output_path.stat().st_size if output_path.exists() else 0

            # Try to get duration from FFmpeg output
            duration = self._parse_duration_from_stderr(stderr_text)

            return ConversionResult(
                success=True,
                output_path=output_path,
                input_format=input_format,
                output_format=settings.format,
                duration_seconds=duration,
                file_size_bytes=file_size,
                ffmpeg_stderr=stderr_text,
            )

        except FileNotFoundError:
            return ConversionResult(
                success=False,
                error="FFmpeg executable not found",
            )
        except Exception as e:
            logger.exception(f"Conversion error: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
            )

    def _parse_duration_from_stderr(self, stderr: str) -> float | None:
        """
        Parse duration from FFmpeg stderr output.

        FFmpeg outputs duration in format: "Duration: HH:MM:SS.ms"

        Args:
            stderr: FFmpeg stderr output

        Returns:
            Duration in seconds, or None if not found
        """
        import re

        match = re.search(r"Duration:\s*(\d{2}):(\d{2}):(\d{2})\.(\d+)", stderr)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = int(match.group(3))
            ms = int(match.group(4)[:3].ljust(3, "0"))  # Normalize to 3 digits
            return hours * 3600 + minutes * 60 + seconds + ms / 1000

        return None

    async def probe_format(self, input_path: Path) -> tuple[AudioFormat | None, dict | None]:
        """
        Probe an audio file to detect its format and metadata.

        Uses FFprobe to get detailed format information.

        Args:
            input_path: Path to audio file

        Returns:
            Tuple of (AudioFormat or None, metadata dict or None)
        """
        try:
            ffmpeg = self._get_ffmpeg()
            ffprobe = ffmpeg.parent / ("ffprobe.exe" if os.name == "nt" else "ffprobe")

            if not ffprobe.exists():
                # Try system PATH
                import shutil

                probe_path = shutil.which("ffprobe")
                if probe_path:
                    ffprobe = Path(probe_path)
                else:
                    return (get_format_by_extension(input_path.suffix), None)

            cmd = [
                str(ffprobe),
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                str(input_path),
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, _ = await process.communicate()

            if process.returncode == 0 and stdout:
                import json

                data = json.loads(stdout.decode("utf-8"))

                # Extract format info
                format_info = data.get("format", {})
                format_name = format_info.get("format_name", "")

                # Map ffprobe format to our AudioFormat
                detected_format = self._map_ffprobe_format(format_name, input_path.suffix)

                return (detected_format, format_info)

        except Exception as e:
            logger.debug(f"FFprobe failed: {e}")

        # Fallback to extension-based detection
        return (get_format_by_extension(input_path.suffix), None)

    def _map_ffprobe_format(self, format_name: str, extension: str) -> AudioFormat | None:
        """Map FFprobe format name to AudioFormat."""
        format_map = {
            "wav": AudioFormat.WAV,
            "mp3": AudioFormat.MP3,
            "flac": AudioFormat.FLAC,
            "ogg": AudioFormat.OGG,
            "opus": AudioFormat.OPUS,
            "mov,mp4,m4a,3gp,3g2,mj2": AudioFormat.M4A,
            "aac": AudioFormat.AAC,
            "asf": AudioFormat.WMA,
            "aiff": AudioFormat.AIFF,
        }

        for key, fmt in format_map.items():
            if key in format_name.lower():
                return fmt

        # Fallback to extension
        return get_format_by_extension(extension)


# Singleton instance for convenience
_conversion_service: AudioConversionService | None = None


def get_conversion_service() -> AudioConversionService:
    """
    Get the singleton AudioConversionService instance.

    Returns:
        AudioConversionService instance
    """
    global _conversion_service
    if _conversion_service is None:
        _conversion_service = AudioConversionService()
    return _conversion_service
