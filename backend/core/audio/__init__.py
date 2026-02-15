"""
Audio core module for VoiceStudio.

Provides centralized audio format definitions, conversion services,
and audio processing utilities.
"""

from .conversion import (
    AudioConversionService,
    ConversionResult,
    ConversionSettings,
    get_conversion_service,
)
from .formats import (
    STANDARD_AUDIO_FORMATS,
    AudioFormat,
    AudioFormatInfo,
    get_all_extensions,
    get_all_mime_types,
    get_canonical_extension,
    get_ffmpeg_codec,
    get_ffmpeg_output_args,
    get_format_by_extension,
    get_format_by_mime_type,
    get_format_info,
    get_magic_bytes_for_validation,
    is_supported_extension,
    normalize_extension,
)

__all__ = [
    "STANDARD_AUDIO_FORMATS",
    # Conversion service
    "AudioConversionService",
    # Format catalog
    "AudioFormat",
    "AudioFormatInfo",
    "ConversionResult",
    "ConversionSettings",
    "get_all_extensions",
    "get_all_mime_types",
    "get_canonical_extension",
    "get_conversion_service",
    "get_ffmpeg_codec",
    "get_ffmpeg_output_args",
    "get_format_by_extension",
    "get_format_by_mime_type",
    "get_format_info",
    "get_magic_bytes_for_validation",
    "is_supported_extension",
    "normalize_extension",
]
