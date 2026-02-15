"""Database migration framework."""

from backend.data.migrations.migration_runner import (
    Migration,
    MigrationRunner,
    MigrationStatus,
)
from backend.data.migrations.v001_core_persistence_tables import (
    CorePersistenceTablesMigration,
)
from backend.data.migrations.v002_performance_indexes import (
    PerformanceIndexesMigration,
)
from backend.data.migrations.v003_library_tables import (
    LibraryTablesMigration,
)

__all__ = [
    "CorePersistenceTablesMigration",
    "LibraryTablesMigration",
    "Migration",
    "MigrationRunner",
    "MigrationStatus",
    "PerformanceIndexesMigration",
]


def get_all_migrations() -> list[type[Migration]]:
    """Return all migration classes in order."""
    return [
        CorePersistenceTablesMigration,
        PerformanceIndexesMigration,
        LibraryTablesMigration,
    ]
