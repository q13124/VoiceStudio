"""
Phase 8: Metrics Collection
Task 8.2: Application metrics collection and reporting.
"""

import asyncio
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Optional
import logging
import threading

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricValue:
    """A metric value with timestamp."""
    value: float
    timestamp: datetime
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class MetricDefinition:
    """Definition of a metric."""
    name: str
    type: MetricType
    description: str = ""
    unit: str = ""
    tags: dict[str, str] = field(default_factory=dict)


class Counter:
    """A counter metric that only increases."""
    
    def __init__(self, name: str, description: str = "", tags: Optional[dict[str, str]] = None):
        self.name = name
        self.description = description
        self.tags = tags or {}
        self._value = 0
        self._lock = threading.Lock()
    
    def inc(self, amount: float = 1, tags: Optional[dict[str, str]] = None) -> None:
        """Increment the counter."""
        with self._lock:
            self._value += amount
    
    def get(self) -> float:
        """Get the current value."""
        return self._value
    
    def reset(self) -> None:
        """Reset the counter."""
        with self._lock:
            self._value = 0


class Gauge:
    """A gauge metric that can go up and down."""
    
    def __init__(self, name: str, description: str = "", tags: Optional[dict[str, str]] = None):
        self.name = name
        self.description = description
        self.tags = tags or {}
        self._value = 0.0
        self._lock = threading.Lock()
    
    def set(self, value: float, tags: Optional[dict[str, str]] = None) -> None:
        """Set the gauge value."""
        with self._lock:
            self._value = value
    
    def inc(self, amount: float = 1) -> None:
        """Increment the gauge."""
        with self._lock:
            self._value += amount
    
    def dec(self, amount: float = 1) -> None:
        """Decrement the gauge."""
        with self._lock:
            self._value -= amount
    
    def get(self) -> float:
        """Get the current value."""
        return self._value


class Histogram:
    """A histogram metric for distribution analysis."""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        buckets: Optional[list[float]] = None,
        tags: Optional[dict[str, str]] = None
    ):
        self.name = name
        self.description = description
        self.tags = tags or {}
        self.buckets = buckets or [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
        
        self._values: list[float] = []
        self._sum = 0.0
        self._count = 0
        self._bucket_counts: dict[float, int] = {b: 0 for b in self.buckets}
        self._bucket_counts[float('inf')] = 0
        self._lock = threading.Lock()
    
    def observe(self, value: float, tags: Optional[dict[str, str]] = None) -> None:
        """Record an observation."""
        with self._lock:
            self._values.append(value)
            self._sum += value
            self._count += 1
            
            for bucket in sorted(self.buckets):
                if value <= bucket:
                    self._bucket_counts[bucket] += 1
                    break
            else:
                self._bucket_counts[float('inf')] += 1
            
            # Limit stored values
            if len(self._values) > 10000:
                self._values = self._values[-10000:]
    
    def get_sum(self) -> float:
        """Get the sum of all observations."""
        return self._sum
    
    def get_count(self) -> int:
        """Get the count of observations."""
        return self._count
    
    def get_bucket_counts(self) -> dict[float, int]:
        """Get bucket counts."""
        return self._bucket_counts.copy()


class Timer(Histogram):
    """A timer metric for measuring durations."""
    
    def time(self):
        """Context manager for timing operations."""
        return TimerContext(self)


class TimerContext:
    """Context manager for timing."""
    
    def __init__(self, timer: Timer):
        self._timer = timer
        self._start: Optional[float] = None
    
    def __enter__(self):
        self._start = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._start:
            duration = time.perf_counter() - self._start
            self._timer.observe(duration)


class MetricsCollector:
    """Collector for application metrics."""
    
    def __init__(self):
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}
        self._timers: dict[str, Timer] = {}
        self._lock = threading.Lock()
        
        # Register default metrics
        self._register_default_metrics()
    
    def counter(
        self,
        name: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None
    ) -> Counter:
        """Get or create a counter."""
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name, description, tags)
            return self._counters[name]
    
    def gauge(
        self,
        name: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None
    ) -> Gauge:
        """Get or create a gauge."""
        with self._lock:
            if name not in self._gauges:
                self._gauges[name] = Gauge(name, description, tags)
            return self._gauges[name]
    
    def histogram(
        self,
        name: str,
        description: str = "",
        buckets: Optional[list[float]] = None,
        tags: Optional[dict[str, str]] = None
    ) -> Histogram:
        """Get or create a histogram."""
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(name, description, buckets, tags)
            return self._histograms[name]
    
    def timer(
        self,
        name: str,
        description: str = "",
        tags: Optional[dict[str, str]] = None
    ) -> Timer:
        """Get or create a timer."""
        with self._lock:
            if name not in self._timers:
                self._timers[name] = Timer(name, description, tags=tags)
            return self._timers[name]
    
    def get_all_metrics(self) -> dict[str, Any]:
        """Get all metrics."""
        metrics = {}
        
        for name, counter in self._counters.items():
            metrics[name] = {
                "type": "counter",
                "value": counter.get(),
            }
        
        for name, gauge in self._gauges.items():
            metrics[name] = {
                "type": "gauge",
                "value": gauge.get(),
            }
        
        for name, histogram in self._histograms.items():
            metrics[name] = {
                "type": "histogram",
                "count": histogram.get_count(),
                "sum": histogram.get_sum(),
                "buckets": histogram.get_bucket_counts(),
            }
        
        for name, timer in self._timers.items():
            metrics[name] = {
                "type": "timer",
                "count": timer.get_count(),
                "sum": timer.get_sum(),
            }
        
        return metrics
    
    def export_prometheus(self) -> str:
        """Export metrics in Prometheus format."""
        lines = []
        
        for name, counter in self._counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {counter.get()}")
        
        for name, gauge in self._gauges.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {gauge.get()}")
        
        for name, histogram in self._histograms.items():
            lines.append(f"# TYPE {name} histogram")
            lines.append(f"{name}_count {histogram.get_count()}")
            lines.append(f"{name}_sum {histogram.get_sum()}")
            for bucket, count in histogram.get_bucket_counts().items():
                le = "+Inf" if bucket == float('inf') else str(bucket)
                lines.append(f'{name}_bucket{{le="{le}"}} {count}')
        
        return "\n".join(lines)
    
    def _register_default_metrics(self) -> None:
        """Register default application metrics."""
        # Synthesis metrics
        self.counter("synthesis_total", "Total synthesis operations")
        self.counter("synthesis_errors", "Failed synthesis operations")
        self.histogram("synthesis_duration_seconds", "Synthesis duration")
        
        # API metrics
        self.counter("api_requests_total", "Total API requests")
        self.histogram("api_request_duration_seconds", "API request duration")
        
        # Engine metrics
        self.gauge("engines_loaded", "Number of loaded engines")
        self.gauge("engine_memory_mb", "Engine memory usage")
        
        # System metrics
        self.gauge("cpu_usage_percent", "CPU usage percentage")
        self.gauge("memory_usage_mb", "Memory usage in MB")
        self.gauge("gpu_memory_mb", "GPU memory usage in MB")


# Global collector instance
_collector: Optional[MetricsCollector] = None


def get_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector
