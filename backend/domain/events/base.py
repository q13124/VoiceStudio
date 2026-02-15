"""
Domain Events System.

Task 3.1.3: Event-driven integration between bounded contexts.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from abc import ABC
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DomainEvent(ABC):
    """
    Base class for domain events.

    Domain events represent something that happened in the domain
    that other parts of the system might be interested in.
    """

    # Unique event ID
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # When the event occurred
    occurred_at: datetime = field(default_factory=datetime.now)

    # ID of the aggregate that raised the event
    aggregate_id: str | None = None

    # Event version for schema evolution
    version: int = 1

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def event_type(self) -> str:
        """Get the event type name."""
        return self.__class__.__name__

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "aggregate_id": self.aggregate_id,
            "version": self.version,
            "metadata": self.metadata,
            "payload": self._get_payload(),
        }

    def _get_payload(self) -> dict[str, Any]:
        """Get event-specific payload. Override in subclasses."""
        return {}


# Type alias for event handlers
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus:
    """
    Event bus for publishing and subscribing to domain events.

    Features:
    - Async event handling
    - Multiple handlers per event type
    - Error isolation between handlers
    - Event history for debugging
    """

    def __init__(self, max_history: int = 1000):
        """
        Initialize event bus.

        Args:
            max_history: Maximum events to keep in history
        """
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = {}
        self._global_handlers: list[EventHandler] = []
        self._history: list[DomainEvent] = []
        self._max_history = max_history
        self._lock = asyncio.Lock()

    def subscribe(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: Type of event to handle
            handler: Async handler function
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)
        logger.debug(f"Subscribed handler to {event_type.__name__}")

    def subscribe_all(self, handler: EventHandler) -> None:
        """
        Subscribe to all events.

        Args:
            handler: Async handler function
        """
        self._global_handlers.append(handler)
        logger.debug("Subscribed global handler")

    def unsubscribe(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> bool:
        """
        Unsubscribe from an event type.

        Args:
            event_type: Type of event
            handler: Handler to remove

        Returns:
            True if handler was removed
        """
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                return True
            except ValueError:
                pass  # ALLOWED: bare except - handler not in list, return False below
        return False

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: Event to publish
        """
        # Add to history
        async with self._lock:
            self._history.append(event)
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history:]

        logger.debug(f"Publishing event: {event.event_type}")

        # Get handlers for this event type
        handlers = self._handlers.get(type(event), []).copy()
        handlers.extend(self._global_handlers)

        # Execute handlers concurrently
        if handlers:
            await asyncio.gather(
                *[self._safe_handle(handler, event) for handler in handlers],
                return_exceptions=True,
            )

    async def _safe_handle(
        self,
        handler: EventHandler,
        event: DomainEvent,
    ) -> None:
        """Execute handler with error isolation."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(
                f"Event handler error for {event.event_type}: {e}",
                exc_info=True,
            )

    async def publish_many(self, events: list[DomainEvent]) -> None:
        """
        Publish multiple events.

        Args:
            events: Events to publish
        """
        for event in events:
            await self.publish(event)

    def get_history(
        self,
        event_type: type[DomainEvent] | None = None,
        limit: int = 100,
    ) -> list[DomainEvent]:
        """
        Get event history.

        Args:
            event_type: Filter by event type
            limit: Maximum events to return

        Returns:
            List of events (newest first)
        """
        events = self._history.copy()

        if event_type:
            events = [e for e in events if isinstance(e, event_type)]

        return events[-limit:][::-1]

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()


# Global event bus instance
_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get or create the global event bus."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


async def publish_event(event: DomainEvent) -> None:
    """Convenience function to publish an event."""
    await get_event_bus().publish(event)


def subscribe_to_event(
    event_type: type[DomainEvent],
    handler: EventHandler,
) -> None:
    """Convenience function to subscribe to an event."""
    get_event_bus().subscribe(event_type, handler)
