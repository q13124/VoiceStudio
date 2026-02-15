"""
Audio Format Catalog - Single Source of Truth

Centralizes all audio format definitions for VoiceStudio including:
- File extensions and aliases
- MIME types
- Magic bytes for validation
- FFmpeg codec mappings
- Format metadata (lossy/lossless, default bitrates)

This module prevents format drift by providing a single authoritative
source for audio format information across the backend.

Standard Format Set (per Audio Format Expansion Plan):
- WAV, MP3, FLAC, OGG/Opus, M4A, AAC, WMA, AIFF/AIF
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AudioFormat(Enum):
    """Supported audio formats in VoiceStudio."""

    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    OPUS = "opus"
    M4A = "m4a"
    AAC = "aac"
    WMA = "wma"
    AIFF = "aiff"


@dataclass(frozen=True)
class AudioFormatInfo:
    """Complete information about an audio format."""

    format: AudioFormat
    name: str
    description: str

    # File extensions (primary first, then aliases)
    extensions: tuple[str, ...]

    # MIME types (primary first)
    mime_types: tuple[str, ...]

    # Magic bytes: (bytes, offset) pairs for detection
    magic_bytes: tuple[tuple[bytes, int], ...]

    # FFmpeg codec for encoding
    ffmpeg_codec: str

    # FFmpeg container format (for -f flag if needed)
    ffmpeg_format: str | None = None

    # Audio characteristics
    is_lossy: bool = False
    supports_metadata: bool = True

    # Default encoding settings
    default_bitrate_kbps: int | None = None  # For lossy formats
    default_sample_rate: int = 44100
    default_bit_depth: int = 16
    default_channels: int = 2

    @property
    def primary_extension(self) -> str:
        """Get the primary (canonical) file extension."""
        return self.extensions[0]

    @property
    def primary_mime_type(self) -> str:
        """Get the primary MIME type."""
        return self.mime_types[0]


# =============================================================================
# STANDARD AUDIO FORMAT DEFINITIONS
# =============================================================================

STANDARD_AUDIO_FORMATS: dict[AudioFormat, AudioFormatInfo] = {
    AudioFormat.WAV: AudioFormatInfo(
        format=AudioFormat.WAV,
        name="WAV",
        description="Waveform Audio File Format (uncompressed PCM)",
        extensions=("wav", "wave"),
        mime_types=("audio/wav", "audio/x-wav", "audio/wave"),
        magic_bytes=(
            (b"RIFF", 0),  # RIFF header (requires secondary check for WAVE)
        ),
        ffmpeg_codec="pcm_s16le",
        ffmpeg_format="wav",
        is_lossy=False,
        supports_metadata=False,
        default_bit_depth=16,
    ),

    AudioFormat.MP3: AudioFormatInfo(
        format=AudioFormat.MP3,
        name="MP3",
        description="MPEG Audio Layer III",
        extensions=("mp3",),
        mime_types=("audio/mpeg", "audio/mp3"),
        magic_bytes=(
            (b"ID3", 0),        # ID3v2 tag
            (b"\xff\xfb", 0),   # MPEG frame sync (Layer III)
            (b"\xff\xfa", 0),   # MPEG frame sync (Layer III)
            (b"\xff\xf3", 0),   # MPEG frame sync (Layer III)
            (b"\xff\xf2", 0),   # MPEG frame sync (Layer III)
        ),
        ffmpeg_codec="libmp3lame",
        is_lossy=True,
        supports_metadata=True,
        default_bitrate_kbps=192,
    ),

    AudioFormat.FLAC: AudioFormatInfo(
        format=AudioFormat.FLAC,
        name="FLAC",
        description="Free Lossless Audio Codec",
        extensions=("flac",),
        mime_types=("audio/flac", "audio/x-flac"),
        magic_bytes=(
            (b"fLaC", 0),
        ),
        ffmpeg_codec="flac",
        is_lossy=False,
        supports_metadata=True,
        default_bit_depth=16,
    ),

    AudioFormat.OGG: AudioFormatInfo(
        format=AudioFormat.OGG,
        name="OGG Vorbis",
        description="OGG container with Vorbis audio",
        extensions=("ogg", "oga"),
        mime_types=("audio/ogg", "audio/vorbis", "application/ogg"),
        magic_bytes=(
            (b"OggS", 0),
        ),
        ffmpeg_codec="libvorbis",
        ffmpeg_format="ogg",
        is_lossy=True,
        supports_metadata=True,
        default_bitrate_kbps=192,
    ),

    AudioFormat.OPUS: AudioFormatInfo(
        format=AudioFormat.OPUS,
        name="Opus",
        description="Opus audio codec (OGG container)",
        extensions=("opus",),
        mime_types=("audio/opus", "audio/ogg; codecs=opus"),
        magic_bytes=(
            (b"OggS", 0),  # OGG container (requires secondary check for Opus)
        ),
        ffmpeg_codec="libopus",
        ffmpeg_format="opus",
        is_lossy=True,
        supports_metadata=True,
        default_bitrate_kbps=128,
    ),

    AudioFormat.M4A: AudioFormatInfo(
        format=AudioFormat.M4A,
        name="M4A",
        description="MPEG-4 Audio (AAC in MP4 container)",
        extensions=("m4a",),
        mime_types=("audio/mp4", "audio/x-m4a", "audio/m4a"),
        magic_bytes=(
            (b"ftyp", 4),  # MP4 container (offset 4, requires secondary check)
        ),
        ffmpeg_codec="aac",
        ffmpeg_format="ipod",  # Creates compatible M4A
        is_lossy=True,
        supports_metadata=True,
        default_bitrate_kbps=192,
    ),

    AudioFormat.AAC: AudioFormatInfo(
        format=AudioFormat.AAC,
        name="AAC",
        description="Advanced Audio Coding (raw AAC stream)",
        extensions=("aac",),
        mime_types=("audio/aac", "audio/x-aac"),
        magic_bytes=(
            (b"\xff\xf1", 0),  # AAC ADTS frame sync (MPEG-4)
            (b"\xff\xf9", 0),  # AAC ADTS frame sync (MPEG-2)
            (b"ftyp", 4),      # May be in MP4 container
        ),
        ffmpeg_codec="aac",
        ffmpeg_format="adts",  # Raw AAC ADTS stream
        is_lossy=True,
        supports_metadata=False,  # Raw AAC has limited metadata
        default_bitrate_kbps=192,
    ),

    AudioFormat.WMA: AudioFormatInfo(
        format=AudioFormat.WMA,
        name="WMA",
        description="Windows Media Audio",
        extensions=("wma",),
        mime_types=("audio/x-ms-wma", "audio/wma"),
        magic_bytes=(
            (b"\x30\x26\xb2\x75\x8e\x66\xcf\x11", 0),  # ASF header GUID
        ),
        ffmpeg_codec="wmav2",
        ffmpeg_format="asf",
        is_lossy=True,
        supports_metadata=True,
        default_bitrate_kbps=192,
    ),

    AudioFormat.AIFF: AudioFormatInfo(
        format=AudioFormat.AIFF,
        name="AIFF",
        description="Audio Interchange File Format",
        extensions=("aiff", "aif", "aifc"),
        mime_types=("audio/aiff", "audio/x-aiff"),
        magic_bytes=(
            (b"FORM", 0),  # FORM header (requires secondary check for AIFF)
        ),
        ffmpeg_codec="pcm_s16be",
        ffmpeg_format="aiff",
        is_lossy=False,
        supports_metadata=True,
        default_bit_depth=16,
    ),
}


# =============================================================================
# LOOKUP INDEXES (built at module load time)
# =============================================================================

# Extension to format lookup (includes aliases)
_EXTENSION_TO_FORMAT: dict[str, AudioFormat] = {}
for fmt_info in STANDARD_AUDIO_FORMATS.values():
    for ext in fmt_info.extensions:
        _EXTENSION_TO_FORMAT[ext.lower()] = fmt_info.format

# MIME type to format lookup
_MIME_TO_FORMAT: dict[str, AudioFormat] = {}
for fmt_info in STANDARD_AUDIO_FORMATS.values():
    for mime in fmt_info.mime_types:
        _MIME_TO_FORMAT[mime.lower()] = fmt_info.format

# All supported extensions as a frozen set
_ALL_EXTENSIONS: frozenset[str] = frozenset(_EXTENSION_TO_FORMAT.keys())

# All supported MIME types as a frozen set
_ALL_MIME_TYPES: frozenset[str] = frozenset(_MIME_TO_FORMAT.keys())


# =============================================================================
# PUBLIC API
# =============================================================================

def get_format_info(fmt: AudioFormat) -> AudioFormatInfo:
    """
    Get complete format information for an AudioFormat.

    Args:
        fmt: The AudioFormat enum value

    Returns:
        AudioFormatInfo with all format details

    Raises:
        KeyError: If format not in catalog (should never happen)
    """
    return STANDARD_AUDIO_FORMATS[fmt]


def get_format_by_extension(extension: str) -> AudioFormat | None:
    """
    Look up AudioFormat by file extension.

    Handles aliases (e.g., 'aif' -> AIFF, 'wave' -> WAV).

    Args:
        extension: File extension with or without leading dot

    Returns:
        AudioFormat if recognized, None otherwise
    """
    normalized = normalize_extension(extension)
    return _EXTENSION_TO_FORMAT.get(normalized)


def get_format_by_mime_type(mime_type: str) -> AudioFormat | None:
    """
    Look up AudioFormat by MIME type.

    Args:
        mime_type: MIME type string (case-insensitive)

    Returns:
        AudioFormat if recognized, None otherwise
    """
    return _MIME_TO_FORMAT.get(mime_type.lower())


def get_all_extensions() -> frozenset[str]:
    """
    Get all supported file extensions (lowercase, without dots).

    Returns:
        Frozen set of all supported extensions
    """
    return _ALL_EXTENSIONS


def get_all_mime_types() -> frozenset[str]:
    """
    Get all supported MIME types.

    Returns:
        Frozen set of all supported MIME types
    """
    return _ALL_MIME_TYPES


def normalize_extension(extension: str) -> str:
    """
    Normalize a file extension to canonical form.

    - Removes leading dot
    - Converts to lowercase
    - Maps aliases to primary extension

    Args:
        extension: Extension to normalize

    Returns:
        Normalized extension (e.g., '.AIF' -> 'aif')
    """
    ext = extension.lower().lstrip(".")
    return ext


def is_supported_extension(extension: str) -> bool:
    """
    Check if a file extension is supported.

    Args:
        extension: Extension to check (with or without dot)

    Returns:
        True if supported, False otherwise
    """
    return normalize_extension(extension) in _ALL_EXTENSIONS


def get_canonical_extension(extension: str) -> str | None:
    """
    Get the canonical (primary) extension for a given extension.

    Useful for normalizing aliases to standard form.

    Args:
        extension: Extension to look up

    Returns:
        Primary extension (e.g., 'aif' -> 'aiff'), or None if unsupported
    """
    fmt = get_format_by_extension(extension)
    if fmt is None:
        return None
    return STANDARD_AUDIO_FORMATS[fmt].primary_extension


def get_magic_bytes_for_validation() -> list[tuple[bytes, int, str, str, str]]:
    """
    Get magic byte signatures in the format expected by file_validation.py.

    Returns:
        List of (magic_bytes, offset, extension, mime_type, description) tuples
    """
    signatures = []
    for fmt_info in STANDARD_AUDIO_FORMATS.values():
        for magic, offset in fmt_info.magic_bytes:
            signatures.append((
                magic,
                offset,
                fmt_info.primary_extension,
                fmt_info.primary_mime_type,
                fmt_info.description,
            ))
    return signatures


def get_ffmpeg_codec(fmt: AudioFormat) -> str:
    """
    Get the FFmpeg codec name for encoding to a format.

    Args:
        fmt: Target audio format

    Returns:
        FFmpeg codec name (e.g., 'libmp3lame', 'flac')
    """
    return STANDARD_AUDIO_FORMATS[fmt].ffmpeg_codec


def get_ffmpeg_output_args(
    fmt: AudioFormat,
    bitrate_kbps: int | None = None,
    sample_rate: int | None = None,
    channels: int | None = None,
) -> list[str]:
    """
    Get FFmpeg arguments for encoding to a format.

    Args:
        fmt: Target audio format
        bitrate_kbps: Bitrate in kbps (uses default if not specified)
        sample_rate: Sample rate in Hz (uses default if not specified)
        channels: Number of channels (uses default if not specified)

    Returns:
        List of FFmpeg arguments (without input/output paths)
    """
    info = STANDARD_AUDIO_FORMATS[fmt]
    args = []

    # Codec
    args.extend(["-c:a", info.ffmpeg_codec])

    # Format if needed
    if info.ffmpeg_format:
        args.extend(["-f", info.ffmpeg_format])

    # Sample rate
    sr = sample_rate or info.default_sample_rate
    args.extend(["-ar", str(sr)])

    # Channels
    ch = channels or info.default_channels
    args.extend(["-ac", str(ch)])

    # Bitrate for lossy formats
    if info.is_lossy:
        br = bitrate_kbps or info.default_bitrate_kbps
        if br:
            args.extend(["-b:a", f"{br}k"])

    return args
