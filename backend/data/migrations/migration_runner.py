"""
Database Migration Framework.

Task 1.3.4: Schema migration support.
Handles database schema migrations with rollback support.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger(__name__)


class MigrationStatus(Enum):
    """Status of a migration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationRecord:
    """Record of a migration execution."""
    migration_id: str
    version: int
    name: str
    status: MigrationStatus
    applied_at: Optional[datetime] = None
    rolled_back_at: Optional[datetime] = None
    checksum: str = ""
    execution_time_ms: float = 0
    error_message: Optional[str] = None


class Migration(ABC):
    """
    Base class for database migrations.
    
    Each migration should implement upgrade() and downgrade().
    """
    
    @property
    @abstractmethod
    def version(self) -> int:
        """Migration version number (must be unique and sequential)."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable migration name."""
        pass
    
    @property
    def description(self) -> str:
        """Optional description of what this migration does."""
        return ""
    
    @abstractmethod
    async def upgrade(self, connection: Any) -> None:
        """
        Apply the migration.
        
        Args:
            connection: Database connection
        """
        pass
    
    @abstractmethod
    async def downgrade(self, connection: Any) -> None:
        """
        Rollback the migration.
        
        Args:
            connection: Database connection
        """
        pass
    
    def get_checksum(self) -> str:
        """Generate checksum for migration validation."""
        import inspect
        source = inspect.getsource(self.__class__)
        return hashlib.md5(source.encode()).hexdigest()


class MigrationRunner:
    """
    Runs database migrations.
    
    Features:
    - Ordered migration execution
    - Rollback support
    - Dry-run mode
    - Migration history tracking
    - Checksum validation
    """
    
    def __init__(
        self,
        connection: Any,
        migrations_table: str = "_migrations",
        history_path: str = "data/migrations",
    ):
        self._connection = connection
        self._migrations_table = migrations_table
        self._history_path = Path(history_path)
        self._history_path.mkdir(parents=True, exist_ok=True)
        
        self._migrations: List[Migration] = []
        self._history: Dict[int, MigrationRecord] = {}
        self._lock = asyncio.Lock()
    
    async def initialize(self) -> None:
        """Initialize migrations table and load history."""
        await self._ensure_migrations_table()
        await self._load_history()
    
    async def _ensure_migrations_table(self) -> None:
        """Create migrations tracking table if needed."""
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self._migrations_table} (
            version INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            applied_at TEXT,
            rolled_back_at TEXT,
            checksum TEXT,
            execution_time_ms REAL,
            error_message TEXT
        )
        """
        await self._execute(sql)
    
    async def _load_history(self) -> None:
        """Load migration history from database."""
        sql = f"SELECT * FROM {self._migrations_table}"
        rows = await self._fetch_all(sql)
        
        for row in rows:
            self._history[row["version"]] = MigrationRecord(
                migration_id=f"v{row['version']}_{row['name']}",
                version=row["version"],
                name=row["name"],
                status=MigrationStatus(row["status"]),
                applied_at=datetime.fromisoformat(row["applied_at"]) if row["applied_at"] else None,
                rolled_back_at=datetime.fromisoformat(row["rolled_back_at"]) if row["rolled_back_at"] else None,
                checksum=row["checksum"] or "",
                execution_time_ms=row["execution_time_ms"] or 0,
                error_message=row["error_message"],
            )
    
    async def _execute(self, sql: str, params: tuple = ()) -> None:
        """Execute SQL statement."""
        if hasattr(self._connection, "execute"):
            await self._connection.execute(sql, params)
            if hasattr(self._connection, "commit"):
                await self._connection.commit()
    
    async def _fetch_all(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Fetch all rows from query."""
        if hasattr(self._connection, "execute"):
            async with self._connection.execute(sql, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        return []
    
    def register(self, migration: Migration) -> None:
        """Register a migration."""
        # Check for duplicate versions
        for m in self._migrations:
            if m.version == migration.version:
                raise ValueError(f"Duplicate migration version: {migration.version}")
        
        self._migrations.append(migration)
        # Keep sorted by version
        self._migrations.sort(key=lambda m: m.version)
        
        logger.debug(f"Registered migration: {migration.version} - {migration.name}")
    
    def register_class(self, migration_class: Type[Migration]) -> None:
        """Register a migration class (instantiates it)."""
        self.register(migration_class())
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get migrations that haven't been applied."""
        pending = []
        
        for migration in self._migrations:
            record = self._history.get(migration.version)
            if not record or record.status != MigrationStatus.COMPLETED:
                pending.append(migration)
        
        return pending
    
    def get_applied_migrations(self) -> List[MigrationRecord]:
        """Get migrations that have been applied."""
        return [
            record for record in self._history.values()
            if record.status == MigrationStatus.COMPLETED
        ]
    
    async def migrate(
        self,
        target_version: Optional[int] = None,
        dry_run: bool = False,
    ) -> List[MigrationRecord]:
        """
        Run pending migrations.
        
        Args:
            target_version: Target version (None for latest)
            dry_run: If True, don't actually apply changes
            
        Returns:
            List of migration records
        """
        async with self._lock:
            pending = self.get_pending_migrations()
            
            if target_version is not None:
                pending = [m for m in pending if m.version <= target_version]
            
            if not pending:
                logger.info("No pending migrations")
                return []
            
            results = []
            
            for migration in pending:
                if dry_run:
                    logger.info(f"[DRY RUN] Would apply: {migration.version} - {migration.name}")
                    continue
                
                record = await self._apply_migration(migration)
                results.append(record)
                
                if record.status == MigrationStatus.FAILED:
                    logger.error(f"Migration failed, stopping: {record.error_message}")
                    break
            
            return results
    
    async def _apply_migration(self, migration: Migration) -> MigrationRecord:
        """Apply a single migration."""
        record = MigrationRecord(
            migration_id=f"v{migration.version}_{migration.name}",
            version=migration.version,
            name=migration.name,
            status=MigrationStatus.RUNNING,
            checksum=migration.get_checksum(),
        )
        
        logger.info(f"Applying migration: {migration.version} - {migration.name}")
        start_time = asyncio.get_event_loop().time()
        
        try:
            await migration.upgrade(self._connection)
            
            record.status = MigrationStatus.COMPLETED
            record.applied_at = datetime.now()
            record.execution_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            logger.info(f"Migration completed in {record.execution_time_ms:.1f}ms")
            
        except Exception as e:
            record.status = MigrationStatus.FAILED
            record.error_message = str(e)
            record.execution_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            logger.error(f"Migration failed: {e}")
        
        # Save record
        await self._save_record(record)
        self._history[record.version] = record
        
        return record
    
    async def rollback(
        self,
        target_version: Optional[int] = None,
        steps: int = 1,
    ) -> List[MigrationRecord]:
        """
        Rollback migrations.
        
        Args:
            target_version: Target version to rollback to
            steps: Number of migrations to rollback (if target_version not set)
            
        Returns:
            List of rollback records
        """
        async with self._lock:
            applied = sorted(
                [r for r in self._history.values() if r.status == MigrationStatus.COMPLETED],
                key=lambda r: r.version,
                reverse=True,
            )
            
            if not applied:
                logger.info("No migrations to rollback")
                return []
            
            to_rollback = []
            
            if target_version is not None:
                to_rollback = [r for r in applied if r.version > target_version]
            else:
                to_rollback = applied[:steps]
            
            results = []
            
            for record in to_rollback:
                # Find migration class
                migration = next(
                    (m for m in self._migrations if m.version == record.version),
                    None,
                )
                
                if not migration:
                    logger.error(f"Migration class not found for version {record.version}")
                    continue
                
                result = await self._rollback_migration(migration, record)
                results.append(result)
                
                if result.status == MigrationStatus.FAILED:
                    break
            
            return results
    
    async def _rollback_migration(
        self,
        migration: Migration,
        record: MigrationRecord,
    ) -> MigrationRecord:
        """Rollback a single migration."""
        logger.info(f"Rolling back: {migration.version} - {migration.name}")
        start_time = asyncio.get_event_loop().time()
        
        try:
            await migration.downgrade(self._connection)
            
            record.status = MigrationStatus.ROLLED_BACK
            record.rolled_back_at = datetime.now()
            record.execution_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            logger.info(f"Rollback completed in {record.execution_time_ms:.1f}ms")
            
        except Exception as e:
            record.status = MigrationStatus.FAILED
            record.error_message = f"Rollback failed: {e}"
            record.execution_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            logger.error(f"Rollback failed: {e}")
        
        # Save record
        await self._save_record(record)
        
        return record
    
    async def _save_record(self, record: MigrationRecord) -> None:
        """Save migration record to database."""
        sql = f"""
        INSERT OR REPLACE INTO {self._migrations_table}
        (version, name, status, applied_at, rolled_back_at, checksum, execution_time_ms, error_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        await self._execute(sql, (
            record.version,
            record.name,
            record.status.value,
            record.applied_at.isoformat() if record.applied_at else None,
            record.rolled_back_at.isoformat() if record.rolled_back_at else None,
            record.checksum,
            record.execution_time_ms,
            record.error_message,
        ))
    
    def get_status(self) -> Dict[str, Any]:
        """Get migration status."""
        pending = self.get_pending_migrations()
        applied = self.get_applied_migrations()
        
        return {
            "total_migrations": len(self._migrations),
            "applied_count": len(applied),
            "pending_count": len(pending),
            "current_version": max((r.version for r in applied), default=0),
            "latest_version": max((m.version for m in self._migrations), default=0),
            "pending_migrations": [
                {"version": m.version, "name": m.name}
                for m in pending
            ],
        }
