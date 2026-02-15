"""
Migration v003: Library Persistence Tables.

Creates tables for library asset and folder storage:
- library_assets: Audio files, voice profiles, and other assets (was _assets dict in library.py)
- library_folders: Folder organization for library (was _asset_folders dict in library.py)

Panel Workflow Integration Plan - Library Persistence.
"""

from __future__ import annotations

from typing import Any

from backend.data.migrations.migration_runner import Migration


class LibraryTablesMigration(Migration):
    """
    Creates library persistence tables for asset and folder storage.

    Priority: CRITICAL
    Impact: Library data lost on backend restart without these tables.
    """

    @property
    def version(self) -> int:
        return 3

    @property
    def name(self) -> str:
        return "library_tables"

    @property
    def description(self) -> str:
        return (
            "Creates tables for library_assets and library_folders "
            "to persist library content across backend restarts."
        )

    async def upgrade(self, connection: Any) -> None:
        """Create library persistence tables."""

        # 1. Library Folders Table
        # Replaces: backend/api/routes/library.py:35 (_asset_folders dict)
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS library_folders (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                parent_id TEXT,
                path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                deleted_at TEXT,
                FOREIGN KEY (parent_id) REFERENCES library_folders(id) ON DELETE SET NULL
            )
        """)
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_folders_parent ON library_folders(parent_id)"
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_folders_name ON library_folders(name)"
        )

        # 2. Library Assets Table
        # Replaces: backend/api/routes/library.py:34 (_assets dict)
        await connection.execute("""
            CREATE TABLE IF NOT EXISTS library_assets (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                path TEXT NOT NULL,
                folder_id TEXT,
                tags TEXT,
                metadata TEXT,
                size INTEGER DEFAULT 0,
                duration REAL,
                thumbnail_url TEXT,
                created_at TEXT NOT NULL,
                modified_at TEXT NOT NULL,
                deleted_at TEXT,
                FOREIGN KEY (folder_id) REFERENCES library_folders(id) ON DELETE SET NULL
            )
        """)
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_assets_folder ON library_assets(folder_id)"
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_assets_type ON library_assets(type)"
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_assets_name ON library_assets(name)"
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_library_assets_modified ON library_assets(modified_at)"
        )

        await connection.commit()

    async def downgrade(self, connection: Any) -> None:
        """Drop library tables (in reverse order of dependencies)."""
        tables = [
            "library_assets",
            "library_folders",
        ]

        for table in tables:
            await connection.execute(f"DROP TABLE IF EXISTS {table}")

        await connection.commit()


# Export the migration class
migration = LibraryTablesMigration
