"""
Unit Tests for Audio Format Catalog
Tests the centralized audio format definitions and lookup functions.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend.core.audio.formats import (
        STANDARD_AUDIO_FORMATS,
        AudioFormat,
        AudioFormatInfo,
        get_ffmpeg_output_args,
        get_format_by_extension,
        get_format_info,
        get_magic_bytes_for_validation,
    )
except ImportError:
    pytest.skip("Could not import audio formats module", allow_module_level=True)


class TestAudioFormatEnum:
    """Test AudioFormat enum."""

    def test_all_standard_formats_defined(self):
        """Test all standard audio formats are defined in enum."""
        expected_formats = ["WAV", "MP3", "FLAC", "OGG", "OPUS", "M4A", "AAC", "WMA", "AIFF"]
        for fmt_name in expected_formats:
            assert hasattr(AudioFormat, fmt_name), f"AudioFormat missing {fmt_name}"

    def test_format_values_are_lowercase(self):
        """Test format enum values are lowercase strings."""
        for fmt in AudioFormat:
            assert fmt.value.islower(), f"Format {fmt.name} value should be lowercase"


class TestStandardAudioFormats:
    """Test STANDARD_AUDIO_FORMATS dictionary."""

    def test_all_formats_have_info(self):
        """Test all AudioFormat enum values have corresponding info."""
        for fmt in AudioFormat:
            assert fmt in STANDARD_AUDIO_FORMATS, f"Missing info for {fmt.name}"

    def test_format_info_has_required_fields(self):
        """Test all format info has required fields."""
        for fmt, info in STANDARD_AUDIO_FORMATS.items():
            assert isinstance(info, AudioFormatInfo), f"{fmt.name} info is not AudioFormatInfo"
            assert info.format == fmt, f"{fmt.name} info.format mismatch"
            assert len(info.name) > 0, f"{fmt.name} missing name"
            assert len(info.description) > 0, f"{fmt.name} missing description"
            assert len(info.extensions) > 0, f"{fmt.name} missing extensions"
            assert len(info.mime_types) > 0, f"{fmt.name} missing mime_types"
            assert len(info.ffmpeg_codec) > 0, f"{fmt.name} missing ffmpeg_codec"

    def test_wav_format_is_lossless(self):
        """Test WAV format is marked as lossless."""
        wav_info = STANDARD_AUDIO_FORMATS[AudioFormat.WAV]
        assert wav_info.is_lossy is False, "WAV should be lossless"

    def test_mp3_format_is_lossy(self):
        """Test MP3 format is marked as lossy."""
        mp3_info = STANDARD_AUDIO_FORMATS[AudioFormat.MP3]
        assert mp3_info.is_lossy is True, "MP3 should be lossy"

    def test_lossy_formats_have_default_bitrate(self):
        """Test lossy formats have default bitrate."""
        for fmt, info in STANDARD_AUDIO_FORMATS.items():
            if info.is_lossy:
                assert info.default_bitrate_kbps is not None, f"Lossy format {fmt.name} missing default bitrate"


class TestGetFormatInfo:
    """Test get_format_info function."""

    def test_get_wav_format_info(self):
        """Test getting WAV format info."""
        info = get_format_info(AudioFormat.WAV)
        assert info.name == "WAV"
        assert "wav" in info.extensions
        assert "audio/wav" in info.mime_types

    def test_get_mp3_format_info(self):
        """Test getting MP3 format info."""
        info = get_format_info(AudioFormat.MP3)
        assert info.name == "MP3"
        assert "mp3" in info.extensions
        assert info.is_lossy is True

    def test_get_flac_format_info(self):
        """Test getting FLAC format info."""
        info = get_format_info(AudioFormat.FLAC)
        assert info.name == "FLAC"
        assert info.is_lossy is False


class TestGetFormatByExtension:
    """Test get_format_by_extension function."""

    def test_get_format_by_wav_extension(self):
        """Test looking up format by .wav extension."""
        fmt = get_format_by_extension("wav")
        assert fmt == AudioFormat.WAV

    def test_get_format_by_wave_alias(self):
        """Test looking up format by .wave alias."""
        fmt = get_format_by_extension("wave")
        assert fmt == AudioFormat.WAV

    def test_get_format_by_mp3_extension(self):
        """Test looking up format by .mp3 extension."""
        fmt = get_format_by_extension("mp3")
        assert fmt == AudioFormat.MP3

    def test_get_format_by_ogg_extension(self):
        """Test looking up format by .ogg extension."""
        fmt = get_format_by_extension("ogg")
        assert fmt == AudioFormat.OGG

    def test_get_format_by_aiff_aliases(self):
        """Test looking up format by AIFF aliases."""
        assert get_format_by_extension("aiff") == AudioFormat.AIFF
        assert get_format_by_extension("aif") == AudioFormat.AIFF
        assert get_format_by_extension("aifc") == AudioFormat.AIFF

    def test_get_format_unknown_extension(self):
        """Test looking up unknown extension returns None."""
        fmt = get_format_by_extension("xyz")
        assert fmt is None

    def test_get_format_case_insensitive(self):
        """Test extension lookup is case-insensitive."""
        assert get_format_by_extension("WAV") == AudioFormat.WAV
        assert get_format_by_extension("Mp3") == AudioFormat.MP3
        assert get_format_by_extension("FLAC") == AudioFormat.FLAC


class TestGetMagicBytesForValidation:
    """Test get_magic_bytes_for_validation function."""

    def test_returns_list_of_tuples(self):
        """Test function returns properly formatted list."""
        magic_bytes = get_magic_bytes_for_validation()
        assert isinstance(magic_bytes, list)
        assert len(magic_bytes) > 0

    def test_magic_bytes_tuple_format(self):
        """Test each magic byte entry has correct format."""
        magic_bytes = get_magic_bytes_for_validation()
        for entry in magic_bytes:
            assert len(entry) == 5, "Each entry should be (bytes, offset, ext, category, mime)"
            magic, offset, ext, category, mime = entry
            assert isinstance(magic, bytes), "First element should be bytes"
            assert isinstance(offset, int), "Second element should be int"
            assert isinstance(ext, str), "Third element should be string"
            assert category == "audio", "Category should be 'audio'"
            assert isinstance(mime, str), "Fifth element should be string"


class TestGetFfmpegOutputArgs:
    """Test get_ffmpeg_output_args function."""

    def test_wav_output_args(self):
        """Test FFmpeg output args for WAV."""
        args = get_ffmpeg_output_args(AudioFormat.WAV)
        assert "-c:a" in args or "-acodec" in args
        assert "pcm_s16le" in args

    def test_mp3_output_args_with_bitrate(self):
        """Test FFmpeg output args for MP3 with custom bitrate."""
        args = get_ffmpeg_output_args(AudioFormat.MP3, bitrate_kbps=320)
        assert "-b:a" in args
        assert "320k" in args

    def test_flac_output_args(self):
        """Test FFmpeg output args for FLAC."""
        args = get_ffmpeg_output_args(AudioFormat.FLAC)
        assert "flac" in args

    def test_sample_rate_included(self):
        """Test sample rate is included in args."""
        args = get_ffmpeg_output_args(AudioFormat.WAV, sample_rate=48000)
        assert "-ar" in args
        assert "48000" in args

    def test_channels_included(self):
        """Test channel count is included in args."""
        args = get_ffmpeg_output_args(AudioFormat.WAV, channels=1)
        assert "-ac" in args
        assert "1" in args
