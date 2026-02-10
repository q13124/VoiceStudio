"""
Domain Layer - Core Business Logic.

Task 3.1: Domain-Driven Design implementation.
Contains entities, value objects, domain services, and events.
"""

from backend.domain.entities.base import Entity, AggregateRoot
from backend.domain.value_objects.base import ValueObject
from backend.domain.events.base import DomainEvent, EventBus
from backend.domain.services.base import DomainService

__all__ = [
    "Entity", "AggregateRoot",
    "ValueObject",
    "DomainEvent", "EventBus",
    "DomainService",
]
