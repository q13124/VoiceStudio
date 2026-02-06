"""
Audit-to-Issue Bridge for VoiceStudio.

Automatically creates issues in the IssueStore when error-severity
audit entries are logged. Enables automatic routing to Debug Role.
"""

from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional, Set

from .schema import AuditEntry, AuditEventType


class AuditIssueBridge:
    """
    Bridge between the audit logging system and the issue store.
    
    Monitors audit entries for error-severity events and automatically
    creates corresponding issues in the IssueStore. Supports:
    - Deduplication via pattern hashing
    - Severity-based filtering
    - Correlation ID linking between audit entries and issues
    """
    
    # Event types that trigger issue creation
    ISSUE_TRIGGERING_EVENTS = {
        AuditEventType.RUNTIME_EXCEPTION.value,
        AuditEventType.BUILD_ERROR.value,
        AuditEventType.XAML_COMPILE_FAILURE.value,
        AuditEventType.XAML_BINDING_FAILURE.value,
        AuditEventType.COMPATIBILITY_DRIFT.value,
        AuditEventType.TEST_FAILURE.value,
    }
    
    # Severity levels that warrant issue creation
    ISSUE_SEVERITIES = {"error", "critical", "warning"}
    
    def __init__(
        self,
        enable_notifications: bool = True,
        deduplicate_window_hours: int = 24,
    ):
        """
        Initialize the AuditIssueBridge.
        
        Args:
            enable_notifications: If True, notify DebugRoleNotifier on issue creation
            deduplicate_window_hours: Hours to remember pattern hashes for deduplication
        """
        self._enable_notifications = enable_notifications
        self._deduplicate_hours = deduplicate_window_hours
        self._recent_pattern_hashes: Dict[str, datetime] = {}
        self._issue_store = None
        self._debug_notifier = None
        self._correlation_map: Dict[str, str] = {}  # audit_entry_id -> issue_id
    
    def set_issue_store(self, store) -> None:
        """Set the IssueStore instance for issue persistence."""
        self._issue_store = store
    
    def set_debug_notifier(self, notifier) -> None:
        """Set the DebugRoleNotifier for automatic routing."""
        self._debug_notifier = notifier
    
    def on_audit_entry(self, entry: AuditEntry) -> Optional[str]:
        """
        Process an audit entry and create an issue if warranted.
        
        Args:
            entry: The AuditEntry to process
            
        Returns:
            Issue ID if an issue was created, None otherwise
        """
        # Check if this event type triggers issue creation
        if entry.event_type not in self.ISSUE_TRIGGERING_EVENTS:
            return None
        
        # Check severity (allow warning for compatibility drift)
        severity = (entry.severity or "").lower()
        if severity not in self.ISSUE_SEVERITIES:
            # Special case: compatibility_drift at warning level is still relevant
            if entry.event_type != AuditEventType.COMPATIBILITY_DRIFT.value:
                return None
        
        # Generate pattern hash for deduplication
        pattern_hash = self._generate_pattern_hash(entry)
        
        # Check if we've seen this pattern recently
        if self._is_duplicate(pattern_hash):
            return None
        
        # Create the issue
        issue_id = self._create_issue(entry, pattern_hash)
        
        if issue_id:
            # Record the pattern hash
            self._recent_pattern_hashes[pattern_hash] = datetime.now(timezone.utc)
            
            # Map audit entry to issue for correlation
            self._correlation_map[entry.entry_id] = issue_id
            
            # Notify Debug Role if enabled
            if self._enable_notifications and self._debug_notifier:
                self._notify_debug_role(entry, issue_id)
        
        return issue_id
    
    def _generate_pattern_hash(self, entry: AuditEntry) -> str:
        """
        Generate a pattern hash for deduplication.
        
        The hash is based on:
        - Event type
        - Error code (if any)
        - File path (if any)
        - Subsystem
        - First line of message (to group similar errors)
        """
        components = [
            entry.event_type or "",
            entry.error_code or "",
            entry.file_path or "",
            entry.subsystem or "",
        ]
        
        # Include first line of message to group similar errors
        if entry.message:
            first_line = entry.message.split("\n")[0][:100]
            components.append(first_line)
        
        hash_input = "|".join(components)
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _is_duplicate(self, pattern_hash: str) -> bool:
        """Check if this pattern was seen recently."""
        if pattern_hash not in self._recent_pattern_hashes:
            return False
        
        # Check if the hash is within the deduplication window
        last_seen = self._recent_pattern_hashes[pattern_hash]
        age_hours = (datetime.now(timezone.utc) - last_seen).total_seconds() / 3600
        
        if age_hours > self._deduplicate_hours:
            # Hash expired, remove it
            del self._recent_pattern_hashes[pattern_hash]
            return False
        
        return True
    
    def _create_issue(self, entry: AuditEntry, pattern_hash: str) -> Optional[str]:
        """
        Create an Issue from an AuditEntry and store it.
        
        Returns:
            Issue ID if created, None if store not available
        """
        if not self._issue_store:
            return None
        
        try:
            # Lazy import to avoid circular dependencies
            from tools.overseer.issues.models import (
                Issue,
                InstanceType,
                IssueSeverity,
                IssueStatus,
            )
            
            # Map audit event type to instance type
            instance_type = self._map_instance_type(entry)
            
            # Map severity
            severity = self._map_severity(entry.severity)
            
            # Determine category for role routing
            category = self._determine_category(entry)
            
            # Generate issue ID
            issue_id = f"ISS-{entry.entry_id}"
            
            # Build context from entry
            context: Dict[str, Any] = {
                "audit_entry_id": entry.entry_id,
                "correlation_id": entry.correlation_id,
                "subsystem": entry.subsystem,
                "file_path": entry.file_path,
                "commit_hash": entry.commit_hash,
                "task_id": entry.task_id,
                "role": entry.role,
            }
            
            if entry.stack_trace:
                context["traceback"] = entry.stack_trace
            if entry.error_code:
                context["_error_codes"] = [entry.error_code]
            if entry.extra:
                context.update(entry.extra)
            
            # Create the Issue object
            issue = Issue(
                id=issue_id,
                timestamp=datetime.fromisoformat(entry.timestamp.replace("Z", "+00:00"))
                    if entry.timestamp else datetime.now(timezone.utc),
                instance_type=instance_type,
                instance_id=entry.subsystem or "audit-bridge",
                correlation_id=entry.correlation_id,
                severity=severity,
                category=category,
                error_type=entry.event_type,
                message=entry.message or entry.summary or "No message",
                context=context,
                pattern_hash=pattern_hash,
                status=IssueStatus.NEW,
            )
            
            # Store the issue
            self._issue_store.append(issue)
            
            return issue_id
            
        except ImportError:
            # Issue system not available
            return None
        except Exception:
            # Log but don't crash on issue creation failure
            return None
    
    def _map_instance_type(self, entry: AuditEntry):
        """Map audit entry to InstanceType."""
        from tools.overseer.issues.models import InstanceType
        
        event_type = entry.event_type or ""
        subsystem = (entry.subsystem or "").lower()
        
        if "xaml" in event_type.lower() or "ui" in subsystem:
            return InstanceType.FRONTEND
        if "build" in event_type.lower():
            return InstanceType.BUILD
        if "engine" in subsystem:
            return InstanceType.ENGINE
        if "backend" in subsystem or "api" in subsystem:
            return InstanceType.BACKEND
        
        return InstanceType.AGENT
    
    def _map_severity(self, severity_str: Optional[str]):
        """Map severity string to IssueSeverity enum."""
        from tools.overseer.issues.models import IssueSeverity
        
        severity_map = {
            "critical": IssueSeverity.CRITICAL,
            "error": IssueSeverity.HIGH,
            "warning": IssueSeverity.MEDIUM,
            "info": IssueSeverity.LOW,
        }
        return severity_map.get((severity_str or "").lower(), IssueSeverity.MEDIUM)
    
    def _determine_category(self, entry: AuditEntry) -> str:
        """
        Determine the category for role routing.
        
        Categories map to roles in task_generator.py CATEGORY_TO_ROLE.
        """
        event_type = entry.event_type or ""
        subsystem = (entry.subsystem or "").lower()
        
        # Event-based categorization
        if "xaml" in event_type.lower():
            return "UI"
        if "build" in event_type.lower():
            return "BUILD"
        if "exception" in event_type.lower():
            return "EXCEPTION"
        if "drift" in event_type.lower():
            return "RUNTIME"
        if "test" in event_type.lower():
            return "DEBUG"
        
        # Subsystem-based categorization
        if "ui" in subsystem or "panel" in subsystem:
            return "UI"
        if "engine" in subsystem:
            return "ENGINE"
        if "backend" in subsystem or "api" in subsystem:
            return "RUNTIME"
        if "storage" in subsystem or "database" in subsystem:
            return "STORAGE"
        
        # Default to ERROR for Debug Role routing
        return "ERROR"
    
    def _notify_debug_role(self, entry: AuditEntry, issue_id: str) -> None:
        """Notify the Debug Role of a new issue."""
        if not self._debug_notifier:
            return
        
        try:
            self._debug_notifier.notify(
                issue_id=issue_id,
                severity=entry.severity or "error",
                message=entry.message or entry.summary or "New issue from audit",
                subsystem=entry.subsystem,
                correlation_id=entry.correlation_id,
            )
        except Exception:
            # Don't let notification failures break the audit flow
            pass
    
    def get_issue_for_entry(self, entry_id: str) -> Optional[str]:
        """Get the issue ID associated with an audit entry ID."""
        return self._correlation_map.get(entry_id)
    
    def cleanup_expired_hashes(self) -> int:
        """
        Remove expired pattern hashes from memory.
        
        Returns:
            Number of hashes removed
        """
        now = datetime.now(timezone.utc)
        expired = []
        
        for pattern_hash, last_seen in self._recent_pattern_hashes.items():
            age_hours = (now - last_seen).total_seconds() / 3600
            if age_hours > self._deduplicate_hours:
                expired.append(pattern_hash)
        
        for pattern_hash in expired:
            del self._recent_pattern_hashes[pattern_hash]
        
        return len(expired)


# Global bridge instance
_audit_issue_bridge: Optional[AuditIssueBridge] = None


def get_audit_issue_bridge() -> AuditIssueBridge:
    """Get or create the global AuditIssueBridge instance."""
    global _audit_issue_bridge
    if _audit_issue_bridge is None:
        _audit_issue_bridge = AuditIssueBridge()
        
        # Try to connect to issue store
        try:
            from tools.overseer.issues.store import IssueStore
            _audit_issue_bridge.set_issue_store(IssueStore())
        # ALLOWED: bare except - Optional dependency, import failure is acceptable
        except ImportError:
            pass
    
    return _audit_issue_bridge


def setup_audit_issue_bridge(
    enable_notifications: bool = True,
    deduplicate_window_hours: int = 24,
) -> AuditIssueBridge:
    """
    Setup the global AuditIssueBridge with custom configuration.
    
    Args:
        enable_notifications: Enable Debug Role notifications
        deduplicate_window_hours: Deduplication window in hours
        
    Returns:
        Configured AuditIssueBridge instance
    """
    global _audit_issue_bridge
    _audit_issue_bridge = AuditIssueBridge(
        enable_notifications=enable_notifications,
        deduplicate_window_hours=deduplicate_window_hours,
    )
    
    # Try to connect to issue store
    try:
        from tools.overseer.issues.store import IssueStore
        _audit_issue_bridge.set_issue_store(IssueStore())
    # ALLOWED: bare except - Optional dependency, import failure is acceptable
    except ImportError:
        pass
    
    return _audit_issue_bridge
