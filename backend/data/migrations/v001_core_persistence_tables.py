"""
Migration v001: Core Persistence Tables.

Creates tables for data that was previously stored in-memory:
- job_history: Job progress and history (was _jobs dict in jobs.py)
- training_jobs: Training job state and logs (was _training_jobs in training.py)
- deepfake_jobs: Deepfake processing jobs (was _deepfake_jobs in deepfake_creator.py)
- sessions: User authentication sessions (was _sessions in session.py)
- transcriptions: Transcription cache (was _transcriptions in transcribe.py)
- pipeline_sessions: Pipeline processing sessions (was _sessions in pipeline.py)
- abx_sessions: ABX evaluation sessions (was _abx_sessions in eval_abx.py)

Backend-Frontend Integration Plan - Phase 1.
"""

from __future__ import annotations

from typing import Any

from backend.data.migrations.migration_runner import Migration


class CorePersistenceTablesMigration(Migration):
    """
    Creates core persistence tables for in-memory data migration.

    Priority: CRITICAL
    Impact: Data lost on backend restart without these tables.
    """

    @property
    def version(self) -> int:
        return 1

    @property
    def name(self) -> str:
        return "core_persistence_tables"

    @property
    def description(self) -> str:
        return (
            "Creates tables for job_history, training_jobs, deepfake_jobs, "
            "sessions, transcriptions, pipeline_sessions, and abx_sessions."
        )

    async def upgrade(self, connection: Any) -> None:
        """Create all core persistence tables."""

        # 1. Job History Table (HIGH PRIORITY)
        # Replaces: backend/api/routes/jobs.py:27 (_jobs dict)
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS job_history (
                id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                progress REAL DEFAULT 0.0,
                current_step TEXT,
                total_steps INTEGER,
                error TEXT,
                result_path TEXT,
                metadata TEXT,
                user_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                deleted_at TEXT
            )
        """
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_job_history_status ON job_history(status)"
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_job_history_type ON job_history(job_type)"
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_job_history_user ON job_history(user_id)"
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_job_history_created ON job_history(created_at)"
        )

        # 2. Training Jobs Table (HIGH PRIORITY)
        # Replaces: backend/api/routes/training.py:59-67 (4 in-memory dicts)
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS training_jobs (
                id TEXT PRIMARY KEY,
                dataset_id TEXT,
                engine_id TEXT,
                model_name TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                progress REAL DEFAULT 0.0,
                current_epoch INTEGER DEFAULT 0,
                total_epochs INTEGER,
                current_step INTEGER DEFAULT 0,
                total_steps INTEGER,
                learning_rate REAL,
                loss REAL,
                validation_loss REAL,
                best_loss REAL,
                metrics TEXT,
                hyperparameters TEXT,
                checkpoints TEXT,
                error TEXT,
                output_path TEXT,
                user_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                deleted_at TEXT
            )
        """
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_training_jobs_status ON training_jobs(status)"
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_training_jobs_dataset ON training_jobs(dataset_id)"
        )

        # 3. Training Logs Table (part of training migration)
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS training_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                level TEXT NOT NULL DEFAULT 'info',
                message TEXT NOT NULL,
                data TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES training_jobs(id) ON DELETE CASCADE
            )
        """
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_training_logs_job ON training_logs(job_id)"
        )

        # 4. Training Quality History Table
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS training_quality_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                epoch INTEGER NOT NULL,
                step INTEGER,
                mos_score REAL,
                similarity_score REAL,
                naturalness_score REAL,
                intelligibility_score REAL,
                metrics TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES training_jobs(id) ON DELETE CASCADE
            )
        """
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_training_quality_job ON training_quality_history(job_id)"
        )

        # 5. Deepfake Jobs Table (HIGH PRIORITY)
        # Replaces: backend/api/routes/deepfake_creator.py:25-27
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS deepfake_jobs (
                id TEXT PRIMARY KEY,
                engine_id TEXT,
                source_video_path TEXT,
                source_audio_path TEXT,
                target_face_path TEXT,
                output_path TEXT,
                status TEXT NOT NULL DEFAULT 'queued',
                progress REAL DEFAULT 0.0,
                queue_position INTEGER,
                error TEXT,
                settings TEXT,
                quality_metrics TEXT,
                user_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                deleted_at TEXT
            )
        """
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_deepfake_jobs_status ON deepfake_jobs(status)"
        )

        # 6. Sessions Table (HIGH PRIORITY)
        # Replaces: backend/security/session.py:77-78
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                token_hash TEXT NOT NULL,
                device_info TEXT,
                ip_address TEXT,
                user_agent TEXT,
                is_active INTEGER DEFAULT 1,
                last_activity TEXT,
                expires_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                deleted_at TEXT
            )
        """
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)"
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token_hash)"
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_active ON sessions(is_active)"
        )

        # 7. Transcriptions Table (MEDIUM PRIORITY)
        # Replaces: backend/api/routes/transcribe.py:33
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transcriptions (
                id TEXT PRIMARY KEY,
                audio_path TEXT,
                language TEXT,
                text TEXT,
                segments TEXT,
                word_timestamps TEXT,
                duration REAL,
                confidence REAL,
                engine_id TEXT,
                user_id TEXT,
                created_at TEXT NOT NULL,
                expires_at TEXT,
                deleted_at TEXT
            )
        """
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_transcriptions_user ON transcriptions(user_id)"
        )

        # 8. Pipeline Sessions Table (MEDIUM PRIORITY)
        # Replaces: backend/api/routes/pipeline.py:40
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_sessions (
                id TEXT PRIMARY KEY,
                session_type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'active',
                input_mode TEXT,
                output_mode TEXT,
                stt_engine TEXT,
                llm_provider TEXT,
                llm_model TEXT,
                tts_engine TEXT,
                tts_voice TEXT,
                settings TEXT,
                conversation_history TEXT,
                user_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                ended_at TEXT,
                deleted_at TEXT
            )
        """
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_pipeline_sessions_status ON pipeline_sessions(status)"
        )

        # 9. ABX Sessions Table (MEDIUM PRIORITY)
        # Replaces: backend/api/routes/eval_abx.py:47-48
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS abx_sessions (
                id TEXT PRIMARY KEY,
                session_name TEXT,
                test_type TEXT NOT NULL DEFAULT 'abx',
                status TEXT NOT NULL DEFAULT 'active',
                samples_config TEXT,
                total_trials INTEGER,
                completed_trials INTEGER DEFAULT 0,
                results TEXT,
                statistics TEXT,
                user_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                deleted_at TEXT
            )
        """
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_abx_sessions_status ON abx_sessions(status)"
        )

        # 10. ABX Results Table
        await connection.execute(
            """
            CREATE TABLE IF NOT EXISTS abx_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                trial_number INTEGER NOT NULL,
                sample_a TEXT,
                sample_b TEXT,
                sample_x TEXT,
                user_choice TEXT,
                correct INTEGER,
                response_time_ms INTEGER,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES abx_sessions(id) ON DELETE CASCADE
            )
        """
        )
        await connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_abx_results_session ON abx_results(session_id)"
        )

        await connection.commit()

    async def downgrade(self, connection: Any) -> None:
        """Drop all created tables (in reverse order of dependencies)."""
        tables = [
            "abx_results",
            "abx_sessions",
            "pipeline_sessions",
            "transcriptions",
            "sessions",
            "deepfake_jobs",
            "training_quality_history",
            "training_logs",
            "training_jobs",
            "job_history",
        ]

        for table in tables:
            await connection.execute(f"DROP TABLE IF EXISTS {table}")

        await connection.commit()


# Export the migration class
migration = CorePersistenceTablesMigration
