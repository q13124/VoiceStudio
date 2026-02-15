"""
Command Pattern Base Classes.

Task 3.2.1: CQRS command pattern implementation.
"""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class Command(ABC):
    """
    Base class for commands.

    Commands represent an intent to change system state.
    They are named as verbs (CreateProject, UpdateSettings).
    """

    # Unique command ID for tracking
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # When the command was issued
    timestamp: datetime = field(default_factory=datetime.now)

    # Optional correlation ID for request tracing
    correlation_id: str | None = None

    # User who issued the command
    user_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "command_type": self.__class__.__name__,
            "command_id": self.command_id,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
        }


@dataclass
class CommandResult(Generic[T]):
    """
    Result of a command execution.

    Wraps the result or error from command handling.
    """

    success: bool
    data: T | None = None
    error_message: str | None = None
    error_code: str | None = None

    @classmethod
    def ok(cls, data: T = None) -> CommandResult[T]:
        """Create a successful result."""
        return cls(success=True, data=data)

    @classmethod
    def fail(
        cls,
        message: str,
        code: str | None = None,
    ) -> CommandResult[T]:
        """Create a failed result."""
        return cls(
            success=False,
            error_message=message,
            error_code=code,
        )


class CommandHandler(ABC, Generic[T]):
    """
    Base class for command handlers.

    Handlers process commands and return results.
    Each command type has exactly one handler.
    """

    @abstractmethod
    async def handle(self, command: Command) -> CommandResult[T]:
        """
        Handle the command.

        Args:
            command: The command to handle

        Returns:
            CommandResult with success/failure and optional data
        """
        pass

    @property
    @abstractmethod
    def command_type(self) -> type:
        """Return the type of command this handler processes."""
        pass
