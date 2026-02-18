"""
Plugin Metrics Collector.

Tracks per-plugin performance and usage metrics.
"""

import logging
import statistics
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics collected."""

    # Execution metrics
    EXECUTION_COUNT = "execution.count"
    EXECUTION_DURATION = "execution.duration_ms"
    EXECUTION_SUCCESS = "execution.success"
    EXECUTION_ERROR = "execution.error"

    # Resource metrics
    MEMORY_USAGE = "resource.memory_bytes"
    CPU_TIME = "resource.cpu_ms"

    # IPC metrics
    IPC_REQUESTS = "ipc.requests"
    IPC_RESPONSES = "ipc.responses"
    IPC_ERRORS = "ipc.errors"
    IPC_LATENCY = "ipc.latency_ms"

    # Permission metrics
    PERMISSION_CHECKS = "permission.checks"
    PERMISSION_GRANTS = "permission.grants"
    PERMISSION_DENIALS = "permission.denials"

    # Lifecycle metrics
    LIFECYCLE_STARTS = "lifecycle.starts"
    LIFECYCLE_STOPS = "lifecycle.stops"
    LIFECYCLE_CRASHES = "lifecycle.crashes"

    # Custom metrics
    CUSTOM_COUNTER = "custom.counter"
    CUSTOM_GAUGE = "custom.gauge"
    CUSTOM_HISTOGRAM = "custom.histogram"


@dataclass
class PluginMetric:
    """Individual metric data point."""

    metric_type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    labels: Dict[str, str] = field(default_factory=dict)
    plugin_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.metric_type.value,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "labels": self.labels,
            "plugin_id": self.plugin_id,
        }


@dataclass
class ExecutionStats:
    """Statistics for a specific method execution."""

    method: str
    call_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    durations: List[float] = field(default_factory=list)

    @property
    def avg_duration_ms(self) -> float:
        """Average duration in milliseconds."""
        if self.call_count == 0:
            return 0.0
        return self.total_duration_ms / self.call_count

    @property
    def p50_duration_ms(self) -> float:
        """50th percentile (median) duration."""
        if not self.durations:
            return 0.0
        return statistics.median(self.durations)

    @property
    def p95_duration_ms(self) -> float:
        """95th percentile duration."""
        if len(self.durations) < 2:
            return self.max_duration_ms
        sorted_durations = sorted(self.durations)
        idx = int(len(sorted_durations) * 0.95)
        return sorted_durations[min(idx, len(sorted_durations) - 1)]

    @property
    def p99_duration_ms(self) -> float:
        """99th percentile duration."""
        if len(self.durations) < 2:
            return self.max_duration_ms
        sorted_durations = sorted(self.durations)
        idx = int(len(sorted_durations) * 0.99)
        return sorted_durations[min(idx, len(sorted_durations) - 1)]

    @property
    def success_rate(self) -> float:
        """Success rate as percentage."""
        if self.call_count == 0:
            return 100.0
        return (self.success_count / self.call_count) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "method": self.method,
            "call_count": self.call_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_rate,
            "total_duration_ms": self.total_duration_ms,
            "avg_duration_ms": self.avg_duration_ms,
            "min_duration_ms": self.min_duration_ms if self.call_count > 0 else 0,
            "max_duration_ms": self.max_duration_ms,
            "p50_duration_ms": self.p50_duration_ms,
            "p95_duration_ms": self.p95_duration_ms,
            "p99_duration_ms": self.p99_duration_ms,
        }


class PluginMetricsCollector:
    """
    Per-plugin metrics collector.

    Tracks execution timing, error rates, resource usage, and custom metrics.
    Thread-safe for concurrent access.
    """

    # Maximum duration samples to keep for percentile calculations
    MAX_DURATION_SAMPLES = 1000

    def __init__(
        self,
        plugin_id: str,
        max_metrics: int = 10000,
    ) -> None:
        """
        Initialize metrics collector.

        Args:
            plugin_id: Plugin identifier
            max_metrics: Maximum metrics to retain in memory
        """
        self._plugin_id = plugin_id
        self._max_metrics = max_metrics
        self._lock = threading.RLock()

        # Execution statistics by method
        self._execution_stats: Dict[str, ExecutionStats] = {}

        # Raw metrics buffer
        self._metrics: List[PluginMetric] = []

        # Counters
        self._counters: Dict[str, int] = defaultdict(int)

        # Gauges (current values)
        self._gauges: Dict[str, float] = {}

        # Error tracking
        self._errors: Dict[str, List[Tuple[datetime, str]]] = defaultdict(list)

        # Timestamps
        self._created_at = datetime.now()
        self._last_activity: Optional[datetime] = None

    @property
    def plugin_id(self) -> str:
        """Get plugin ID."""
        return self._plugin_id

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def last_activity(self) -> Optional[datetime]:
        """Get last activity timestamp."""
        return self._last_activity

    def _touch(self) -> None:
        """Update last activity timestamp."""
        self._last_activity = datetime.now()

    def _add_metric(
        self,
        metric_type: MetricType,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Add a metric to the buffer."""
        metric = PluginMetric(
            metric_type=metric_type,
            value=value,
            labels=labels or {},
            plugin_id=self._plugin_id,
        )
        with self._lock:
            self._metrics.append(metric)
            # Trim if exceeding max
            if len(self._metrics) > self._max_metrics:
                self._metrics = self._metrics[-self._max_metrics:]
            self._touch()

    # === Execution Metrics ===

    def record_execution(
        self,
        method: str,
        duration_ms: float,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """
        Record a method execution.

        Args:
            method: Method name
            duration_ms: Execution duration in milliseconds
            success: Whether execution succeeded
            error: Error message if failed
        """
        with self._lock:
            if method not in self._execution_stats:
                self._execution_stats[method] = ExecutionStats(method=method)

            stats = self._execution_stats[method]
            stats.call_count += 1
            stats.total_duration_ms += duration_ms
            stats.min_duration_ms = min(stats.min_duration_ms, duration_ms)
            stats.max_duration_ms = max(stats.max_duration_ms, duration_ms)

            # Keep duration samples for percentile calculations
            if len(stats.durations) >= self.MAX_DURATION_SAMPLES:
                stats.durations.pop(0)
            stats.durations.append(duration_ms)

            if success:
                stats.success_count += 1
            else:
                stats.error_count += 1
                if error:
                    self._errors[method].append((datetime.now(), error))

            self._touch()

        # Add to metrics buffer
        self._add_metric(
            MetricType.EXECUTION_DURATION,
            duration_ms,
            {"method": method},
        )
        self._add_metric(
            MetricType.EXECUTION_SUCCESS if success else MetricType.EXECUTION_ERROR,
            1,
            {"method": method},
        )

    def time_execution(self, method: str) -> "ExecutionTimer":
        """
        Context manager for timing executions.

        Usage:
            with collector.time_execution("process_audio") as timer:
                result = process()
                if failed:
                    timer.mark_error("Processing failed")
        """
        return ExecutionTimer(self, method)

    def record_error(
        self,
        method: str,
        error: str,
        error_type: Optional[str] = None,
    ) -> None:
        """
        Record an error occurrence.

        Args:
            method: Method where error occurred
            error: Error message
            error_type: Type of error (e.g., ValueError)
        """
        with self._lock:
            self._errors[method].append((datetime.now(), error))
            self._counters["error_count"] += 1
            self._touch()

        labels = {"method": method}
        if error_type:
            labels["error_type"] = error_type
        self._add_metric(MetricType.EXECUTION_ERROR, 1, labels)

    # === Resource Metrics ===

    def record_memory_usage(self, bytes_used: int) -> None:
        """Record memory usage in bytes."""
        with self._lock:
            self._gauges["memory_bytes"] = bytes_used
            self._touch()
        self._add_metric(MetricType.MEMORY_USAGE, float(bytes_used))

    def record_cpu_time(self, cpu_ms: float) -> None:
        """Record CPU time in milliseconds."""
        with self._lock:
            prev = self._gauges.get("cpu_ms", 0)
            self._gauges["cpu_ms"] = prev + cpu_ms
            self._touch()
        self._add_metric(MetricType.CPU_TIME, cpu_ms)

    # === IPC Metrics ===

    def record_ipc_request(
        self,
        method: str,
        latency_ms: Optional[float] = None,
    ) -> None:
        """Record an IPC request."""
        with self._lock:
            self._counters["ipc_requests"] += 1
            self._touch()

        self._add_metric(MetricType.IPC_REQUESTS, 1, {"method": method})
        if latency_ms is not None:
            self._add_metric(MetricType.IPC_LATENCY, latency_ms, {"method": method})

    def record_ipc_response(self, method: str) -> None:
        """Record an IPC response."""
        with self._lock:
            self._counters["ipc_responses"] += 1
            self._touch()
        self._add_metric(MetricType.IPC_RESPONSES, 1, {"method": method})

    def record_ipc_error(self, method: str, error_code: int) -> None:
        """Record an IPC error."""
        with self._lock:
            self._counters["ipc_errors"] += 1
            self._touch()
        self._add_metric(
            MetricType.IPC_ERRORS,
            1,
            {"method": method, "error_code": str(error_code)},
        )

    # === Permission Metrics ===

    def record_permission_check(
        self,
        permission: str,
        granted: bool,
    ) -> None:
        """Record a permission check."""
        with self._lock:
            self._counters["permission_checks"] += 1
            if granted:
                self._counters["permission_grants"] += 1
            else:
                self._counters["permission_denials"] += 1
            self._touch()

        self._add_metric(
            MetricType.PERMISSION_GRANTS if granted else MetricType.PERMISSION_DENIALS,
            1,
            {"permission": permission},
        )

    # === Lifecycle Metrics ===

    def record_start(self) -> None:
        """Record plugin start."""
        with self._lock:
            self._counters["lifecycle_starts"] += 1
            self._touch()
        self._add_metric(MetricType.LIFECYCLE_STARTS, 1)

    def record_stop(self) -> None:
        """Record plugin stop."""
        with self._lock:
            self._counters["lifecycle_stops"] += 1
            self._touch()
        self._add_metric(MetricType.LIFECYCLE_STOPS, 1)

    def record_crash(self, exit_code: Optional[int] = None) -> None:
        """Record plugin crash."""
        with self._lock:
            self._counters["lifecycle_crashes"] += 1
            self._touch()

        labels = {}
        if exit_code is not None:
            labels["exit_code"] = str(exit_code)
        self._add_metric(MetricType.LIFECYCLE_CRASHES, 1, labels)

    # === Custom Metrics ===

    def increment_counter(
        self,
        name: str,
        value: int = 1,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Increment a custom counter."""
        with self._lock:
            self._counters[f"custom.{name}"] += value
            self._touch()

        metric_labels = {"name": name}
        if labels:
            metric_labels.update(labels)
        self._add_metric(MetricType.CUSTOM_COUNTER, float(value), metric_labels)

    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Set a custom gauge value."""
        with self._lock:
            self._gauges[f"custom.{name}"] = value
            self._touch()

        metric_labels = {"name": name}
        if labels:
            metric_labels.update(labels)
        self._add_metric(MetricType.CUSTOM_GAUGE, value, metric_labels)

    def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a histogram value."""
        metric_labels = {"name": name}
        if labels:
            metric_labels.update(labels)
        self._add_metric(MetricType.CUSTOM_HISTOGRAM, value, metric_labels)
        self._touch()

    # === Statistics ===

    def get_execution_stats(
        self,
        method: Optional[str] = None,
    ) -> Dict[str, ExecutionStats]:
        """Get execution statistics."""
        with self._lock:
            if method:
                stats = self._execution_stats.get(method)
                return {method: stats} if stats else {}
            return dict(self._execution_stats)

    def get_counters(self) -> Dict[str, int]:
        """Get all counters."""
        with self._lock:
            return dict(self._counters)

    def get_gauges(self) -> Dict[str, float]:
        """Get all gauge values."""
        with self._lock:
            return dict(self._gauges)

    def get_errors(
        self,
        method: Optional[str] = None,
        limit: int = 100,
    ) -> Dict[str, List[Tuple[datetime, str]]]:
        """Get recent errors."""
        with self._lock:
            if method:
                errors = self._errors.get(method, [])
                return {method: errors[-limit:]}
            return {m: e[-limit:] for m, e in self._errors.items()}

    def get_metrics(
        self,
        metric_type: Optional[MetricType] = None,
        since: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[PluginMetric]:
        """Get raw metrics."""
        with self._lock:
            metrics = self._metrics

            if metric_type:
                metrics = [m for m in metrics if m.metric_type == metric_type]

            if since:
                metrics = [m for m in metrics if m.timestamp >= since]

            return metrics[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics.

        Returns a dictionary with:
        - summary: Overall summary
        - execution: Per-method execution stats
        - counters: All counters
        - gauges: All gauges
        - errors: Recent errors
        """
        with self._lock:
            total_calls = sum(s.call_count for s in self._execution_stats.values())
            total_errors = sum(s.error_count for s in self._execution_stats.values())
            total_duration = sum(
                s.total_duration_ms for s in self._execution_stats.values()
            )

            return {
                "plugin_id": self._plugin_id,
                "created_at": self._created_at.isoformat(),
                "last_activity": (
                    self._last_activity.isoformat() if self._last_activity else None
                ),
                "summary": {
                    "total_calls": total_calls,
                    "total_errors": total_errors,
                    "total_duration_ms": total_duration,
                    "error_rate": (
                        (total_errors / total_calls * 100) if total_calls > 0 else 0
                    ),
                    "methods_tracked": len(self._execution_stats),
                },
                "execution": {
                    m: s.to_dict() for m, s in self._execution_stats.items()
                },
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "error_count": len(
                    [e for errors in self._errors.values() for e in errors]
                ),
            }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._execution_stats.clear()
            self._metrics.clear()
            self._counters.clear()
            self._gauges.clear()
            self._errors.clear()
            self._last_activity = None


class ExecutionTimer:
    """Context manager for timing method executions."""

    def __init__(self, collector: PluginMetricsCollector, method: str) -> None:
        self._collector = collector
        self._method = method
        self._start_time: float = 0
        self._error: Optional[str] = None
        self._success = True

    def __enter__(self) -> "ExecutionTimer":
        self._start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        duration_ms = (time.perf_counter() - self._start_time) * 1000

        if exc_type is not None:
            self._success = False
            self._error = str(exc_val) if exc_val else exc_type.__name__

        self._collector.record_execution(
            method=self._method,
            duration_ms=duration_ms,
            success=self._success,
            error=self._error,
        )

    def mark_error(self, error: str) -> None:
        """Mark execution as failed with error."""
        self._success = False
        self._error = error


# === Global Registry ===

_collectors: Dict[str, PluginMetricsCollector] = {}
_collectors_lock = threading.Lock()


def get_metrics_collector(plugin_id: str) -> PluginMetricsCollector:
    """
    Get or create metrics collector for a plugin.

    Args:
        plugin_id: Plugin identifier

    Returns:
        PluginMetricsCollector for the plugin
    """
    with _collectors_lock:
        if plugin_id not in _collectors:
            _collectors[plugin_id] = PluginMetricsCollector(plugin_id)
        return _collectors[plugin_id]


def get_all_collectors() -> Dict[str, PluginMetricsCollector]:
    """Get all metrics collectors."""
    with _collectors_lock:
        return dict(_collectors)


def reset_metrics(plugin_id: Optional[str] = None) -> None:
    """
    Reset metrics for a plugin or all plugins.

    Args:
        plugin_id: Plugin ID to reset, or None for all
    """
    with _collectors_lock:
        if plugin_id:
            if plugin_id in _collectors:
                _collectors[plugin_id].reset()
        else:
            for collector in _collectors.values():
                collector.reset()
