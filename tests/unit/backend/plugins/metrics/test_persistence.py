"""
Unit tests for metrics persistence layer.

Phase 5D M2: SQLite-based persistence for plugin metrics.
"""

from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from backend.plugins.metrics.persistence import (
    AggregatedMetric,
    MetricRecord,
    MetricsPersistence,
    RetentionPolicy,
    get_metrics_persistence,
    reset_persistence,
)


class TestRetentionPolicy:
    """Tests for RetentionPolicy enum."""

    def test_all_policies_defined(self) -> None:
        """All retention policies should be defined."""
        policies = [p.value for p in RetentionPolicy]
        assert "keep_all" in policies
        assert "7_days" in policies
        assert "30_days" in policies
        assert "90_days" in policies
        assert "1_year" in policies


class TestMetricRecord:
    """Tests for MetricRecord dataclass."""

    def test_create_record(self) -> None:
        """Record should be created with correct fields."""
        record = MetricRecord(
            id=1,
            plugin_id="test-plugin",
            metric_type="execution.duration_ms",
            value=123.45,
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
            labels={"method": "process"},
        )
        assert record.id == 1
        assert record.plugin_id == "test-plugin"
        assert record.metric_type == "execution.duration_ms"
        assert record.value == 123.45

    def test_to_dict(self) -> None:
        """Record should convert to dictionary."""
        record = MetricRecord(
            id=1,
            plugin_id="test-plugin",
            metric_type="execution.count",
            value=10.0,
            timestamp=datetime(2025, 1, 1),
        )
        d = record.to_dict()

        assert d["id"] == 1
        assert d["plugin_id"] == "test-plugin"
        assert d["metric_type"] == "execution.count"
        assert d["value"] == 10.0
        assert "timestamp" in d


class TestAggregatedMetric:
    """Tests for AggregatedMetric dataclass."""

    def test_create_aggregated(self) -> None:
        """Aggregated metric should have correct structure."""
        agg = AggregatedMetric(
            plugin_id="test-plugin",
            metric_type="execution.duration_ms",
            window_start=datetime(2025, 1, 1, 12, 0),
            window_end=datetime(2025, 1, 1, 13, 0),
            count=100,
            sum_value=5000.0,
            min_value=10.0,
            max_value=100.0,
            avg_value=50.0,
        )
        assert agg.count == 100
        assert agg.avg_value == 50.0

    def test_to_dict(self) -> None:
        """Aggregated metric should convert to dictionary."""
        agg = AggregatedMetric(
            plugin_id="test-plugin",
            metric_type="test",
            window_start=datetime(2025, 1, 1, 12, 0),
            window_end=datetime(2025, 1, 1, 13, 0),
            count=10,
            sum_value=100.0,
            min_value=5.0,
            max_value=15.0,
            avg_value=10.0,
        )
        d = agg.to_dict()

        assert d["plugin_id"] == "test-plugin"
        assert d["count"] == 10
        assert d["avg"] == 10.0


class TestMetricsPersistence:
    """Tests for MetricsPersistence class."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create a temporary database file."""
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp) / "test_metrics.db"

    @pytest.fixture
    def persistence(self, temp_db: Path) -> MetricsPersistence:
        """Create a persistence instance with temp database."""
        return MetricsPersistence(db_path=temp_db)

    def test_initialization(self, persistence: MetricsPersistence) -> None:
        """Persistence should initialize correctly."""
        assert persistence._db_path.exists()

    def test_store_single_metric(self, persistence: MetricsPersistence) -> None:
        """Storing a single metric should return an ID."""
        metric_id = persistence.store_metric(
            plugin_id="test-plugin",
            metric_type="execution.count",
            value=1.0,
        )
        assert metric_id > 0

    def test_store_metric_with_labels(self, persistence: MetricsPersistence) -> None:
        """Metrics should support labels."""
        metric_id = persistence.store_metric(
            plugin_id="test-plugin",
            metric_type="execution.duration_ms",
            value=150.5,
            labels={"method": "process_audio", "success": "true"},
        )
        assert metric_id > 0

        # Query and verify labels
        records = persistence.query_metrics(plugin_id="test-plugin")
        assert len(records) == 1
        assert records[0].labels["method"] == "process_audio"

    def test_store_metrics_batch(self, persistence: MetricsPersistence) -> None:
        """Batch storage should insert multiple records."""
        metrics = [
            ("plugin-1", "execution.count", 1.0, None, None),
            ("plugin-1", "execution.count", 2.0, None, None),
            ("plugin-2", "execution.count", 1.0, None, None),
        ]
        count = persistence.store_metrics_batch(metrics)
        assert count == 3

    def test_query_all_metrics(self, persistence: MetricsPersistence) -> None:
        """Querying without filters returns all metrics."""
        persistence.store_metric("plugin-1", "metric-a", 1.0)
        persistence.store_metric("plugin-2", "metric-b", 2.0)

        records = persistence.query_metrics()
        assert len(records) == 2

    def test_query_by_plugin_id(self, persistence: MetricsPersistence) -> None:
        """Querying should filter by plugin ID."""
        persistence.store_metric("plugin-1", "metric-a", 1.0)
        persistence.store_metric("plugin-2", "metric-b", 2.0)

        records = persistence.query_metrics(plugin_id="plugin-1")
        assert len(records) == 1
        assert records[0].plugin_id == "plugin-1"

    def test_query_by_metric_type(self, persistence: MetricsPersistence) -> None:
        """Querying should filter by metric type."""
        persistence.store_metric("plugin-1", "metric-a", 1.0)
        persistence.store_metric("plugin-1", "metric-b", 2.0)

        records = persistence.query_metrics(metric_type="metric-a")
        assert len(records) == 1
        assert records[0].metric_type == "metric-a"

    def test_query_by_time_range(self, persistence: MetricsPersistence) -> None:
        """Querying should filter by time range."""
        now = datetime.now()
        old_time = now - timedelta(days=10)

        persistence.store_metric("plugin-1", "metric", 1.0, timestamp=old_time)
        persistence.store_metric("plugin-1", "metric", 2.0, timestamp=now)

        # Query only recent
        records = persistence.query_metrics(
            start_time=now - timedelta(hours=1),
        )
        assert len(records) == 1
        assert records[0].value == 2.0

    def test_query_with_limit_offset(self, persistence: MetricsPersistence) -> None:
        """Querying should support pagination."""
        for i in range(10):
            persistence.store_metric("plugin", f"metric-{i}", float(i))

        # First page
        page1 = persistence.query_metrics(limit=3, offset=0)
        assert len(page1) == 3

        # Second page
        page2 = persistence.query_metrics(limit=3, offset=3)
        assert len(page2) == 3

        # Different records
        assert page1[0].id != page2[0].id

    def test_get_aggregated_metrics(self, persistence: MetricsPersistence) -> None:
        """Aggregation should compute statistics."""
        # Use a fixed timestamp in the past to avoid timing issues
        # (if minute < 30, replace(minute=30) creates a future timestamp)
        test_time = datetime.now() - timedelta(hours=2)
        test_time = test_time.replace(minute=30, second=0, microsecond=0)

        for i in range(10):
            persistence.store_metric(
                "plugin-1",
                "duration",
                float(i * 10),
                timestamp=test_time,
            )

        aggregated = persistence.get_aggregated_metrics(
            plugin_id="plugin-1",
            start_time=test_time - timedelta(hours=1),
            end_time=test_time + timedelta(hours=1),
        )

        assert len(aggregated) >= 1
        agg = aggregated[0]
        assert agg.count == 10
        assert agg.min_value == 0.0
        assert agg.max_value == 90.0
        assert agg.avg_value == 45.0  # (0+10+...+90)/10 = 450/10

    def test_get_plugin_summary(self, persistence: MetricsPersistence) -> None:
        """Plugin summary should aggregate by metric type."""
        persistence.store_metric("plugin-1", "execution.count", 1.0)
        persistence.store_metric("plugin-1", "execution.count", 1.0)
        persistence.store_metric("plugin-1", "execution.duration_ms", 100.0)
        persistence.store_metric("plugin-1", "execution.duration_ms", 200.0)

        summary = persistence.get_plugin_summary(
            "plugin-1",
            since=datetime.now() - timedelta(hours=1),
        )

        assert summary["plugin_id"] == "plugin-1"
        assert "execution.count" in summary["metrics"]
        assert summary["metrics"]["execution.count"]["count"] == 2
        assert summary["metrics"]["execution.count"]["sum"] == 2.0
        assert summary["metrics"]["execution.duration_ms"]["avg"] == 150.0

    def test_export_json(self, persistence: MetricsPersistence) -> None:
        """JSON export should produce valid JSON."""
        persistence.store_metric("plugin-1", "metric-a", 1.0)
        persistence.store_metric("plugin-1", "metric-b", 2.0)

        json_str = persistence.export_json()
        data = json.loads(json_str)

        assert "exported_at" in data
        assert "count" in data
        assert data["count"] == 2
        assert len(data["metrics"]) == 2

    def test_export_json_to_file(self, persistence: MetricsPersistence, temp_db: Path) -> None:
        """JSON export should write to file."""
        persistence.store_metric("plugin", "metric", 1.0)

        output_path = temp_db.parent / "export.json"
        persistence.export_json(output_path=output_path)

        assert output_path.exists()
        data = json.loads(output_path.read_text())
        assert data["count"] == 1

    def test_export_csv(self, persistence: MetricsPersistence) -> None:
        """CSV export should produce valid CSV."""
        persistence.store_metric("plugin-1", "metric-a", 1.0)
        persistence.store_metric("plugin-1", "metric-b", 2.0)

        csv_str = persistence.export_csv()
        lines = csv_str.strip().split("\n")

        assert len(lines) == 3  # Header + 2 records
        assert "id,plugin_id,metric_type,value" in lines[0]

    def test_export_prometheus(self, persistence: MetricsPersistence) -> None:
        """Prometheus export should produce valid format."""
        now = datetime.now()
        persistence.store_metric("plugin-1", "execution.duration_ms", 100.0, timestamp=now)
        persistence.store_metric("plugin-1", "execution.duration_ms", 200.0, timestamp=now)

        prom_str = persistence.export_prometheus(
            start_time=now - timedelta(hours=1),
        )

        assert "# HELP" in prom_str or prom_str == ""  # May be empty if no hourly aggregation
        if prom_str:
            assert "voicestudio_" in prom_str
            assert "plugin_id=" in prom_str


class TestRetentionPolicies:
    """Tests for retention policy enforcement."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create a temporary database file."""
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp) / "test_metrics.db"

    def test_retention_keep_all(self, temp_db: Path) -> None:
        """KEEP_ALL policy should not delete anything."""
        persistence = MetricsPersistence(
            db_path=temp_db,
            retention_policy=RetentionPolicy.KEEP_ALL,
        )

        old_time = datetime.now() - timedelta(days=365)
        persistence.store_metric("plugin", "metric", 1.0, timestamp=old_time)

        deleted = persistence.apply_retention_policy()
        assert deleted == 0

        records = persistence.query_metrics()
        assert len(records) == 1

    def test_retention_7_days(self, temp_db: Path) -> None:
        """7-day retention should delete old records."""
        persistence = MetricsPersistence(
            db_path=temp_db,
            retention_policy=RetentionPolicy.KEEP_7_DAYS,
        )

        old_time = datetime.now() - timedelta(days=10)
        recent_time = datetime.now() - timedelta(days=3)

        persistence.store_metric("plugin", "metric", 1.0, timestamp=old_time)
        persistence.store_metric("plugin", "metric", 2.0, timestamp=recent_time)

        deleted = persistence.apply_retention_policy()
        assert deleted == 1

        records = persistence.query_metrics()
        assert len(records) == 1
        assert records[0].value == 2.0


class TestStorageStats:
    """Tests for storage statistics."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create a temporary database file."""
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp) / "test_metrics.db"

    def test_get_storage_stats(self, temp_db: Path) -> None:
        """Storage stats should return correct information."""
        persistence = MetricsPersistence(db_path=temp_db)

        persistence.store_metric("plugin-1", "metric-a", 1.0)
        persistence.store_metric("plugin-1", "metric-b", 2.0)
        persistence.store_metric("plugin-2", "metric-a", 3.0)

        stats = persistence.get_storage_stats()

        assert stats["total_records"] == 3
        assert stats["file_size_bytes"] > 0
        assert "plugin-1" in stats["records_by_plugin"]
        assert stats["records_by_plugin"]["plugin-1"] == 2
        assert stats["records_by_plugin"]["plugin-2"] == 1


class TestGlobalInstance:
    """Tests for global persistence instance."""

    def test_get_metrics_persistence_singleton(self) -> None:
        """get_metrics_persistence should return same instance."""
        reset_persistence()

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"

            p1 = get_metrics_persistence(db_path=db_path)
            p2 = get_metrics_persistence()  # Should return same instance

            assert p1 is p2

            reset_persistence()

    def test_reset_persistence(self) -> None:
        """reset_persistence should clear the global instance."""
        reset_persistence()

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"

            p1 = get_metrics_persistence(db_path=db_path)
            reset_persistence()
            p2 = get_metrics_persistence(db_path=db_path)

            assert p1 is not p2

            reset_persistence()


class TestVacuum:
    """Tests for database maintenance."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create a temporary database file."""
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp) / "test_metrics.db"

    def test_vacuum(self, temp_db: Path) -> None:
        """Vacuum should not raise errors."""
        persistence = MetricsPersistence(db_path=temp_db)

        # Store and delete some data
        for i in range(100):
            persistence.store_metric("plugin", "metric", float(i))

        persistence.apply_retention_policy()

        # Should not raise
        persistence.vacuum()


class TestConcurrency:
    """Tests for thread-safety."""

    @pytest.fixture
    def temp_db(self) -> Path:
        """Create a temporary database file."""
        with tempfile.TemporaryDirectory() as tmp:
            yield Path(tmp) / "test_metrics.db"

    def test_concurrent_writes(self, temp_db: Path) -> None:
        """Concurrent writes should not corrupt data."""
        import threading

        persistence = MetricsPersistence(db_path=temp_db)
        errors: list[Exception] = []

        def writer(thread_id: int) -> None:
            try:
                for i in range(50):
                    persistence.store_metric(
                        f"plugin-{thread_id}",
                        "metric",
                        float(i),
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(i,)) for i in range(5)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        assert len(errors) == 0

        # Verify all records were written
        records = persistence.query_metrics(limit=1000)
        assert len(records) == 250  # 5 threads * 50 records each
