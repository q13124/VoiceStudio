"""
Session Management.

Task 2.1.3: Secure session handling.
Manages user sessions with security best practices.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """A user session."""
    session_id: str
    user_id: str
    created_at: datetime
    last_accessed: datetime
    expires_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    refresh_token_hash: Optional[str] = None
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        return self.is_active and not self.is_expired
    
    def touch(self) -> None:
        """Update last accessed time."""
        self.last_accessed = datetime.now()


@dataclass
class SessionConfig:
    """Configuration for session management."""
    session_lifetime_hours: int = 24
    idle_timeout_minutes: int = 30
    max_sessions_per_user: int = 5
    secure_cookies: bool = True
    http_only: bool = True
    same_site: str = "lax"
    refresh_token_enabled: bool = True
    refresh_token_lifetime_days: int = 7


class SessionManager:
    """
    Secure session management.
    
    Features:
    - Session creation and validation
    - Automatic expiry
    - Idle timeout
    - Concurrent session limiting
    - Refresh token support
    - Session data storage
    """
    
    def __init__(self, config: Optional[SessionConfig] = None):
        self.config = config or SessionConfig()
        
        self._sessions: Dict[str, Session] = {}
        self._user_sessions: Dict[str, list[str]] = {}
        self._refresh_tokens: Dict[str, str] = {}  # hash -> session_id
        self._lock = asyncio.Lock()
        self._running = False
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start session cleanup task."""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Session manager started")
    
    async def stop(self) -> None:
        """Stop session manager."""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Session manager stopped")
    
    async def _cleanup_loop(self) -> None:
        """Periodically clean up expired sessions."""
        while self._running:
            try:
                await self._cleanup_expired()
                await asyncio.sleep(300)  # Every 5 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
    
    async def _cleanup_expired(self) -> int:
        """Remove expired sessions."""
        async with self._lock:
            now = datetime.now()
            idle_cutoff = now - timedelta(minutes=self.config.idle_timeout_minutes)
            
            expired = []
            for session_id, session in self._sessions.items():
                if session.is_expired or session.last_accessed < idle_cutoff:
                    expired.append(session_id)
            
            for session_id in expired:
                await self._remove_session_internal(session_id)
            
            return len(expired)
    
    async def create_session(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> tuple[Session, Optional[str]]:
        """
        Create a new session.
        
        Returns:
            Tuple of (session, refresh_token)
        """
        async with self._lock:
            # Check session limit
            user_session_ids = self._user_sessions.get(user_id, [])
            while len(user_session_ids) >= self.config.max_sessions_per_user:
                # Remove oldest session
                oldest_id = user_session_ids[0]
                await self._remove_session_internal(oldest_id)
                user_session_ids = self._user_sessions.get(user_id, [])
            
            # Create session
            session_id = secrets.token_urlsafe(32)
            now = datetime.now()
            
            session = Session(
                session_id=session_id,
                user_id=user_id,
                created_at=now,
                last_accessed=now,
                expires_at=now + timedelta(hours=self.config.session_lifetime_hours),
                ip_address=ip_address,
                user_agent=user_agent,
                data=data or {},
            )
            
            # Create refresh token
            refresh_token = None
            if self.config.refresh_token_enabled:
                refresh_token = secrets.token_urlsafe(48)
                token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
                session.refresh_token_hash = token_hash
                self._refresh_tokens[token_hash] = session_id
            
            self._sessions[session_id] = session
            
            if user_id not in self._user_sessions:
                self._user_sessions[user_id] = []
            self._user_sessions[user_id].append(session_id)
            
            logger.info(f"Created session for user {user_id}")
            return session, refresh_token
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        session = self._sessions.get(session_id)
        
        if not session:
            return None
        
        if not session.is_valid:
            await self.invalidate_session(session_id)
            return None
        
        # Check idle timeout
        idle_cutoff = datetime.now() - timedelta(minutes=self.config.idle_timeout_minutes)
        if session.last_accessed < idle_cutoff:
            await self.invalidate_session(session_id)
            return None
        
        session.touch()
        return session
    
    async def refresh_session(
        self,
        refresh_token: str,
    ) -> tuple[Optional[Session], Optional[str]]:
        """
        Refresh a session using refresh token.
        
        Returns:
            Tuple of (new_session, new_refresh_token)
        """
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        async with self._lock:
            session_id = self._refresh_tokens.get(token_hash)
            if not session_id:
                return None, None
            
            session = self._sessions.get(session_id)
            if not session:
                return None, None
            
            # Remove old refresh token
            del self._refresh_tokens[token_hash]
            
            # Check if within refresh window
            refresh_deadline = session.created_at + timedelta(
                days=self.config.refresh_token_lifetime_days
            )
            if datetime.now() > refresh_deadline:
                await self._remove_session_internal(session_id)
                return None, None
        
        # Create new session (releases lock temporarily)
        return await self.create_session(
            user_id=session.user_id,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            data=session.data,
        )
    
    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        async with self._lock:
            return await self._remove_session_internal(session_id)
    
    async def _remove_session_internal(self, session_id: str) -> bool:
        """Internal session removal (must hold lock)."""
        session = self._sessions.pop(session_id, None)
        if not session:
            return False
        
        # Remove from user sessions
        user_sessions = self._user_sessions.get(session.user_id, [])
        if session_id in user_sessions:
            user_sessions.remove(session_id)
        
        # Remove refresh token
        if session.refresh_token_hash:
            self._refresh_tokens.pop(session.refresh_token_hash, None)
        
        logger.debug(f"Removed session {session_id}")
        return True
    
    async def invalidate_user_sessions(self, user_id: str) -> int:
        """Invalidate all sessions for a user."""
        async with self._lock:
            session_ids = self._user_sessions.pop(user_id, [])
            
            for session_id in session_ids:
                session = self._sessions.pop(session_id, None)
                if session and session.refresh_token_hash:
                    self._refresh_tokens.pop(session.refresh_token_hash, None)
            
            return len(session_ids)
    
    def get_user_sessions(self, user_id: str) -> list[Session]:
        """Get all sessions for a user."""
        session_ids = self._user_sessions.get(user_id, [])
        return [
            self._sessions[sid] for sid in session_ids
            if sid in self._sessions and self._sessions[sid].is_valid
        ]
    
    def get_stats(self) -> Dict:
        """Get session statistics."""
        active = sum(1 for s in self._sessions.values() if s.is_valid)
        
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": active,
            "users_with_sessions": len(self._user_sessions),
            "refresh_tokens": len(self._refresh_tokens),
        }


# Global session manager
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create the global session manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
