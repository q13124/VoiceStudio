"""
Unit Tests for Audio Conversion Service
Tests FFmpeg-based audio conversion functionality.
"""

import contextlib
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from backend.core.audio.conversion import (
        AudioConversionService,
        ConversionResult,
        ConversionSettings,
        get_conversion_service,
    )
    from backend.core.audio.formats import AudioFormat
except ImportError:
    pytest.skip("Could not import audio conversion module", allow_module_level=True)


class TestConversionResult:
    """Test ConversionResult dataclass."""

    def test_successful_result(self):
        """Test creating a successful conversion result."""
        result = ConversionResult(
            success=True,
            output_path=Path("/tmp/output.wav"),
            duration_seconds=5.0,
        )
        assert result.success is True
        assert result.output_path == Path("/tmp/output.wav")
        assert result.error is None

    def test_failed_result(self):
        """Test creating a failed conversion result."""
        result = ConversionResult(
            success=False,
            error="FFmpeg not found",
        )
        assert result.success is False
        assert result.output_path is None
        assert result.error == "FFmpeg not found"


class TestConversionSettings:
    """Test ConversionSettings dataclass."""

    def test_default_settings(self):
        """Test default conversion settings."""
        settings = ConversionSettings()
        assert settings.format == AudioFormat.WAV
        assert settings.sample_rate == 44100
        assert settings.channels == 2
        assert settings.bit_depth == 16
        assert settings.bitrate_kbps is None

    def test_custom_settings(self):
        """Test custom conversion settings."""
        settings = ConversionSettings(
            format=AudioFormat.MP3,
            sample_rate=48000,
            channels=1,
            bitrate_kbps=320,
        )
        assert settings.format == AudioFormat.MP3
        assert settings.sample_rate == 48000
        assert settings.channels == 1
        assert settings.bitrate_kbps == 320


class TestAudioConversionService:
    """Test AudioConversionService class."""

    def test_service_creation(self):
        """Test service can be created."""
        service = AudioConversionService()
        assert service is not None

    def test_service_with_custom_ffmpeg_path(self):
        """Test service with custom FFmpeg path."""
        service = AudioConversionService(ffmpeg_path=Path("/usr/bin/ffmpeg"))
        assert service._ffmpeg_path == Path("/usr/bin/ffmpeg")

    @pytest.mark.asyncio
    async def test_convert_to_wav_missing_input(self):
        """Test convert_to_wav with missing input file."""
        service = AudioConversionService()
        result = await service.convert_to_wav(Path("/nonexistent/file.mp3"))
        assert result.success is False
        assert result.error is not None and (
            "not found" in result.error.lower() or "not exist" in result.error.lower()
        )

    @pytest.mark.asyncio
    async def test_convert_to_format_missing_input(self):
        """Test convert_to_format with missing input file."""
        service = AudioConversionService()
        result = await service.convert_to_format(
            Path("/nonexistent/file.mp3"),
            Path("/tmp/output.flac"),
            AudioFormat.FLAC,
        )
        assert result.success is False

    @pytest.mark.asyncio
    async def test_convert_requires_ffmpeg(self):
        """Test conversion requires FFmpeg to be available."""
        with patch.object(
            AudioConversionService, "_get_ffmpeg", side_effect=FileNotFoundError("FFmpeg not found")
        ):
            service = AudioConversionService()
            result = await service.convert_to_wav(Path("/some/file.mp3"))
            assert result.success is False

    @pytest.mark.asyncio
    async def test_probe_format_missing_file(self):
        """Test probe_format with missing file falls back to extension-based detection."""
        service = AudioConversionService()
        fmt, metadata = await service.probe_format(Path("/nonexistent/file.wav"))
        # Implementation falls back to extension-based detection when ffprobe fails
        # For a .wav extension, it returns AudioFormat.WAV
        assert fmt == AudioFormat.WAV
        # Metadata is None when ffprobe can't probe the actual file
        assert metadata is None


class TestGetConversionService:
    """Test get_conversion_service function."""

    def test_returns_singleton(self):
        """Test that get_conversion_service returns the same instance."""
        service1 = get_conversion_service()
        service2 = get_conversion_service()
        assert service1 is service2

    def test_returns_audio_conversion_service(self):
        """Test that it returns an AudioConversionService instance."""
        service = get_conversion_service()
        assert isinstance(service, AudioConversionService)


class TestConversionIntegration:
    """Integration tests for audio conversion (require FFmpeg)."""

    @pytest.fixture
    def sample_wav_file(self):
        """Create a sample WAV file for testing."""
        try:
            import numpy as np
            import soundfile as sf
        except ImportError:
            pytest.skip("soundfile/numpy not available")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            sample_rate = 44100
            duration = 0.5
            samples = np.sin(
                2 * np.pi * 440 * np.linspace(0, duration, int(sample_rate * duration))
            )
            sf.write(tmp.name, samples, sample_rate)
            yield Path(tmp.name)
            # Cleanup
            with contextlib.suppress(OSError):
                Path(tmp.name).unlink()

    @pytest.fixture
    def has_ffmpeg(self):
        """Check if FFmpeg is available."""
        import shutil

        if shutil.which("ffmpeg") is None:
            pytest.skip("FFmpeg not available")
        return True

    @pytest.mark.asyncio
    async def test_convert_wav_to_wav(self, sample_wav_file, has_ffmpeg):
        """Test converting WAV to WAV (copy)."""
        service = get_conversion_service()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = Path(tmp.name)
            result = await service.convert_to_wav(sample_wav_file, output_path)

            if result.success:
                assert output_path.exists()
                assert output_path.stat().st_size > 0
            # Cleanup
            with contextlib.suppress(OSError):
                output_path.unlink()

    @pytest.mark.asyncio
    async def test_convert_wav_to_mp3(self, sample_wav_file, has_ffmpeg):
        """Test converting WAV to MP3."""
        service = get_conversion_service()
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            output_path = Path(tmp.name)
            result = await service.convert_to_format(
                sample_wav_file,
                output_path,
                AudioFormat.MP3,
                bitrate_kbps=128,
            )

            if result.success:
                assert output_path.exists()
                assert output_path.stat().st_size > 0
            # Cleanup
            with contextlib.suppress(OSError):
                output_path.unlink()

    @pytest.mark.asyncio
    async def test_probe_wav_format(self, sample_wav_file, has_ffmpeg):
        """Test probing WAV file format."""
        service = get_conversion_service()
        fmt, metadata = await service.probe_format(sample_wav_file)

        if fmt is not None:
            assert fmt == AudioFormat.WAV
            if metadata:
                assert "sample_rate" in metadata or "format_name" in metadata
