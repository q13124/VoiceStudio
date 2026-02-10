"""
Phase 8: Application Performance Monitoring
Task 8.1: APM for tracking application performance.
"""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
import logging
import statistics
import functools

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of operations to monitor."""
    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"
    SYNTHESIS = "synthesis"
    ENGINE_CALL = "engine_call"
    FILE_IO = "file_io"
    EXTERNAL_API = "external_api"
    CUSTOM = "custom"


@dataclass
class OperationSpan:
    """A span representing an operation."""
    operation_id: str
    operation_type: OperationType
    name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    parent_id: Optional[str] = None
    tags: dict[str, str] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    status: str = "ok"
    error: Optional[str] = None


@dataclass
class PerformanceStats:
    """Performance statistics for an operation type."""
    operation_type: str
    count: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float('inf')
    max_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    error_count: int = 0
    error_rate: float = 0.0


class PerformanceMonitor:
    """Monitor for tracking application performance."""
    
    def __init__(
        self,
        sample_rate: float = 1.0,
        max_spans: int = 10000,
        retention_hours: int = 24
    ):
        self._sample_rate = sample_rate
        self._max_spans = max_spans
        self._retention_hours = retention_hours
        
        self._spans: list[OperationSpan] = []
        self._durations: dict[str, list[float]] = defaultdict(list)
        self._error_counts: dict[str, int] = defaultdict(int)
        self._active_spans: dict[str, OperationSpan] = {}
        
        self._enabled = True
    
    @property
    def enabled(self) -> bool:
        """Check if monitoring is enabled."""
        return self._enabled
    
    def enable(self) -> None:
        """Enable performance monitoring."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable performance monitoring."""
        self._enabled = False
    
    def start_span(
        self,
        name: str,
        operation_type: OperationType,
        parent_id: Optional[str] = None,
        tags: Optional[dict[str, str]] = None
    ) -> OperationSpan:
        """Start a new operation span."""
        import uuid
        
        span = OperationSpan(
            operation_id=str(uuid.uuid4()),
            operation_type=operation_type,
            name=name,
            start_time=datetime.now(),
            parent_id=parent_id,
            tags=tags or {},
        )
        
        if self._enabled:
            self._active_spans[span.operation_id] = span
        
        return span
    
    def end_span(
        self,
        span: OperationSpan,
        status: str = "ok",
        error: Optional[str] = None
    ) -> None:
        """End an operation span."""
        span.end_time = datetime.now()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        span.status = status
        span.error = error
        
        if not self._enabled:
            return
        
        # Remove from active spans
        if span.operation_id in self._active_spans:
            del self._active_spans[span.operation_id]
        
        # Record span
        self._record_span(span)
    
    def _record_span(self, span: OperationSpan) -> None:
        """Record a completed span."""
        key = f"{span.operation_type.value}:{span.name}"
        
        # Store duration
        self._durations[key].append(span.duration_ms)
        
        # Limit duration history
        if len(self._durations[key]) > 1000:
            self._durations[key] = self._durations[key][-1000:]
        
        # Track errors
        if span.error:
            self._error_counts[key] += 1
        
        # Store span
        self._spans.append(span)
        
        # Trim old spans
        if len(self._spans) > self._max_spans:
            self._spans = self._spans[-self._max_spans:]
    
    def track_operation(
        self,
        name: str,
        operation_type: OperationType = OperationType.CUSTOM
    ):
        """Decorator to track operation performance."""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                span = self.start_span(name, operation_type)
                try:
                    result = await func(*args, **kwargs)
                    self.end_span(span)
                    return result
                except Exception as e:
                    self.end_span(span, status="error", error=str(e))
                    raise
            
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                span = self.start_span(name, operation_type)
                try:
                    result = func(*args, **kwargs)
                    self.end_span(span)
                    return result
                except Exception as e:
                    self.end_span(span, status="error", error=str(e))
                    raise
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        
        return decorator
    
    def get_stats(
        self,
        operation_type: Optional[str] = None,
        name: Optional[str] = None
    ) -> list[PerformanceStats]:
        """Get performance statistics."""
        stats = []
        
        for key, durations in self._durations.items():
            if not durations:
                continue
            
            if operation_type and not key.startswith(operation_type):
                continue
            
            if name and name not in key:
                continue
            
            sorted_durations = sorted(durations)
            count = len(sorted_durations)
            
            error_count = self._error_counts.get(key, 0)
            
            stats.append(PerformanceStats(
                operation_type=key,
                count=count,
                total_duration_ms=sum(sorted_durations),
                min_duration_ms=min(sorted_durations),
                max_duration_ms=max(sorted_durations),
                avg_duration_ms=statistics.mean(sorted_durations),
                p50_ms=self._percentile(sorted_durations, 50),
                p95_ms=self._percentile(sorted_durations, 95),
                p99_ms=self._percentile(sorted_durations, 99),
                error_count=error_count,
                error_rate=error_count / count if count > 0 else 0,
            ))
        
        return stats
    
    def get_recent_spans(
        self,
        count: int = 100,
        operation_type: Optional[OperationType] = None,
        status: Optional[str] = None
    ) -> list[OperationSpan]:
        """Get recent operation spans."""
        spans = self._spans
        
        if operation_type:
            spans = [s for s in spans if s.operation_type == operation_type]
        
        if status:
            spans = [s for s in spans if s.status == status]
        
        return spans[-count:]
    
    def get_slow_operations(
        self,
        threshold_ms: float = 1000,
        count: int = 20
    ) -> list[OperationSpan]:
        """Get slow operations above threshold."""
        slow = [s for s in self._spans if s.duration_ms > threshold_ms]
        slow.sort(key=lambda s: s.duration_ms, reverse=True)
        return slow[:count]
    
    def get_error_operations(self, count: int = 20) -> list[OperationSpan]:
        """Get operations that resulted in errors."""
        errors = [s for s in self._spans if s.error]
        return errors[-count:]
    
    def clear(self) -> None:
        """Clear all recorded data."""
        self._spans.clear()
        self._durations.clear()
        self._error_counts.clear()
        self._active_spans.clear()
    
    def _percentile(self, sorted_data: list[float], percentile: int) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0.0
        
        k = (len(sorted_data) - 1) * percentile / 100
        f = int(k)
        c = f + 1
        
        if c >= len(sorted_data):
            return sorted_data[-1]
        
        return sorted_data[f] + (k - f) * (sorted_data[c] - sorted_data[f])


# Global monitor instance
_monitor: Optional[PerformanceMonitor] = None


def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    global _monitor
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor


def track(name: str, operation_type: OperationType = OperationType.CUSTOM):
    """Decorator shortcut for tracking operations."""
    return get_monitor().track_operation(name, operation_type)
