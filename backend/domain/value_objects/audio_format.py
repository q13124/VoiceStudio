"""
Audio Format Value Object.

Task 3.1.2: Value object for audio format specification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from backend.domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class AudioFormat(ValueObject):
    """
    Audio format specification.
    
    Describes the technical format of an audio file.
    """
    
    # File format
    container: str = "wav"  # wav, mp3, ogg, flac
    
    # Audio codec
    codec: str = "pcm"  # pcm, mp3, vorbis, flac
    
    # Sample rate in Hz
    sample_rate: int = 22050
    
    # Bit depth (for PCM) or bitrate (for compressed)
    bit_depth: int = 16
    bitrate_kbps: int = 0  # 0 for uncompressed
    
    # Channels
    channels: int = 1
    
    # MIME type
    mime_type: str = "audio/wav"
    
    def _validate(self) -> None:
        """Validate audio format."""
        valid_containers = {"wav", "mp3", "ogg", "flac", "m4a", "webm"}
        if self.container not in valid_containers:
            raise ValueError(f"Invalid container: {self.container}")
        
        valid_codecs = {"pcm", "mp3", "vorbis", "flac", "aac", "opus"}
        if self.codec not in valid_codecs:
            raise ValueError(f"Invalid codec: {self.codec}")
        
        if self.sample_rate <= 0:
            raise ValueError(f"Invalid sample rate: {self.sample_rate}")
        
        if self.channels < 1 or self.channels > 8:
            raise ValueError(f"Invalid channels: {self.channels}")
    
    @property
    def is_compressed(self) -> bool:
        """Check if format uses compression."""
        return self.codec not in ("pcm",)
    
    @property
    def is_lossless(self) -> bool:
        """Check if format is lossless."""
        return self.codec in ("pcm", "flac")
    
    @property
    def file_extension(self) -> str:
        """Get file extension."""
        return f".{self.container}"
    
    def bytes_per_second(self) -> int:
        """Calculate bytes per second (for uncompressed)."""
        if self.is_compressed:
            return (self.bitrate_kbps * 1000) // 8
        
        bytes_per_sample = self.bit_depth // 8
        return self.sample_rate * self.channels * bytes_per_sample
    
    def estimate_file_size(self, duration_seconds: float) -> int:
        """Estimate file size in bytes."""
        return int(self.bytes_per_second() * duration_seconds)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "container": self.container,
            "codec": self.codec,
            "sample_rate": self.sample_rate,
            "bit_depth": self.bit_depth,
            "bitrate_kbps": self.bitrate_kbps,
            "channels": self.channels,
            "mime_type": self.mime_type,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AudioFormat":
        """Create from dictionary."""
        return cls(
            container=data.get("container", "wav"),
            codec=data.get("codec", "pcm"),
            sample_rate=data.get("sample_rate", 22050),
            bit_depth=data.get("bit_depth", 16),
            bitrate_kbps=data.get("bitrate_kbps", 0),
            channels=data.get("channels", 1),
            mime_type=data.get("mime_type", "audio/wav"),
        )
    
    # Common format presets
    
    @classmethod
    def wav_mono_22k(cls) -> "AudioFormat":
        """Standard WAV format for TTS."""
        return cls(
            container="wav",
            codec="pcm",
            sample_rate=22050,
            bit_depth=16,
            channels=1,
            mime_type="audio/wav",
        )
    
    @classmethod
    def wav_stereo_44k(cls) -> "AudioFormat":
        """CD quality WAV."""
        return cls(
            container="wav",
            codec="pcm",
            sample_rate=44100,
            bit_depth=16,
            channels=2,
            mime_type="audio/wav",
        )
    
    @classmethod
    def mp3_128k(cls) -> "AudioFormat":
        """Standard MP3."""
        return cls(
            container="mp3",
            codec="mp3",
            sample_rate=44100,
            bit_depth=0,
            bitrate_kbps=128,
            channels=2,
            mime_type="audio/mpeg",
        )
    
    @classmethod
    def mp3_320k(cls) -> "AudioFormat":
        """High quality MP3."""
        return cls(
            container="mp3",
            codec="mp3",
            sample_rate=44100,
            bit_depth=0,
            bitrate_kbps=320,
            channels=2,
            mime_type="audio/mpeg",
        )
    
    @classmethod
    def flac_lossless(cls) -> "AudioFormat":
        """Lossless FLAC."""
        return cls(
            container="flac",
            codec="flac",
            sample_rate=44100,
            bit_depth=24,
            channels=2,
            mime_type="audio/flac",
        )
