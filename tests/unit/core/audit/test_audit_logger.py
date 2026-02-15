"""
Unit tests for AuditLogger service.

Tests:
- File change logging
- Build event logging
- Exception logging with correlation
- XAML failure logging
- Crash artifact linking
- Context enricher integration
"""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest


class TestAuditLogger:
    """Tests for AuditLogger class."""

    @pytest.fixture
    def temp_audit_dir(self):
        """Create a temporary directory for audit logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def audit_logger(self, temp_audit_dir):
        """Create an AuditLogger instance with temp directory."""
        from app.core.audit.audit_logger import AuditLogger

        return AuditLogger(
            audit_dir=temp_audit_dir,
            enable_markdown=True,
            enable_console=False,
            enable_issue_bridge=False,
        )

    def test_log_file_change(self, audit_logger, temp_audit_dir):
        """Test logging a file change entry."""
        entry_id = audit_logger.log_file_change(
            file_path="src/test.py",
            operation="modify",
            role="Role 2",
            task_id="VS-0001",
            summary="Fixed bug in test module",
            lines_added=10,
            lines_removed=5,
        )

        assert entry_id is not None
        assert len(entry_id) == 8

        # Verify log file was created
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = temp_audit_dir / f"log-{today}.jsonl"
        assert log_file.exists()

        # Verify entry content
        with open(log_file, encoding="utf-8") as f:
            lines = f.readlines()
            assert len(lines) >= 1

            entry = json.loads(lines[-1])
            assert entry["file_path"] == "src/test.py"
            assert entry["operation"] == "modify"
            assert entry["role"] == "Role 2"
            assert entry["task_id"] == "VS-0001"

    def test_log_build_event_warnings(self, audit_logger, temp_audit_dir):
        """Test logging build warnings."""
        entry_ids = audit_logger.log_build_event(
            warnings=["CS8618", "RCS1163"],
            errors=[],
            commit_hash="abc1234",
            task_id="VS-0002",
        )

        # Should log 2 warnings + 1 success
        assert len(entry_ids) == 3

        # Verify log file
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = temp_audit_dir / f"log-{today}.jsonl"

        with open(log_file, encoding="utf-8") as f:
            lines = f.readlines()

            # Check warning entries
            warning_entries = [
                json.loads(line) for line in lines
                if "build_warning" in line
            ]
            assert len(warning_entries) == 2

            # Check success entry
            success_entries = [
                json.loads(line) for line in lines
                if "build_success" in line
            ]
            assert len(success_entries) == 1

    def test_log_build_event_errors(self, audit_logger, temp_audit_dir):
        """Test logging build errors (no success entry)."""
        entry_ids = audit_logger.log_build_event(
            warnings=[],
            errors=["CS0234", "CS0103"],
            commit_hash="def5678",
        )

        # Should log 2 errors (no success when errors exist)
        assert len(entry_ids) == 2

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = temp_audit_dir / f"log-{today}.jsonl"

        with open(log_file, encoding="utf-8") as f:
            lines = f.readlines()

            error_entries = [
                json.loads(line) for line in lines
                if "build_error" in line
            ]
            assert len(error_entries) == 2

    def test_log_runtime_exception(self, audit_logger, temp_audit_dir):
        """Test logging runtime exceptions."""
        try:
            raise ValueError("Test exception message")
        except ValueError as e:
            entry_id = audit_logger.log_runtime_exception(
                exception=e,
                context={
                    "request_id": "REQ-123",
                    "path": "/api/test",
                    "subsystem": "Backend.API",
                },
            )

        assert entry_id is not None

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = temp_audit_dir / f"log-{today}.jsonl"

        with open(log_file, encoding="utf-8") as f:
            entry = json.loads(f.readline())
            assert entry["event_type"] == "runtime_exception"
            assert "Test exception message" in entry["message"]
            assert entry["severity"] == "error"

    def test_log_xaml_failure(self, audit_logger, temp_audit_dir):
        """Test logging XAML failures."""
        entry_id = audit_logger.log_xaml_failure(
            file_path="Views/Panels/TestPanel.xaml",
            error_type="compile",
            message="XamlCompiler error: Unknown type 'StackPanelx'",
            commit_hash="ghi9012",
        )

        assert entry_id is not None

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = temp_audit_dir / f"log-{today}.jsonl"

        with open(log_file, encoding="utf-8") as f:
            entry = json.loads(f.readline())
            assert entry["event_type"] == "xaml_compile_failure"
            assert "StackPanelx" in entry["message"]

    def test_get_recent_entries(self, audit_logger):
        """Test retrieving recent entries."""
        # Log some entries
        for i in range(5):
            audit_logger.log_file_change(
                file_path=f"src/file{i}.py",
                operation="modify",
                role="Role 2",
                task_id="VS-0003",
                summary=f"Change {i}",
            )

        entries = audit_logger.get_recent_entries(limit=3)

        assert len(entries) == 3
        # Should be in reverse order (most recent first)
        assert "file4" in entries[0].file_path

    def test_markdown_summary_created(self, audit_logger, temp_audit_dir):
        """Test that Markdown summary is created."""
        audit_logger.log_file_change(
            file_path="src/test.py",
            operation="create",
            role="Role 3",
            task_id="VS-0004",
            summary="Created new file",
        )

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        md_file = temp_audit_dir / f"log-{today}.md"

        assert md_file.exists()

        with open(md_file, encoding="utf-8") as f:
            content = f.read()
            assert "Audit Log" in content
            assert "src/test.py" in content or "test.py" in content

    def test_per_file_log_created(self, audit_logger, temp_audit_dir):
        """Test that per-file logs are created."""
        audit_logger.log_file_change(
            file_path="src/unique_file.py",
            operation="modify",
            role="Role 2",
            task_id="VS-0005",
            summary="Modified unique file",
        )

        # Check files directory
        files_dir = temp_audit_dir / "files"
        assert files_dir.exists()

        # Find the log file
        log_files = list(files_dir.glob("*.log"))
        assert len(log_files) >= 1

    def test_per_task_log_created(self, audit_logger, temp_audit_dir):
        """Test that per-task logs are created."""
        task_id = "VS-0006"

        audit_logger.log_file_change(
            file_path="src/task_file.py",
            operation="modify",
            role="Role 2",
            task_id=task_id,
            summary="Task-related change",
        )

        # Check tasks directory
        tasks_dir = temp_audit_dir / "tasks"
        assert tasks_dir.exists()

        task_file = tasks_dir / f"{task_id}.json"
        assert task_file.exists()

        with open(task_file, encoding="utf-8") as f:
            entries = json.load(f)
            assert len(entries) >= 1
            assert entries[0]["task_id"] == task_id


class TestAuditEntry:
    """Tests for AuditEntry schema."""

    def test_to_dict(self):
        """Test AuditEntry serialization."""
        from app.core.audit.schema import AuditEntry, AuditEventType

        entry = AuditEntry(
            event_type=AuditEventType.FILE_MODIFY.value,
            file_path="test.py",
            task_id="VS-0007",
            summary="Test entry",
        )

        data = entry.to_dict()

        assert data["event_type"] == "file_modify"
        assert data["file_path"] == "test.py"
        assert data["task_id"] == "VS-0007"
        assert "entry_id" in data
        assert "timestamp" in data

    def test_to_json(self):
        """Test AuditEntry JSON serialization."""
        from app.core.audit.schema import AuditEntry

        entry = AuditEntry(
            event_type="test_event",
            summary="JSON test",
        )

        json_str = entry.to_json()

        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert data["event_type"] == "test_event"

    def test_from_dict(self):
        """Test AuditEntry deserialization."""
        from app.core.audit.schema import AuditEntry

        data = {
            "timestamp": "2026-02-03T12:00:00+00:00",
            "entry_id": "test1234",
            "event_type": "file_create",
            "file_path": "new_file.py",
            "summary": "Created file",
        }

        entry = AuditEntry.from_dict(data)

        assert entry.entry_id == "test1234"
        assert entry.event_type == "file_create"
        assert entry.file_path == "new_file.py"

    def test_to_markdown(self):
        """Test AuditEntry Markdown formatting."""
        from app.core.audit.schema import AuditEntry

        entry = AuditEntry(
            event_type="file_modify",
            file_path="src/component.py",
            role="Role 3",
            task_id="VS-0008",
            summary="Updated component",
        )

        md = entry.to_markdown()

        assert "|" in md
        assert "file_modify" in md
        assert "Role 3" in md
