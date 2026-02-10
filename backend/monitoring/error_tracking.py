"""
Phase 8: Error Tracking System
Task 8.5: Error tracking and reporting.
"""

import hashlib
import json
import traceback
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional
import logging
import threading

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors."""
    SYSTEM = "system"
    ENGINE = "engine"
    API = "api"
    UI = "ui"
    DATABASE = "database"
    NETWORK = "network"
    USER = "user"
    UNKNOWN = "unknown"


@dataclass
class ErrorContext:
    """Context information for an error."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    operation: Optional[str] = None
    component: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrackedError:
    """A tracked error occurrence."""
    error_id: str
    fingerprint: str
    exception_type: str
    message: str
    stacktrace: str
    severity: ErrorSeverity
    category: ErrorCategory
    first_seen: datetime
    last_seen: datetime
    occurrence_count: int = 1
    context: ErrorContext = field(default_factory=ErrorContext)
    resolved: bool = False
    tags: list[str] = field(default_factory=list)


@dataclass
class ErrorStats:
    """Error statistics."""
    total_errors: int = 0
    errors_by_severity: dict[str, int] = field(default_factory=dict)
    errors_by_category: dict[str, int] = field(default_factory=dict)
    top_errors: list[tuple[str, int]] = field(default_factory=list)
    error_rate_per_minute: float = 0.0


class ErrorTracker:
    """Service for tracking and analyzing errors."""
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        max_errors: int = 10000,
        retention_days: int = 30
    ):
        self._storage_path = storage_path
        self._max_errors = max_errors
        self._retention_days = retention_days
        
        self._errors: dict[str, TrackedError] = {}
        self._error_times: list[datetime] = []
        self._callbacks: list[Callable[[TrackedError], None]] = []
        self._lock = threading.Lock()
        
        if storage_path:
            self._load_errors()
    
    def track(
        self,
        exception: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[ErrorContext] = None,
        tags: Optional[list[str]] = None
    ) -> TrackedError:
        """Track an error occurrence."""
        # Get exception details
        exc_type = type(exception).__name__
        message = str(exception)
        stacktrace = traceback.format_exc()
        
        # Generate fingerprint
        fingerprint = self._generate_fingerprint(exc_type, message, stacktrace)
        
        with self._lock:
            now = datetime.now()
            
            if fingerprint in self._errors:
                # Update existing error
                error = self._errors[fingerprint]
                error.last_seen = now
                error.occurrence_count += 1
                
                # Update context if provided
                if context:
                    error.context = context
                
            else:
                # Create new error
                import uuid
                
                error = TrackedError(
                    error_id=str(uuid.uuid4()),
                    fingerprint=fingerprint,
                    exception_type=exc_type,
                    message=message,
                    stacktrace=stacktrace,
                    severity=severity,
                    category=category,
                    first_seen=now,
                    last_seen=now,
                    context=context or ErrorContext(),
                    tags=tags or [],
                )
                
                self._errors[fingerprint] = error
            
            # Record time for rate calculation
            self._error_times.append(now)
            self._cleanup_error_times()
            
            # Trim old errors if needed
            self._trim_errors()
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.warning(f"Error callback failed: {e}")
        
        # Log the error
        logger.error(
            f"Tracked error: {exc_type}: {message}",
            extra={
                "error_id": error.error_id,
                "fingerprint": fingerprint,
                "severity": severity.value,
                "category": category.value,
            }
        )
        
        return error
    
    def track_exception(
        self,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Optional[ErrorContext] = None
    ):
        """Decorator to track exceptions from a function."""
        def decorator(func: Callable) -> Callable:
            import functools
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.track(e, severity, category, context)
                    raise
            
            return wrapper
        
        return decorator
    
    def get_error(self, error_id: str) -> Optional[TrackedError]:
        """Get an error by ID."""
        for error in self._errors.values():
            if error.error_id == error_id:
                return error
        return None
    
    def get_errors(
        self,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None,
        resolved: Optional[bool] = None,
        limit: int = 100
    ) -> list[TrackedError]:
        """Get filtered list of errors."""
        errors = list(self._errors.values())
        
        if severity:
            errors = [e for e in errors if e.severity == severity]
        
        if category:
            errors = [e for e in errors if e.category == category]
        
        if resolved is not None:
            errors = [e for e in errors if e.resolved == resolved]
        
        # Sort by last seen, most recent first
        errors.sort(key=lambda e: e.last_seen, reverse=True)
        
        return errors[:limit]
    
    def get_stats(self, period_hours: int = 24) -> ErrorStats:
        """Get error statistics."""
        cutoff = datetime.now() - timedelta(hours=period_hours)
        
        errors = [e for e in self._errors.values() if e.last_seen >= cutoff]
        
        by_severity: dict[str, int] = defaultdict(int)
        by_category: dict[str, int] = defaultdict(int)
        
        for error in errors:
            by_severity[error.severity.value] += error.occurrence_count
            by_category[error.category.value] += error.occurrence_count
        
        # Top errors by occurrence
        top_errors = sorted(
            [(e.exception_type, e.occurrence_count) for e in errors],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Calculate error rate
        recent_times = [t for t in self._error_times if t >= cutoff]
        rate = len(recent_times) / (period_hours * 60) if period_hours > 0 else 0
        
        return ErrorStats(
            total_errors=sum(e.occurrence_count for e in errors),
            errors_by_severity=dict(by_severity),
            errors_by_category=dict(by_category),
            top_errors=top_errors,
            error_rate_per_minute=rate,
        )
    
    def resolve(self, error_id: str) -> bool:
        """Mark an error as resolved."""
        error = self.get_error(error_id)
        if error:
            error.resolved = True
            return True
        return False
    
    def add_callback(self, callback: Callable[[TrackedError], None]) -> None:
        """Add an error callback."""
        self._callbacks.append(callback)
    
    def _generate_fingerprint(
        self,
        exc_type: str,
        message: str,
        stacktrace: str
    ) -> str:
        """Generate a fingerprint for error deduplication."""
        # Extract key parts of stacktrace
        lines = stacktrace.strip().split('\n')
        key_lines = [l for l in lines if 'File "' in l][-3:]  # Last 3 file references
        
        content = f"{exc_type}:{message}:{'|'.join(key_lines)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _trim_errors(self) -> None:
        """Trim old errors if limit exceeded."""
        if len(self._errors) <= self._max_errors:
            return
        
        # Sort by last seen and remove oldest
        sorted_errors = sorted(
            self._errors.items(),
            key=lambda x: x[1].last_seen
        )
        
        to_remove = len(self._errors) - self._max_errors
        for fingerprint, _ in sorted_errors[:to_remove]:
            del self._errors[fingerprint]
    
    def _cleanup_error_times(self) -> None:
        """Remove old timestamps from rate calculation."""
        cutoff = datetime.now() - timedelta(hours=1)
        self._error_times = [t for t in self._error_times if t >= cutoff]
    
    def _load_errors(self) -> None:
        """Load errors from storage."""
        if not self._storage_path or not self._storage_path.exists():
            return
        
        try:
            data = json.loads(self._storage_path.read_text())
            
            for error_data in data.get("errors", []):
                error = TrackedError(
                    error_id=error_data["error_id"],
                    fingerprint=error_data["fingerprint"],
                    exception_type=error_data["exception_type"],
                    message=error_data["message"],
                    stacktrace=error_data["stacktrace"],
                    severity=ErrorSeverity(error_data["severity"]),
                    category=ErrorCategory(error_data["category"]),
                    first_seen=datetime.fromisoformat(error_data["first_seen"]),
                    last_seen=datetime.fromisoformat(error_data["last_seen"]),
                    occurrence_count=error_data["occurrence_count"],
                    resolved=error_data.get("resolved", False),
                )
                self._errors[error.fingerprint] = error
                
        except Exception as e:
            logger.warning(f"Failed to load errors: {e}")
    
    def save(self) -> None:
        """Save errors to storage."""
        if not self._storage_path:
            return
        
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "errors": [
                    {
                        "error_id": e.error_id,
                        "fingerprint": e.fingerprint,
                        "exception_type": e.exception_type,
                        "message": e.message,
                        "stacktrace": e.stacktrace,
                        "severity": e.severity.value,
                        "category": e.category.value,
                        "first_seen": e.first_seen.isoformat(),
                        "last_seen": e.last_seen.isoformat(),
                        "occurrence_count": e.occurrence_count,
                        "resolved": e.resolved,
                    }
                    for e in self._errors.values()
                ]
            }
            
            self._storage_path.write_text(json.dumps(data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to save errors: {e}")


# Global tracker instance
_tracker: Optional[ErrorTracker] = None


def get_tracker() -> ErrorTracker:
    """Get the global error tracker."""
    global _tracker
    if _tracker is None:
        _tracker = ErrorTracker()
    return _tracker


def track_error(
    exception: Exception,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.UNKNOWN
) -> TrackedError:
    """Convenience function to track an error."""
    return get_tracker().track(exception, severity, category)
