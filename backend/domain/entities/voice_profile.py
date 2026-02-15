"""
Voice Profile Entity.

Task 3.1.1: Domain entity for voice profiles/clones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from backend.domain.entities.base import AggregateRoot


class VoiceType(Enum):
    """Type of voice profile."""
    CLONED = "cloned"         # User-created voice clone
    PRESET = "preset"         # Built-in preset voice
    SYNTHESIZED = "synthesized"  # AI-generated voice


class VoiceGender(Enum):
    """Voice gender classification."""
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


@dataclass
class VoiceProfile(AggregateRoot):
    """
    Voice profile aggregate.

    Represents a voice that can be used for synthesis,
    either cloned from audio samples or a preset.
    """

    name: str = ""
    description: str = ""
    voice_type: VoiceType = field(default=VoiceType.CLONED)
    gender: VoiceGender = field(default=VoiceGender.NEUTRAL)

    # Voice characteristics
    language: str = "en"
    accent: str = ""

    # Model references
    model_path: str | None = None
    engine_id: str | None = None

    # Sample audio
    sample_audio_paths: list[str] = field(default_factory=list)
    reference_audio_path: str | None = None

    # Quality metrics
    quality_score: float = 0.0
    similarity_score: float = 0.0

    # Metadata
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Training state
    is_trained: bool = False
    training_started_at: datetime | None = None
    training_completed_at: datetime | None = None

    # Domain methods

    def rename(self, new_name: str) -> None:
        """Rename the voice profile."""
        if not new_name.strip():
            raise ValueError("Voice profile name cannot be empty")

        self.name = new_name.strip()
        self.touch()

    def add_sample(self, audio_path: str) -> None:
        """Add a training sample."""
        if audio_path not in self.sample_audio_paths:
            self.sample_audio_paths.append(audio_path)
            self.touch()

    def remove_sample(self, audio_path: str) -> None:
        """Remove a training sample."""
        if audio_path in self.sample_audio_paths:
            self.sample_audio_paths.remove(audio_path)
            self.touch()

    def set_reference_audio(self, audio_path: str) -> None:
        """Set the reference audio for synthesis."""
        self.reference_audio_path = audio_path
        self.touch()

    def start_training(self) -> None:
        """Mark training as started."""
        self.is_trained = False
        self.training_started_at = datetime.now()
        self.training_completed_at = None
        self.touch()

    def complete_training(
        self,
        model_path: str,
        quality_score: float = 0.0,
        similarity_score: float = 0.0,
    ) -> None:
        """Mark training as complete."""
        self.is_trained = True
        self.training_completed_at = datetime.now()
        self.model_path = model_path
        self.quality_score = quality_score
        self.similarity_score = similarity_score
        self.touch()

    def update_quality_metrics(
        self,
        quality_score: float,
        similarity_score: float,
    ) -> None:
        """Update quality metrics."""
        self.quality_score = quality_score
        self.similarity_score = similarity_score
        self.touch()

    def can_synthesize(self) -> bool:
        """Check if profile can be used for synthesis."""
        if self.voice_type == VoiceType.PRESET:
            return True
        return self.is_trained and self.model_path is not None

    # Persistence

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for persistence."""
        base = super().to_dict()
        base.update({
            "name": self.name,
            "description": self.description,
            "voice_type": self.voice_type.value,
            "gender": self.gender.value,
            "language": self.language,
            "accent": self.accent,
            "model_path": self.model_path,
            "engine_id": self.engine_id,
            "sample_audio_paths": self.sample_audio_paths,
            "reference_audio_path": self.reference_audio_path,
            "quality_score": self.quality_score,
            "similarity_score": self.similarity_score,
            "tags": self.tags,
            "metadata": self.metadata,
            "is_trained": self.is_trained,
            "training_started_at": self.training_started_at.isoformat() if self.training_started_at else None,
            "training_completed_at": self.training_completed_at.isoformat() if self.training_completed_at else None,
        })
        return base

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VoiceProfile:
        """Create from dictionary."""
        training_started = None
        if data.get("training_started_at"):
            training_started = datetime.fromisoformat(data["training_started_at"])

        training_completed = None
        if data.get("training_completed_at"):
            training_completed = datetime.fromisoformat(data["training_completed_at"])

        return cls(
            id=data["id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            version=data.get("version", 0),
            name=data["name"],
            description=data.get("description", ""),
            voice_type=VoiceType(data.get("voice_type", "cloned")),
            gender=VoiceGender(data.get("gender", "neutral")),
            language=data.get("language", "en"),
            accent=data.get("accent", ""),
            model_path=data.get("model_path"),
            engine_id=data.get("engine_id"),
            sample_audio_paths=data.get("sample_audio_paths", []),
            reference_audio_path=data.get("reference_audio_path"),
            quality_score=data.get("quality_score", 0.0),
            similarity_score=data.get("similarity_score", 0.0),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            is_trained=data.get("is_trained", False),
            training_started_at=training_started,
            training_completed_at=training_completed,
        )
