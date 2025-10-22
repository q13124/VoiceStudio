"""
VoiceStudio Telemetry Persistence System
Implements telemetry persistence and quality history tracking
"""

import sqlite3
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import threading
import queue


@dataclass
class JobRecord:
    """Telemetry record for a single job"""

    job_id: str
    engine_id: str
    language: str
    quality_tier: str
    text_length: int
    latency_ms: int
    success: bool
    quality_score: Optional[float] = None
    error_message: Optional[str] = None
    timestamp: datetime = None
    user_id: Optional[str] = None
    ip_address: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class QualityHistory:
    """Quality history record for learning"""

    engine_id: str
    language: str
    quality_tier: str
    text_features: Dict[str, Any]
    predicted_score: float
    actual_score: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class TelemetryPersistence:
    """Persistent telemetry storage with SQLite backend"""

    def __init__(self, db_path: str = "voicestudio_telemetry.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

        # Background processing queue
        self._queue = queue.Queue()
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

    def _init_db(self):
        """Initialize telemetry database"""
        with sqlite3.connect(self.db_path) as conn:
            # Jobs table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT UNIQUE NOT NULL,
                    engine_id TEXT NOT NULL,
                    language TEXT NOT NULL,
                    quality_tier TEXT NOT NULL,
                    text_length INTEGER NOT NULL,
                    latency_ms INTEGER NOT NULL,
                    success BOOLEAN NOT NULL,
                    quality_score REAL,
                    error_message TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    ip_address TEXT
                )
            """
            )

            # Quality history table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS quality_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    engine_id TEXT NOT NULL,
                    language TEXT NOT NULL,
                    quality_tier TEXT NOT NULL,
                    text_features TEXT NOT NULL,
                    predicted_score REAL NOT NULL,
                    actual_score REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Engine performance summary table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS engine_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    engine_id TEXT NOT NULL,
                    language TEXT NOT NULL,
                    quality_tier TEXT NOT NULL,
                    date DATE NOT NULL,
                    total_jobs INTEGER DEFAULT 0,
                    successful_jobs INTEGER DEFAULT 0,
                    avg_latency_ms REAL DEFAULT 0,
                    avg_quality_score REAL DEFAULT 0,
                    total_latency_ms INTEGER DEFAULT 0,
                    total_quality_score REAL DEFAULT 0,
                    UNIQUE(engine_id, language, quality_tier, date)
                )
            """
            )

            # Create indexes
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_timestamp ON jobs(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_engine_id ON jobs(engine_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_language ON jobs(language)"
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_jobs_success ON jobs(success)")

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_quality_history_timestamp ON quality_history(timestamp)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_quality_history_engine_id ON quality_history(engine_id)"
            )

            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_engine_performance_date ON engine_performance(date)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_engine_performance_engine_id ON engine_performance(engine_id)"
            )

    def record_job(self, job_record: JobRecord):
        """Record a job asynchronously"""
        self._queue.put(("job", job_record))

    def record_quality_history(self, quality_record: QualityHistory):
        """Record quality history asynchronously"""
        self._queue.put(("quality", quality_record))

    def _process_queue(self):
        """Process telemetry queue in background"""
        while True:
            try:
                record_type, record = self._queue.get(timeout=1.0)

                if record_type == "job":
                    self._insert_job_record(record)
                    self._update_performance_summary(record)
                elif record_type == "quality":
                    self._insert_quality_history(record)

                self._queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing telemetry queue: {e}")

    def _insert_job_record(self, record: JobRecord):
        """Insert job record into database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO jobs
                (job_id, engine_id, language, quality_tier, text_length, latency_ms,
                 success, quality_score, error_message, timestamp, user_id, ip_address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    record.job_id,
                    record.engine_id,
                    record.language,
                    record.quality_tier,
                    record.text_length,
                    record.latency_ms,
                    record.success,
                    record.quality_score,
                    record.error_message,
                    record.timestamp,
                    record.user_id,
                    record.ip_address,
                ),
            )

    def _insert_quality_history(self, record: QualityHistory):
        """Insert quality history record into database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO quality_history
                (engine_id, language, quality_tier, text_features, predicted_score,
                 actual_score, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    record.engine_id,
                    record.language,
                    record.quality_tier,
                    json.dumps(record.text_features),
                    record.predicted_score,
                    record.actual_score,
                    record.timestamp,
                ),
            )

    def _update_performance_summary(self, record: JobRecord):
        """Update daily performance summary"""
        date = record.timestamp.date()

        with sqlite3.connect(self.db_path) as conn:
            # Get existing summary
            cursor = conn.execute(
                """
                SELECT total_jobs, successful_jobs, total_latency_ms, total_quality_score
                FROM engine_performance
                WHERE engine_id = ? AND language = ? AND quality_tier = ? AND date = ?
            """,
                (record.engine_id, record.language, record.quality_tier, date),
            )

            row = cursor.fetchone()

            if row:
                total_jobs, successful_jobs, total_latency, total_quality = row
                total_jobs += 1
                if record.success:
                    successful_jobs += 1
                total_latency += record.latency_ms
                if record.quality_score:
                    total_quality += record.quality_score

                conn.execute(
                    """
                    UPDATE engine_performance
                    SET total_jobs = ?, successful_jobs = ?, total_latency_ms = ?,
                        total_quality_score = ?, avg_latency_ms = ?, avg_quality_score = ?
                    WHERE engine_id = ? AND language = ? AND quality_tier = ? AND date = ?
                """,
                    (
                        total_jobs,
                        successful_jobs,
                        total_latency,
                        total_quality,
                        total_latency / total_jobs,
                        total_quality / max(1, successful_jobs),
                        record.engine_id,
                        record.language,
                        record.quality_tier,
                        date,
                    ),
                )
            else:
                # Create new summary
                conn.execute(
                    """
                    INSERT INTO engine_performance
                    (engine_id, language, quality_tier, date, total_jobs, successful_jobs,
                     total_latency_ms, total_quality_score, avg_latency_ms, avg_quality_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        record.engine_id,
                        record.language,
                        record.quality_tier,
                        date,
                        1,
                        1 if record.success else 0,
                        record.latency_ms,
                        record.quality_score or 0,
                        record.latency_ms,
                        record.quality_score or 0,
                    ),
                )

    def get_engine_stats(self, engine_id: str, hours: int = 24) -> Dict[str, Any]:
        """Get engine statistics for the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_jobs,
                    AVG(latency_ms) as avg_latency_ms,
                    AVG(quality_score) as avg_quality_score,
                    MIN(latency_ms) as min_latency_ms,
                    MAX(latency_ms) as max_latency_ms
                FROM jobs
                WHERE engine_id = ? AND timestamp >= ?
            """,
                (engine_id, cutoff),
            )

            row = cursor.fetchone()

            if row and row[0] > 0:
                (
                    total_jobs,
                    successful_jobs,
                    avg_latency,
                    avg_quality,
                    min_latency,
                    max_latency,
                ) = row
                return {
                    "total_jobs": total_jobs,
                    "successful_jobs": successful_jobs,
                    "success_rate": (
                        (successful_jobs / total_jobs) * 100 if total_jobs > 0 else 0
                    ),
                    "avg_latency_ms": avg_latency or 0,
                    "avg_quality_score": avg_quality or 0,
                    "min_latency_ms": min_latency or 0,
                    "max_latency_ms": max_latency or 0,
                }
            else:
                return {
                    "total_jobs": 0,
                    "successful_jobs": 0,
                    "success_rate": 0,
                    "avg_latency_ms": 0,
                    "avg_quality_score": 0,
                    "min_latency_ms": 0,
                    "max_latency_ms": 0,
                }

    def get_top_engines(
        self, language: str, quality_tier: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top performing engines for a language/quality combination"""
        cutoff = datetime.now() - timedelta(days=7)  # Last 7 days

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT
                    engine_id,
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_jobs,
                    AVG(latency_ms) as avg_latency_ms,
                    AVG(quality_score) as avg_quality_score
                FROM jobs
                WHERE language = ? AND quality_tier = ? AND timestamp >= ?
                GROUP BY engine_id
                HAVING total_jobs >= 5
                ORDER BY
                    (successful_jobs * 1.0 / total_jobs) DESC,
                    avg_quality_score DESC,
                    avg_latency_ms ASC
                LIMIT ?
            """,
                (language, quality_tier, cutoff, limit),
            )

            results = []
            for row in cursor.fetchall():
                engine_id, total_jobs, successful_jobs, avg_latency, avg_quality = row
                results.append(
                    {
                        "engine_id": engine_id,
                        "total_jobs": total_jobs,
                        "success_rate": (successful_jobs / total_jobs) * 100,
                        "avg_latency_ms": avg_latency or 0,
                        "avg_quality_score": avg_quality or 0,
                    }
                )

            return results

    def get_quality_prediction_data(
        self, engine_id: str, language: str, quality_tier: str
    ) -> List[Dict[str, Any]]:
        """Get quality prediction training data"""
        cutoff = datetime.now() - timedelta(days=30)  # Last 30 days

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT text_features, predicted_score, actual_score
                FROM quality_history
                WHERE engine_id = ? AND language = ? AND quality_tier = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """,
                (engine_id, language, quality_tier, cutoff),
            )

            results = []
            for row in cursor.fetchall():
                text_features, predicted_score, actual_score = row
                results.append(
                    {
                        "text_features": json.loads(text_features),
                        "predicted_score": predicted_score,
                        "actual_score": actual_score,
                    }
                )

            return results

    def cleanup_old_data(self, days: int = 90):
        """Clean up old telemetry data"""
        cutoff = datetime.now() - timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            # Clean up old jobs
            conn.execute("DELETE FROM jobs WHERE timestamp < ?", (cutoff,))

            # Clean up old quality history
            conn.execute("DELETE FROM quality_history WHERE timestamp < ?", (cutoff,))

            # Clean up old performance summaries
            conn.execute(
                "DELETE FROM engine_performance WHERE date < ?", (cutoff.date(),)
            )

            # Vacuum database
            conn.execute("VACUUM")

    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get metrics for dashboard display"""
        cutoff = datetime.now() - timedelta(hours=24)

        with sqlite3.connect(self.db_path) as conn:
            # Overall stats
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_jobs,
                    AVG(latency_ms) as avg_latency_ms,
                    COUNT(DISTINCT engine_id) as active_engines
                FROM jobs
                WHERE timestamp >= ?
            """,
                (cutoff,),
            )

            overall = cursor.fetchone()

            # Engine breakdown
            cursor = conn.execute(
                """
                SELECT
                    engine_id,
                    COUNT(*) as total_jobs,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_jobs,
                    AVG(latency_ms) as avg_latency_ms,
                    AVG(quality_score) as avg_quality_score
                FROM jobs
                WHERE timestamp >= ?
                GROUP BY engine_id
                ORDER BY total_jobs DESC
            """,
                (cutoff,),
            )

            engines = []
            for row in cursor.fetchall():
                engine_id, total_jobs, successful_jobs, avg_latency, avg_quality = row
                engines.append(
                    {
                        "engine_id": engine_id,
                        "total_jobs": total_jobs,
                        "success_rate": (
                            (successful_jobs / total_jobs) * 100
                            if total_jobs > 0
                            else 0
                        ),
                        "avg_latency_ms": avg_latency or 0,
                        "avg_quality_score": avg_quality or 0,
                    }
                )

            return {
                "overall": {
                    "total_jobs": overall[0] or 0,
                    "success_rate": (
                        (overall[1] / overall[0]) * 100 if overall[0] > 0 else 0
                    ),
                    "avg_latency_ms": overall[2] or 0,
                    "active_engines": overall[3] or 0,
                },
                "engines": engines,
                "period": "24h",
            }


# Global telemetry instance
_telemetry_persistence: Optional[TelemetryPersistence] = None


def get_telemetry_persistence() -> TelemetryPersistence:
    """Get the global telemetry persistence instance"""
    global _telemetry_persistence

    if _telemetry_persistence is None:
        from config.config_loader import get_telemetry_config

        telemetry_config = get_telemetry_config()
        _telemetry_persistence = TelemetryPersistence(telemetry_config.db_path)

    return _telemetry_persistence


def record_job_telemetry(
    job_id: str,
    engine_id: str,
    language: str,
    quality_tier: str,
    text_length: int,
    latency_ms: int,
    success: bool,
    quality_score: Optional[float] = None,
    error_message: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
):
    """Record job telemetry"""
    record = JobRecord(
        job_id=job_id,
        engine_id=engine_id,
        language=language,
        quality_tier=quality_tier,
        text_length=text_length,
        latency_ms=latency_ms,
        success=success,
        quality_score=quality_score,
        error_message=error_message,
        user_id=user_id,
        ip_address=ip_address,
    )
    get_telemetry_persistence().record_job(record)


def record_quality_history(
    engine_id: str,
    language: str,
    quality_tier: str,
    text_features: Dict[str, Any],
    predicted_score: float,
    actual_score: float,
):
    """Record quality history for learning"""
    record = QualityHistory(
        engine_id=engine_id,
        language=language,
        quality_tier=quality_tier,
        text_features=text_features,
        predicted_score=predicted_score,
        actual_score=actual_score,
    )
    get_telemetry_persistence().record_quality_history(record)


if __name__ == "__main__":
    # Test telemetry persistence
    telemetry = TelemetryPersistence("test_telemetry.db")

    # Record some test data
    record_job_telemetry("test_job_1", "xtts", "en", "balanced", 50, 1000, True, 0.8)
    record_job_telemetry(
        "test_job_2", "openvoice", "en", "quality", 30, 2000, True, 0.9
    )

    # Get stats
    stats = telemetry.get_engine_stats("xtts", hours=1)
    print(f"XTTS stats: {stats}")

    # Get dashboard metrics
    metrics = telemetry.get_dashboard_metrics()
    print(f"Dashboard metrics: {metrics}")

    # Cleanup
    telemetry.cleanup_old_data(days=0)
