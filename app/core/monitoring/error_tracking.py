"""
Error Tracking System

Provides error tracking and aggregation for monitoring and debugging.
"""

from __future__ import annotations

import traceback
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorRecord:
    """Error record data structure."""

    error_type: str
    message: str
    severity: ErrorSeverity
    timestamp: datetime = field(default_factory=datetime.now)
    traceback: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    count: int = 1
    first_occurrence: datetime = field(default_factory=datetime.now)
    last_occurrence: datetime = field(default_factory=datetime.now)


class ErrorTracker:
    """
    Error tracker for monitoring and debugging.
    """

    def __init__(self, max_errors: int = 1000):
        """
        Initialize error tracker.

        Args:
            max_errors: Maximum number of unique errors to track
        """
        self.max_errors = max_errors
        self.errors: dict[str, ErrorRecord] = {}
        self.error_counts: dict[str, int] = defaultdict(int)
        self.lock = Lock()

    def record_error(
        self,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: dict[str, Any] | None = None,
    ):
        """
        Record an error.

        Args:
            error: Exception to record
            severity: Error severity
            context: Optional context information
        """
        error_type = type(error).__name__
        error_key = f"{error_type}:{error!s}"

        with self.lock:
            # Update count
            self.error_counts[error_key] += 1

            # Get or create error record
            if error_key in self.errors:
                record = self.errors[error_key]
                record.count += 1
                record.last_occurrence = datetime.now()
            else:
                # Create new record
                record = ErrorRecord(
                    error_type=error_type,
                    message=str(error),
                    severity=severity,
                    traceback=traceback.format_exc(),
                    context=context or {},
                )
                self.errors[error_key] = record

            # Limit number of errors
            if len(self.errors) > self.max_errors:
                # Remove oldest errors
                sorted_errors = sorted(self.errors.items(), key=lambda x: x[1].last_occurrence)
                for key, _ in sorted_errors[: len(sorted_errors) - self.max_errors]:
                    del self.errors[key]

    def get_error_summary(self) -> dict[str, Any]:
        """
        Get error summary.

        Returns:
            Error summary with counts and recent errors
        """
        with self.lock:
            # Group by severity
            by_severity = defaultdict(int)
            for record in self.errors.values():
                by_severity[record.severity.value] += record.count

            # Get top errors
            top_errors = sorted(self.errors.values(), key=lambda x: x.count, reverse=True)[:10]

            return {
                "total_unique_errors": len(self.errors),
                "total_error_count": sum(self.error_counts.values()),
                "by_severity": dict(by_severity),
                "top_errors": [
                    {
                        "error_type": err.error_type,
                        "message": err.message,
                        "severity": err.severity.value,
                        "count": err.count,
                        "first_occurrence": err.first_occurrence.isoformat(),
                        "last_occurrence": err.last_occurrence.isoformat(),
                    }
                    for err in top_errors
                ],
            }

    def get_errors_by_type(self, error_type: str) -> list[ErrorRecord]:
        """
        Get errors by type.

        Args:
            error_type: Error type name

        Returns:
            List of error records
        """
        with self.lock:
            return [record for record in self.errors.values() if record.error_type == error_type]

    def clear(self):
        """Clear all error records."""
        with self.lock:
            self.errors.clear()
            self.error_counts.clear()


# Global error tracker
_error_tracker: ErrorTracker | None = None
_tracker_lock = Lock()


def get_error_tracker() -> ErrorTracker:
    """
    Get or create global error tracker.

    Returns:
        Error tracker instance
    """
    global _error_tracker
    with _tracker_lock:
        if _error_tracker is None:
            _error_tracker = ErrorTracker()
        return _error_tracker
