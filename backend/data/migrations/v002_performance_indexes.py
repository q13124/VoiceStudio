"""
Migration v002: Performance Indexes.

Adds composite indexes for common query patterns to improve
listing, filtering, and sorting performance.

Production Completion Plan - Phase 3.
"""

from __future__ import annotations

from typing import Any

from backend.data.migrations.migration_runner import Migration


class PerformanceIndexesMigration(Migration):
    """
    Adds composite and covering indexes for high-frequency queries.

    Targets:
    - Job listing by status+type (dashboard, job panel)
    - Transcription listing by language (transcribe panel filter)
    - Session cleanup by expiry
    - Training job lookup by engine
    """

    @property
    def version(self) -> int:
        return 2

    @property
    def name(self) -> str:
        return "performance_indexes"

    @property
    def description(self) -> str:
        return (
            "Adds composite indexes for common query patterns: "
            "job_history(status,job_type), transcriptions(language), "
            "sessions(expires_at), training_jobs(engine_id,status)."
        )

    async def upgrade(self, connection: Any) -> None:
        """Add performance indexes."""
        indexes = [
            # Jobs: dashboard filters by status+type
            "CREATE INDEX IF NOT EXISTS idx_job_history_status_type "
            "ON job_history(status, job_type)",
            # Jobs: sort by updated
            "CREATE INDEX IF NOT EXISTS idx_job_history_updated " "ON job_history(updated_at)",
            # Transcriptions: filter by language
            "CREATE INDEX IF NOT EXISTS idx_transcriptions_language " "ON transcriptions(language)",
            # Transcriptions: sort by created
            "CREATE INDEX IF NOT EXISTS idx_transcriptions_created "
            "ON transcriptions(created_at)",
            # Sessions: cleanup expired
            "CREATE INDEX IF NOT EXISTS idx_sessions_expires " "ON sessions(expires_at)",
            # Training: filter by engine+status
            "CREATE INDEX IF NOT EXISTS idx_training_jobs_engine_status "
            "ON training_jobs(engine_id, status)",
            # Deepfake: sort by created
            "CREATE INDEX IF NOT EXISTS idx_deepfake_jobs_created " "ON deepfake_jobs(created_at)",
            # Pipeline: sort by updated
            "CREATE INDEX IF NOT EXISTS idx_pipeline_sessions_updated "
            "ON pipeline_sessions(updated_at)",
        ]
        for sql in indexes:
            await connection.execute(sql)
        await connection.commit()

    async def downgrade(self, connection: Any) -> None:
        """Drop added indexes."""
        indexes = [
            "idx_job_history_status_type",
            "idx_job_history_updated",
            "idx_transcriptions_language",
            "idx_transcriptions_created",
            "idx_sessions_expires",
            "idx_training_jobs_engine_status",
            "idx_deepfake_jobs_created",
            "idx_pipeline_sessions_updated",
        ]
        for idx in indexes:
            await connection.execute(f"DROP INDEX IF EXISTS {idx}")
        await connection.commit()


migration = PerformanceIndexesMigration
