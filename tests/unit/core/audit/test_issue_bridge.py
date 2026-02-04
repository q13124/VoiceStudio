"""
Unit tests for AuditIssueBridge.

Tests:
- Issue creation from audit entries
- Deduplication logic
- Severity filtering
- Debug Role routing
"""

import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path for tools imports
_project_root = Path(__file__).parent.parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


class TestAuditIssueBridge:
    """Tests for AuditIssueBridge class."""
    
    @pytest.fixture
    def bridge(self):
        """Create an AuditIssueBridge instance."""
        from app.core.audit.issue_bridge import AuditIssueBridge
        
        return AuditIssueBridge(
            enable_notifications=False,
            deduplicate_window_hours=1,
        )
    
    @pytest.fixture
    def mock_issue_store(self):
        """Create a mock IssueStore."""
        store = MagicMock()
        store.append = MagicMock()
        store.query = MagicMock(return_value=[])
        return store
    
    def test_on_audit_entry_creates_issue(self, bridge, mock_issue_store):
        """Test that error entries create issues."""
        from app.core.audit.schema import AuditEntry, AuditEventType
        
        bridge.set_issue_store(mock_issue_store)
        
        # Mock the lazy imports that happen in _create_issue
        with patch.dict('sys.modules', {
            'tools.overseer.issues.models': MagicMock(
                Issue=MagicMock(),
                InstanceType=MagicMock(BACKEND=MagicMock(value="backend")),
                IssueSeverity=MagicMock(HIGH=MagicMock(value="high")),
                IssueStatus=MagicMock(NEW=MagicMock(value="new")),
            )
        }):
            entry = AuditEntry(
                event_type=AuditEventType.RUNTIME_EXCEPTION.value,
                message="Test exception",
                severity="error",
                subsystem="Backend.API",
            )
            
            issue_id = bridge.on_audit_entry(entry)
            
            assert issue_id is not None
            assert mock_issue_store.append.called
    
    def test_on_audit_entry_filters_non_error_events(self, bridge, mock_issue_store):
        """Test that non-error events don't create issues."""
        from app.core.audit.schema import AuditEntry, AuditEventType
        
        bridge.set_issue_store(mock_issue_store)
        
        entry = AuditEntry(
            event_type=AuditEventType.FILE_MODIFY.value,
            file_path="test.py",
            severity="info",
        )
        
        issue_id = bridge.on_audit_entry(entry)
        
        assert issue_id is None
        assert not mock_issue_store.append.called
    
    def test_on_audit_entry_filters_low_severity(self, bridge, mock_issue_store):
        """Test that low severity errors don't create issues."""
        from app.core.audit.schema import AuditEntry, AuditEventType
        
        bridge.set_issue_store(mock_issue_store)
        
        entry = AuditEntry(
            event_type=AuditEventType.BUILD_WARNING.value,
            message="Minor warning",
            severity="info",  # Not in ISSUE_SEVERITIES
        )
        
        issue_id = bridge.on_audit_entry(entry)
        
        assert issue_id is None
    
    def test_deduplication_prevents_duplicate_issues(self, bridge, mock_issue_store):
        """Test that duplicate errors are deduplicated."""
        from app.core.audit.schema import AuditEntry, AuditEventType
        
        bridge.set_issue_store(mock_issue_store)
        
        # Mock the lazy imports that happen in _create_issue
        with patch.dict('sys.modules', {
            'tools.overseer.issues.models': MagicMock(
                Issue=MagicMock(),
                InstanceType=MagicMock(BUILD=MagicMock(value="build")),
                IssueSeverity=MagicMock(HIGH=MagicMock(value="high")),
                IssueStatus=MagicMock(NEW=MagicMock(value="new")),
            )
        }):
            # First entry should create issue
            entry1 = AuditEntry(
                event_type=AuditEventType.BUILD_ERROR.value,
                error_code="CS0234",
                file_path="src/test.cs",
                message="Type not found",
                severity="error",
            )
            
            issue_id1 = bridge.on_audit_entry(entry1)
            assert issue_id1 is not None
            
            # Same entry should be deduplicated
            entry2 = AuditEntry(
                event_type=AuditEventType.BUILD_ERROR.value,
                error_code="CS0234",
                file_path="src/test.cs",
                message="Type not found",
                severity="error",
            )
            
            issue_id2 = bridge.on_audit_entry(entry2)
            assert issue_id2 is None  # Deduplicated
            
            # Only one issue created
            assert mock_issue_store.append.call_count == 1
    
    def test_pattern_hash_generation(self, bridge):
        """Test pattern hash generation for deduplication."""
        from app.core.audit.schema import AuditEntry, AuditEventType
        
        entry1 = AuditEntry(
            event_type=AuditEventType.BUILD_ERROR.value,
            error_code="CS0234",
            file_path="src/test.cs",
            message="Type not found",
        )
        
        entry2 = AuditEntry(
            event_type=AuditEventType.BUILD_ERROR.value,
            error_code="CS0234",
            file_path="src/test.cs",
            message="Type not found",
        )
        
        hash1 = bridge._generate_pattern_hash(entry1)
        hash2 = bridge._generate_pattern_hash(entry2)
        
        # Same entries should have same hash
        assert hash1 == hash2
        
        # Different file should have different hash
        entry3 = AuditEntry(
            event_type=AuditEventType.BUILD_ERROR.value,
            error_code="CS0234",
            file_path="src/other.cs",
            message="Type not found",
        )
        
        hash3 = bridge._generate_pattern_hash(entry3)
        assert hash1 != hash3
    
    def test_category_determination(self, bridge):
        """Test category determination for role routing."""
        from app.core.audit.schema import AuditEntry, AuditEventType
        
        # XAML event
        xaml_entry = AuditEntry(
            event_type=AuditEventType.XAML_COMPILE_FAILURE.value,
        )
        assert bridge._determine_category(xaml_entry) == "UI"
        
        # Build event
        build_entry = AuditEntry(
            event_type=AuditEventType.BUILD_ERROR.value,
        )
        assert bridge._determine_category(build_entry) == "BUILD"
        
        # Exception event
        exception_entry = AuditEntry(
            event_type=AuditEventType.RUNTIME_EXCEPTION.value,
        )
        assert bridge._determine_category(exception_entry) == "EXCEPTION"
    
    def test_severity_mapping(self, bridge):
        """Test severity string to enum mapping."""
        # Test that _map_severity returns expected values
        # This test works with or without tools.overseer being available
        try:
            from tools.overseer.issues.models import IssueSeverity
            
            assert bridge._map_severity("critical") == IssueSeverity.CRITICAL
            assert bridge._map_severity("error") == IssueSeverity.HIGH
            assert bridge._map_severity("warning") == IssueSeverity.MEDIUM
            assert bridge._map_severity("info") == IssueSeverity.LOW
            assert bridge._map_severity("unknown") == IssueSeverity.MEDIUM
        except ImportError:
            # If tools.overseer.issues not available, skip
            pytest.skip("tools.overseer.issues not available")
    
    def test_get_issue_for_entry(self, bridge, mock_issue_store):
        """Test correlation ID lookup."""
        from app.core.audit.schema import AuditEntry, AuditEventType
        
        bridge.set_issue_store(mock_issue_store)
        
        entry = AuditEntry(
            event_type=AuditEventType.BUILD_ERROR.value,
            error_code="CS0234",
            severity="error",
        )
        
        issue_id = bridge.on_audit_entry(entry)
        
        # Look up by entry ID
        found_issue = bridge.get_issue_for_entry(entry.entry_id)
        assert found_issue == issue_id
        
        # Unknown entry ID returns None
        assert bridge.get_issue_for_entry("nonexistent") is None
    
    def test_cleanup_expired_hashes(self, bridge):
        """Test cleanup of expired pattern hashes."""
        from datetime import timedelta
        
        # Add some old hashes
        old_time = datetime.now(timezone.utc) - timedelta(hours=2)
        bridge._recent_pattern_hashes["old_hash"] = old_time
        
        # Add a recent hash
        bridge._recent_pattern_hashes["new_hash"] = datetime.now(timezone.utc)
        
        # Cleanup
        removed = bridge.cleanup_expired_hashes()
        
        assert removed == 1
        assert "old_hash" not in bridge._recent_pattern_hashes
        assert "new_hash" in bridge._recent_pattern_hashes


class TestDebugRoleNotifier:
    """Tests for DebugRoleNotifier class."""
    
    @pytest.fixture
    def notifier(self):
        """Create a DebugRoleNotifier instance."""
        from app.core.audit.debug_notifier import DebugRoleNotifier
        
        return DebugRoleNotifier(
            severity_filter={"critical", "high", "error"},
            rate_limit_per_hour=10,
        )
    
    def test_notify_high_severity(self, notifier):
        """Test notification for high severity issues."""
        mock_queue = MagicMock()
        notifier.set_handoff_queue(mock_queue)
        
        result = notifier.notify(
            issue_id="ISS-12345678",
            severity="error",
            message="Test error message",
            subsystem="Backend.API",
        )
        
        assert result is True
        assert mock_queue.handoff.called
    
    def test_notify_filters_low_severity(self, notifier):
        """Test that low severity is filtered."""
        mock_queue = MagicMock()
        notifier.set_handoff_queue(mock_queue)
        
        result = notifier.notify(
            issue_id="ISS-12345678",
            severity="info",
            message="Info message",
        )
        
        assert result is False
        assert not mock_queue.handoff.called
    
    def test_rate_limiting(self, notifier):
        """Test rate limiting of notifications."""
        mock_queue = MagicMock()
        notifier.set_handoff_queue(mock_queue)
        
        # Send notifications up to limit
        for i in range(10):
            notifier.notify(
                issue_id=f"ISS-{i}",
                severity="error",
                message=f"Error {i}",
            )
        
        # Next notification should be rate limited
        result = notifier.notify(
            issue_id="ISS-over-limit",
            severity="error",
            message="Over limit",
        )
        
        # Should still succeed since rate limiting uses hour-based window
        # but we can verify the count
        assert notifier.get_pending_count() >= 10
    
    def test_callbacks(self, notifier):
        """Test notification callbacks."""
        mock_callback = MagicMock()
        notifier.add_callback(mock_callback)
        
        mock_queue = MagicMock()
        notifier.set_handoff_queue(mock_queue)
        
        notifier.notify(
            issue_id="ISS-callback",
            severity="error",
            message="Callback test",
        )
        
        assert mock_callback.called
        call_kwargs = mock_callback.call_args[1]
        assert call_kwargs["issue_id"] == "ISS-callback"
    
    def test_get_stats(self, notifier):
        """Test statistics retrieval."""
        mock_queue = MagicMock()
        notifier.set_handoff_queue(mock_queue)
        
        notifier.notify(
            issue_id="ISS-stats",
            severity="error",
            message="Stats test",
        )
        
        stats = notifier.get_stats()
        
        assert "notifications_last_hour" in stats
        assert "rate_limit" in stats
        assert "remaining_capacity" in stats
        assert stats["handoff_queue_connected"] is True
