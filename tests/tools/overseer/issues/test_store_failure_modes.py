"""Failure mode tests for Overseer IssueStore (concurrent writes, disk full, permissions)."""

from __future__ import annotations

import errno
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.overseer.issues.models import (
    InstanceType,
    Issue,
    IssueSeverity,
    IssueStatus,
)
from tools.overseer.issues.store import IssueStore


def _issue(id_: str = "id-1", pattern_hash: str = "hash1") -> Issue:
    return Issue(
        id=id_,
        timestamp=datetime.now(timezone.utc),
        instance_type=InstanceType.AGENT,
        instance_id="agent-1",
        correlation_id="corr-1",
        severity=IssueSeverity.MEDIUM,
        category="Test",
        error_type="ValueError",
        message="Error message",
        context={},
        pattern_hash=pattern_hash,
        status=IssueStatus.NEW,
        recommendations=[],
        resolved_at=None,
        resolved_by=None,
    )


class TestConcurrentAppends:
    """Concurrent append from multiple threads; verify no corruption and all issues present."""

    def test_concurrent_appends_no_corruption(self, tmp_path: Path) -> None:
        store = IssueStore(
            storage_dir=tmp_path,
            max_file_size_mb=1,
            retention_days=90,
        )
        issues_per_thread = 20
        num_threads = 5
        total = issues_per_thread * num_threads
        errors: list[Exception] = []

        def append_many(thread_id: int) -> None:
            for i in range(issues_per_thread):
                try:
                    issue = _issue(
                        id_=f"t{thread_id}-{i}",
                        pattern_hash=f"ph-{thread_id}-{i}",
                    )
                    store.append(issue)
                except Exception as e:
                    errors.append(e)

        threads = [
            threading.Thread(target=append_many, args=(t,))
            for t in range(num_threads)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Concurrent appends raised: {errors}"
        results = store.query(limit=total + 100)
        assert len(results) == total
        ids = {r.id for r in results}
        for t in range(num_threads):
            for i in range(issues_per_thread):
                assert f"t{t}-{i}" in ids


class TestAppendRaisesOnWriteFailure:
    """When file write fails (disk full, permission), append propagates the error."""

    def test_append_propagates_os_error_on_write(self, tmp_path: Path) -> None:
        store = IssueStore(
            storage_dir=tmp_path,
            max_file_size_mb=1,
            retention_days=90,
        )
        issue = _issue(id_="fail-1")

        def failing_open(*args, **kwargs):
            if "a" in kwargs.get("mode", args[1] if len(args) > 1 else ""):
                raise OSError(errno.ENOSPC, "No space left on device")
            return open(*args, **kwargs)

        with patch("builtins.open", failing_open):
            with pytest.raises(OSError) as exc_info:
                store.append(issue)
            assert exc_info.value.errno == errno.ENOSPC

    def test_append_propagates_permission_error(self, tmp_path: Path) -> None:
        store = IssueStore(
            storage_dir=tmp_path,
            max_file_size_mb=1,
            retention_days=90,
        )
        issue = _issue(id_="perm-1")

        def permission_error_open(*args, **kwargs):
            if "a" in kwargs.get("mode", args[1] if len(args) > 1 else ""):
                raise PermissionError("Permission denied")
            return open(*args, **kwargs)

        with patch("builtins.open", permission_error_open):
            with pytest.raises(PermissionError):
                store.append(issue)


class TestFileLockTimeout:
    """File lock acquisition timeout raises when lock cannot be obtained."""

    def test_file_lock_timeout_raises(self, tmp_path: Path) -> None:
        from tools.overseer.issues.store import _file_lock

        log_file = tmp_path / "issues_2026-01-01_0.jsonl"
        log_file.touch()
        lock_file = log_file.with_suffix(log_file.suffix + ".lock")
        lock_file.touch()

        with patch("tools.overseer.issues.store._FILE_LOCK_WAIT_SEC", 0.1):
            with patch("tools.overseer.issues.store._FILE_LOCK_POLL_SEC", 0.02):
                with pytest.raises(TimeoutError):
                    with _file_lock(log_file):
                        pass
        lock_file.unlink(missing_ok=True)
