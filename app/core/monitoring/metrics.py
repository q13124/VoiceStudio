"""
Metrics Collection System

Provides metrics collection for performance monitoring, error tracking, and system health.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock
from typing import Any, Dict, List, Optional


class MetricType(Enum):
    """Metric types."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class Metric:
    """Metric data structure."""

    name: str
    type: MetricType
    value: float
    timestamp: datetime = field(default_factory=datetime.now)
    tags: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None


class MetricsCollector:
    """
    Metrics collector for performance monitoring.
    """

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: List[Metric] = []
        self.counters: Dict[str, float] = defaultdict(float)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self.timers: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()
        self.max_metrics = 10000  # Maximum metrics to keep in memory

    def increment(
        self,
        name: str,
        value: float = 1.0,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Increment a counter metric.

        Args:
            name: Metric name
            value: Increment value
            tags: Optional tags
        """
        with self.lock:
            self.counters[name] += value
            self._add_metric(
                Metric(
                    name=name,
                    type=MetricType.COUNTER,
                    value=self.counters[name],
                    tags=tags or {},
                )
            )

    def gauge(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
        unit: Optional[str] = None,
    ):
        """
        Set a gauge metric.

        Args:
            name: Metric name
            value: Gauge value
            tags: Optional tags
            unit: Optional unit (e.g., "bytes", "seconds")
        """
        with self.lock:
            self.gauges[name] = value
            self._add_metric(
                Metric(
                    name=name,
                    type=MetricType.GAUGE,
                    value=value,
                    tags=tags or {},
                    unit=unit,
                )
            )

    def histogram(
        self,
        name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Record a histogram value.

        Args:
            name: Metric name
            value: Histogram value
            tags: Optional tags
        """
        with self.lock:
            self.histograms[name].append(value)
            # Keep only last 1000 values
            if len(self.histograms[name]) > 1000:
                self.histograms[name] = self.histograms[name][-1000:]

            self._add_metric(
                Metric(
                    name=name,
                    type=MetricType.HISTOGRAM,
                    value=value,
                    tags=tags or {},
                )
            )

    def timer(
        self,
        name: str,
        duration: float,
        tags: Optional[Dict[str, str]] = None,
    ):
        """
        Record a timer value.

        Args:
            name: Metric name
            duration: Duration in seconds
            tags: Optional tags
        """
        with self.lock:
            self.timers[name].append(duration)
            # Keep only last 1000 values
            if len(self.timers[name]) > 1000:
                self.timers[name] = self.timers[name][-1000:]

            self._add_metric(
                Metric(
                    name=name,
                    type=MetricType.TIMER,
                    value=duration,
                    tags=tags or {},
                    unit="seconds",
                )
            )

    def _add_metric(self, metric: Metric):
        """Add metric to collection."""
        self.metrics.append(metric)

        # Limit metrics in memory
        if len(self.metrics) > self.max_metrics:
            self.metrics = self.metrics[-self.max_metrics :]

    def get_counter(self, name: str) -> float:
        """Get counter value."""
        with self.lock:
            return self.counters.get(name, 0.0)

    def get_gauge(self, name: str) -> Optional[float]:
        """Get gauge value."""
        with self.lock:
            return self.gauges.get(name)

    def get_histogram_stats(self, name: str) -> Optional[Dict[str, float]]:
        """Get histogram statistics."""
        with self.lock:
            values = self.histograms.get(name)
            if not values:
                return None

            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "p50": sorted(values)[len(values) // 2] if values else 0.0,
                "p95": sorted(values)[int(len(values) * 0.95)] if values else 0.0,
                "p99": sorted(values)[int(len(values) * 0.99)] if values else 0.0,
            }

    def get_timer_stats(self, name: str) -> Optional[Dict[str, float]]:
        """Get timer statistics."""
        with self.lock:
            values = self.timers.get(name)
            if not values:
                return None

            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
                "p50": sorted(values)[len(values) // 2] if values else 0.0,
                "p95": sorted(values)[int(len(values) * 0.95)] if values else 0.0,
                "p99": sorted(values)[int(len(values) * 0.99)] if values else 0.0,
            }

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics summary."""
        with self.lock:
            return {
                "counters": dict(self.counters),
                "gauges": dict(self.gauges),
                "histograms": {
                    name: self.get_histogram_stats(name)
                    for name in self.histograms.keys()
                },
                "timers": {
                    name: self.get_timer_stats(name) for name in self.timers.keys()
                },
            }

    def clear(self):
        """Clear all metrics."""
        with self.lock:
            self.metrics.clear()
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()
            self.timers.clear()


# Global metrics collector
_metrics_collector: Optional[MetricsCollector] = None
_collector_lock = Lock()


def get_metrics_collector() -> MetricsCollector:
    """
    Get or create global metrics collector.

    Returns:
        Metrics collector instance
    """
    global _metrics_collector
    with _collector_lock:
        if _metrics_collector is None:
            _metrics_collector = MetricsCollector()
        return _metrics_collector


class Timer:
    """
    Context manager for timing operations.
    """

    def __init__(
        self,
        name: str,
        tags: Optional[Dict[str, str]] = None,
        auto_record: bool = True,
    ):
        """
        Initialize timer.

        Args:
            name: Timer name
            tags: Optional tags
            auto_record: Automatically record to metrics
        """
        self.name = name
        self.tags = tags or {}
        self.auto_record = auto_record
        self.start_time: Optional[float] = None
        self.duration: Optional[float] = None

    def __enter__(self):
        """Start timer."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timer and record."""
        if self.start_time is not None:
            self.duration = time.time() - self.start_time
            if self.auto_record:
                get_metrics_collector().timer(self.name, self.duration, self.tags)

    def elapsed(self) -> Optional[float]:
        """Get elapsed time."""
        if self.start_time is None:
            return None
        if self.duration is not None:
            return self.duration
        return time.time() - self.start_time
