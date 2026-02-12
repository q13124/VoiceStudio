"""
Debug Role Notifier for VoiceStudio.

Automatically notifies the Debug Role (Role 7) when high-severity
issues are created. Integrates with the HandoffQueue for cross-role
escalation.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import threading


class DebugRoleNotifier:
    """
    Notifies the Debug Role when errors are documented.
    
    Monitors issues created by AuditIssueBridge and routes high-severity
    ones to the Debug Role via the HandoffQueue. Supports:
    - Severity-based filtering (only CRITICAL/HIGH by default)
    - Rate limiting to prevent notification floods
    - Correlation with audit entries for full context
    """
    
    # Severity levels that warrant Debug Role notification
    NOTIFY_SEVERITIES = {"critical", "high", "error"}
    
    # Rate limiting: max notifications per window
    MAX_NOTIFICATIONS_PER_HOUR = 20
    
    def __init__(
        self,
        severity_filter: Optional[set] = None,
        rate_limit_per_hour: int = 20,
    ):
        """
        Initialize the DebugRoleNotifier.
        
        Args:
            severity_filter: Set of severity levels to notify on
            rate_limit_per_hour: Maximum notifications per hour
        """
        self._severity_filter = severity_filter or self.NOTIFY_SEVERITIES
        self._rate_limit = rate_limit_per_hour
        self._notification_times: List[datetime] = []
        self._lock = threading.Lock()
        self._handoff_queue = None
        self._callbacks: List[callable] = []
    
    def set_handoff_queue(self, queue) -> None:
        """Set the HandoffQueue for cross-role escalation."""
        self._handoff_queue = queue
    
    def add_callback(self, callback: callable) -> None:
        """Add a callback to be invoked on notifications."""
        self._callbacks.append(callback)
    
    def notify(
        self,
        issue_id: str,
        severity: str,
        message: str,
        subsystem: Optional[str] = None,
        correlation_id: Optional[str] = None,
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Notify Debug Role of a new issue.
        
        Args:
            issue_id: The issue ID
            severity: Severity level (critical, high, error, warning, info)
            message: Issue message/description
            subsystem: Subsystem where the issue occurred
            correlation_id: Correlation ID for tracing
            extra_context: Additional context data
            
        Returns:
            True if notification was sent, False if filtered/rate-limited
        """
        # Check severity filter
        if severity.lower() not in self._severity_filter:
            return False
        
        # Check rate limit
        if not self._check_rate_limit():
            return False
        
        # Record notification time
        with self._lock:
            self._notification_times.append(datetime.now(timezone.utc))
        
        # Create handoff entry
        handoff_created = self._create_handoff(
            issue_id=issue_id,
            severity=severity,
            message=message,
            subsystem=subsystem,
            correlation_id=correlation_id,
        )
        
        # Invoke callbacks
        for callback in self._callbacks:
            try:
                callback(
                    issue_id=issue_id,
                    severity=severity,
                    message=message,
                    subsystem=subsystem,
                    correlation_id=correlation_id,
                    extra_context=extra_context,
                )
            except Exception as e:
                # Don't let callback failures break notification flow
                logger.debug(f"Callback failed during notification (non-critical): {e}")
        
        return handoff_created
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        now = datetime.now(timezone.utc)
        one_hour_ago = now - timedelta(hours=1)
        
        with self._lock:
            # Clean up old entries
            self._notification_times = [
                t for t in self._notification_times
                if t > one_hour_ago
            ]
            
            # Check limit
            return len(self._notification_times) < self._rate_limit
    
    def _create_handoff(
        self,
        issue_id: str,
        severity: str,
        message: str,
        subsystem: Optional[str],
        correlation_id: Optional[str],
    ) -> bool:
        """Create a handoff entry to Debug Role."""
        if not self._handoff_queue:
            # Try to initialize handoff queue
            try:
                from tools.overseer.issues.handoff import HandoffQueue
                self._handoff_queue = HandoffQueue()
            except ImportError:
                return False
        
        try:
            # Determine priority based on severity
            priority_map = {
                "critical": "urgent",
                "high": "high",
                "error": "high",
                "warning": "medium",
                "info": "low",
            }
            priority = priority_map.get(severity.lower(), "medium")
            
            # Build handoff reason
            reason = f"Auto-routed: {severity.upper()} severity error detected"
            if subsystem:
                reason += f" in {subsystem}"
            if message:
                reason += f" - {message[:100]}"
            
            # Create handoff
            self._handoff_queue.handoff(
                issue_id=issue_id,
                from_role="audit-system",
                to_role="debug-agent",
                reason=reason,
                priority=priority,
                severity=severity.lower(),
            )
            
            return True
            
        except Exception as e:
            logger.debug(f"Failed to create handoff entry: {e}")
            return False
    
    def get_pending_count(self) -> int:
        """Get count of pending notifications in the last hour."""
        with self._lock:
            now = datetime.now(timezone.utc)
            one_hour_ago = now - timedelta(hours=1)
            return len([t for t in self._notification_times if t > one_hour_ago])
    
    def get_stats(self) -> Dict[str, Any]:
        """Get notification statistics."""
        with self._lock:
            now = datetime.now(timezone.utc)
            one_hour_ago = now - timedelta(hours=1)
            recent = [t for t in self._notification_times if t > one_hour_ago]
            
            return {
                "notifications_last_hour": len(recent),
                "rate_limit": self._rate_limit,
                "remaining_capacity": max(0, self._rate_limit - len(recent)),
                "severity_filter": list(self._severity_filter),
                "handoff_queue_connected": self._handoff_queue is not None,
            }


# Global notifier instance
_debug_notifier: Optional[DebugRoleNotifier] = None


def get_debug_notifier() -> DebugRoleNotifier:
    """Get or create the global DebugRoleNotifier instance."""
    global _debug_notifier
    if _debug_notifier is None:
        _debug_notifier = DebugRoleNotifier()
        
        # Try to connect to handoff queue
        try:
            from tools.overseer.issues.handoff import HandoffQueue
            _debug_notifier.set_handoff_queue(HandoffQueue())
        # ALLOWED: bare except - Optional dependency, import failure is acceptable
        except ImportError:
            pass
    
    return _debug_notifier


def setup_debug_notifier(
    severity_filter: Optional[set] = None,
    rate_limit_per_hour: int = 20,
) -> DebugRoleNotifier:
    """
    Setup the global DebugRoleNotifier with custom configuration.
    
    Args:
        severity_filter: Set of severity levels to notify on
        rate_limit_per_hour: Maximum notifications per hour
        
    Returns:
        Configured DebugRoleNotifier instance
    """
    global _debug_notifier
    _debug_notifier = DebugRoleNotifier(
        severity_filter=severity_filter,
        rate_limit_per_hour=rate_limit_per_hour,
    )
    
    # Try to connect to handoff queue
    try:
        from tools.overseer.issues.handoff import HandoffQueue
        _debug_notifier.set_handoff_queue(HandoffQueue())
    # ALLOWED: bare except - Optional dependency, import failure is acceptable
    except ImportError:
        pass
    
    return _debug_notifier


def connect_to_issue_bridge() -> bool:
    """
    Connect the DebugRoleNotifier to the AuditIssueBridge.
    
    Call this after both systems are initialized to enable
    automatic Debug Role notification on issue creation.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        from .issue_bridge import get_audit_issue_bridge
        
        notifier = get_debug_notifier()
        bridge = get_audit_issue_bridge()
        bridge.set_debug_notifier(notifier)
        
        return True
    except Exception:
        return False
