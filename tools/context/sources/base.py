from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from tools.context.core.models import AllocationContext, SourceResult
from tools.context.core.protocols import ContextSourceProtocol

logger = logging.getLogger(__name__)


def _estimate_size(data: Any) -> int:
    try:
        return len(json.dumps(data, ensure_ascii=False, default=str))
    except Exception:
        return len(str(data))


@dataclass
class SourceHealthStatus:
    """Health status for a context source."""

    source_name: str
    is_healthy: bool
    last_check: datetime = field(default_factory=datetime.now)
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    consecutive_failures: int = 0
    avg_fetch_time_ms: float = 0.0
    total_fetches: int = 0
    total_failures: int = 0
    last_error: Optional[str] = None

    def record_success(self, fetch_time_ms: float) -> None:
        """Record a successful fetch."""
        self.is_healthy = True
        self.last_check = datetime.now()
        self.last_success = datetime.now()
        self.consecutive_failures = 0
        self.total_fetches += 1
        # Update rolling average
        if self.total_fetches == 1:
            self.avg_fetch_time_ms = fetch_time_ms
        else:
            self.avg_fetch_time_ms = (
                self.avg_fetch_time_ms * (self.total_fetches - 1) + fetch_time_ms
            ) / self.total_fetches

    def record_failure(self, error: str) -> None:
        """Record a failed fetch."""
        self.last_check = datetime.now()
        self.last_failure = datetime.now()
        self.consecutive_failures += 1
        self.total_fetches += 1
        self.total_failures += 1
        self.last_error = error
        # Mark unhealthy after 3 consecutive failures
        if self.consecutive_failures >= 3:
            self.is_healthy = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_name": self.source_name,
            "is_healthy": self.is_healthy,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "consecutive_failures": self.consecutive_failures,
            "avg_fetch_time_ms": round(self.avg_fetch_time_ms, 2),
            "total_fetches": self.total_fetches,
            "total_failures": self.total_failures,
            "failure_rate": round(self.total_failures / max(1, self.total_fetches) * 100, 1),
            "last_error": self.last_error,
        }


@dataclass
class SourceTelemetry:
    """Telemetry data for all source adapters."""

    sources: Dict[str, SourceHealthStatus] = field(default_factory=dict)
    collection_started: datetime = field(default_factory=datetime.now)

    def get_or_create(self, source_name: str) -> SourceHealthStatus:
        """Get or create health status for a source."""
        if source_name not in self.sources:
            self.sources[source_name] = SourceHealthStatus(
                source_name=source_name,
                is_healthy=True,
            )
        return self.sources[source_name]

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all source health."""
        total = len(self.sources)
        healthy = sum(1 for s in self.sources.values() if s.is_healthy)
        unhealthy = [s.source_name for s in self.sources.values() if not s.is_healthy]
        return {
            "total_sources": total,
            "healthy_sources": healthy,
            "unhealthy_sources": unhealthy,
            "collection_started": self.collection_started.isoformat(),
            "sources": {name: status.to_dict() for name, status in self.sources.items()},
        }


# Global telemetry instance (singleton)
_global_telemetry = SourceTelemetry()


def get_source_telemetry() -> SourceTelemetry:
    """Get the global source telemetry instance."""
    return _global_telemetry


def reset_source_telemetry() -> None:
    """Reset global telemetry (for testing)."""
    global _global_telemetry
    _global_telemetry = SourceTelemetry()


class BaseSourceAdapter(ContextSourceProtocol):
    """Base class for context source adapters with timing/error handling and health checks."""

    def __init__(self, source_name: str, priority: int = 0, offline: bool = True):
        self.source_name = source_name
        self.priority = priority
        self.offline = offline
        self._offline = offline
        self._health = get_source_telemetry().get_or_create(source_name)

    @property
    def health_status(self) -> SourceHealthStatus:
        """Get health status for this source."""
        return self._health

    def health_check(self) -> bool:
        """
        Perform a health check on this source.

        Override in subclasses for source-specific health checks.
        Default implementation returns True if no recent failures.
        """
        return self._health.is_healthy

    def _measure(self, loader: Callable[[], Dict[str, Any]], context: AllocationContext) -> SourceResult:
        start = time.perf_counter()
        try:
            data = loader() or {}
            size = _estimate_size(data)
            fetch_time_ms = (time.perf_counter() - start) * 1000.0

            # Record success in telemetry
            self._health.record_success(fetch_time_ms)

            return SourceResult(
                source_name=self.source_name,
                success=True,
                data=data,
                size_chars=size,
                fetch_time_ms=fetch_time_ms,
                error=None,
            )
        except Exception as exc:
            fetch_time_ms = (time.perf_counter() - start) * 1000.0
            error_msg = str(exc)

            # Record failure in telemetry
            self._health.record_failure(error_msg)

            logger.warning(
                "Source %s fetch failed: %s (consecutive failures: %d)",
                self.source_name,
                error_msg,
                self._health.consecutive_failures,
            )

            return SourceResult(
                source_name=self.source_name,
                success=False,
                data={},
                size_chars=0,
                fetch_time_ms=fetch_time_ms,
                error=error_msg,
            )

    def estimate_size(self, context: AllocationContext) -> int:
        return 0
