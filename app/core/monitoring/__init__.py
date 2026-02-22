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
    "ErrorRecord",
    # Error Tracking
    "ErrorSeverity",
    "ErrorTracker",
    "Metric",
    # Metrics
    "MetricType",
    "MetricsCollector",
    # Performance Profiling
    "PerformanceProfiler",
    "ProfileEntry",
    # Structured Logging
    "StructuredFormatter",
    "StructuredLogger",
    "Timer",
    "get_error_tracker",
    "get_metrics_collector",
    "get_profiler",
    "get_structured_logger",
    "setup_structured_logging",
]
