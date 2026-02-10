"""
Authentication Audit Trail.

Task 2.1.5: Log all authentication attempts.
Comprehensive logging for security monitoring.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AuthEventType(Enum):
    """Types of authentication events."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    TOKEN_ISSUED = "token_issued"
    TOKEN_REFRESH = "token_refresh"
    TOKEN_REVOKED = "token_revoked"
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    MFA_CHALLENGE = "mfa_challenge"
    MFA_SUCCESS = "mfa_success"
    MFA_FAILURE = "mfa_failure"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class RiskLevel(Enum):
    """Risk level of auth event."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuthEvent:
    """An authentication event."""
    id: str
    event_type: AuthEventType
    timestamp: datetime
    user_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    success: bool
    risk_level: RiskLevel
    details: Dict[str, Any] = field(default_factory=dict)
    session_id: Optional[str] = None
    location: Optional[Dict[str, str]] = None


@dataclass
class AuthAuditConfig:
    """Configuration for auth audit."""
    storage_path: str = "data/auth_audit"
    retention_days: int = 365
    alert_on_risk_level: RiskLevel = RiskLevel.HIGH
    max_login_failures: int = 5
    lockout_duration_minutes: int = 30


class AuthAuditLogger:
    """
    Authentication audit logger.
    
    Features:
    - Comprehensive auth event logging
    - Risk assessment
    - Suspicious activity detection
    - Login failure tracking
    - Account lockout support
    """
    
    def __init__(self, config: Optional[AuthAuditConfig] = None):
        self.config = config or AuthAuditConfig()
        
        self._storage_path = Path(self.config.storage_path)
        self._storage_path.mkdir(parents=True, exist_ok=True)
        
        self._login_failures: Dict[str, List[datetime]] = {}
        self._locked_accounts: Dict[str, datetime] = {}
        self._event_counter = 0
        self._lock = asyncio.Lock()
    
    async def log_event(
        self,
        event_type: AuthEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        details: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> AuthEvent:
        """Log an authentication event."""
        async with self._lock:
            self._event_counter += 1
            event_id = f"auth_{datetime.now().strftime('%Y%m%d')}_{self._event_counter}"
            
            # Assess risk
            risk_level = self._assess_risk(event_type, success, user_id, ip_address)
            
            event = AuthEvent(
                id=event_id,
                event_type=event_type,
                timestamp=datetime.now(),
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                risk_level=risk_level,
                details=details or {},
                session_id=session_id,
            )
            
            # Write to storage
            await self._write_event(event)
            
            # Track failures
            if event_type == AuthEventType.LOGIN_FAILURE and user_id:
                await self._track_failure(user_id)
            elif event_type == AuthEventType.LOGIN_SUCCESS and user_id:
                self._clear_failures(user_id)
            
            # Alert if high risk
            if risk_level.value >= self.config.alert_on_risk_level.value:
                logger.warning(f"High risk auth event: {event_type.value} for {user_id}")
            
            return event
    
    def _assess_risk(
        self,
        event_type: AuthEventType,
        success: bool,
        user_id: Optional[str],
        ip_address: Optional[str],
    ) -> RiskLevel:
        """Assess risk level of event."""
        # Critical events
        if event_type in (AuthEventType.ACCOUNT_LOCKED, AuthEventType.SUSPICIOUS_ACTIVITY):
            return RiskLevel.CRITICAL
        
        # High risk
        if event_type == AuthEventType.LOGIN_FAILURE:
            if user_id and self._get_failure_count(user_id) >= 3:
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM
        
        if event_type == AuthEventType.PASSWORD_RESET_REQUEST:
            return RiskLevel.MEDIUM
        
        # Default
        return RiskLevel.LOW
    
    async def _write_event(self, event: AuthEvent) -> None:
        """Write event to storage."""
        file_path = self._storage_path / f"auth_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        
        event_dict = {
            "id": event.id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "success": event.success,
            "risk_level": event.risk_level.value,
            "details": event.details,
            "session_id": event.session_id,
        }
        
        with open(file_path, "a") as f:
            f.write(json.dumps(event_dict) + "\n")
    
    async def _track_failure(self, user_id: str) -> None:
        """Track login failure."""
        now = datetime.now()
        
        if user_id not in self._login_failures:
            self._login_failures[user_id] = []
        
        self._login_failures[user_id].append(now)
        
        # Clean old failures
        cutoff = now - timedelta(minutes=self.config.lockout_duration_minutes)
        self._login_failures[user_id] = [
            t for t in self._login_failures[user_id] if t > cutoff
        ]
        
        # Check for lockout
        if len(self._login_failures[user_id]) >= self.config.max_login_failures:
            await self._lock_account(user_id)
    
    def _get_failure_count(self, user_id: str) -> int:
        """Get recent failure count for user."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=self.config.lockout_duration_minutes)
        
        failures = self._login_failures.get(user_id, [])
        return sum(1 for t in failures if t > cutoff)
    
    def _clear_failures(self, user_id: str) -> None:
        """Clear failure tracking for user."""
        self._login_failures.pop(user_id, None)
    
    async def _lock_account(self, user_id: str) -> None:
        """Lock an account."""
        self._locked_accounts[user_id] = datetime.now()
        
        await self.log_event(
            event_type=AuthEventType.ACCOUNT_LOCKED,
            user_id=user_id,
            success=False,
            details={"reason": "Too many failed login attempts"},
        )
    
    def is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked."""
        if user_id not in self._locked_accounts:
            return False
        
        locked_at = self._locked_accounts[user_id]
        unlock_time = locked_at + timedelta(minutes=self.config.lockout_duration_minutes)
        
        if datetime.now() > unlock_time:
            del self._locked_accounts[user_id]
            return False
        
        return True
    
    async def unlock_account(self, user_id: str) -> bool:
        """Manually unlock an account."""
        if user_id in self._locked_accounts:
            del self._locked_accounts[user_id]
            self._clear_failures(user_id)
            
            await self.log_event(
                event_type=AuthEventType.ACCOUNT_UNLOCKED,
                user_id=user_id,
                success=True,
            )
            return True
        return False
    
    async def query_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[AuthEventType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[AuthEvent]:
        """Query auth events."""
        results = []
        
        files = sorted(self._storage_path.glob("auth_*.jsonl"), reverse=True)
        
        for file_path in files:
            with open(file_path, "r") as f:
                for line in f:
                    if len(results) >= limit:
                        return results
                    
                    try:
                        data = json.loads(line)
                        
                        # Apply filters
                        if user_id and data.get("user_id") != user_id:
                            continue
                        if event_type and data.get("event_type") != event_type.value:
                            continue
                        
                        event = AuthEvent(
                            id=data["id"],
                            event_type=AuthEventType(data["event_type"]),
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            user_id=data.get("user_id"),
                            ip_address=data.get("ip_address"),
                            user_agent=data.get("user_agent"),
                            success=data.get("success", True),
                            risk_level=RiskLevel(data.get("risk_level", "low")),
                            details=data.get("details", {}),
                            session_id=data.get("session_id"),
                        )
                        
                        results.append(event)
                        
                    except Exception:
                        continue
        
        return results
    
    def get_stats(self) -> Dict:
        """Get audit statistics."""
        return {
            "locked_accounts": len(self._locked_accounts),
            "tracked_failures": sum(len(f) for f in self._login_failures.values()),
            "storage_path": str(self._storage_path),
            "retention_days": self.config.retention_days,
        }


# Global auth audit logger
_auth_audit: Optional[AuthAuditLogger] = None


def get_auth_audit_logger() -> AuthAuditLogger:
    """Get or create the global auth audit logger."""
    global _auth_audit
    if _auth_audit is None:
        _auth_audit = AuthAuditLogger()
    return _auth_audit
