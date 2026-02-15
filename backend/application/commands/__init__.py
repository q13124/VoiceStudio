"""Application commands package."""

from backend.application.commands.base import Command, CommandHandler, CommandResult
from backend.application.commands.project_commands import (
    CreateProject,
    DeleteProject,
    UpdateProject,
)
from backend.application.commands.synthesis_commands import (
    ProcessAudioClip,
    SynthesizeSpeech,
)

__all__ = [
    "Command",
    "CommandHandler",
    "CommandResult",
    "CreateProject",
    "DeleteProject",
    "ProcessAudioClip",
    "SynthesizeSpeech",
    "UpdateProject",
]
