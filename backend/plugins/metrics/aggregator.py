"""
Plugin Metrics Aggregator.

Aggregates metrics across all plugins for dashboard and reporting.
"""

import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .collector import (
    MetricType,
    PluginMetric,
    PluginMetricsCollector,
    get_all_collectors,
)

logger = logging.getLogger(__name__)


@dataclass
class PluginHealthSummary:
    """Health summary for a single plugin."""

    plugin_id: str
    status: str  # healthy, degraded, unhealthy, unknown
    error_rate: float
    avg_latency_ms: float
    total_calls: int
    total_errors: int
    last_activity: Optional[datetime]
    memory_bytes: Optional[int] = None
    crash_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plugin_id": self.plugin_id,
            "status": self.status,
            "error_rate": self.error_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "total_calls": self.total_calls,
            "total_errors": self.total_errors,
            "last_activity": (
                self.last_activity.isoformat() if self.last_activity else None
            ),
            "memory_bytes": self.memory_bytes,
            "crash_count": self.crash_count,
        }


@dataclass
class SystemHealthSummary:
    """Health summary for the entire plugin system."""

    total_plugins: int
    healthy_plugins: int
    degraded_plugins: int
    unhealthy_plugins: int
    total_calls: int
    total_errors: int
    system_error_rate: float
    avg_latency_ms: float
    total_memory_bytes: int
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_plugins": self.total_plugins,
            "healthy_plugins": self.healthy_plugins,
            "degraded_plugins": self.degraded_plugins,
            "unhealthy_plugins": self.unhealthy_plugins,
            "total_calls": self.total_calls,
            "total_errors": self.total_errors,
            "system_error_rate": self.system_error_rate,
            "avg_latency_ms": self.avg_latency_ms,
            "total_memory_bytes": self.total_memory_bytes,
            "timestamp": self.timestamp.isoformat(),
        }


class MetricsAggregator:
    """
    Aggregates metrics across all plugins.

    Provides system-wide health overview and per-plugin comparisons.
    """

    # Health thresholds
    ERROR_RATE_HEALTHY = 1.0  # < 1% errors = healthy
    ERROR_RATE_DEGRADED = 5.0  # < 5% errors = degraded
    LATENCY_HEALTHY_MS = 500  # < 500ms avg = healthy
    LATENCY_DEGRADED_MS = 2000  # < 2s avg = degraded
    INACTIVE_THRESHOLD_MINUTES = 60  # No activity for 1 hour = check health

    def __init__(self) -> None:
        """Initialize aggregator."""
        self._lock = threading.Lock()
        self._last_snapshot: Optional[SystemHealthSummary] = None

    def _determine_health_status(
        self,
        error_rate: float,
        avg_latency_ms: float,
        crash_count: int,
        last_activity: Optional[datetime],
    ) -> str:
        """Determine plugin health status."""
        # Crashes always indicate unhealthy
        if crash_count > 0:
            return "unhealthy"

        # Check inactivity
        if last_activity:
            inactive_minutes = (datetime.now() - last_activity).total_seconds() / 60
            if inactive_minutes > self.INACTIVE_THRESHOLD_MINUTES:
                return "unknown"

        # Check error rate
        if error_rate >= self.ERROR_RATE_DEGRADED:
            return "unhealthy"
        if error_rate >= self.ERROR_RATE_HEALTHY:
            return "degraded"

        # Check latency
        if avg_latency_ms >= self.LATENCY_DEGRADED_MS:
            return "unhealthy"
        if avg_latency_ms >= self.LATENCY_HEALTHY_MS:
            return "degraded"

        return "healthy"

    def get_plugin_health(self, plugin_id: str) -> Optional[PluginHealthSummary]:
        """
        Get health summary for a specific plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            PluginHealthSummary or None if not found
        """
        collectors = get_all_collectors()
        collector = collectors.get(plugin_id)
        if not collector:
            return None

        stats = collector.get_stats()
        summary = stats.get("summary", {})
        counters = stats.get("counters", {})
        gauges = stats.get("gauges", {})

        total_calls = summary.get("total_calls", 0)
        total_errors = summary.get("total_errors", 0)
        error_rate = summary.get("error_rate", 0.0)

        # Calculate average latency
        total_duration = summary.get("total_duration_ms", 0.0)
        avg_latency = total_duration / total_calls if total_calls > 0 else 0.0

        crash_count = counters.get("lifecycle_crashes", 0)
        memory_bytes = gauges.get("memory_bytes")

        last_activity = None
        if stats.get("last_activity"):
            try:
                last_activity = datetime.fromisoformat(stats["last_activity"])
            except (ValueError, TypeError) as e:
                # Invalid timestamp format - leave last_activity as None
                logger.debug(f"Could not parse last_activity for {plugin_id}: {e}")

        status = self._determine_health_status(
            error_rate, avg_latency, crash_count, last_activity
        )

        return PluginHealthSummary(
            plugin_id=plugin_id,
            status=status,
            error_rate=error_rate,
            avg_latency_ms=avg_latency,
            total_calls=total_calls,
            total_errors=total_errors,
            last_activity=last_activity,
            memory_bytes=int(memory_bytes) if memory_bytes else None,
            crash_count=crash_count,
        )

    def get_all_plugin_health(self) -> List[PluginHealthSummary]:
        """Get health summaries for all plugins."""
        collectors = get_all_collectors()
        summaries = []

        for plugin_id in collectors:
            health = self.get_plugin_health(plugin_id)
            if health:
                summaries.append(health)

        return summaries

    def get_system_health(self) -> SystemHealthSummary:
        """
        Get system-wide health summary.

        Returns aggregated statistics across all plugins.
        """
        plugin_summaries = self.get_all_plugin_health()

        total_plugins = len(plugin_summaries)
        healthy = sum(1 for p in plugin_summaries if p.status == "healthy")
        degraded = sum(1 for p in plugin_summaries if p.status == "degraded")
        unhealthy = sum(1 for p in plugin_summaries if p.status == "unhealthy")

        total_calls = sum(p.total_calls for p in plugin_summaries)
        total_errors = sum(p.total_errors for p in plugin_summaries)
        total_memory = sum(p.memory_bytes or 0 for p in plugin_summaries)

        system_error_rate = (
            (total_errors / total_calls * 100) if total_calls > 0 else 0.0
        )

        # Weighted average latency
        total_latency_weighted = sum(
            p.avg_latency_ms * p.total_calls for p in plugin_summaries
        )
        avg_latency = total_latency_weighted / total_calls if total_calls > 0 else 0.0

        summary = SystemHealthSummary(
            total_plugins=total_plugins,
            healthy_plugins=healthy,
            degraded_plugins=degraded,
            unhealthy_plugins=unhealthy,
            total_calls=total_calls,
            total_errors=total_errors,
            system_error_rate=system_error_rate,
            avg_latency_ms=avg_latency,
            total_memory_bytes=total_memory,
        )

        with self._lock:
            self._last_snapshot = summary

        return summary

    def get_top_plugins_by_calls(self, limit: int = 10) -> List[PluginHealthSummary]:
        """Get plugins with most calls."""
        summaries = self.get_all_plugin_health()
        return sorted(summaries, key=lambda p: p.total_calls, reverse=True)[:limit]

    def get_top_plugins_by_errors(self, limit: int = 10) -> List[PluginHealthSummary]:
        """Get plugins with most errors."""
        summaries = self.get_all_plugin_health()
        return sorted(summaries, key=lambda p: p.total_errors, reverse=True)[:limit]

    def get_top_plugins_by_latency(self, limit: int = 10) -> List[PluginHealthSummary]:
        """Get plugins with highest average latency."""
        summaries = self.get_all_plugin_health()
        return sorted(summaries, key=lambda p: p.avg_latency_ms, reverse=True)[:limit]

    def get_unhealthy_plugins(self) -> List[PluginHealthSummary]:
        """Get all unhealthy plugins."""
        summaries = self.get_all_plugin_health()
        return [p for p in summaries if p.status in ("unhealthy", "degraded")]

    def get_aggregated_metrics(
        self,
        metric_type: Optional[MetricType] = None,
        since: Optional[datetime] = None,
        limit: int = 1000,
    ) -> List[PluginMetric]:
        """
        Get aggregated metrics from all plugins.

        Args:
            metric_type: Filter by metric type
            since: Filter by timestamp
            limit: Maximum metrics to return

        Returns:
            List of PluginMetric from all plugins
        """
        collectors = get_all_collectors()
        all_metrics: List[PluginMetric] = []

        for collector in collectors.values():
            metrics = collector.get_metrics(
                metric_type=metric_type,
                since=since,
                limit=limit,
            )
            all_metrics.extend(metrics)

        # Sort by timestamp and limit
        all_metrics.sort(key=lambda m: m.timestamp)
        return all_metrics[-limit:]

    def get_metric_time_series(
        self,
        metric_type: MetricType,
        interval_minutes: int = 5,
        duration_hours: int = 1,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get time series data for a metric type.

        Args:
            metric_type: Type of metric to aggregate
            interval_minutes: Bucket size in minutes
            duration_hours: How far back to look

        Returns:
            Dictionary mapping timestamps to aggregated values
        """
        since = datetime.now() - timedelta(hours=duration_hours)
        metrics = self.get_aggregated_metrics(metric_type=metric_type, since=since)

        # Bucket metrics by interval
        buckets: Dict[str, Dict[str, List[float]]] = {}

        for metric in metrics:
            # Round timestamp to interval
            bucket_time = metric.timestamp.replace(
                minute=(metric.timestamp.minute // interval_minutes) * interval_minutes,
                second=0,
                microsecond=0,
            )
            bucket_key = bucket_time.isoformat()

            if bucket_key not in buckets:
                buckets[bucket_key] = {}

            plugin_id = metric.plugin_id
            if plugin_id not in buckets[bucket_key]:
                buckets[bucket_key][plugin_id] = []

            buckets[bucket_key][plugin_id].append(metric.value)

        # Aggregate each bucket
        result: Dict[str, List[Dict[str, Any]]] = {}
        for timestamp, plugin_values in sorted(buckets.items()):
            result[timestamp] = []
            for plugin_id, values in plugin_values.items():
                result[timestamp].append({
                    "plugin_id": plugin_id,
                    "count": len(values),
                    "sum": sum(values),
                    "avg": sum(values) / len(values) if values else 0,
                    "min": min(values) if values else 0,
                    "max": max(values) if values else 0,
                })

        return result

    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data.

        Returns data suitable for rendering a health dashboard.
        """
        system_health = self.get_system_health()
        plugin_health = self.get_all_plugin_health()
        unhealthy = self.get_unhealthy_plugins()
        top_by_calls = self.get_top_plugins_by_calls(5)
        top_by_errors = self.get_top_plugins_by_errors(5)

        return {
            "system": system_health.to_dict(),
            "plugins": [p.to_dict() for p in plugin_health],
            "alerts": {
                "unhealthy_count": len(unhealthy),
                "unhealthy_plugins": [p.to_dict() for p in unhealthy],
            },
            "top_by_calls": [p.to_dict() for p in top_by_calls],
            "top_by_errors": [p.to_dict() for p in top_by_errors],
            "last_updated": datetime.now().isoformat(),
        }


# Global aggregator instance
_aggregator: Optional[MetricsAggregator] = None


def get_aggregator() -> MetricsAggregator:
    """Get the global metrics aggregator."""
    global _aggregator
    if _aggregator is None:
        _aggregator = MetricsAggregator()
    return _aggregator
