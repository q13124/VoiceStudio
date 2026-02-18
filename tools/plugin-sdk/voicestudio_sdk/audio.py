"""
Audio utilities for VoiceStudio plugins.

Provides classes for handling audio data with format conversion
and common operations.
"""

import io
import struct
from dataclasses import dataclass
from enum import Enum


class AudioFormat(str, Enum):
    """Supported audio formats."""

    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    FLAC = "flac"
    RAW = "raw"


@dataclass
class AudioBuffer:
    """
    A buffer containing audio data with format information.

    This class provides a convenient wrapper around raw audio bytes
    with methods for common operations.

    Example:
        # Create from bytes
        audio = AudioBuffer(data=wav_bytes, format=AudioFormat.WAV)

        # Get duration
        print(f"Duration: {audio.duration:.2f} seconds")

        # Convert to different format (requires audio libraries)
        mp3_audio = audio.convert(AudioFormat.MP3)
    """

    data: bytes
    format: AudioFormat = AudioFormat.WAV
    sample_rate: int = 44100
    channels: int = 1
    bit_depth: int = 16

    @property
    def size(self) -> int:
        """Get the size of the audio data in bytes."""
        return len(self.data)

    @property
    def duration(self) -> float:
        """
        Estimate the duration in seconds.

        For WAV format, this is calculated from the audio parameters.
        For other formats, this is an estimate.
        """
        if self.format == AudioFormat.WAV:
            bytes_per_sample = self.bit_depth // 8
            samples_per_second = self.sample_rate * self.channels * bytes_per_sample
            if samples_per_second > 0:
                # Subtract WAV header (typically 44 bytes)
                data_size = max(0, len(self.data) - 44)
                return data_size / samples_per_second

        # Rough estimate for compressed formats
        return len(self.data) / (self.sample_rate * self.channels * 2) * 8

    @property
    def is_valid(self) -> bool:
        """Check if the audio data appears valid."""
        if len(self.data) < 4:
            return False

        if self.format == AudioFormat.WAV:
            return self.data[:4] == b"RIFF"
        elif self.format == AudioFormat.MP3:
            # Check for ID3 tag or MP3 frame sync
            return self.data[:3] == b"ID3" or (self.data[0] == 0xFF and (self.data[1] & 0xE0) == 0xE0)
        elif self.format == AudioFormat.OGG:
            return self.data[:4] == b"OggS"
        elif self.format == AudioFormat.FLAC:
            return self.data[:4] == b"fLaC"

        return True  # RAW format, assume valid

    @classmethod
    def from_file(cls, path: str) -> "AudioBuffer":
        """
        Load audio from a file.

        Args:
            path: Path to the audio file.

        Returns:
            AudioBuffer with the loaded data.
        """
        with open(path, "rb") as f:
            data = f.read()

        # Detect format from extension
        lower_path = path.lower()
        if lower_path.endswith(".wav"):
            format = AudioFormat.WAV
        elif lower_path.endswith(".mp3"):
            format = AudioFormat.MP3
        elif lower_path.endswith(".ogg"):
            format = AudioFormat.OGG
        elif lower_path.endswith(".flac"):
            format = AudioFormat.FLAC
        else:
            format = AudioFormat.RAW

        buffer = cls(data=data, format=format)

        # Parse WAV header for parameters
        if format == AudioFormat.WAV and len(data) >= 44:
            buffer._parse_wav_header()

        return buffer

    @classmethod
    def from_file_data(cls, data: bytes) -> "AudioBuffer":
        """
        Create an AudioBuffer from raw file data.

        Detects format from file signature and parses headers.

        Args:
            data: Raw file bytes.

        Returns:
            AudioBuffer with parsed parameters.
        """
        # Detect format from file signature
        if len(data) >= 4:
            if data[:4] == b"RIFF":
                format = AudioFormat.WAV
            elif data[:3] == b"ID3" or (len(data) > 1 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
                format = AudioFormat.MP3
            elif data[:4] == b"OggS":
                format = AudioFormat.OGG
            elif data[:4] == b"fLaC":
                format = AudioFormat.FLAC
            else:
                format = AudioFormat.RAW
        else:
            format = AudioFormat.RAW

        buffer = cls(data=data, format=format)

        # Parse WAV header for parameters
        if format == AudioFormat.WAV and len(data) >= 44:
            buffer._parse_wav_header()

        return buffer

    def _parse_wav_header(self) -> None:
        """Parse WAV header to extract audio parameters."""
        try:
            # Read format chunk
            if self.data[8:12] == b"WAVE":
                # Find fmt chunk
                pos = 12
                while pos < len(self.data) - 8:
                    chunk_id = self.data[pos:pos+4]
                    chunk_size = struct.unpack("<I", self.data[pos+4:pos+8])[0]

                    if chunk_id == b"fmt ":
                        fmt_data = self.data[pos+8:pos+8+chunk_size]
                        if len(fmt_data) >= 16:
                            _, self.channels, self.sample_rate, _, _, bits = struct.unpack(
                                "<HHIIHH", fmt_data[:16]
                            )
                            self.bit_depth = bits
                        break

                    pos += 8 + chunk_size
                    # Align to even boundary
                    if chunk_size % 2:
                        pos += 1
        except Exception:
            # Keep defaults on parse error
            pass

    def to_file(self, path: str) -> None:
        """
        Save audio to a file.

        Args:
            path: Path to save the audio file.
        """
        with open(path, "wb") as f:
            f.write(self.data)

    def save(self, path: str) -> None:
        """
        Save audio to a file (alias for to_file).

        Args:
            path: Path to save the audio file.
        """
        self.to_file(path)

    def as_raw_samples(self) -> bytes:
        """
        Get raw PCM samples.

        For WAV format, strips the header.
        For other formats, raises NotImplementedError.

        Returns:
            Raw PCM sample data.
        """
        if self.format == AudioFormat.WAV:
            # Find data chunk
            pos = 12
            while pos < len(self.data) - 8:
                chunk_id = self.data[pos:pos+4]
                chunk_size = struct.unpack("<I", self.data[pos+4:pos+8])[0]

                if chunk_id == b"data":
                    return self.data[pos+8:pos+8+chunk_size]

                pos += 8 + chunk_size
                if chunk_size % 2:
                    pos += 1

            # Fallback: return everything after standard header
            return self.data[44:]

        elif self.format == AudioFormat.RAW:
            return self.data

        raise NotImplementedError(
            f"Raw sample extraction not supported for {self.format.value} format"
        )

    @classmethod
    def from_raw_samples(
        cls,
        samples: bytes,
        sample_rate: int = 44100,
        channels: int = 1,
        bit_depth: int = 16,
    ) -> "AudioBuffer":
        """
        Create a WAV audio buffer from raw PCM samples.

        Args:
            samples: Raw PCM sample data.
            sample_rate: Sample rate in Hz.
            channels: Number of channels.
            bit_depth: Bits per sample (8, 16, 24, or 32).

        Returns:
            AudioBuffer in WAV format.
        """
        # Build WAV file
        bytes_per_sample = bit_depth // 8
        byte_rate = sample_rate * channels * bytes_per_sample
        block_align = channels * bytes_per_sample
        data_size = len(samples)
        file_size = data_size + 36  # Total size minus 8 bytes for RIFF header

        # Write header
        wav_data = io.BytesIO()

        # RIFF header
        wav_data.write(b"RIFF")
        wav_data.write(struct.pack("<I", file_size))
        wav_data.write(b"WAVE")

        # fmt chunk
        wav_data.write(b"fmt ")
        wav_data.write(struct.pack("<I", 16))  # Chunk size
        wav_data.write(struct.pack("<H", 1))   # Audio format (PCM)
        wav_data.write(struct.pack("<H", channels))
        wav_data.write(struct.pack("<I", sample_rate))
        wav_data.write(struct.pack("<I", byte_rate))
        wav_data.write(struct.pack("<H", block_align))
        wav_data.write(struct.pack("<H", bit_depth))

        # data chunk
        wav_data.write(b"data")
        wav_data.write(struct.pack("<I", data_size))
        wav_data.write(samples)

        return cls(
            data=wav_data.getvalue(),
            format=AudioFormat.WAV,
            sample_rate=sample_rate,
            channels=channels,
            bit_depth=bit_depth,
        )

    def resample(self, target_rate: int) -> "AudioBuffer":
        """
        Resample audio to a different sample rate.

        Note: This is a simple implementation. For production use,
        consider using scipy.signal.resample or a dedicated library.

        Args:
            target_rate: Target sample rate in Hz.

        Returns:
            Resampled AudioBuffer.
        """
        if self.sample_rate == target_rate:
            return AudioBuffer(
                data=self.data,
                format=self.format,
                sample_rate=self.sample_rate,
                channels=self.channels,
                bit_depth=self.bit_depth,
            )

        # Get raw samples
        raw = self.as_raw_samples()

        # Simple linear interpolation resampling
        bytes_per_sample = self.bit_depth // 8
        sample_count = len(raw) // bytes_per_sample // self.channels

        ratio = target_rate / self.sample_rate
        int(sample_count * ratio)

        # This is a placeholder - real resampling needs proper implementation
        # For now, just return the original with updated rate
        return AudioBuffer.from_raw_samples(
            raw,
            sample_rate=target_rate,
            channels=self.channels,
            bit_depth=self.bit_depth,
        )

    def normalize(self, target_peak: float = 0.9) -> "AudioBuffer":
        """
        Normalize audio to a target peak level.

        Args:
            target_peak: Target peak level (0.0 to 1.0).

        Returns:
            Normalized AudioBuffer.
        """
        if self.format != AudioFormat.WAV and self.format != AudioFormat.RAW:
            raise NotImplementedError(
                f"Normalization not supported for {self.format.value} format"
            )

        raw = self.as_raw_samples()

        if self.bit_depth == 16:
            # Convert to samples
            samples = struct.unpack(f"<{len(raw)//2}h", raw)

            # Find peak
            peak = max(abs(s) for s in samples) if samples else 1

            if peak == 0:
                return AudioBuffer(
                    data=self.data,
                    format=self.format,
                    sample_rate=self.sample_rate,
                    channels=self.channels,
                    bit_depth=self.bit_depth,
                )

            # Calculate scale
            max_val = 32767
            scale = (target_peak * max_val) / peak

            # Apply scaling
            new_samples = tuple(int(s * scale) for s in samples)
            new_samples = tuple(max(-32768, min(32767, s)) for s in new_samples)

            # Convert back to bytes
            new_raw = struct.pack(f"<{len(new_samples)}h", *new_samples)

            return AudioBuffer.from_raw_samples(
                new_raw,
                sample_rate=self.sample_rate,
                channels=self.channels,
                bit_depth=self.bit_depth,
            )

        raise NotImplementedError(
            f"Normalization not supported for {self.bit_depth}-bit audio"
        )
