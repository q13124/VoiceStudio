"""
Overseer Issue Async Aggregator.

Async recording with a write-behind buffer so hot paths are not blocked
by file I/O. Issues are built synchronously and enqueued; a background
thread flushes them to the store.
"""

from __future__ import annotations

import logging
import queue
import threading
import time

from tools.overseer.issues.aggregator import (
    _get_store,
    _severity_from_context,
    calculate_pattern_hash,
    enrich_context,
)
from tools.overseer.issues.models import (
    InstanceType,
    Issue,
    IssueSeverity,
    IssueStatus,
)
from tools.overseer.issues.sanitizer import sanitize_context, sanitize_message

logger = logging.getLogger(__name__)

# Buffer: max size and drain interval (seconds)
_BUFFER_MAX_SIZE = 500
_DRAIN_INTERVAL_SEC = 2.0
_DRAIN_TIMEOUT_SEC = 5.0

_write_queue: queue.Queue | None = None
_worker_thread: threading.Thread | None = None
_worker_stop = threading.Event()


def _drain_worker() -> None:
    """Background thread: drain queue to store."""
    store = _get_store()
    while not _worker_stop.is_set():
        try:
            issue = _write_queue.get(timeout=_DRAIN_INTERVAL_SEC)
        except queue.Empty:
            continue
        try:
            store.append(issue)
        except Exception as e:
            logger.warning("Async issue append failed: %s", e)
        finally:
            _write_queue.task_done()


def _ensure_worker() -> queue.Queue:
    """Start the write-behind worker if not already running."""
    global _write_queue, _worker_thread
    if _write_queue is None:
        _write_queue = queue.Queue(maxsize=_BUFFER_MAX_SIZE * 2)
        _worker_thread = threading.Thread(target=_drain_worker, daemon=True)
        _worker_stop.clear()
        _worker_thread.start()
    return _write_queue


def enqueue_issue(issue: Issue) -> None:
    """
    Enqueue an already-built issue for write-behind append.
    Used when VOICESTUDIO_ISSUES_ASYNC is set; record_issue builds once and enqueues.
    """
    q = _ensure_worker()
    try:
        q.put(issue, block=True, timeout=_DRAIN_TIMEOUT_SEC)
    except queue.Full:
        logger.warning("Async issue queue full; appending synchronously")
        _get_store().append(issue)


def record_issue_async(
    instance_type: InstanceType,
    instance_id: str,
    correlation_id: str,
    error_type: str,
    message: str,
    context: dict | None = None,
    severity: IssueSeverity | None = None,
    category: str | None = None,
) -> Issue:
    """
    Record an issue asynchronously: build the issue and enqueue for write.
    Returns the Issue immediately; actual append happens in a background thread.
    """
    import uuid
    from datetime import datetime, timezone

    context = context or {}
    message = sanitize_message(message)
    context = sanitize_context(context)
    context = enrich_context(context, instance_type, instance_id)
    pattern_hash = calculate_pattern_hash(message, error_type)
    if severity is None:
        severity = _severity_from_context(context)
    if category is None:
        category = error_type

    issue = Issue(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc),
        instance_type=instance_type,
        instance_id=instance_id,
        correlation_id=correlation_id,
        severity=severity,
        category=category,
        error_type=error_type,
        message=message,
        context=context,
        pattern_hash=pattern_hash,
        status=IssueStatus.NEW,
        recommendations=[],
        resolved_at=None,
        resolved_by=None,
    )

    q = _ensure_worker()
    try:
        q.put(issue, block=True, timeout=_DRAIN_TIMEOUT_SEC)
    except queue.Full:
        logger.warning("Async issue queue full; appending synchronously")
        _get_store().append(issue)
    return issue


def flush_async_writes(timeout: float | None = None) -> None:
    """
    Block until the write-behind queue is drained or timeout.
    timeout: seconds to wait (default _DRAIN_TIMEOUT_SEC * 2).
    """
    if _write_queue is None:
        return
    tout = timeout if timeout is not None else _DRAIN_TIMEOUT_SEC * 2
    deadline = time.monotonic() + tout
    while _write_queue.unfinished_tasks > 0 and time.monotonic() < deadline:
        time.sleep(0.05)
