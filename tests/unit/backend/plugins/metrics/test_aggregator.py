"""
Tests for Plugin Metrics Aggregator.

Phase 4 Enhancement: Tests for system-wide metrics aggregation.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from backend.plugins.metrics.aggregator import (
    MetricsAggregator,
    PluginHealthSummary,
    SystemHealthSummary,
    get_aggregator,
)
from backend.plugins.metrics.collector import (
    PluginMetricsCollector,
    get_metrics_collector,
    reset_metrics,
)


class TestPluginHealthSummary:
    """Tests for PluginHealthSummary dataclass."""

    def test_create_summary(self):
        """Test creating a health summary."""
        summary = PluginHealthSummary(
            plugin_id="test.plugin",
            status="healthy",
            error_rate=0.5,
            avg_latency_ms=50.0,
            total_calls=1000,
            total_errors=5,
            last_activity=datetime.now(),
        )
        assert summary.plugin_id == "test.plugin"
        assert summary.status == "healthy"
        assert summary.error_rate == 0.5

    def test_to_dict(self):
        """Test converting summary to dictionary."""
        summary = PluginHealthSummary(
            plugin_id="test.plugin",
            status="degraded",
            error_rate=3.0,
            avg_latency_ms=800.0,
            total_calls=500,
            total_errors=15,
            last_activity=datetime.now(),
            memory_bytes=1024 * 1024,
            crash_count=1,
        )

        d = summary.to_dict()
        assert d["plugin_id"] == "test.plugin"
        assert d["status"] == "degraded"
        assert d["crash_count"] == 1
        assert d["memory_bytes"] == 1024 * 1024


class TestSystemHealthSummary:
    """Tests for SystemHealthSummary dataclass."""

    def test_create_summary(self):
        """Test creating a system health summary."""
        summary = SystemHealthSummary(
            total_plugins=10,
            healthy_plugins=8,
            degraded_plugins=1,
            unhealthy_plugins=1,
            total_calls=10000,
            total_errors=50,
            system_error_rate=0.5,
            avg_latency_ms=75.0,
            total_memory_bytes=100 * 1024 * 1024,
        )
        assert summary.total_plugins == 10
        assert summary.healthy_plugins == 8

    def test_to_dict(self):
        """Test converting summary to dictionary."""
        summary = SystemHealthSummary(
            total_plugins=5,
            healthy_plugins=4,
            degraded_plugins=1,
            unhealthy_plugins=0,
            total_calls=5000,
            total_errors=25,
            system_error_rate=0.5,
            avg_latency_ms=100.0,
            total_memory_bytes=50 * 1024 * 1024,
        )

        d = summary.to_dict()
        assert d["total_plugins"] == 5
        assert "timestamp" in d


class TestMetricsAggregator:
    """Tests for MetricsAggregator."""

    @pytest.fixture(autouse=True)
    def reset_collectors(self):
        """Reset collectors before each test."""
        reset_metrics()
        yield

    @pytest.fixture
    def aggregator(self):
        """Create a fresh aggregator."""
        return MetricsAggregator()

    @pytest.fixture
    def populated_collectors(self):
        """Create collectors with test data."""
        # Healthy plugin
        healthy = get_metrics_collector("test.healthy")
        for _ in range(100):
            healthy.record_execution("process", duration_ms=50.0, success=True)

        # Degraded plugin (high latency)
        degraded = get_metrics_collector("test.degraded")
        for _ in range(50):
            degraded.record_execution("process", duration_ms=1000.0, success=True)

        # Unhealthy plugin (high error rate)
        unhealthy = get_metrics_collector("test.unhealthy")
        for _ in range(100):
            if _ < 10:
                unhealthy.record_execution("process", duration_ms=50.0, success=False)
            else:
                unhealthy.record_execution("process", duration_ms=50.0, success=True)

        return {"healthy": healthy, "degraded": degraded, "unhealthy": unhealthy}

    def test_health_status_healthy(self, aggregator):
        """Test healthy status determination."""
        status = aggregator._determine_health_status(
            error_rate=0.5,
            avg_latency_ms=100.0,
            crash_count=0,
            last_activity=datetime.now(),
        )
        assert status == "healthy"

    def test_health_status_degraded_error_rate(self, aggregator):
        """Test degraded status from error rate."""
        status = aggregator._determine_health_status(
            error_rate=3.0,
            avg_latency_ms=100.0,
            crash_count=0,
            last_activity=datetime.now(),
        )
        assert status == "degraded"

    def test_health_status_degraded_latency(self, aggregator):
        """Test degraded status from latency."""
        status = aggregator._determine_health_status(
            error_rate=0.5,
            avg_latency_ms=800.0,
            crash_count=0,
            last_activity=datetime.now(),
        )
        assert status == "degraded"

    def test_health_status_unhealthy_error_rate(self, aggregator):
        """Test unhealthy status from high error rate."""
        status = aggregator._determine_health_status(
            error_rate=10.0,
            avg_latency_ms=100.0,
            crash_count=0,
            last_activity=datetime.now(),
        )
        assert status == "unhealthy"

    def test_health_status_unhealthy_crash(self, aggregator):
        """Test unhealthy status from crashes."""
        status = aggregator._determine_health_status(
            error_rate=0.0,
            avg_latency_ms=50.0,
            crash_count=1,
            last_activity=datetime.now(),
        )
        assert status == "unhealthy"

    def test_health_status_unknown_inactive(self, aggregator):
        """Test unknown status from inactivity."""
        old_time = datetime.now() - timedelta(hours=2)
        status = aggregator._determine_health_status(
            error_rate=0.0,
            avg_latency_ms=50.0,
            crash_count=0,
            last_activity=old_time,
        )
        assert status == "unknown"

    def test_get_plugin_health(self, aggregator, populated_collectors):
        """Test getting plugin health summary."""
        health = aggregator.get_plugin_health("test.healthy")

        assert health is not None
        assert health.plugin_id == "test.healthy"
        assert health.status == "healthy"
        assert health.total_calls == 100

    def test_get_plugin_health_not_found(self, aggregator):
        """Test getting health for non-existent plugin."""
        health = aggregator.get_plugin_health("nonexistent.plugin")
        assert health is None

    def test_get_all_plugin_health(self, aggregator, populated_collectors):
        """Test getting health for all plugins."""
        all_health = aggregator.get_all_plugin_health()

        # Should have at least our 3 test plugins
        plugin_ids = [h.plugin_id for h in all_health]
        assert "test.healthy" in plugin_ids
        assert "test.degraded" in plugin_ids
        assert "test.unhealthy" in plugin_ids

    def test_get_system_health(self, aggregator, populated_collectors):
        """Test getting system-wide health."""
        system = aggregator.get_system_health()

        assert system.total_plugins >= 3
        assert system.total_calls >= 250  # 100 + 50 + 100
        assert system.total_errors >= 10

    def test_get_top_plugins_by_calls(self, aggregator, populated_collectors):
        """Test getting top plugins by calls."""
        top = aggregator.get_top_plugins_by_calls(limit=3)

        assert len(top) >= 2
        # Healthy and unhealthy have 100 calls each
        assert top[0].total_calls >= top[1].total_calls

    def test_get_top_plugins_by_errors(self, aggregator, populated_collectors):
        """Test getting top plugins by errors."""
        top = aggregator.get_top_plugins_by_errors(limit=3)

        # Unhealthy plugin has most errors
        assert any(p.plugin_id == "test.unhealthy" for p in top)

    def test_get_top_plugins_by_latency(self, aggregator, populated_collectors):
        """Test getting top plugins by latency."""
        top = aggregator.get_top_plugins_by_latency(limit=3)

        # Degraded plugin has highest latency
        assert any(p.plugin_id == "test.degraded" for p in top)
        assert top[0].avg_latency_ms >= top[-1].avg_latency_ms

    def test_get_unhealthy_plugins(self, aggregator, populated_collectors):
        """Test getting unhealthy plugins."""
        unhealthy = aggregator.get_unhealthy_plugins()

        statuses = [p.status for p in unhealthy]
        assert all(s in ("unhealthy", "degraded") for s in statuses)

    def test_get_aggregated_metrics(self, aggregator, populated_collectors):
        """Test getting aggregated metrics."""
        metrics = aggregator.get_aggregated_metrics(limit=500)

        assert len(metrics) > 0
        # Should have metrics from the populated collectors
        plugin_ids = {m.plugin_id for m in metrics}
        # At least one plugin should have metrics
        assert len(plugin_ids) >= 1
        # Check that we get metrics from our test plugins
        assert any("test." in pid for pid in plugin_ids)

    def test_get_dashboard_data(self, aggregator, populated_collectors):
        """Test getting dashboard data."""
        data = aggregator.get_dashboard_data()

        assert "system" in data
        assert "plugins" in data
        assert "alerts" in data
        assert "top_by_calls" in data
        assert "last_updated" in data


class TestGlobalAggregator:
    """Tests for global aggregator instance."""

    def test_get_aggregator(self):
        """Test getting global aggregator."""
        agg = get_aggregator()
        assert isinstance(agg, MetricsAggregator)

    def test_get_same_aggregator(self):
        """Test getting same aggregator instance."""
        agg1 = get_aggregator()
        agg2 = get_aggregator()
        assert agg1 is agg2
