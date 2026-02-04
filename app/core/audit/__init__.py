"""
VoiceStudio Audit Logging System.

Provides comprehensive audit logging for:
- AI agent file changes
- Build warnings and errors
- Runtime exceptions
- XAML compiler failures
- Crash artifact correlation

This module integrates with existing monitoring infrastructure
(StructuredLogger, ErrorTracker) rather than replacing it.
"""

from .schema import (
    AuditEntry,
    AuditEventType,
    AuditActor,
    AuditOperation,
)
from .audit_logger import AuditLogger, get_audit_logger, setup_audit_logger
from .context_enricher import ContextEnricher
from .issue_bridge import (
    AuditIssueBridge,
    get_audit_issue_bridge,
    setup_audit_issue_bridge,
)
from .debug_notifier import (
    DebugRoleNotifier,
    get_debug_notifier,
    setup_debug_notifier,
    connect_to_issue_bridge,
)

__all__ = [
    "AuditEntry",
    "AuditEventType",
    "AuditActor",
    "AuditOperation",
    "AuditLogger",
    "get_audit_logger",
    "setup_audit_logger",
    "ContextEnricher",
    "AuditIssueBridge",
    "get_audit_issue_bridge",
    "setup_audit_issue_bridge",
    "DebugRoleNotifier",
    "get_debug_notifier",
    "setup_debug_notifier",
    "connect_to_issue_bridge",
]
