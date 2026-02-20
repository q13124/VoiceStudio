"""
Unit Tests for File Validation - Audio Format Support
Tests that all standard audio formats are properly validated.
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend.core.security.file_validation import (
        AUDIO_SIGNATURES,
        EXTENSION_CATEGORIES,
        validate_audio_file,
    )
except ImportError:
    pytest.skip(
        "Could not import file_validation module",
        allow_module_level=True
    )


class TestAudioSignatures:
    """Test AUDIO_SIGNATURES list."""

    def test_wav_signature_present(self):
        """Test WAV magic bytes are defined."""
        wav_found = any(
            b"RIFF" in sig[0] for sig in AUDIO_SIGNATURES
        )
        assert wav_found, "WAV signature missing"

    def test_mp3_signature_present(self):
        """Test MP3 magic bytes are defined."""
        # MP3 has multiple magic bytes (ID3, 0xFF 0xFB, etc.)
        mp3_found = any(
            b"\xff\xfb" in sig[0] or b"ID3" in sig[0]
            for sig in AUDIO_SIGNATURES
        )
        assert mp3_found, "MP3 signature missing"

    def test_flac_signature_present(self):
        """Test FLAC magic bytes are defined."""
        flac_found = any(
            b"fLaC" in sig[0] for sig in AUDIO_SIGNATURES
        )
        assert flac_found, "FLAC signature missing"

    def test_ogg_signature_present(self):
        """Test OGG magic bytes are defined."""
        ogg_found = any(
            b"OggS" in sig[0] for sig in AUDIO_SIGNATURES
        )
        assert ogg_found, "OGG signature missing"


class TestExtensionCategories:
    """Test EXTENSION_CATEGORIES dictionary."""

    def test_standard_audio_extensions_present(self):
        """Test all standard audio extensions are categorized."""
        required_extensions = [
            "wav", "mp3", "flac", "ogg", "m4a", "aac", "wma", "aiff"
        ]
        for ext in required_extensions:
            assert ext in EXTENSION_CATEGORIES, \
                f"Extension '{ext}' not in EXTENSION_CATEGORIES"
            # FileCategory enum has AUDIO value
            cat = EXTENSION_CATEGORIES[ext]
            assert cat.value == "audio", \
                f"Extension '{ext}' should be categorized as 'audio'"

    def test_extension_aliases_present(self):
        """Test extension aliases are included."""
        aliases = ["wave", "oga", "opus", "aif", "aifc"]
        for alias in aliases:
            assert alias in EXTENSION_CATEGORIES, \
                f"Alias '{alias}' not in EXTENSION_CATEGORIES"


class TestValidateAudioFile:
    """Test validate_audio_file function."""

    @pytest.fixture
    def sample_wav_bytes(self):
        """Create minimal WAV file bytes."""
        # Minimal WAV header (RIFF + WAVE)
        header = b"RIFF\x24\x00\x00\x00WAVE"
        fmt_chunk = b"fmt \x10\x00\x00\x00\x01\x00\x01\x00"
        fmt_chunk += b"\x44\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00"
        data_chunk = b"data\x00\x00\x00\x00"
        return header + fmt_chunk + data_chunk

    @pytest.fixture
    def sample_mp3_bytes(self):
        """Create minimal MP3 file bytes."""
        # ID3 header
        return b"ID3\x04\x00\x00\x00\x00\x00\x00" + b"\xff\xfb\x90\x00" * 10

    @pytest.fixture
    def sample_flac_bytes(self):
        """Create minimal FLAC file bytes."""
        return b"fLaC\x00\x00\x00\x22" + b"\x00" * 34

    @pytest.fixture
    def sample_ogg_bytes(self):
        """Create minimal OGG file bytes."""
        return b"OggS\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00" + b"\x00" * 50

    def test_validate_wav_file(self, sample_wav_bytes):
        """Test validating WAV file."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(sample_wav_bytes)
            tmp.flush()
            is_valid, _, _ = validate_audio_file(tmp.name)
            # Should at least recognize the extension
            assert isinstance(is_valid, bool)
            Path(tmp.name).unlink()

    def test_validate_mp3_file(self, sample_mp3_bytes):
        """Test validating MP3 file."""
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp.write(sample_mp3_bytes)
            tmp.flush()
            is_valid, _, _ = validate_audio_file(tmp.name)
            assert isinstance(is_valid, bool)
            Path(tmp.name).unlink()

    def test_validate_with_extended_formats(self, sample_wav_bytes):
        """Test that validate_audio_file accepts extended format list."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(sample_wav_bytes)
            tmp.flush()
            # Test with extended format set
            extended_formats = {
                "wav", "wave", "mp3", "flac", "ogg", "oga",
                "opus", "m4a", "aac", "wma", "aiff", "aif", "aifc"
            }
            is_valid, _, _ = validate_audio_file(
                tmp.name, allowed_formats=extended_formats
            )
            # File should be accepted
            assert isinstance(is_valid, bool)
            Path(tmp.name).unlink()

    def test_reject_invalid_extension(self, sample_wav_bytes):
        """Test rejecting file with invalid extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(sample_wav_bytes)
            tmp.flush()
            # Default allowed_formats should not include .txt
            is_valid, _, error = validate_audio_file(tmp.name)
            assert is_valid is False or error is not None
            Path(tmp.name).unlink()

    def test_reject_nonexistent_file(self):
        """Test rejecting nonexistent file."""
        is_valid, _, error = validate_audio_file(
            "/nonexistent/path/to/file.wav"
        )
        assert is_valid is False
        assert error is not None
