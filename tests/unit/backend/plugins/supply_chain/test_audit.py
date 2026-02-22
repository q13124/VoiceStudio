"""
Unit tests for Plugin Audit Trail System.

Tests the AuditLogger, AuditEvent, and related classes.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.plugins.supply_chain.audit import (
    AuditCategory,
    AuditEvent,
    AuditEventType,
    AuditLogger,
    AuditQuery,
    AuditSeverity,
    AuditSummary,
    get_default_audit_logger,
    log_crash,
    log_installation,
    log_plugin_event,
    log_signature_verification,
    log_uninstallation,
    log_vulnerability_scan,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_db_path(tmp_path):
    """Create a temporary database path."""
    return tmp_path / "test_audit.db"


@pytest.fixture
def audit_logger(temp_db_path):
    """Create an audit logger instance."""
    return AuditLogger(temp_db_path)


@pytest.fixture
def sample_event():
    """Create a sample audit event."""
    return AuditEvent(
        event_type=AuditEventType.PLUGIN_INSTALLED,
        plugin_id="test-plugin",
        plugin_version="1.0.0",
        severity=AuditSeverity.INFO,
        category=AuditCategory.LIFECYCLE,
        details={"source": "gallery"},
    )


# =============================================================================
# Test AuditEventType Enum
# =============================================================================


class TestAuditEventType:
    """Tests for AuditEventType enum."""

    def test_lifecycle_events_defined(self):
        """Test lifecycle event types are defined."""
        assert hasattr(AuditEventType, "PLUGIN_INSTALLED")
        assert hasattr(AuditEventType, "PLUGIN_UNINSTALLED")
        assert hasattr(AuditEventType, "PLUGIN_UPDATED")

    def test_security_events_defined(self):
        """Test security event types are defined."""
        assert hasattr(AuditEventType, "SIGNATURE_VERIFIED")
        assert hasattr(AuditEventType, "SIGNATURE_FAILED")
        assert hasattr(AuditEventType, "VULNERABILITY_SCAN")

    def test_runtime_events_defined(self):
        """Test runtime event types are defined."""
        assert hasattr(AuditEventType, "PLUGIN_STARTED")
        assert hasattr(AuditEventType, "PLUGIN_STOPPED")
        assert hasattr(AuditEventType, "PLUGIN_CRASHED")


# =============================================================================
# Test AuditSeverity Enum
# =============================================================================


class TestAuditSeverity:
    """Tests for AuditSeverity enum."""

    def test_all_severities_defined(self):
        """Test all severity levels are defined."""
        expected = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for name in expected:
            assert hasattr(AuditSeverity, name)

    def test_severity_values(self):
        """Test severity values."""
        assert AuditSeverity.DEBUG.value == "debug"
        assert AuditSeverity.CRITICAL.value == "critical"


# =============================================================================
# Test AuditCategory Enum
# =============================================================================


class TestAuditCategory:
    """Tests for AuditCategory enum."""

    def test_all_categories_defined(self):
        """Test all categories are defined."""
        expected = ["LIFECYCLE", "RUNTIME", "SECURITY", "CONFIGURATION", "RESOURCE", "GENERAL"]
        for name in expected:
            assert hasattr(AuditCategory, name)


# =============================================================================
# Test AuditEvent
# =============================================================================


class TestAuditEvent:
    """Tests for AuditEvent dataclass."""

    def test_basic_creation(self, sample_event):
        """Test creating an audit event."""
        assert sample_event.plugin_id == "test-plugin"
        assert sample_event.event_type == AuditEventType.PLUGIN_INSTALLED
        assert sample_event.event_id != ""
        assert sample_event.timestamp != ""

    def test_auto_id_generation(self):
        """Test that event ID is auto-generated."""
        event = AuditEvent(
            event_type=AuditEventType.INFO,
            plugin_id="test",
        )
        assert event.event_id != ""
        assert len(event.event_id) == 36  # UUID format

    def test_to_dict(self, sample_event):
        """Test converting to dictionary."""
        data = sample_event.to_dict()

        assert data["plugin_id"] == "test-plugin"
        assert data["event_type"] == "plugin_installed"
        assert data["severity"] == "info"
        assert data["category"] == "lifecycle"
        assert "event_id" in data
        assert "timestamp" in data

    def test_to_json(self, sample_event):
        """Test converting to JSON."""
        json_str = sample_event.to_json()
        parsed = json.loads(json_str)

        assert parsed["plugin_id"] == "test-plugin"

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "event_id": "evt-123",
            "event_type": "plugin_started",
            "category": "runtime",
            "severity": "info",
            "plugin_id": "my-plugin",
            "plugin_version": "2.0.0",
            "timestamp": "2025-01-01T00:00:00+00:00",
            "details": {"pid": 1234},
            "metadata": {},
        }

        event = AuditEvent.from_dict(data)

        assert event.event_id == "evt-123"
        assert event.event_type == AuditEventType.PLUGIN_STARTED
        assert event.plugin_version == "2.0.0"


# =============================================================================
# Test AuditSummary
# =============================================================================


class TestAuditSummary:
    """Tests for AuditSummary dataclass."""

    def test_basic_creation(self):
        """Test creating a summary."""
        summary = AuditSummary(
            total_events=100,
            by_type={"plugin_installed": 50, "plugin_started": 50},
        )

        assert summary.total_events == 100
        assert len(summary.by_type) == 2

    def test_to_dict(self):
        """Test converting to dictionary."""
        summary = AuditSummary(total_events=10)
        data = summary.to_dict()

        assert data["total_events"] == 10
        assert "by_type" in data
        assert "by_severity" in data


# =============================================================================
# Test AuditQuery
# =============================================================================


class TestAuditQuery:
    """Tests for AuditQuery dataclass."""

    def test_default_values(self):
        """Test default query values."""
        query = AuditQuery()

        assert query.limit == 100
        assert query.offset == 0
        assert query.order_desc is True

    def test_with_filters(self):
        """Test query with filters."""
        query = AuditQuery(
            plugin_id="my-plugin",
            event_types=[AuditEventType.PLUGIN_INSTALLED],
            severities=[AuditSeverity.INFO, AuditSeverity.WARNING],
            limit=50,
        )

        assert query.plugin_id == "my-plugin"
        assert len(query.event_types) == 1
        assert len(query.severities) == 2


# =============================================================================
# Test AuditLogger
# =============================================================================


class TestAuditLogger:
    """Tests for AuditLogger class."""

    def test_create_logger(self, temp_db_path):
        """Test creating an audit logger."""
        logger = AuditLogger(temp_db_path)

        assert temp_db_path.exists()

    def test_log_event(self, audit_logger):
        """Test logging an event."""
        event = audit_logger.log_event(
            AuditEventType.PLUGIN_INSTALLED,
            plugin_id="test-plugin",
            plugin_version="1.0.0",
        )

        assert event.event_id != ""
        assert event.plugin_id == "test-plugin"

    def test_get_event(self, audit_logger):
        """Test retrieving a specific event."""
        event = audit_logger.log_event(
            AuditEventType.PLUGIN_STARTED,
            plugin_id="test",
        )

        retrieved = audit_logger.get_event(event.event_id)

        assert retrieved is not None
        assert retrieved.event_id == event.event_id

    def test_get_nonexistent_event(self, audit_logger):
        """Test retrieving a non-existent event."""
        result = audit_logger.get_event("nonexistent-id")
        assert result is None

    def test_query_events(self, audit_logger):
        """Test querying events."""
        # Log several events
        audit_logger.log_event(
            AuditEventType.PLUGIN_INSTALLED,
            plugin_id="plugin-a",
        )
        audit_logger.log_event(
            AuditEventType.PLUGIN_STARTED,
            plugin_id="plugin-a",
        )
        audit_logger.log_event(
            AuditEventType.PLUGIN_INSTALLED,
            plugin_id="plugin-b",
        )

        # Query for plugin-a
        events = audit_logger.query_events(AuditQuery(plugin_id="plugin-a"))

        assert len(events) == 2
        assert all(e.plugin_id == "plugin-a" for e in events)

    def test_query_by_event_type(self, audit_logger):
        """Test querying by event type."""
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="a")
        audit_logger.log_event(AuditEventType.PLUGIN_STARTED, plugin_id="b")
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="c")

        events = audit_logger.query_events(
            AuditQuery(event_types=[AuditEventType.PLUGIN_INSTALLED])
        )

        assert len(events) == 2
        assert all(e.event_type == AuditEventType.PLUGIN_INSTALLED for e in events)

    def test_query_by_severity(self, audit_logger):
        """Test querying by severity."""
        audit_logger.log_event(
            AuditEventType.INFO,
            plugin_id="a",
            severity=AuditSeverity.INFO,
        )
        audit_logger.log_event(
            AuditEventType.ERROR,
            plugin_id="b",
            severity=AuditSeverity.ERROR,
        )

        events = audit_logger.query_events(AuditQuery(severities=[AuditSeverity.ERROR]))

        assert len(events) == 1
        assert events[0].severity == AuditSeverity.ERROR

    def test_get_plugin_events(self, audit_logger):
        """Test getting events for a specific plugin."""
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="target")
        audit_logger.log_event(AuditEventType.PLUGIN_STARTED, plugin_id="target")
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="other")

        events = audit_logger.get_plugin_events("target")

        assert len(events) == 2

    def test_get_recent_events(self, audit_logger):
        """Test getting recent events."""
        for i in range(10):
            audit_logger.log_event(
                AuditEventType.INFO,
                plugin_id=f"plugin-{i}",
            )

        events = audit_logger.get_recent_events(limit=5)

        assert len(events) == 5

    def test_get_security_events(self, audit_logger):
        """Test getting security events."""
        audit_logger.log_event(
            AuditEventType.SIGNATURE_VERIFIED,
            plugin_id="a",
        )
        audit_logger.log_event(
            AuditEventType.PLUGIN_INSTALLED,
            plugin_id="b",
        )
        audit_logger.log_event(
            AuditEventType.VULNERABILITY_SCAN,
            plugin_id="c",
        )

        events = audit_logger.get_security_events()

        assert len(events) == 2
        assert all(e.category == AuditCategory.SECURITY for e in events)

    def test_category_auto_detection(self, audit_logger):
        """Test that category is auto-detected from event type."""
        event = audit_logger.log_event(
            AuditEventType.PLUGIN_INSTALLED,
            plugin_id="test",
        )
        assert event.category == AuditCategory.LIFECYCLE

        event = audit_logger.log_event(
            AuditEventType.PLUGIN_CRASHED,
            plugin_id="test",
        )
        assert event.category == AuditCategory.RUNTIME

        event = audit_logger.log_event(
            AuditEventType.SIGNATURE_FAILED,
            plugin_id="test",
        )
        assert event.category == AuditCategory.SECURITY

    def test_get_summary(self, audit_logger):
        """Test getting summary statistics."""
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="a")
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="b")
        audit_logger.log_event(AuditEventType.PLUGIN_STARTED, plugin_id="a")

        summary = audit_logger.get_summary()

        assert summary.total_events == 3
        assert summary.by_type.get("plugin_installed") == 2
        assert summary.by_type.get("plugin_started") == 1

    def test_get_summary_by_plugin(self, audit_logger):
        """Test getting summary for a specific plugin."""
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="target")
        audit_logger.log_event(AuditEventType.PLUGIN_STARTED, plugin_id="target")
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="other")

        summary = audit_logger.get_summary(plugin_id="target")

        assert summary.total_events == 2

    def test_count_events(self, audit_logger):
        """Test counting events."""
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="a")
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="b")
        audit_logger.log_event(AuditEventType.PLUGIN_STARTED, plugin_id="a")

        count = audit_logger.count_events()
        assert count == 3

        count = audit_logger.count_events(plugin_id="a")
        assert count == 2

        count = audit_logger.count_events(event_type=AuditEventType.PLUGIN_INSTALLED)
        assert count == 2

    def test_delete_old_events(self, audit_logger):
        """Test deleting old events."""
        # Log some events
        audit_logger.log_event(AuditEventType.INFO, plugin_id="a")
        audit_logger.log_event(AuditEventType.INFO, plugin_id="b")

        # Delete all events (using far future timestamp)
        deleted = audit_logger.delete_old_events("2099-01-01T00:00:00Z")

        assert deleted == 2
        assert audit_logger.count_events() == 0

    def test_export_events_json(self, audit_logger, tmp_path):
        """Test exporting events to JSON."""
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="a")
        audit_logger.log_event(AuditEventType.PLUGIN_STARTED, plugin_id="b")

        output_path = tmp_path / "export.json"
        count = audit_logger.export_events(output_path)

        assert count == 2
        assert output_path.exists()

        data = json.loads(output_path.read_text())
        assert len(data) == 2

    def test_export_events_csv(self, audit_logger, tmp_path):
        """Test exporting events to CSV."""
        audit_logger.log_event(AuditEventType.PLUGIN_INSTALLED, plugin_id="a")
        audit_logger.log_event(AuditEventType.PLUGIN_STARTED, plugin_id="b")

        output_path = tmp_path / "export.csv"
        count = audit_logger.export_events(output_path, format="csv")

        assert count == 2
        assert output_path.exists()

        lines = output_path.read_text().strip().split("\n")
        assert len(lines) == 3  # Header + 2 events

    def test_event_listener(self, audit_logger):
        """Test event listeners."""
        received_events = []

        def listener(event: AuditEvent):
            received_events.append(event)

        audit_logger.add_listener(listener)
        audit_logger.log_event(AuditEventType.INFO, plugin_id="test")

        assert len(received_events) == 1
        assert received_events[0].plugin_id == "test"

    def test_remove_listener(self, audit_logger):
        """Test removing event listeners."""
        received_events = []

        def listener(event: AuditEvent):
            received_events.append(event)

        audit_logger.add_listener(listener)
        audit_logger.log_event(AuditEventType.INFO, plugin_id="before")

        audit_logger.remove_listener(listener)
        audit_logger.log_event(AuditEventType.INFO, plugin_id="after")

        assert len(received_events) == 1


# =============================================================================
# Test Convenience Functions
# =============================================================================


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_log_installation(self, audit_logger):
        """Test log_installation helper."""
        event = log_installation(
            audit_logger,
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            source="gallery",
            signature_verified=True,
        )

        assert event.event_type == AuditEventType.PLUGIN_INSTALLED
        assert event.details["source"] == "gallery"
        assert event.details["signature_verified"] is True

    def test_log_uninstallation(self, audit_logger):
        """Test log_uninstallation helper."""
        event = log_uninstallation(
            audit_logger,
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            reason="user requested",
        )

        assert event.event_type == AuditEventType.PLUGIN_UNINSTALLED
        assert event.details["reason"] == "user requested"

    def test_log_vulnerability_scan(self, audit_logger):
        """Test log_vulnerability_scan helper."""
        event = log_vulnerability_scan(
            audit_logger,
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            vulnerability_count=5,
            critical_count=1,
            high_count=2,
        )

        assert event.event_type == AuditEventType.VULNERABILITY_SCAN
        assert event.severity == AuditSeverity.CRITICAL  # Has critical vulns
        assert event.details["total_vulnerabilities"] == 5

    def test_log_vulnerability_scan_no_critical(self, audit_logger):
        """Test vulnerability scan severity without critical issues."""
        event = log_vulnerability_scan(
            audit_logger,
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            vulnerability_count=3,
            critical_count=0,
            high_count=1,
        )

        assert event.severity == AuditSeverity.WARNING  # Has high vulns

    def test_log_signature_verification_success(self, audit_logger):
        """Test log_signature_verification for success."""
        event = log_signature_verification(
            audit_logger,
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            success=True,
            key_id="key-123",
        )

        assert event.event_type == AuditEventType.SIGNATURE_VERIFIED
        assert event.severity == AuditSeverity.INFO

    def test_log_signature_verification_failure(self, audit_logger):
        """Test log_signature_verification for failure."""
        event = log_signature_verification(
            audit_logger,
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            success=False,
            reason="invalid signature",
        )

        assert event.event_type == AuditEventType.SIGNATURE_FAILED
        assert event.severity == AuditSeverity.WARNING
        assert event.details["reason"] == "invalid signature"

    def test_log_crash(self, audit_logger):
        """Test log_crash helper."""
        event = log_crash(
            audit_logger,
            plugin_id="my-plugin",
            plugin_version="1.0.0",
            error_message="Out of memory",
            stack_trace="...",
        )

        assert event.event_type == AuditEventType.PLUGIN_CRASHED
        assert event.severity == AuditSeverity.ERROR
        assert "stack_trace" in event.details


# =============================================================================
# Test Default Logger
# =============================================================================


class TestDefaultLogger:
    """Tests for default audit logger."""

    def test_get_default_logger(self, tmp_path):
        """Test getting default audit logger."""
        # Reset the module-level logger
        import backend.plugins.supply_chain.audit as audit_module

        audit_module._default_logger = None

        with patch.dict("os.environ", {"VOICESTUDIO_DATA_PATH": str(tmp_path)}):
            logger = get_default_audit_logger()
            assert logger is not None

            # Should return same instance
            logger2 = get_default_audit_logger()
            assert logger is logger2

        # Clean up
        audit_module._default_logger = None
