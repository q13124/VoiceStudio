"""
Audio Clip Entity.

Task 3.1.1: Domain entity for audio clips.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from backend.domain.entities.base import AggregateRoot


class ClipStatus(Enum):
    """Audio clip processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class ClipType(Enum):
    """Type of audio clip."""
    ORIGINAL = "original"     # Original recorded/imported audio
    SYNTHESIZED = "synthesized"  # Generated via TTS
    CLONED = "cloned"         # Generated via voice cloning
    PROCESSED = "processed"   # Post-processed audio


@dataclass
class AudioClip(AggregateRoot):
    """
    Audio clip aggregate.

    Represents a segment of audio in a project.
    """

    name: str = ""
    description: str = ""

    # Audio properties
    file_path: str | None = None
    duration_seconds: float = 0.0
    sample_rate: int = 22050
    channels: int = 1
    bit_depth: int = 16
    file_size_bytes: int = 0

    # Content
    transcript: str = ""
    language: str = "en"

    # Processing state
    status: ClipStatus = field(default=ClipStatus.PENDING)
    clip_type: ClipType = field(default=ClipType.ORIGINAL)
    error_message: str | None = None

    # References
    project_id: str | None = None
    voice_profile_id: str | None = None
    source_clip_id: str | None = None  # For processed clips

    # Timeline position
    start_time: float = 0.0
    end_time: float = 0.0
    track_index: int = 0

    # Metadata
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Domain methods

    def rename(self, new_name: str) -> None:
        """Rename the audio clip."""
        if not new_name.strip():
            raise ValueError("Audio clip name cannot be empty")

        self.name = new_name.strip()
        self.touch()

    def set_transcript(self, transcript: str) -> None:
        """Set the transcript text."""
        self.transcript = transcript
        self.touch()

    def start_processing(self) -> None:
        """Mark clip as processing."""
        self.status = ClipStatus.PROCESSING
        self.error_message = None
        self.touch()

    def complete_processing(
        self,
        file_path: str,
        duration_seconds: float,
        sample_rate: int = 22050,
        channels: int = 1,
        bit_depth: int = 16,
        file_size_bytes: int = 0,
    ) -> None:
        """Mark processing as complete with audio details."""
        self.status = ClipStatus.READY
        self.file_path = file_path
        self.duration_seconds = duration_seconds
        self.sample_rate = sample_rate
        self.channels = channels
        self.bit_depth = bit_depth
        self.file_size_bytes = file_size_bytes
        self.end_time = self.start_time + duration_seconds
        self.touch()

    def fail_processing(self, error_message: str) -> None:
        """Mark processing as failed."""
        self.status = ClipStatus.FAILED
        self.error_message = error_message
        self.touch()

    def set_timeline_position(
        self,
        start_time: float,
        track_index: int = 0,
    ) -> None:
        """Set position on timeline."""
        self.start_time = start_time
        self.end_time = start_time + self.duration_seconds
        self.track_index = track_index
        self.touch()

    def move_to_track(self, track_index: int) -> None:
        """Move to a different track."""
        self.track_index = track_index
        self.touch()

    def is_ready(self) -> bool:
        """Check if clip is ready for playback."""
        return self.status == ClipStatus.READY and self.file_path is not None

    def overlaps_with(self, other: AudioClip) -> bool:
        """Check if this clip overlaps with another on the same track."""
        if self.track_index != other.track_index:
            return False

        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)

    # Persistence

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for persistence."""
        base = super().to_dict()
        base.update({
            "name": self.name,
            "description": self.description,
            "file_path": self.file_path,
            "duration_seconds": self.duration_seconds,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bit_depth": self.bit_depth,
            "file_size_bytes": self.file_size_bytes,
            "transcript": self.transcript,
            "language": self.language,
            "status": self.status.value,
            "clip_type": self.clip_type.value,
            "error_message": self.error_message,
            "project_id": self.project_id,
            "voice_profile_id": self.voice_profile_id,
            "source_clip_id": self.source_clip_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "track_index": self.track_index,
            "tags": self.tags,
            "metadata": self.metadata,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AudioClip:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=data.get("version", 0),
            name=data["name"],
            description=data.get("description", ""),
            file_path=data.get("file_path"),
            duration_seconds=data.get("duration_seconds", 0.0),
            sample_rate=data.get("sample_rate", 22050),
            channels=data.get("channels", 1),
            bit_depth=data.get("bit_depth", 16),
            file_size_bytes=data.get("file_size_bytes", 0),
            transcript=data.get("transcript", ""),
            language=data.get("language", "en"),
            status=ClipStatus(data.get("status", "pending")),
            clip_type=ClipType(data.get("clip_type", "original")),
            error_message=data.get("error_message"),
            project_id=data.get("project_id"),
            voice_profile_id=data.get("voice_profile_id"),
            source_clip_id=data.get("source_clip_id"),
            start_time=data.get("start_time", 0.0),
            end_time=data.get("end_time", 0.0),
            track_index=data.get("track_index", 0),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )
