"""
Audio Settings Value Object.

Task 3.1.2: Value object for audio configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class AudioSettings(ValueObject):
    """
    Audio settings configuration.

    Immutable settings for audio processing and output.
    """

    # Sample rate in Hz
    sample_rate: int = 22050

    # Bit depth
    bit_depth: int = 16

    # Number of channels (1=mono, 2=stereo)
    channels: int = 1

    # Output format
    format: str = "wav"

    # Normalization
    normalize: bool = True
    target_db: float = -3.0

    # Silence removal
    remove_silence: bool = False
    silence_threshold_db: float = -40.0
    min_silence_duration: float = 0.1

    # Speed/pitch adjustment
    speed: float = 1.0
    pitch: float = 0.0

    # Effects
    add_reverb: bool = False
    reverb_room_size: float = 0.5

    def _validate(self) -> None:
        """Validate audio settings."""
        if self.sample_rate not in (8000, 16000, 22050, 24000, 44100, 48000):
            raise ValueError(f"Invalid sample rate: {self.sample_rate}")

        if self.bit_depth not in (8, 16, 24, 32):
            raise ValueError(f"Invalid bit depth: {self.bit_depth}")

        if self.channels not in (1, 2):
            raise ValueError(f"Invalid channels: {self.channels}")

        if self.format not in ("wav", "mp3", "ogg", "flac"):
            raise ValueError(f"Invalid format: {self.format}")

        if self.speed < 0.25 or self.speed > 4.0:
            raise ValueError(f"Speed must be 0.25-4.0: {self.speed}")

        if self.pitch < -12.0 or self.pitch > 12.0:
            raise ValueError(f"Pitch must be -12 to +12: {self.pitch}")

    def with_sample_rate(self, sample_rate: int) -> AudioSettings:
        """Create new settings with different sample rate."""
        return AudioSettings(
            sample_rate=sample_rate,
            bit_depth=self.bit_depth,
            channels=self.channels,
            format=self.format,
            normalize=self.normalize,
            target_db=self.target_db,
            remove_silence=self.remove_silence,
            silence_threshold_db=self.silence_threshold_db,
            min_silence_duration=self.min_silence_duration,
            speed=self.speed,
            pitch=self.pitch,
            add_reverb=self.add_reverb,
            reverb_room_size=self.reverb_room_size,
        )

    def with_format(self, format: str) -> AudioSettings:
        """Create new settings with different format."""
        return AudioSettings(
            sample_rate=self.sample_rate,
            bit_depth=self.bit_depth,
            channels=self.channels,
            format=format,
            normalize=self.normalize,
            target_db=self.target_db,
            remove_silence=self.remove_silence,
            silence_threshold_db=self.silence_threshold_db,
            min_silence_duration=self.min_silence_duration,
            speed=self.speed,
            pitch=self.pitch,
            add_reverb=self.add_reverb,
            reverb_room_size=self.reverb_room_size,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sample_rate": self.sample_rate,
            "bit_depth": self.bit_depth,
            "channels": self.channels,
            "format": self.format,
            "normalize": self.normalize,
            "target_db": self.target_db,
            "remove_silence": self.remove_silence,
            "silence_threshold_db": self.silence_threshold_db,
            "min_silence_duration": self.min_silence_duration,
            "speed": self.speed,
            "pitch": self.pitch,
            "add_reverb": self.add_reverb,
            "reverb_room_size": self.reverb_room_size,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AudioSettings:
        """Create from dictionary."""
        return cls(
            sample_rate=data.get("sample_rate", 22050),
            bit_depth=data.get("bit_depth", 16),
            channels=data.get("channels", 1),
            format=data.get("format", "wav"),
            normalize=data.get("normalize", True),
            target_db=data.get("target_db", -3.0),
            remove_silence=data.get("remove_silence", False),
            silence_threshold_db=data.get("silence_threshold_db", -40.0),
            min_silence_duration=data.get("min_silence_duration", 0.1),
            speed=data.get("speed", 1.0),
            pitch=data.get("pitch", 0.0),
            add_reverb=data.get("add_reverb", False),
            reverb_room_size=data.get("reverb_room_size", 0.5),
        )
