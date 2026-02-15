"""
Audio Domain Events.

Task 3.1.3: Events for audio processing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.domain.events.base import DomainEvent


@dataclass
class AudioClipCreated(DomainEvent):
    """Event raised when an audio clip is created."""

    clip_id: str = ""
    project_id: str | None = None
    name: str = ""
    source: str = ""  # "import", "record", "synthesis"

    def __post_init__(self):
        self.aggregate_id = self.clip_id

    def _get_payload(self) -> dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "project_id": self.project_id,
            "name": self.name,
            "source": self.source,
        }


@dataclass
class AudioClipProcessed(DomainEvent):
    """Event raised when audio processing completes."""

    clip_id: str = ""
    project_id: str | None = None
    duration_seconds: float = 0.0
    file_path: str = ""
    engine_id: str | None = None

    def __post_init__(self):
        self.aggregate_id = self.clip_id

    def _get_payload(self) -> dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "project_id": self.project_id,
            "duration_seconds": self.duration_seconds,
            "file_path": self.file_path,
            "engine_id": self.engine_id,
        }


@dataclass
class AudioClipFailed(DomainEvent):
    """Event raised when audio processing fails."""

    clip_id: str = ""
    project_id: str | None = None
    error_message: str = ""
    error_type: str = ""

    def __post_init__(self):
        self.aggregate_id = self.clip_id

    def _get_payload(self) -> dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "project_id": self.project_id,
            "error_message": self.error_message,
            "error_type": self.error_type,
        }


@dataclass
class AudioExportCompleted(DomainEvent):
    """Event raised when audio export completes."""

    project_id: str = ""
    output_path: str = ""
    format: str = ""
    duration_seconds: float = 0.0
    file_size_bytes: int = 0

    def __post_init__(self):
        self.aggregate_id = self.project_id

    def _get_payload(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "output_path": self.output_path,
            "format": self.format,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
        }
