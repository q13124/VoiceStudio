"""
Unit tests for AuditSourceAdapter.

Tests:
- Audit entry fetching
- Severity filtering
- Context integration
"""

import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path for tools imports BEFORE any pytest imports
_project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_project_root))

import pytest

# Try to import the modules, skip tests if not available
try:
    from tools.context.sources.audit_adapter import AuditSourceAdapter
    from tools.context.core.models import AllocationContext, ContextLevel
    from tools.context.core.registry import build_default_registry
    TOOLS_AVAILABLE = True
except ImportError as e:
    TOOLS_AVAILABLE = False
    AuditSourceAdapter = None
    AllocationContext = None
    ContextLevel = None
    build_default_registry = None


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available in path")
class TestAuditSourceAdapter:
    """Tests for AuditSourceAdapter class."""
    
    @pytest.fixture
    def temp_audit_dir(self):
        """Create a temporary directory with sample audit logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_dir = Path(tmpdir)
            
            # Create sample log file for today
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            log_file = audit_dir / f"log-{today}.jsonl"
            
            entries = [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "entry_id": "entry001",
                    "event_type": "runtime_exception",
                    "severity": "error",
                    "subsystem": "Backend.API",
                    "message": "Test error message",
                    "summary": "Exception in Backend",
                },
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "entry_id": "entry002",
                    "event_type": "build_warning",
                    "severity": "warning",
                    "subsystem": "Build",
                    "message": "Warning CS8618",
                    "summary": "Build warning",
                },
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "entry_id": "entry003",
                    "event_type": "file_modify",
                    "severity": "info",
                    "subsystem": "UI.Panels",
                    "message": "File modified",
                    "summary": "Modified panel",
                },
            ]
            
            with open(log_file, "w", encoding="utf-8") as f:
                for entry in entries:
                    f.write(json.dumps(entry) + "\n")
            
            yield audit_dir
    
    @pytest.fixture
    def adapter(self, temp_audit_dir):
        """Create an AuditSourceAdapter instance."""
        return AuditSourceAdapter(
            max_entries=20,
            severity_filter=["error", "warning", "critical"],
            hours_lookback=24,
            audit_dir=temp_audit_dir,
        )
    
    def test_fetch_returns_entries(self, adapter):
        """Test that fetch returns audit entries."""
        context = AllocationContext(
            task_id="TEST-0001",
            phase="Test",
            role="debug-agent",
            include_git=False,
            budget_chars=5000,
            max_level=ContextLevel.MID,
        )
        
        result = adapter.fetch(context)
        
        assert result.success is True
        assert result.source_name == "audit"
        assert "audit_entries" in result.data
        
        # Should filter out info severity
        entries = result.data["audit_entries"]
        assert all(e["severity"] in ["error", "warning", "critical"] for e in entries)
    
    def test_fetch_filters_by_severity(self, adapter):
        """Test that fetch filters by severity."""
        context = AllocationContext(
            task_id="TEST-0002",
            phase="Test",
            role="debug-agent",
            include_git=False,
            budget_chars=5000,
            max_level=ContextLevel.MID,
        )
        
        result = adapter.fetch(context)
        
        entries = result.data["audit_entries"]
        
        # Should have error and warning, but not info
        severities = {e["severity"] for e in entries}
        assert "error" in severities or "warning" in severities
        assert "info" not in severities
    
    def test_fetch_groups_by_subsystem(self, adapter):
        """Test that fetch groups entries by subsystem."""
        context = AllocationContext(
            task_id="TEST-0003",
            phase="Test",
            role="debug-agent",
            include_git=False,
            budget_chars=5000,
            max_level=ContextLevel.MID,
        )
        
        result = adapter.fetch(context)
        
        assert "by_subsystem" in result.data
        by_subsystem = result.data["by_subsystem"]
        
        # Should have Backend.API and Build subsystems
        assert any("Backend" in s or "Build" in s for s in by_subsystem.keys())
    
    def test_fetch_includes_stats(self, adapter):
        """Test that fetch includes statistics."""
        context = AllocationContext(
            task_id="TEST-0004",
            phase="Test",
            role="debug-agent",
            include_git=False,
            budget_chars=5000,
            max_level=ContextLevel.MID,
        )
        
        result = adapter.fetch(context)
        
        assert "stats" in result.data
        stats = result.data["stats"]
        
        assert "total_entries" in stats
        assert "by_severity" in stats
        assert "by_event_type" in stats
    
    def test_fetch_empty_directory(self):
        """Test fetch with empty audit directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = AuditSourceAdapter(
                max_entries=20,
                audit_dir=Path(tmpdir),
            )
            
            context = AllocationContext(
                task_id="TEST-0005",
                phase="Test",
                role="debug-agent",
                include_git=False,
                budget_chars=5000,
                max_level=ContextLevel.MID,
            )
            
            result = adapter.fetch(context)
            
            assert result.success is True
            assert result.data["audit_entries"] == []
    
    def test_estimate_size(self, adapter):
        """Test size estimation."""
        context = AllocationContext(
            task_id="TEST-0006",
            phase="Test",
            role="debug-agent",
            include_git=False,
            budget_chars=5000,
            max_level=ContextLevel.MID,
        )
        
        size = adapter.estimate_size(context)
        
        # Should return reasonable estimate
        assert size > 0
        assert size <= 3000
    
    def test_fetch_respects_max_entries(self, temp_audit_dir):
        """Test that fetch respects max_entries limit."""
        # Add more entries to the log
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = temp_audit_dir / f"log-{today}.jsonl"
        
        with open(log_file, "a", encoding="utf-8") as f:
            for i in range(25):
                entry = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "entry_id": f"extra{i:03d}",
                    "event_type": "build_error",
                    "severity": "error",
                    "message": f"Extra error {i}",
                    "summary": f"Error {i}",
                }
                f.write(json.dumps(entry) + "\n")
        
        adapter = AuditSourceAdapter(
            max_entries=5,
            severity_filter=["error", "warning"],
            audit_dir=temp_audit_dir,
        )
        
        context = AllocationContext(
            task_id="TEST-0007",
            phase="Test",
            role="debug-agent",
            include_git=False,
            budget_chars=5000,
            max_level=ContextLevel.MID,
        )
        
        result = adapter.fetch(context)
        
        entries = result.data["audit_entries"]
        assert len(entries) <= 5
    
    def test_entry_formatting(self, adapter):
        """Test that entries are properly formatted."""
        context = AllocationContext(
            task_id="TEST-0008",
            phase="Test",
            role="debug-agent",
            include_git=False,
            budget_chars=5000,
            max_level=ContextLevel.MID,
        )
        
        result = adapter.fetch(context)
        
        for entry in result.data["audit_entries"]:
            # Check required fields
            assert "id" in entry
            assert "type" in entry
            assert "severity" in entry
            assert "time" in entry
            assert "summary" in entry


@pytest.mark.skipif(not TOOLS_AVAILABLE, reason="tools.context not available in path")
class TestContextManagerIntegration:
    """Integration tests for audit adapter with context manager."""
    
    def test_adapter_registered_in_registry(self):
        """Test that audit adapter is registered in the source registry."""
        config = {
            "audit": {
                "enabled": True,
                "max_entries": 10,
            }
        }
        
        registry = build_default_registry(config)
        sources = registry.by_name()
        
        assert "audit" in sources
    
    def test_adapter_disabled_when_configured(self):
        """Test that audit adapter is not registered when disabled."""
        config = {
            "audit": {
                "enabled": False,
            }
        }
        
        registry = build_default_registry(config)
        sources = registry.by_name()
        
        assert "audit" not in sources
