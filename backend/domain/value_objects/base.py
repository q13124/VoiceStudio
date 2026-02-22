"""
Base Value Object.

Task 3.1.2: Immutable value objects for domain modeling.
"""

from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValueObject(ABC):
    """
    Base class for value objects.

    Value objects are immutable and compared by their attributes,
    not by identity. They have no lifecycle and can be freely
    shared and copied.

    Key characteristics:
    - Immutable (frozen dataclass)
    - Equality by value (all attributes)
    - Self-validating
    - Side-effect free methods
    """

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        # Default implementation using dataclass fields
        from dataclasses import fields

        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ValueObject:
        """Create from dictionary."""
        return cls(**data)

    def __post_init__(self):
        """Validate on creation."""
        self._validate()

    def _validate(self) -> None:
        """
        Validate the value object.

        Override in subclasses to add validation logic.
        Raise ValueError if validation fails.
        """
        pass
