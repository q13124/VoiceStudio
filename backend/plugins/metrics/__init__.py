"""
VoiceStudio Plugin Metrics Collector.

Phase 4 Enhancement: Per-plugin telemetry and performance metrics.
Phase 5D M2: SQLite persistence layer with export to JSON/CSV/Prometheus.

This module provides:
- PluginMetric: Individual metric data point
- PluginMetricsCollector: Per-plugin metrics collection
- MetricsAggregator: Aggregates metrics across plugins
- MetricsExporter: Export metrics for dashboards
- MetricsPersistence: SQLite-based durable storage for metrics

Architecture:
    Each plugin has its own MetricsCollector that tracks:
    - Execution counts and timing
    - Memory and resource usage
    - Error rates and recovery
    - IPC message counts
    - Permission check statistics

    The MetricsPersistence layer stores metrics durably in SQLite with:
    - Historical analysis and trending
    - Cross-session metric continuity
    - Export to JSON, CSV, and Prometheus formats
    - Configurable retention policies

Usage:
    from backend.plugins.metrics import get_metrics_collector, get_metrics_persistence

    # Real-time collection
    collector = get_metrics_collector("com.example.plugin")
    collector.record_execution("process_audio", duration_ms=150.5)
    collector.record_error("process_audio", "ValueError")

    # Persistent storage
    persistence = get_metrics_persistence()
    persistence.store_metric("com.example.plugin", "execution.duration_ms", 150.5)
    metrics = persistence.query_metrics(plugin_id="com.example.plugin")

    stats = collector.get_stats()
"""

from .aggregator import MetricsAggregator, get_aggregator
from .collector import (
    MetricType,
    PluginMetric,
    PluginMetricsCollector,
    get_metrics_collector,
    reset_metrics,
)
from .exporter import MetricsExporter, MetricsFormat
from .persistence import (
    AggregatedMetric,
    MetricRecord,
    MetricsPersistence,
    RetentionPolicy,
    get_metrics_persistence,
    reset_persistence,
)

__all__ = [
    # Persistence (Phase 5D M2)
    "AggregatedMetric",
    "MetricRecord",
    "MetricType",
    # Aggregator
    "MetricsAggregator",
    # Exporter
    "MetricsExporter",
    "MetricsFormat",
    "MetricsPersistence",
    # Collector
    "PluginMetric",
    "PluginMetricsCollector",
    "RetentionPolicy",
    "get_aggregator",
    "get_metrics_collector",
    "get_metrics_persistence",
    "reset_metrics",
    "reset_persistence",
]
