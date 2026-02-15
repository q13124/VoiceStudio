"""
Session Repository.

Backend-Frontend Integration Plan - Phase 1.
Replaces in-memory storage in backend/security/session.py.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from backend.data.repository_base import (
    BaseEntity,
    BaseRepository,
    ConnectionConfig,
    QueryOptions,
)

logger = logging.getLogger(__name__)


@dataclass
class SessionEntity(BaseEntity):
    """
    Session entity for persistent storage.

    Maps to sessions table.
    """
    user_id: str = ""
    token_hash: str = ""
    device_info: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    is_active: bool = True
    last_activity: str | None = None
    expires_at: str = ""
    data: str = "{}"  # JSON for session data

    def get_data(self) -> dict[str, Any]:
        """Parse session data JSON."""
        try:
            return json.loads(self.data) if self.data else {}
        except json.JSONDecodeError:
            return {}

    def set_data(self, data: dict[str, Any]) -> None:
        """Set session data as JSON string."""
        self.data = json.dumps(data)

    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        if not self.expires_at:
            return True
        try:
            expires = datetime.fromisoformat(self.expires_at)
            return datetime.now() > expires
        except ValueError:
            return True

    @property
    def is_valid(self) -> bool:
        """Check if session is valid."""
        return self.is_active and not self.is_expired


class SessionRepository(BaseRepository[SessionEntity]):
    """
    Repository for session persistence.

    Replaces the in-memory _sessions dict with database-backed storage.
    """

    def __init__(self, config: ConnectionConfig | None = None):
        super().__init__(
            entity_type=SessionEntity,
            table_name="sessions",
            config=config,
        )

    def _entity_to_dict(self, entity: SessionEntity) -> dict[str, Any]:
        """Convert SessionEntity to database row dict."""
        return {
            "id": entity.id,
            "user_id": entity.user_id,
            "token_hash": entity.token_hash,
            "device_info": entity.device_info,
            "ip_address": entity.ip_address,
            "user_agent": entity.user_agent,
            "is_active": 1 if entity.is_active else 0,
            "last_activity": entity.last_activity,
            "expires_at": entity.expires_at,
            "created_at": entity.created_at.isoformat() if isinstance(entity.created_at, datetime) else entity.created_at,
            "deleted_at": entity.deleted_at.isoformat() if entity.deleted_at else None,
        }

    def _row_to_entity(self, row: dict[str, Any]) -> SessionEntity:
        """Convert database row to SessionEntity."""
        return SessionEntity(
            id=row["id"],
            user_id=row.get("user_id", ""),
            token_hash=row.get("token_hash", ""),
            device_info=row.get("device_info"),
            ip_address=row.get("ip_address"),
            user_agent=row.get("user_agent"),
            is_active=bool(row.get("is_active", 1)),
            last_activity=row.get("last_activity"),
            expires_at=row.get("expires_at", ""),
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else datetime.now(),
            deleted_at=datetime.fromisoformat(row["deleted_at"]) if row.get("deleted_at") else None,
        )

    async def get_by_token_hash(self, token_hash: str) -> SessionEntity | None:
        """Get session by token hash."""
        return await self.find_one({"token_hash": token_hash})

    async def get_user_sessions(self, user_id: str) -> list[SessionEntity]:
        """Get all sessions for a user."""
        return await self.find(
            {"user_id": user_id, "is_active": 1},
            QueryOptions(order_by="created_at", order_desc=True),
        )

    async def get_active_sessions(self) -> list[SessionEntity]:
        """Get all active sessions."""
        await self.connect()

        query = f"""
            SELECT * FROM {self.table_name}
            WHERE is_active = 1
            AND deleted_at IS NULL
            AND datetime(expires_at) > datetime('now')
            ORDER BY last_activity DESC
        """

        async with self._connection.execute(query) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_entity(dict(row)) for row in rows]

    async def touch(self, session_id: str) -> SessionEntity | None:
        """Update last activity time."""
        return await self.update(session_id, {
            "last_activity": datetime.now().isoformat(),
        })

    async def deactivate(self, session_id: str) -> SessionEntity | None:
        """Deactivate a session."""
        return await self.update(session_id, {"is_active": 0})

    async def deactivate_user_sessions(self, user_id: str) -> int:
        """Deactivate all sessions for a user."""
        await self.connect()

        query = f"""
            UPDATE {self.table_name}
            SET is_active = 0, updated_at = ?
            WHERE user_id = ? AND is_active = 1
        """

        await self._connection.execute(query, (datetime.now().isoformat(), user_id))
        await self._connection.commit()

        return self._connection.total_changes

    async def cleanup_expired(self) -> int:
        """Clean up expired sessions (soft delete)."""
        await self.connect()

        query = f"""
            UPDATE {self.table_name}
            SET deleted_at = ?, is_active = 0
            WHERE datetime(expires_at) < datetime('now')
            AND deleted_at IS NULL
        """

        await self._connection.execute(query, (datetime.now().isoformat(),))
        await self._connection.commit()

        return self._connection.total_changes

    async def get_session_count_by_user(self, user_id: str) -> int:
        """Get count of active sessions for a user."""
        return await self.count({"user_id": user_id, "is_active": 1})


# Singleton instance
_session_repository: SessionRepository | None = None


def get_session_repository() -> SessionRepository:
    """Get or create SessionRepository singleton."""
    global _session_repository
    if _session_repository is None:
        _session_repository = SessionRepository()
    return _session_repository
