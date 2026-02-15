"""
Overseer Issue Store.

Append-only JSONL storage for unified issues with querying and rotation.
Uses process-local threading.Lock and cross-process file locking for
concurrent write safety.
"""

from __future__ import annotations

import gzip
import json
import os
import threading
import time
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from tools.overseer.issues.config import (
    COMPRESS_AFTER_DAYS,
    ISSUES_LOG_DIR,
    MAX_FILE_SIZE_MB,
    RECOMMENDATION_FEEDBACK_FILENAME,
    RETENTION_DAYS,
)
from tools.overseer.issues.models import (
    InstanceType,
    Issue,
    IssueSeverity,
    IssueStatus,
)

# Cross-process file lock: max wait (seconds) and retry interval
_FILE_LOCK_WAIT_SEC = 30.0
_FILE_LOCK_POLL_SEC = 0.05


@contextmanager
def _file_lock(log_file: Path):
    """
    Cross-process exclusive lock for a log file.
    Uses a companion .lock file; safe for concurrent appends from multiple processes.
    """
    lock_file = log_file.with_suffix(log_file.suffix + ".lock")
    fd: int | None = None
    deadline = time.monotonic() + _FILE_LOCK_WAIT_SEC
    while True:
        try:
            fd = os.open(
                lock_file,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o644,
            )
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                raise TimeoutError(
                    f"Could not acquire file lock for {log_file} within {_FILE_LOCK_WAIT_SEC}s"
                )
            time.sleep(_FILE_LOCK_POLL_SEC)
    try:
        yield
    finally:
        if fd is not None:
            try:
                os.close(fd)
            # ALLOWED: bare except - Best effort file handle cleanup
            except OSError:
                pass
        try:
            lock_file.unlink(missing_ok=True)
        # ALLOWED: bare except - Best effort lock file cleanup
        except OSError:
            pass


def get_feedback_file_path() -> Path:
    """Path to the recommendation feedback JSONL file."""
    path = ISSUES_LOG_DIR / RECOMMENDATION_FEEDBACK_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def append_feedback_line(line: str) -> None:
    """
    Append a single JSON line to the recommendation feedback file.
    Uses cross-process file locking for concurrent safety.
    """
    path = get_feedback_file_path()
    with _file_lock(path), open(path, "a", encoding="utf-8") as f:
        f.write(line.rstrip() + "\n")


def iter_feedback_lines(
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    days: int | None = None,
) -> Iterator[dict[str, Any]]:
    """
    Iterate over feedback records (for calibration).
    If days is set, only records within the last N days are yielded.
    start_time/end_time can override.
    """
    path = get_feedback_file_path()
    if not path.exists():
        return
    if days is not None and start_time is None and end_time is None:
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=days)
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                applied = data.get("applied_at")
                if applied:
                    if isinstance(applied, str):
                        applied_dt = datetime.fromisoformat(applied.replace("Z", "+00:00"))
                        if applied_dt.tzinfo is None:
                            applied_dt = applied_dt.replace(tzinfo=timezone.utc)
                    else:
                        continue
                    if start_time is not None and applied_dt < start_time:
                        continue
                    if end_time is not None and applied_dt > end_time:
                        continue
                yield data
            except (json.JSONDecodeError, KeyError, ValueError):
                continue


class IssueStore:
    """
    Append-only issue log storage.

    Stores issues in JSONL format. Supports rotation by date and size.
    Location: %APPDATA%/VoiceStudio/logs/overseer_issues/
    Naming: issues_YYYY-MM-DD_NNN.jsonl
    """

    def __init__(
        self,
        storage_dir: Path | None = None,
        max_file_size_mb: int | None = None,
        retention_days: int | None = None,
    ):
        """
        Initialize the issue store.

        Args:
            storage_dir: Directory for issue logs. Defaults to config ISSUES_LOG_DIR.
            max_file_size_mb: Maximum size of a single log file before rotation. Defaults to config.
            retention_days: Number of days to retain logs. Defaults to config.
        """
        if storage_dir is not None:
            self._storage_dir = Path(storage_dir)
        else:
            self._storage_dir = ISSUES_LOG_DIR

        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._max_file_size = (max_file_size_mb if max_file_size_mb is not None else MAX_FILE_SIZE_MB) * 1024 * 1024
        self._retention_days = retention_days if retention_days is not None else RETENTION_DAYS
        self._compress_after_days = COMPRESS_AFTER_DAYS
        self._lock = threading.Lock()
        self._current_file: Path | None = None

    def _get_current_log_file(self) -> Path:
        """Get or create the current log file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        base_name = f"issues_{date_str}"

        index = 0
        while True:
            suffix = f"_{index:03d}" if index > 0 else ""
            log_file = self._storage_dir / f"{base_name}{suffix}.jsonl"

            if not log_file.exists():
                return log_file

            if log_file.stat().st_size < self._max_file_size:
                return log_file

            index += 1

    def append(self, issue: Issue) -> None:
        """
        Append an issue to the store.

        Uses a process-local lock and a per-file cross-process lock so that
        concurrent appends (same process or different processes) do not
        interleave writes.

        Args:
            issue: The issue to append
        """
        with self._lock:
            log_file = self._get_current_log_file()
            with _file_lock(log_file), open(log_file, "a", encoding="utf-8") as f:
                f.write(issue.to_json_line() + "\n")

    def query(
        self,
        severity: list[IssueSeverity] | None = None,
        status: list[IssueStatus] | None = None,
        instance_type: list[InstanceType] | None = None,
        pattern_hash: str | None = None,
        correlation_id: str | None = None,
        error_codes: list[str] | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 1000,
    ) -> list[Issue]:
        """
        Query issues with filters.

        Args:
            severity: Filter by severity
            status: Filter by status
            instance_type: Filter by instance type
            pattern_hash: Filter by pattern hash
            correlation_id: Filter by correlation ID
            error_codes: Filter by at least one extracted error code (e.g. CS0234, HTTP500)
            start_time: Filter issues after this time
            end_time: Filter issues before this time
            limit: Maximum number of issues to return

        Returns:
            List of matching issues
        """
        results = []

        for issue in self._iter_issues(start_time, end_time):
            if severity is not None and issue.severity not in severity:
                continue
            if status is not None and issue.status not in status:
                continue
            if instance_type is not None and issue.instance_type not in instance_type:
                continue
            if pattern_hash is not None and issue.pattern_hash != pattern_hash:
                continue
            if correlation_id is not None and issue.correlation_id != correlation_id:
                continue
            if error_codes is not None:
                issue_codes = {(ic or "").upper() for ic in (issue.context or {}).get("_error_codes") or []}
                requested = {(c or "").upper() for c in error_codes}
                if not issue_codes or not (issue_codes & requested):
                    continue

            results.append(issue)

            if len(results) >= limit:
                break

        return results

    def _iter_issues(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> Iterator[Issue]:
        """Iterate over issues in time range. Reads both .jsonl and .jsonl.gz."""
        candidates: dict[str, Path] = {}
        for p in self._storage_dir.glob("issues_*.jsonl*"):
            base = p.stem.replace(".jsonl", "") if p.suffix == ".gz" else p.stem
            if base not in candidates or p.suffix == ".gz":
                candidates[base] = p
        log_files = sorted(candidates.values(), key=lambda p: p.name, reverse=True)

        for log_file in log_files:
            try:
                stem = log_file.stem.replace(".jsonl", "")
                parts = stem.split("_")
                if len(parts) >= 2:
                    date_str = parts[1]
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")

                    if start_time is not None and file_date.date() < start_time.date():
                        continue
                    if end_time is not None and file_date.date() > end_time.date():
                        continue
            # Best effort - failure is acceptable here
            except (IndexError, ValueError):
                pass

            try:
                if log_file.suffix == ".gz":
                    f = gzip.open(log_file, "rt", encoding="utf-8")
                else:
                    f = open(log_file, encoding="utf-8")
                with f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            data = json.loads(line)
                            issue = Issue.from_dict(data)

                            if start_time is not None and issue.timestamp < start_time:
                                continue
                            if end_time is not None and issue.timestamp > end_time:
                                continue

                            yield issue
                        except (json.JSONDecodeError, KeyError):
                            continue
            except OSError:
                continue

    def get_by_id(self, issue_id: str) -> Issue | None:
        """Get a single issue by ID (latest occurrence when append-only updates)."""
        latest: Issue | None = None
        for issue in self._iter_issues():
            if issue.id == issue_id:
                if latest is None or (issue.timestamp and latest.timestamp and issue.timestamp >= latest.timestamp):
                    latest = issue
        return latest

    def get_by_correlation(self, correlation_id: str) -> list[Issue]:
        """Get all issues for a correlation ID (full trace)."""
        return self.query(correlation_id=correlation_id, limit=10000)

    def count_by_pattern_hash(
        self,
        pattern_hash: str,
        hours: int = 24,
    ) -> int:
        """Count issues with the given pattern hash in the time window."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        return len(
            self.query(pattern_hash=pattern_hash, start_time=since, limit=100000)
        )

    def get_top_patterns(
        self,
        limit: int = 10,
        time_window_hours: int = 24,
    ) -> list[dict[str, Any]]:
        """
        Get top issue patterns by frequency.

        Returns:
            List of dicts with pattern_hash, count, and sample message
        """
        since = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        counter: Counter[str] = Counter()
        samples: dict[str, str] = {}

        for issue in self._iter_issues(start_time=since):
            counter[issue.pattern_hash] += 1
            if issue.pattern_hash not in samples:
                samples[issue.pattern_hash] = issue.message[:200]

        result = []
        for pattern_hash, count in counter.most_common(limit):
            result.append(
                {
                    "pattern_hash": pattern_hash,
                    "count": count,
                    "sample_message": samples.get(pattern_hash, ""),
                }
            )
        return result

    def update_status(
        self,
        issue_id: str,
        status: IssueStatus,
        resolved_by: str | None = None,
    ) -> bool:
        """
        Update issue status (acknowledge, resolve, escalate).

        Note: Store is append-only; this reads, updates, and re-appends.
        For full audit trail the original record remains; we append a new
        record with updated status. Caller may use get_by_id to fetch
        current view and then append an updated copy. This implementation
        does a simple read-all, update-one, write-new-file for the updated
        issue only for simplicity; for production a proper update log or
        index could be used.
        """
        issue = self.get_by_id(issue_id)
        if issue is None:
            return False

        issue.status = status
        if status == IssueStatus.RESOLVED:
            issue.resolved_at = datetime.now(timezone.utc)
            issue.resolved_by = resolved_by

        self.append(issue)
        return True

    def compress_rotated_files(self) -> int:
        """
        Compress .jsonl files older than COMPRESS_AFTER_DAYS to .jsonl.gz.
        Skips files that already have a .jsonl.gz. Returns number compressed.
        """
        if self._compress_after_days <= 0:
            return 0
        cutoff = datetime.now() - timedelta(days=self._compress_after_days)
        compressed = 0
        for log_file in self._storage_dir.glob("issues_*.jsonl"):
            if log_file.suffix != ".jsonl":
                continue
            try:
                parts = log_file.stem.split("_")
                if len(parts) < 2:
                    continue
                date_str = parts[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date.date() >= cutoff.date():
                    continue
                gz_path = log_file.with_suffix(log_file.suffix + ".gz")
                if gz_path.exists():
                    log_file.unlink(missing_ok=True)
                    compressed += 1
                    continue
                with open(log_file, "rb") as f_in:
                    with gzip.open(gz_path, "wb") as f_out:
                        f_out.writelines(f_in)
                log_file.unlink()
                compressed += 1
            except (IndexError, ValueError, OSError):
                continue
        return compressed

    def cleanup_old_logs(self) -> int:
        """
        Remove log files older than retention period.
        Removes both .jsonl and .jsonl.gz. Optionally compresses old .jsonl first.
        Returns number of files removed.
        """
        if self._compress_after_days > 0:
            self.compress_rotated_files()
        cutoff = datetime.now() - timedelta(days=self._retention_days)
        removed = 0
        for pattern in ("issues_*.jsonl", "issues_*.jsonl.gz"):
            for log_file in self._storage_dir.glob(pattern):
                try:
                    stem = log_file.stem.replace(".jsonl", "")
                    parts = stem.split("_")
                    if len(parts) >= 2:
                        date_str = parts[1]
                        file_date = datetime.strptime(date_str, "%Y-%m-%d")
                        if file_date.date() < cutoff.date():
                            log_file.unlink(missing_ok=True)
                            removed += 1
                except (IndexError, ValueError, OSError):
                    continue
        return removed

    def get_stats(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, Any]:
        """Get statistics for the time range."""
        stats: dict[str, Any] = {
            "total": 0,
            "by_severity": {},
            "by_status": {},
            "by_instance_type": {},
            "by_pattern_hash": Counter(),
        }

        for issue in self._iter_issues(start_time, end_time):
            stats["total"] += 1
            sev = issue.severity.value
            stats["by_severity"][sev] = stats["by_severity"].get(sev, 0) + 1
            st = issue.status.value
            stats["by_status"][st] = stats["by_status"].get(st, 0) + 1
            it = issue.instance_type.value
            stats["by_instance_type"][it] = stats["by_instance_type"].get(it, 0) + 1
            stats["by_pattern_hash"][issue.pattern_hash] += 1

        stats["by_pattern_hash"] = dict(stats["by_pattern_hash"])
        return stats
