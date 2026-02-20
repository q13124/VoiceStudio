"""
Tests for Plugin Metrics Collector.

Phase 4 Enhancement: Tests for per-plugin metrics collection.
"""

import time
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from backend.plugins.metrics.collector import (
    ExecutionStats,
    ExecutionTimer,
    MetricType,
    PluginMetric,
    PluginMetricsCollector,
    get_all_collectors,
    get_metrics_collector,
    reset_metrics,
)


class TestMetricType:
    """Tests for MetricType enum."""

    def test_execution_metrics(self):
        """Test execution metric types exist."""
        assert MetricType.EXECUTION_COUNT.value == "execution.count"
        assert MetricType.EXECUTION_DURATION.value == "execution.duration_ms"
        assert MetricType.EXECUTION_SUCCESS.value == "execution.success"
        assert MetricType.EXECUTION_ERROR.value == "execution.error"

    def test_resource_metrics(self):
        """Test resource metric types exist."""
        assert MetricType.MEMORY_USAGE.value == "resource.memory_bytes"
        assert MetricType.CPU_TIME.value == "resource.cpu_ms"

    def test_ipc_metrics(self):
        """Test IPC metric types exist."""
        assert MetricType.IPC_REQUESTS.value == "ipc.requests"
        assert MetricType.IPC_LATENCY.value == "ipc.latency_ms"

    def test_lifecycle_metrics(self):
        """Test lifecycle metric types exist."""
        assert MetricType.LIFECYCLE_STARTS.value == "lifecycle.starts"
        assert MetricType.LIFECYCLE_CRASHES.value == "lifecycle.crashes"


class TestPluginMetric:
    """Tests for PluginMetric dataclass."""

    def test_create_metric(self):
        """Test creating a metric."""
        metric = PluginMetric(
            metric_type=MetricType.EXECUTION_DURATION,
            value=150.5,
            plugin_id="test.plugin",
            labels={"method": "process"},
        )
        assert metric.value == 150.5
        assert metric.plugin_id == "test.plugin"
        assert metric.labels["method"] == "process"

    def test_to_dict(self):
        """Test converting metric to dictionary."""
        metric = PluginMetric(
            metric_type=MetricType.IPC_REQUESTS,
            value=1,
            plugin_id="test.plugin",
        )

        d = metric.to_dict()
        assert d["type"] == "ipc.requests"
        assert d["value"] == 1
        assert "timestamp" in d


class TestExecutionStats:
    """Tests for ExecutionStats dataclass."""

    def test_initial_state(self):
        """Test initial state of execution stats."""
        stats = ExecutionStats(method="test")
        assert stats.call_count == 0
        assert stats.success_count == 0
        assert stats.error_count == 0
        assert stats.avg_duration_ms == 0.0
        assert stats.success_rate == 100.0

    def test_avg_duration(self):
        """Test average duration calculation."""
        stats = ExecutionStats(method="test")
        stats.call_count = 4
        stats.total_duration_ms = 400.0
        assert stats.avg_duration_ms == 100.0

    def test_percentiles(self):
        """Test percentile calculations."""
        stats = ExecutionStats(method="test")
        stats.durations = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

        assert stats.p50_duration_ms == 55.0  # Median
        assert stats.p95_duration_ms == 100  # 95th percentile
        assert stats.p99_duration_ms == 100  # 99th percentile

    def test_success_rate(self):
        """Test success rate calculation."""
        stats = ExecutionStats(method="test")
        stats.call_count = 100
        stats.success_count = 95
        stats.error_count = 5

        assert stats.success_rate == 95.0

    def test_to_dict(self):
        """Test converting stats to dictionary."""
        stats = ExecutionStats(method="test")
        stats.call_count = 10
        stats.success_count = 9
        stats.error_count = 1
        stats.total_duration_ms = 500.0
        stats.min_duration_ms = 25.0
        stats.max_duration_ms = 100.0
        stats.durations = [50.0] * 10

        d = stats.to_dict()
        assert d["method"] == "test"
        assert d["call_count"] == 10
        assert d["success_rate"] == 90.0
        assert d["avg_duration_ms"] == 50.0


class TestPluginMetricsCollector:
    """Tests for PluginMetricsCollector."""

    @pytest.fixture
    def collector(self):
        """Create a fresh collector."""
        return PluginMetricsCollector("test.plugin")

    def test_init(self, collector):
        """Test collector initialization."""
        assert collector.plugin_id == "test.plugin"
        assert collector.last_activity is None
        assert collector.created_at is not None

    def test_record_execution_success(self, collector):
        """Test recording successful execution."""
        collector.record_execution("process_audio", duration_ms=100.0)

        stats = collector.get_execution_stats("process_audio")
        assert "process_audio" in stats
        assert stats["process_audio"].call_count == 1
        assert stats["process_audio"].success_count == 1
        assert stats["process_audio"].error_count == 0

    def test_record_execution_error(self, collector):
        """Test recording failed execution."""
        collector.record_execution(
            "process_audio",
            duration_ms=50.0,
            success=False,
            error="Processing failed",
        )

        stats = collector.get_execution_stats("process_audio")
        assert stats["process_audio"].error_count == 1
        assert stats["process_audio"].success_rate == 0.0

    def test_record_multiple_executions(self, collector):
        """Test recording multiple executions."""
        for i in range(10):
            collector.record_execution("method", duration_ms=float(i * 10))

        stats = collector.get_execution_stats("method")
        assert stats["method"].call_count == 10
        assert stats["method"].min_duration_ms == 0.0
        assert stats["method"].max_duration_ms == 90.0

    def test_record_memory_usage(self, collector):
        """Test recording memory usage."""
        collector.record_memory_usage(1024 * 1024)  # 1MB

        gauges = collector.get_gauges()
        assert gauges["memory_bytes"] == 1024 * 1024

    def test_record_cpu_time(self, collector):
        """Test recording CPU time."""
        collector.record_cpu_time(100.0)
        collector.record_cpu_time(50.0)

        gauges = collector.get_gauges()
        assert gauges["cpu_ms"] == 150.0

    def test_record_ipc_request(self, collector):
        """Test recording IPC request."""
        collector.record_ipc_request("host.audio.play", latency_ms=25.0)

        counters = collector.get_counters()
        assert counters["ipc_requests"] == 1

    def test_record_ipc_error(self, collector):
        """Test recording IPC error."""
        collector.record_ipc_error("host.audio.play", error_code=-32603)

        counters = collector.get_counters()
        assert counters["ipc_errors"] == 1

    def test_record_permission_check(self, collector):
        """Test recording permission check."""
        collector.record_permission_check("audio.playback", granted=True)
        collector.record_permission_check("network.http", granted=False)

        counters = collector.get_counters()
        assert counters["permission_checks"] == 2
        assert counters["permission_grants"] == 1
        assert counters["permission_denials"] == 1

    def test_record_lifecycle_events(self, collector):
        """Test recording lifecycle events."""
        collector.record_start()
        collector.record_stop()
        collector.record_crash(exit_code=1)

        counters = collector.get_counters()
        assert counters["lifecycle_starts"] == 1
        assert counters["lifecycle_stops"] == 1
        assert counters["lifecycle_crashes"] == 1

    def test_custom_counter(self, collector):
        """Test custom counter."""
        collector.increment_counter("custom_events", value=5)
        collector.increment_counter("custom_events", value=3)

        counters = collector.get_counters()
        assert counters["custom.custom_events"] == 8

    def test_custom_gauge(self, collector):
        """Test custom gauge."""
        collector.set_gauge("queue_depth", value=10.0)
        collector.set_gauge("queue_depth", value=5.0)

        gauges = collector.get_gauges()
        assert gauges["custom.queue_depth"] == 5.0

    def test_get_metrics_filtering(self, collector):
        """Test getting metrics with filters."""
        collector.record_execution("method1", 100.0)
        collector.record_ipc_request("host.method")
        collector.record_memory_usage(1024)

        # Filter by type
        exec_metrics = collector.get_metrics(
            metric_type=MetricType.EXECUTION_DURATION
        )
        assert len(exec_metrics) == 1

    def test_get_errors(self, collector):
        """Test getting errors."""
        collector.record_error("method1", "Error 1")
        collector.record_error("method1", "Error 2")
        collector.record_error("method2", "Error 3")

        # All errors
        all_errors = collector.get_errors()
        assert len(all_errors) == 2  # 2 methods
        assert len(all_errors["method1"]) == 2

        # Filtered errors
        method1_errors = collector.get_errors("method1")
        assert len(method1_errors) == 1
        assert len(method1_errors["method1"]) == 2

    def test_get_stats(self, collector):
        """Test getting comprehensive stats."""
        collector.record_execution("method1", 100.0)
        collector.record_execution("method1", 200.0, success=False)
        collector.record_memory_usage(1024)
        collector.increment_counter("custom", 5)

        stats = collector.get_stats()
        assert stats["plugin_id"] == "test.plugin"
        assert stats["summary"]["total_calls"] == 2
        assert stats["summary"]["total_errors"] == 1
        assert "method1" in stats["execution"]
        assert stats["counters"]["custom.custom"] == 5
        assert stats["gauges"]["memory_bytes"] == 1024

    def test_reset(self, collector):
        """Test resetting metrics."""
        collector.record_execution("method", 100.0)
        collector.record_memory_usage(1024)

        collector.reset()

        stats = collector.get_stats()
        assert stats["summary"]["total_calls"] == 0
        assert len(collector.get_gauges()) == 0

    def test_last_activity_updated(self, collector):
        """Test that last activity is updated."""
        assert collector.last_activity is None

        collector.record_execution("method", 100.0)

        assert collector.last_activity is not None


class TestExecutionTimer:
    """Tests for ExecutionTimer context manager."""

    def test_successful_execution(self):
        """Test timing successful execution."""
        collector = PluginMetricsCollector("test.plugin")

        with collector.time_execution("process"):
            time.sleep(0.02)  # 20ms - generous margin to avoid timing flakiness

        stats = collector.get_execution_stats("process")
        assert stats["process"].call_count == 1
        assert stats["process"].success_count == 1
        assert stats["process"].avg_duration_ms >= 15  # Expect at least 15ms

    def test_failed_execution(self):
        """Test timing failed execution."""
        collector = PluginMetricsCollector("test.plugin")

        with pytest.raises(ValueError):
            with collector.time_execution("process"):
                raise ValueError("Test error")

        stats = collector.get_execution_stats("process")
        assert stats["process"].error_count == 1
        assert stats["process"].success_count == 0

    def test_mark_error(self):
        """Test marking execution as error."""
        collector = PluginMetricsCollector("test.plugin")

        with collector.time_execution("process") as timer:
            timer.mark_error("Custom error")

        stats = collector.get_execution_stats("process")
        assert stats["process"].error_count == 1


class TestGlobalRegistry:
    """Tests for global collector registry."""

    def test_get_metrics_collector(self):
        """Test getting collector from registry."""
        collector = get_metrics_collector("test.global.plugin")
        assert isinstance(collector, PluginMetricsCollector)
        assert collector.plugin_id == "test.global.plugin"

    def test_get_same_collector(self):
        """Test getting same collector returns cached instance."""
        collector1 = get_metrics_collector("test.cached.plugin")
        collector2 = get_metrics_collector("test.cached.plugin")
        assert collector1 is collector2

    def test_get_all_collectors(self):
        """Test getting all collectors."""
        get_metrics_collector("test.all.plugin1")
        get_metrics_collector("test.all.plugin2")

        all_collectors = get_all_collectors()
        assert "test.all.plugin1" in all_collectors
        assert "test.all.plugin2" in all_collectors

    def test_reset_single_plugin(self):
        """Test resetting single plugin metrics."""
        collector = get_metrics_collector("test.reset.single")
        collector.record_execution("method", 100.0)

        reset_metrics("test.reset.single")

        stats = collector.get_stats()
        assert stats["summary"]["total_calls"] == 0

    def test_reset_all_plugins(self):
        """Test resetting all plugin metrics."""
        collector1 = get_metrics_collector("test.reset.all1")
        collector2 = get_metrics_collector("test.reset.all2")
        collector1.record_execution("method", 100.0)
        collector2.record_execution("method", 100.0)

        reset_metrics()

        assert collector1.get_stats()["summary"]["total_calls"] == 0
        assert collector2.get_stats()["summary"]["total_calls"] == 0
