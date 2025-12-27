"""
Monitoring Module

Provides structured logging, metrics collection, error tracking,
and performance monitoring.
"""

from .error_tracking import (
    ErrorRecord,
    ErrorSeverity,
    ErrorTracker,
    get_error_tracker,
)
from .metrics import (
    Metric,
    MetricsCollector,
    MetricType,
    Timer,
    get_metrics_collector,
)
from .profiler import (
    PerformanceProfiler,
    ProfileEntry,
    get_profiler,
)
from .structured_logging import (
    StructuredFormatter,
    StructuredLogger,
    get_structured_logger,
    setup_structured_logging,
)

__all__ = [
    # Structured Logging
    "StructuredFormatter",
    "StructuredLogger",
    "setup_structured_logging",
    "get_structured_logger",
    # Metrics
    "MetricType",
    "Metric",
    "MetricsCollector",
    "get_metrics_collector",
    "Timer",
    # Error Tracking
    "ErrorSeverity",
    "ErrorRecord",
    "ErrorTracker",
    "get_error_tracker",
    # Performance Profiling
    "PerformanceProfiler",
    "ProfileEntry",
    "get_profiler",
]

