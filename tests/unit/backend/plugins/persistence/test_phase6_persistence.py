"""
Unit tests for Phase 6 persistence layer.

Tests Q-2 (anomaly baselines), D-1 (analytics), C-1 (privacy) persistence.
"""

import os
import tempfile
from datetime import datetime, timedelta

import pytest

from backend.plugins.persistence.phase6_persistence import (
    Phase6Persistence,
    RetentionPolicy,
    reset_phase6_persistence,
)


@pytest.fixture
def temp_db():
    """Create a temporary database file for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def persistence(temp_db):
    """Create a Phase6Persistence instance for testing."""
    reset_phase6_persistence()
    p = Phase6Persistence(temp_db)
    yield p
    reset_phase6_persistence()


class TestAnomalyBaselinePersistence:
    """Tests for Q-2: Anomaly baseline persistence."""

    def test_save_and_get_baseline(self, persistence):
        """Test saving and retrieving a baseline."""
        rows = persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="latency_ms",
            mean=50.0,
            std=10.0,
            min_val=20.0,
            max_val=100.0,
            q1=40.0,
            median=50.0,
            q3=60.0,
            sample_count=100,
        )
        
        assert rows == 1
        
        baseline = persistence.get_baseline("test-plugin", "latency_ms")
        assert baseline is not None
        assert baseline.plugin_id == "test-plugin"
        assert baseline.metric_name == "latency_ms"
        assert baseline.mean == 50.0
        assert baseline.std == 10.0
        assert baseline.min_val == 20.0
        assert baseline.max_val == 100.0
        assert baseline.q1 == 40.0
        assert baseline.median == 50.0
        assert baseline.q3 == 60.0
        assert baseline.sample_count == 100

    def test_get_nonexistent_baseline(self, persistence):
        """Test retrieving a baseline that doesn't exist."""
        baseline = persistence.get_baseline("nonexistent", "metric")
        assert baseline is None

    def test_update_existing_baseline(self, persistence):
        """Test updating an existing baseline."""
        persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="latency_ms",
            mean=50.0,
            std=10.0,
            min_val=20.0,
            max_val=100.0,
            q1=40.0,
            median=50.0,
            q3=60.0,
            sample_count=100,
        )
        
        persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="latency_ms",
            mean=60.0,
            std=15.0,
            min_val=25.0,
            max_val=120.0,
            q1=45.0,
            median=55.0,
            q3=65.0,
            sample_count=200,
        )
        
        baseline = persistence.get_baseline("test-plugin", "latency_ms")
        assert baseline.mean == 60.0
        assert baseline.std == 15.0

    def test_get_all_baselines(self, persistence):
        """Test retrieving all baselines for a plugin."""
        persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="latency_ms",
            mean=50.0,
            std=10.0,
            min_val=20.0,
            max_val=100.0,
            q1=40.0,
            median=50.0,
            q3=60.0,
            sample_count=100,
        )
        persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="memory_mb",
            mean=256.0,
            std=32.0,
            min_val=128.0,
            max_val=512.0,
            q1=192.0,
            median=256.0,
            q3=320.0,
            sample_count=50,
        )
        persistence.save_baseline(
            plugin_id="other-plugin",
            metric_name="latency_ms",
            mean=30.0,
            std=5.0,
            min_val=20.0,
            max_val=50.0,
            q1=25.0,
            median=30.0,
            q3=35.0,
            sample_count=75,
        )
        
        baselines = persistence.get_all_baselines("test-plugin")
        assert len(baselines) == 2
        metric_names = {b.metric_name for b in baselines}
        assert metric_names == {"latency_ms", "memory_mb"}

    def test_delete_baseline(self, persistence):
        """Test deleting a baseline."""
        persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="latency_ms",
            mean=50.0,
            std=10.0,
            min_val=20.0,
            max_val=100.0,
            q1=40.0,
            median=50.0,
            q3=60.0,
            sample_count=100,
        )
        persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="memory_mb",
            mean=256.0,
            std=32.0,
            min_val=128.0,
            max_val=512.0,
            q1=192.0,
            median=256.0,
            q3=320.0,
            sample_count=50,
        )
        
        deleted = persistence.delete_baseline("test-plugin", "latency_ms")
        assert deleted == 1
        
        remaining = persistence.get_all_baselines("test-plugin")
        assert len(remaining) == 1
        assert remaining[0].metric_name == "memory_mb"

    def test_delete_all_baselines_for_plugin(self, persistence):
        """Test deleting all baselines for a plugin."""
        persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="latency_ms",
            mean=50.0,
            std=10.0,
            min_val=20.0,
            max_val=100.0,
            q1=40.0,
            median=50.0,
            q3=60.0,
            sample_count=100,
        )
        persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="memory_mb",
            mean=256.0,
            std=32.0,
            min_val=128.0,
            max_val=512.0,
            q1=192.0,
            median=256.0,
            q3=320.0,
            sample_count=50,
        )
        
        deleted = persistence.delete_baseline("test-plugin")
        assert deleted == 2
        
        remaining = persistence.get_all_baselines("test-plugin")
        assert len(remaining) == 0


class TestAnalyticsPersistence:
    """Tests for D-1: Analytics persistence."""

    def test_record_and_get_events(self, persistence):
        """Test recording and retrieving analytics events."""
        rows = persistence.record_analytics_event(
            plugin_id="test-plugin",
            event_type="install",
            user_id="user-123",
            metadata={"source": "marketplace"},
        )
        
        assert rows == 1
        
        events = persistence.get_analytics_events(plugin_id="test-plugin")
        assert len(events) == 1
        assert events[0].plugin_id == "test-plugin"
        assert events[0].event_type == "install"
        assert events[0].user_id == "user-123"
        assert events[0].metadata == {"source": "marketplace"}

    def test_filter_events_by_type(self, persistence):
        """Test filtering events by type."""
        persistence.record_analytics_event(
            plugin_id="test-plugin",
            event_type="install",
        )
        persistence.record_analytics_event(
            plugin_id="test-plugin",
            event_type="use",
        )
        persistence.record_analytics_event(
            plugin_id="test-plugin",
            event_type="error",
        )
        
        events = persistence.get_analytics_events(
            plugin_id="test-plugin",
            event_type="use",
        )
        assert len(events) == 1
        assert events[0].event_type == "use"

    def test_events_limit(self, persistence):
        """Test limiting number of events returned."""
        for i in range(10):
            persistence.record_analytics_event(
                plugin_id="test-plugin",
                event_type="use",
            )
        
        events = persistence.get_analytics_events(
            plugin_id="test-plugin",
            limit=5,
        )
        assert len(events) == 5

    def test_update_and_get_metrics(self, persistence):
        """Test updating and retrieving plugin metrics."""
        persistence.update_plugin_metrics(
            plugin_id="test-plugin",
            total_installs=100,
            active_installs=90,
            avg_rating=4.5,
        )
        
        metrics = persistence.get_plugin_metrics("test-plugin")
        assert metrics is not None
        assert metrics.plugin_id == "test-plugin"
        assert metrics.total_installs == 100
        assert metrics.active_installs == 90
        assert metrics.avg_rating == 4.5

    def test_get_nonexistent_metrics(self, persistence):
        """Test retrieving metrics that don't exist."""
        metrics = persistence.get_plugin_metrics("nonexistent")
        assert metrics is None


class TestPrivacyPersistence:
    """Tests for C-1: Privacy metadata persistence."""

    def test_save_and_get_consent(self, persistence):
        """Test saving and retrieving consent records."""
        rows = persistence.save_consent(
            user_id="user-123",
            plugin_id="test-plugin",
            privacy_level="basic",
            categories=["analytics", "personalization"],
        )
        
        assert rows == 1
        
        consent = persistence.get_consent("user-123", "test-plugin")
        assert consent is not None
        assert consent.user_id == "user-123"
        assert consent.plugin_id == "test-plugin"
        assert consent.privacy_level == "basic"
        assert consent.revoked_at is None  # Active consent has no revocation date

    def test_get_nonexistent_consent(self, persistence):
        """Test retrieving consent that doesn't exist."""
        consent = persistence.get_consent("nonexistent", "nonexistent")
        assert consent is None

    def test_revoke_consent(self, persistence):
        """Test revoking consent."""
        persistence.save_consent(
            user_id="user-123",
            plugin_id="test-plugin",
            privacy_level="basic",
            categories=["analytics"],
        )
        
        rows = persistence.revoke_consent("user-123", "test-plugin")
        assert rows == 1  # revoke_consent returns rows affected
        
        consent = persistence.get_consent("user-123", "test-plugin")
        assert consent is not None
        assert consent.revoked_at is not None  # Revoked consent has revocation date

    def test_get_user_consents(self, persistence):
        """Test retrieving all active consents for a user."""
        persistence.save_consent(
            user_id="user-123",
            plugin_id="plugin-1",
            privacy_level="basic",
            categories=["analytics"],
        )
        persistence.save_consent(
            user_id="user-123",
            plugin_id="plugin-2",
            privacy_level="full",
            categories=["personalization"],
        )
        persistence.save_consent(
            user_id="other-user",
            plugin_id="plugin-1",
            privacy_level="basic",
            categories=["analytics"],
        )
        
        consents = persistence.get_user_consents("user-123")
        assert len(consents) == 2
        plugin_ids = {c.plugin_id for c in consents}
        assert plugin_ids == {"plugin-1", "plugin-2"}

    def test_save_and_get_declaration(self, persistence):
        """Test saving and retrieving data declarations."""
        rows = persistence.save_data_declaration(
            plugin_id="test-plugin",
            categories=["usage", "analytics"],
            retention_days=90,
            required_consent_level="basic",
        )
        
        assert rows == 1
        
        decl = persistence.get_data_declaration("test-plugin")
        assert decl is not None
        assert decl.plugin_id == "test-plugin"
        assert decl.categories == ["usage", "analytics"]
        assert decl.retention_days == 90
        assert decl.required_consent_level == "basic"

    def test_get_nonexistent_declaration(self, persistence):
        """Test retrieving declaration that doesn't exist."""
        decl = persistence.get_data_declaration("nonexistent")
        assert decl is None


class TestRetentionAndMaintenance:
    """Tests for retention policy and maintenance operations."""

    def test_apply_retention_policy(self, persistence):
        """Test applying retention policy."""
        result = persistence.apply_retention_policy()
        
        assert "analytics_events" in result

    def test_get_storage_stats(self, persistence):
        """Test getting storage statistics."""
        persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="latency",
            mean=50.0,
            std=10.0,
            min_val=20.0,
            max_val=100.0,
            q1=40.0,
            median=50.0,
            q3=60.0,
            sample_count=100,
        )
        persistence.record_analytics_event(
            plugin_id="test-plugin",
            event_type="install",
        )
        
        stats = persistence.get_storage_stats()
        
        assert "baselines_count" in stats
        assert "events_count" in stats
        assert "metrics_count" in stats
        assert "active_consents" in stats  # actual key name
        assert "declarations_count" in stats
        assert "file_size_bytes" in stats  # actual key name
        
        assert stats["baselines_count"] == 1
        assert stats["events_count"] == 1

    def test_vacuum(self, persistence):
        """Test database vacuum operation."""
        persistence.save_baseline(
            plugin_id="test-plugin",
            metric_name="latency",
            mean=50.0,
            std=10.0,
            min_val=20.0,
            max_val=100.0,
            q1=40.0,
            median=50.0,
            q3=60.0,
            sample_count=100,
        )
        persistence.delete_baseline("test-plugin")
        
        # vacuum() returns None, just verify it doesn't raise
        persistence.vacuum()
