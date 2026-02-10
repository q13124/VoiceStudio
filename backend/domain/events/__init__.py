"""Domain events package."""

from backend.domain.events.base import DomainEvent, EventBus, EventHandler
from backend.domain.events.project_events import (
    ProjectCreated,
    ProjectUpdated,
    ProjectDeleted,
    ProjectStatusChanged,
)
from backend.domain.events.audio_events import (
    AudioClipCreated,
    AudioClipProcessed,
    AudioClipFailed,
)
from backend.domain.events.voice_events import (
    VoiceProfileCreated,
    VoiceTrainingStarted,
    VoiceTrainingCompleted,
)

__all__ = [
    "DomainEvent", "EventBus", "EventHandler",
    "ProjectCreated", "ProjectUpdated", "ProjectDeleted", "ProjectStatusChanged",
    "AudioClipCreated", "AudioClipProcessed", "AudioClipFailed",
    "VoiceProfileCreated", "VoiceTrainingStarted", "VoiceTrainingCompleted",
]
