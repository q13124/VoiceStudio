"""
Project Entity.

Task 3.1.1: Core domain entity for VoiceStudio projects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from backend.domain.entities.base import AggregateRoot
from backend.domain.value_objects.audio_settings import AudioSettings


class ProjectStatus(Enum):
    """Project status enumeration."""

    DRAFT = "draft"
    ACTIVE = "active"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Project(AggregateRoot):
    """
    Project aggregate root.

    A project encapsulates all work for a voice synthesis task,
    including audio clips, voice profiles, and settings.
    """

    name: str = ""
    description: str = ""
    status: ProjectStatus = field(default=ProjectStatus.DRAFT)

    # Project paths
    project_path: str | None = None
    output_path: str | None = None

    # Settings
    audio_settings: AudioSettings | None = None

    # References (IDs to related entities)
    voice_profile_ids: list[str] = field(default_factory=list)
    audio_clip_ids: list[str] = field(default_factory=list)

    # Metadata
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default audio settings."""
        if self.audio_settings is None:
            self.audio_settings = AudioSettings()

    # Domain methods

    def rename(self, new_name: str) -> None:
        """Rename the project."""
        if not new_name.strip():
            raise ValueError("Project name cannot be empty")

        self.name = new_name.strip()
        self.touch()

    def activate(self) -> None:
        """Activate the project for editing."""
        if self.status == ProjectStatus.ARCHIVED:
            raise ValueError("Cannot activate archived project")

        self.status = ProjectStatus.ACTIVE
        self.touch()

    def archive(self) -> None:
        """Archive the project."""
        if self.status == ProjectStatus.PROCESSING:
            raise ValueError("Cannot archive while processing")

        self.status = ProjectStatus.ARCHIVED
        self.touch()

    def start_processing(self) -> None:
        """Mark project as processing."""
        self.status = ProjectStatus.PROCESSING
        self.touch()

    def complete_processing(self) -> None:
        """Mark project as completed."""
        self.status = ProjectStatus.COMPLETED
        self.touch()

    def add_voice_profile(self, profile_id: str) -> None:
        """Add a voice profile reference."""
        if profile_id not in self.voice_profile_ids:
            self.voice_profile_ids.append(profile_id)
            self.touch()

    def remove_voice_profile(self, profile_id: str) -> None:
        """Remove a voice profile reference."""
        if profile_id in self.voice_profile_ids:
            self.voice_profile_ids.remove(profile_id)
            self.touch()

    def add_audio_clip(self, clip_id: str) -> None:
        """Add an audio clip reference."""
        if clip_id not in self.audio_clip_ids:
            self.audio_clip_ids.append(clip_id)
            self.touch()

    def remove_audio_clip(self, clip_id: str) -> None:
        """Remove an audio clip reference."""
        if clip_id in self.audio_clip_ids:
            self.audio_clip_ids.remove(clip_id)
            self.touch()

    def add_tag(self, tag: str) -> None:
        """Add a tag."""
        tag = tag.strip().lower()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.touch()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag."""
        tag = tag.strip().lower()
        if tag in self.tags:
            self.tags.remove(tag)
            self.touch()

    def update_settings(self, settings: AudioSettings) -> None:
        """Update audio settings."""
        self.audio_settings = settings
        self.touch()

    # Persistence

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for persistence."""
        base = super().to_dict()
        base.update(
            {
                "name": self.name,
                "description": self.description,
                "status": self.status.value,
                "project_path": self.project_path,
                "output_path": self.output_path,
                "audio_settings": self.audio_settings.to_dict() if self.audio_settings else None,
                "voice_profile_ids": self.voice_profile_ids,
                "audio_clip_ids": self.audio_clip_ids,
                "tags": self.tags,
                "metadata": self.metadata,
            }
        )
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Project:
        """Create from dictionary."""
        settings = None
        if data.get("audio_settings"):
            settings = AudioSettings.from_dict(data["audio_settings"])

        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=data.get("version", 0),
            name=data["name"],
            description=data.get("description", ""),
            status=ProjectStatus(data.get("status", "draft")),
            project_path=data.get("project_path"),
            output_path=data.get("output_path"),
            audio_settings=settings,
            voice_profile_ids=data.get("voice_profile_ids", []),
            audio_clip_ids=data.get("audio_clip_ids", []),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )
