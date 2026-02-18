"""
Tests for Plugin Metrics Exporter.

Phase 4 Enhancement: Tests for metrics export formats.
"""

import json
from datetime import datetime

import pytest

from backend.plugins.metrics.aggregator import MetricsAggregator
from backend.plugins.metrics.collector import (
    PluginMetricsCollector,
    get_metrics_collector,
    reset_metrics,
)
from backend.plugins.metrics.exporter import MetricsExporter, MetricsFormat


class TestMetricsFormat:
    """Tests for MetricsFormat enum."""

    def test_formats_exist(self):
        """Test all formats exist."""
        assert MetricsFormat.JSON.value == "json"
        assert MetricsFormat.PROMETHEUS.value == "prometheus"
        assert MetricsFormat.CSV.value == "csv"
        assert MetricsFormat.INFLUXDB.value == "influxdb"


class TestMetricsExporter:
    """Tests for MetricsExporter."""

    @pytest.fixture(autouse=True)
    def reset_collectors(self):
        """Reset collectors before each test."""
        reset_metrics()
        yield

    @pytest.fixture
    def exporter(self):
        """Create exporter with fresh aggregator."""
        return MetricsExporter(aggregator=MetricsAggregator())

    @pytest.fixture
    def populated_collector(self):
        """Create collector with test data."""
        collector = get_metrics_collector("test.export.plugin")
        collector.record_execution("process_audio", duration_ms=100.0)
        collector.record_execution("process_audio", duration_ms=150.0)
        collector.record_execution("process_audio", duration_ms=50.0, success=False)
        collector.record_memory_usage(1024 * 1024)
        collector.record_ipc_request("host.audio.play", latency_ms=25.0)
        collector.record_permission_check("audio.playback", granted=True)
        collector.record_start()
        return collector

    def test_export_json(self, exporter, populated_collector):
        """Test JSON export."""
        result = exporter.export(MetricsFormat.JSON)

        data = json.loads(result)
        assert "system" in data
        assert "plugins" in data
        assert "test.export.plugin" in data["plugins"]

    def test_export_json_single_plugin(self, exporter, populated_collector):
        """Test JSON export for single plugin."""
        result = exporter.export(
            MetricsFormat.JSON,
            plugin_id="test.export.plugin",
        )

        data = json.loads(result)
        assert data["plugin_id"] == "test.export.plugin"
        assert "stats" in data
        assert "metrics" in data

    def test_export_json_not_found(self, exporter):
        """Test JSON export for non-existent plugin."""
        result = exporter.export(
            MetricsFormat.JSON,
            plugin_id="nonexistent.plugin",
        )

        data = json.loads(result)
        assert "error" in data

    def test_to_json_pretty(self, exporter, populated_collector):
        """Test pretty JSON export."""
        result = exporter.to_json(pretty=True)
        assert "\n" in result  # Pretty printed

        result = exporter.to_json(pretty=False)
        lines = result.split("\n")
        assert len(lines) == 1  # Not pretty printed

    def test_export_prometheus(self, exporter, populated_collector):
        """Test Prometheus export."""
        result = exporter.export(MetricsFormat.PROMETHEUS)

        # Check metric names
        assert "voicestudio_plugin_calls_total" in result
        assert "voicestudio_plugin_errors_total" in result
        assert "voicestudio_plugin_duration_ms_sum" in result
        assert "voicestudio_plugin_ipc_requests_total" in result

        # Check labels
        assert 'plugin_id="test.export.plugin"' in result

    def test_export_prometheus_quantiles(self, exporter, populated_collector):
        """Test Prometheus export includes quantiles."""
        result = exporter.export(MetricsFormat.PROMETHEUS)

        assert 'quantile="0.5"' in result
        assert 'quantile="0.95"' in result
        assert 'quantile="0.99"' in result

    def test_export_prometheus_single_plugin(self, exporter, populated_collector):
        """Test Prometheus export for single plugin."""
        # Add another plugin
        other = get_metrics_collector("test.other.plugin")
        other.record_execution("method", 100.0)

        result = exporter.export(
            MetricsFormat.PROMETHEUS,
            plugin_id="test.export.plugin",
        )

        assert "test.export.plugin" in result
        assert "test.other.plugin" not in result

    def test_export_csv(self, exporter, populated_collector):
        """Test CSV export."""
        result = exporter.export(MetricsFormat.CSV)

        lines = result.strip().split("\n")

        # Check header
        assert lines[0] == "timestamp,plugin_id,metric_type,value,labels"

        # Check data rows exist
        assert len(lines) > 1

        # Check plugin ID in data
        assert any("test.export.plugin" in line for line in lines[1:])

    def test_export_csv_single_plugin(self, exporter, populated_collector):
        """Test CSV export for single plugin."""
        # Add another plugin
        other = get_metrics_collector("test.csv.other")
        other.record_execution("method", 100.0)

        result = exporter.export(
            MetricsFormat.CSV,
            plugin_id="test.export.plugin",
        )

        assert "test.export.plugin" in result
        assert "test.csv.other" not in result

    def test_export_influxdb(self, exporter, populated_collector):
        """Test InfluxDB line protocol export."""
        result = exporter.export(MetricsFormat.INFLUXDB)

        lines = result.strip().split("\n")

        # Check measurement name
        assert all(line.startswith("voicestudio_plugin,") for line in lines if line)

        # Check tags
        assert any("plugin_id=" in line for line in lines)
        assert any("metric_type=" in line for line in lines)

        # Check value field
        assert any("value=" in line for line in lines)

        # Check timestamp (should be nanoseconds)
        for line in lines:
            if line:
                parts = line.split(" ")
                assert len(parts) == 3  # measurement,tags field timestamp
                timestamp = int(parts[2])
                assert timestamp > 1e18  # Nanosecond timestamp

    def test_export_influxdb_escaping(self, exporter, populated_collector):
        """Test InfluxDB escaping."""
        # Check that special characters are escaped
        result = exporter._escape_influx("test value,with=special")
        assert result == r"test\ value\,with\=special"

    def test_get_summary_report(self, exporter, populated_collector):
        """Test summary report generation."""
        report = exporter.get_summary_report()

        assert "VoiceStudio Plugin Metrics Summary" in report
        assert "System Overview:" in report
        assert "Total Plugins:" in report
        assert "Per-Plugin Details:" in report
        assert "test.export.plugin" in report

    def test_unsupported_format(self, exporter):
        """Test error on unsupported format."""
        with pytest.raises(ValueError):
            exporter.export("invalid_format")  # type: ignore
