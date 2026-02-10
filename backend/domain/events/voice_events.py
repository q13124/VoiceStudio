"""
Voice Profile Domain Events.

Task 3.1.3: Events for voice cloning and profiles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from backend.domain.events.base import DomainEvent


@dataclass
class VoiceProfileCreated(DomainEvent):
    """Event raised when a voice profile is created."""
    
    profile_id: str = ""
    name: str = ""
    voice_type: str = "cloned"
    language: str = "en"
    
    def __post_init__(self):
        self.aggregate_id = self.profile_id
    
    def _get_payload(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
            "voice_type": self.voice_type,
            "language": self.language,
        }


@dataclass
class VoiceTrainingStarted(DomainEvent):
    """Event raised when voice training begins."""
    
    profile_id: str = ""
    engine_id: str = ""
    sample_count: int = 0
    total_duration_seconds: float = 0.0
    
    def __post_init__(self):
        self.aggregate_id = self.profile_id
    
    def _get_payload(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "engine_id": self.engine_id,
            "sample_count": self.sample_count,
            "total_duration_seconds": self.total_duration_seconds,
        }


@dataclass
class VoiceTrainingCompleted(DomainEvent):
    """Event raised when voice training completes."""
    
    profile_id: str = ""
    model_path: str = ""
    quality_score: float = 0.0
    similarity_score: float = 0.0
    training_duration_seconds: float = 0.0
    
    def __post_init__(self):
        self.aggregate_id = self.profile_id
    
    def _get_payload(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "model_path": self.model_path,
            "quality_score": self.quality_score,
            "similarity_score": self.similarity_score,
            "training_duration_seconds": self.training_duration_seconds,
        }


@dataclass
class VoiceTrainingFailed(DomainEvent):
    """Event raised when voice training fails."""
    
    profile_id: str = ""
    error_message: str = ""
    error_type: str = ""
    
    def __post_init__(self):
        self.aggregate_id = self.profile_id
    
    def _get_payload(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "error_message": self.error_message,
            "error_type": self.error_type,
        }


@dataclass
class VoiceProfileDeleted(DomainEvent):
    """Event raised when a voice profile is deleted."""
    
    profile_id: str = ""
    name: str = ""
    
    def __post_init__(self):
        self.aggregate_id = self.profile_id
    
    def _get_payload(self) -> Dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "name": self.name,
        }
