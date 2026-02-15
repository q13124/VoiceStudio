"""
Base Entity and Aggregate Root.

Task 3.1.1: Rich domain model with entity identity.
"""

from __future__ import annotations

import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from backend.domain.events.base import DomainEvent


@dataclass
class Entity(ABC):
    """
    Base entity with identity.

    Entities have a unique identity that persists through time
    and state changes. Two entities with the same ID are equal.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()


@dataclass
class AggregateRoot(Entity):
    """
    Aggregate root - the entry point for a cluster of entities.

    Aggregates encapsulate domain invariants and emit domain events.
    External code should only reference the aggregate root, not
    internal entities.
    """

    _domain_events: list[DomainEvent] = field(
        default_factory=list,
        repr=False,
        compare=False,
    )
    version: int = field(default=0)

    def add_domain_event(self, event: DomainEvent) -> None:
        """
        Record a domain event to be published.

        Events are collected and published after the aggregate
        is successfully persisted.
        """
        self._domain_events.append(event)

    def clear_domain_events(self) -> list[DomainEvent]:
        """
        Clear and return pending domain events.

        Called by the repository after successful persistence.
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events

    def increment_version(self) -> None:
        """Increment version for optimistic concurrency."""
        self.version += 1
        self.touch()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for persistence."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AggregateRoot:
        """Create from dictionary."""
        raise NotImplementedError("Subclasses must implement from_dict")
