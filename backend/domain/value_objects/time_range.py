"""
Time Range Value Object.

Task 3.1.2: Value object for time intervals.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.domain.value_objects.base import ValueObject


@dataclass(frozen=True)
class TimeRange(ValueObject):
    """
    Time range value object.

    Represents a time interval in seconds.
    """

    start: float = 0.0
    end: float = 0.0

    def _validate(self) -> None:
        """Validate time range."""
        if self.start < 0:
            raise ValueError(f"Start time cannot be negative: {self.start}")

        if self.end < 0:
            raise ValueError(f"End time cannot be negative: {self.end}")

        if self.end < self.start:
            raise ValueError(f"End time must be >= start time: {self.start} - {self.end}")

    @property
    def duration(self) -> float:
        """Get duration in seconds."""
        return self.end - self.start

    @property
    def is_empty(self) -> bool:
        """Check if range is empty (zero duration)."""
        return self.duration == 0

    def contains(self, time: float) -> bool:
        """Check if a time point is within this range."""
        return self.start <= time <= self.end

    def overlaps(self, other: TimeRange) -> bool:
        """Check if this range overlaps with another."""
        return not (self.end <= other.start or self.start >= other.end)

    def intersection(self, other: TimeRange) -> TimeRange:
        """Get the intersection with another range."""
        if not self.overlaps(other):
            return TimeRange(0, 0)

        return TimeRange(
            start=max(self.start, other.start),
            end=min(self.end, other.end),
        )

    def union(self, other: TimeRange) -> TimeRange:
        """Get the union with another range."""
        return TimeRange(
            start=min(self.start, other.start),
            end=max(self.end, other.end),
        )

    def shift(self, offset: float) -> TimeRange:
        """Create a new range shifted by offset."""
        return TimeRange(
            start=max(0, self.start + offset),
            end=max(0, self.end + offset),
        )

    def scale(self, factor: float) -> TimeRange:
        """Create a new range with duration scaled."""
        if factor <= 0:
            raise ValueError(f"Scale factor must be positive: {factor}")

        return TimeRange(
            start=self.start,
            end=self.start + (self.duration * factor),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "start": self.start,
            "end": self.end,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TimeRange:
        """Create from dictionary."""
        return cls(
            start=data.get("start", 0.0),
            end=data.get("end", 0.0),
        )

    @classmethod
    def from_duration(cls, start: float, duration: float) -> TimeRange:
        """Create from start and duration."""
        return cls(start=start, end=start + duration)

    def __str__(self) -> str:
        return f"{self.start:.2f}s - {self.end:.2f}s ({self.duration:.2f}s)"
