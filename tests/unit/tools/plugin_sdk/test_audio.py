"""
Unit tests for the audio module.
"""

import math
import os
import struct
import sys
import tempfile
from pathlib import Path

import pytest

# Add SDK to path for testing
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "tools", "plugin-sdk")
)

from voicestudio_sdk.audio import AudioBuffer, AudioFormat


def create_test_wav(
    duration: float = 1.0,
    sample_rate: int = 44100,
    channels: int = 1,
    frequency: float = 440.0,
) -> bytes:
    """Create a test WAV file with a sine wave."""
    num_samples = int(duration * sample_rate)
    samples = []

    for i in range(num_samples):
        t = i / sample_rate
        value = math.sin(2 * math.pi * frequency * t)
        sample = int(value * 32767)
        samples.append(sample)

    # Create raw audio data
    raw_data = struct.pack(f"<{len(samples)}h", *samples)

    # Create WAV header
    data_size = len(raw_data)
    wav_header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,  # Subchunk size
        1,  # Audio format (PCM)
        channels,
        sample_rate,
        sample_rate * channels * 2,  # Byte rate
        channels * 2,  # Block align
        16,  # Bits per sample
        b"data",
        data_size,
    )

    return wav_header + raw_data


class TestAudioFormat:
    """Tests for AudioFormat enum."""

    def test_audio_formats_exist(self):
        """Test that all expected audio formats exist."""
        assert AudioFormat.WAV
        assert AudioFormat.MP3
        assert AudioFormat.OGG
        assert AudioFormat.FLAC
        assert AudioFormat.RAW

    def test_audio_format_values(self):
        """Test audio format string values."""
        assert AudioFormat.WAV.value == "wav"
        assert AudioFormat.MP3.value == "mp3"


class TestAudioBuffer:
    """Tests for AudioBuffer class."""

    def test_create_audio_buffer(self):
        """Test creating an audio buffer."""
        data = create_test_wav(duration=0.1)

        buffer = AudioBuffer(
            data=data,
            format=AudioFormat.WAV,
            sample_rate=44100,
            channels=1,
            bit_depth=16,
        )

        assert buffer.data == data
        assert buffer.format == AudioFormat.WAV
        assert buffer.sample_rate == 44100
        assert buffer.channels == 1
        assert buffer.bit_depth == 16

    def test_audio_buffer_defaults(self):
        """Test audio buffer default values."""
        buffer = AudioBuffer(data=b"test")

        assert buffer.format == AudioFormat.WAV
        assert buffer.sample_rate == 44100
        assert buffer.channels == 1
        assert buffer.bit_depth == 16

    def test_duration_calculation(self):
        """Test duration property calculation."""
        # Create 0.5 second audio at 44100 Hz, 16-bit mono
        duration = 0.5
        data = create_test_wav(duration=duration, sample_rate=44100)

        buffer = AudioBuffer(
            data=data,
            format=AudioFormat.WAV,
            sample_rate=44100,
            channels=1,
            bit_depth=16,
        )

        # Duration should be approximately 0.5 seconds
        # Allow small tolerance for rounding
        assert abs(buffer.duration - duration) < 0.01

    def test_from_file(self):
        """Test loading audio from file."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_data = create_test_wav(duration=0.1)
            f.write(wav_data)
            temp_path = f.name

        try:
            buffer = AudioBuffer.from_file(temp_path)

            assert buffer.data == wav_data
            assert buffer.format == AudioFormat.WAV
            assert buffer.sample_rate == 44100
        finally:
            os.unlink(temp_path)

    def test_from_file_nonexistent(self):
        """Test loading from nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            AudioBuffer.from_file("/nonexistent/path/file.wav")

    def test_save_to_file(self):
        """Test saving audio to file."""
        data = create_test_wav(duration=0.1)
        buffer = AudioBuffer(data=data, format=AudioFormat.WAV)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name

        try:
            buffer.save(temp_path)

            with open(temp_path, "rb") as f:
                saved_data = f.read()

            assert saved_data == data
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_as_raw_samples(self):
        """Test converting to raw samples."""
        data = create_test_wav(duration=0.1)
        buffer = AudioBuffer(
            data=data,
            format=AudioFormat.WAV,
            sample_rate=44100,
            channels=1,
            bit_depth=16,
        )

        raw_samples = buffer.as_raw_samples()

        # Raw samples should not include WAV header (44 bytes)
        assert len(raw_samples) == len(data) - 44

    def test_from_raw_samples(self):
        """Test creating buffer from raw samples."""
        # Create raw 16-bit mono samples
        num_samples = 1000
        samples = [int(32767 * math.sin(2 * math.pi * 440 * i / 44100)) for i in range(num_samples)]
        raw_data = struct.pack(f"<{len(samples)}h", *samples)

        buffer = AudioBuffer.from_raw_samples(
            samples=raw_data,
            sample_rate=44100,
            channels=1,
            bit_depth=16,
        )

        assert buffer.sample_rate == 44100
        assert buffer.channels == 1
        # Duration should be approximately num_samples / sample_rate
        expected_duration = num_samples / 44100
        assert abs(buffer.duration - expected_duration) < 0.01

    def test_normalize(self):
        """Test audio normalization."""
        data = create_test_wav(duration=0.1, frequency=440.0)
        buffer = AudioBuffer(
            data=data,
            format=AudioFormat.WAV,
            sample_rate=44100,
            channels=1,
            bit_depth=16,
        )

        normalized = buffer.normalize(target_peak=0.5)

        # Normalized buffer should have same duration
        assert abs(normalized.duration - buffer.duration) < 0.01
        assert normalized.format == buffer.format

    def test_resample_placeholder(self):
        """Test resampling (placeholder implementation)."""
        data = create_test_wav(duration=0.1, sample_rate=44100)
        buffer = AudioBuffer(
            data=data,
            format=AudioFormat.WAV,
            sample_rate=44100,
            channels=1,
            bit_depth=16,
        )

        # Current implementation is a placeholder that returns self
        resampled = buffer.resample(target_rate=22050)

        # Placeholder just updates sample_rate attribute
        assert resampled.sample_rate == 22050


class TestAudioBufferParsing:
    """Tests for WAV parsing functionality."""

    def test_parse_wav_header(self):
        """Test parsing WAV header."""
        data = create_test_wav(
            duration=0.1,
            sample_rate=22050,
            channels=1,
        )

        buffer = AudioBuffer.from_file_data(data)

        assert buffer.sample_rate == 22050
        assert buffer.channels == 1
        assert buffer.bit_depth == 16
        assert buffer.format == AudioFormat.WAV

    def test_parse_wav_stereo(self):
        """Test parsing stereo WAV."""
        # Create stereo WAV header manually
        sample_rate = 44100
        channels = 2
        num_samples = 4410 * 2  # 0.1 seconds * 2 channels

        samples = [0] * num_samples
        raw_data = struct.pack(f"<{len(samples)}h", *samples)
        data_size = len(raw_data)

        wav_header = struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            36 + data_size,
            b"WAVE",
            b"fmt ",
            16,
            1,  # PCM
            channels,
            sample_rate,
            sample_rate * channels * 2,
            channels * 2,
            16,
            b"data",
            data_size,
        )

        data = wav_header + raw_data
        buffer = AudioBuffer.from_file_data(data)

        assert buffer.channels == 2
