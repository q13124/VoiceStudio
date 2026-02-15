"""
Overseer Issue Aggregator.

Central entry point for all errors from any instance type.
Enriches context, calculates pattern hash, persists to IssueStore.
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from tools.overseer.issues.config import (
    ISSUES_LOG_DIR,
    MAX_FILE_SIZE_MB,
    RETENTION_DAYS,
)
from tools.overseer.issues.models import (
    InstanceType,
    Issue,
    IssueSeverity,
    IssueStatus,
)
from tools.overseer.issues.sanitizer import sanitize_context, sanitize_message
from tools.overseer.issues.store import IssueStore

logger = logging.getLogger(__name__)

# Default store (lazy init to avoid import cycles)
_store: IssueStore | None = None


def _get_store() -> IssueStore:
    """Get or create the issue store."""
    global _store
    if _store is None:
        _store = IssueStore(
            storage_dir=ISSUES_LOG_DIR,
            max_file_size_mb=MAX_FILE_SIZE_MB,
            retention_days=RETENTION_DAYS,
        )
    return _store


def _normalize_message(message: str) -> str:
    """Normalize error message for pattern hashing (strip paths, numbers)."""
    if not message:
        return ""
    s = message.lower().strip()
    # Replace absolute paths with placeholder
    s = re.sub(r"[a-z]:[\\/][^\s]+", "<path>", s)
    s = re.sub(r"/[^\s]+", "<path>", s)
    # Replace hex/numbers that vary
    s = re.sub(r"0x[0-9a-f]+", "<hex>", s)
    s = re.sub(r"\b\d{4,}\b", "<num>", s)
    # Collapse whitespace
    s = re.sub(r"\s+", " ", s)
    return s[:500]


def calculate_pattern_hash(message: str, error_type: str = "") -> str:
    """Compute a stable hash for grouping similar issues."""
    normalized = _normalize_message(message)
    key = f"{error_type}:{normalized}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def enrich_context(
    context: dict[str, Any],
    instance_type: InstanceType,
    instance_id: str,
) -> dict[str, Any]:
    """Add environment and common context to the issue context."""
    enriched = dict(context)
    enriched["_enriched_at"] = datetime.now(timezone.utc).isoformat()
    enriched["_instance_type"] = instance_type.value
    enriched["_instance_id"] = instance_id
    if "stack" not in enriched and "traceback" not in enriched and "error_stack" not in enriched:
        # Leave as-is; callers can pass stack/traceback
        pass
    return enriched


def _severity_from_context(context: dict[str, Any]) -> IssueSeverity:
    """Infer severity from context if present."""
    sev = context.get("severity")
    if sev is None:
        return IssueSeverity.MEDIUM
    if isinstance(sev, str):
        sev = sev.lower()
        for s in IssueSeverity:
            if s.value == sev:
                return s
    return IssueSeverity.MEDIUM


# Error code patterns: CS1234 (C#), HTTP500, errno 2, ENOENT, etc.
_ERROR_CODE_PATTERNS = [
    re.compile(r"\bCS\d{4}\b", re.I),
    re.compile(r"\bHTTP\s*(\d{3})\b", re.I),
    re.compile(r"\berrno\s*(\d+)\b", re.I),
    re.compile(r"\bE[A-Z]+\b"),
]


def extract_error_codes(message: str, context: dict[str, Any] | None = None) -> list:
    """
    Extract error codes from message and context for indexing/querying.
    Returns list of normalized codes (e.g. CS0234, HTTP500, ENOENT).
    """
    codes: list = []
    text = (message or "") + " " + str(context or "")
    for pat in _ERROR_CODE_PATTERNS:
        for m in pat.finditer(text):
            raw = m.group(0).replace(" ", "")
            if raw:
                codes.append(raw.upper())
    if context:
        for key in ("error_code", "code", "status_code"):
            val = context.get(key)
            if val is not None and str(val).strip():
                codes.append(str(val).strip().upper())
    return list(dict.fromkeys(codes))


def record_issue(
    instance_type: InstanceType,
    instance_id: str,
    correlation_id: str,
    error_type: str,
    message: str,
    context: dict[str, Any] | None = None,
    severity: IssueSeverity | None = None,
    category: str | None = None,
    auto_task: bool = True,
) -> Issue:
    """
    Main entry point: record an issue and persist to store.

    Args:
        instance_type: AGENT, ENGINE, or BUILD
        instance_id: Identifier of the source instance
        correlation_id: Cross-layer tracing ID
        error_type: Exception/error type name
        message: Error message
        context: Optional context (stack, env, etc.)
        severity: Optional; inferred from context if not set
        category: Optional category (default: error_type)
        auto_task: If True, automatically create task brief for qualifying issues

    Returns:
        The created Issue (already appended to store)
    """
    context = context or {}
    message = sanitize_message(message)
    context = sanitize_context(context)
    context = enrich_context(context, instance_type, instance_id)
    error_codes = extract_error_codes(message, context)
    if error_codes:
        context["_error_codes"] = error_codes
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

    if os.environ.get("VOICESTUDIO_ISSUES_ASYNC", "").strip().lower() in ("1", "true", "yes"):
        try:
            from tools.overseer.issues.async_aggregator import enqueue_issue
            enqueue_issue(issue)
            logger.debug("Issue enqueued (async): %s", issue.id)
            # Auto-task creation handled after store append
        # ALLOWED: bare except - Optional async dependency
        except ImportError:
            pass
    else:
        store = _get_store()
        store.append(issue)
        logger.debug("Issue recorded: %s", issue.id)

    # Automatic task creation for qualifying issues
    if auto_task and _should_auto_create_task(issue):
        try:
            from tools.overseer.issues.task_generator import IssueToTaskGenerator
            generator = IssueToTaskGenerator(issue_store=_get_store())
            task_path = generator.create_task_file(issue)
            # Update issue with linked task
            issue.context["linked_task"] = task_path.name
            issue.context["task_auto_created"] = True
            # Re-append with updated context
            _get_store().append(issue)
            logger.info(f"Auto-created task {task_path.name} from issue {issue.id}")
        except Exception as e:
            logger.warning(f"Failed to auto-create task from issue {issue.id}: {e}")

    return issue


def _should_auto_create_task(issue: Issue) -> bool:
    """Determine if issue qualifies for automatic task creation."""
    # Only create for critical/high severity
    if issue.severity.value not in {"critical", "high"}:
        return False

    # Skip if already has linked task
    if issue.context.get("linked_task"):
        return False

    # Skip if disabled via env var
    return os.environ.get("VOICESTUDIO_AUTO_TASK_DISABLED", "").strip().lower() not in ("1", "true", "yes")


def record_agent_error(
    agent_id: str,
    correlation_id: str,
    error_type: str,
    message: str,
    context: dict[str, Any],
) -> Issue:
    """Record an issue from agent audit (tools/overseer/agent/audit_logger)."""
    return record_issue(
        instance_type=InstanceType.AGENT,
        instance_id=agent_id,
        correlation_id=correlation_id,
        error_type=error_type,
        message=message,
        context=context,
    )


def record_backend_error(
    error_type: str,
    message: str,
    severity: str,
    traceback: str | None = None,
    context: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> Issue:
    """Record an issue from backend ErrorTracker (app/core/monitoring/error_tracking)."""
    ctx = dict(context or {})
    if traceback:
        ctx["traceback"] = traceback
    sev_map = {
        "low": IssueSeverity.LOW,
        "medium": IssueSeverity.MEDIUM,
        "high": IssueSeverity.HIGH,
        "critical": IssueSeverity.CRITICAL,
    }
    sev = sev_map.get((severity or "medium").lower(), IssueSeverity.MEDIUM)
    return record_issue(
        instance_type=InstanceType.ENGINE,
        instance_id=f"backend-{os.getpid()}",
        correlation_id=request_id or str(uuid.uuid4()),
        error_type=error_type,
        message=message,
        context=ctx,
        severity=sev,
    )


def record_engine_error(
    engine_id: str,
    error: Exception,
    correlation_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> Issue:
    """Record an issue from engine runtime (app/core/runtime)."""
    import traceback as tb
    ctx = dict(context or {})
    ctx["stack"] = tb.format_exc()
    return record_issue(
        instance_type=InstanceType.ENGINE,
        instance_id=engine_id,
        correlation_id=correlation_id or str(uuid.uuid4()),
        error_type=type(error).__name__,
        message=str(error),
        context=ctx,
    )


def record_build_error(
    instance_id: str,
    error_type: str,
    message: str,
    context: dict[str, Any] | None = None,
) -> Issue:
    """Record an issue from build/verification (scripts/run_verification)."""
    return record_issue(
        instance_type=InstanceType.BUILD,
        instance_id=instance_id,
        correlation_id=str(uuid.uuid4()),
        error_type=error_type,
        message=message,
        context=context or {},
    )
