"""
Watermark Database
Stores watermark metadata and tracking information.

Status: Ready for implementation
See: docs/governance/SECURITY_FEATURES_IMPLEMENTATION_PLAN.md
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

# Import query optimizer for optimized database operations
try:
    from app.core.database.query_optimizer import DatabaseQueryOptimizer

    HAS_QUERY_OPTIMIZER = True
except ImportError:
    HAS_QUERY_OPTIMIZER = False
    logger = logging.getLogger(__name__)
    logger.warning("Query optimizer not available. Database operations will be limited.")

logger = logging.getLogger(__name__)


class WatermarkDatabase:
    """Database for storing watermark metadata with query optimization."""

    def __init__(self, db_path: Path | None = None):
        """
        Initialize watermark database.

        Args:
            db_path: Path to SQLite database file
        """
        if db_path is None:
            db_path = Path.home() / ".voicestudio" / "watermarks.db"

        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(db_path)

        # Initialize query optimizer if available
        if HAS_QUERY_OPTIMIZER:
            self.optimizer = DatabaseQueryOptimizer(
                db_path=self.db_path,
                enable_cache=True,
                cache_size=100,
                cache_ttl=3600.0,  # 1 hour
            )
        else:
            self.optimizer = None

        logger.info(f"WatermarkDatabase initialized (path: {db_path})")
        self._init_database()

    def _init_database(self):
        """Initialize database schema."""
        if not self.optimizer:
            logger.warning("Query optimizer not available. Schema initialization skipped.")
            return

        try:
            # Create watermark table
            self.optimizer.execute_query(
                """
                CREATE TABLE IF NOT EXISTS watermarks (
                    watermark_id TEXT PRIMARY KEY,
                    watermark_data TEXT,
                    method TEXT,
                    strength REAL,
                    audio_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """,
                use_cache=False,
            )

            # Create verification log table
            self.optimizer.execute_query(
                """
                CREATE TABLE IF NOT EXISTS verification_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    watermark_id TEXT,
                    result TEXT,
                    confidence REAL,
                    verified_by TEXT,
                    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (watermark_id) REFERENCES watermarks(watermark_id)
                )
                """,
                use_cache=False,
            )

            # Create indexes for performance
            self.optimizer.create_index("watermarks", "created_at")
            self.optimizer.create_index("verification_logs", "watermark_id")
            self.optimizer.create_index("verification_logs", "verified_at")

            logger.info("Watermark database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database schema: {e}")

    def store_watermark(
        self,
        watermark_id: str,
        watermark_data: dict,
        method: str,
        strength: float,
        audio_path: str | None = None,
    ):
        """
        Store watermark metadata.

        Args:
            watermark_id: Unique watermark identifier
            watermark_data: Watermark data dictionary
            method: Watermarking method
            strength: Watermark strength
            audio_path: Optional path to audio file
        """
        if not self.optimizer:
            raise RuntimeError("Query optimizer not available.")

        try:
            watermark_data_json = json.dumps(watermark_data)

            self.optimizer.execute_query(
                """
                INSERT OR REPLACE INTO watermarks
                (watermark_id, watermark_data, method, strength, audio_path)
                VALUES (?, ?, ?, ?, ?)
                """,
                parameters=(
                    watermark_id,
                    watermark_data_json,
                    method,
                    strength,
                    audio_path,
                ),
                use_cache=False,
            )

            # Invalidate cache for this watermark
            if self.optimizer.cache:
                self.optimizer.cache.invalidate(f"watermark_{watermark_id}")

            logger.info(f"Stored watermark: {watermark_id}")
        except Exception as e:
            logger.error(f"Failed to store watermark: {e}")
            raise

    def get_watermark(self, watermark_id: str) -> dict | None:
        """
        Retrieve watermark metadata.

        Args:
            watermark_id: Watermark identifier

        Returns:
            Watermark data dictionary or None if not found
        """
        if not self.optimizer:
            raise RuntimeError("Query optimizer not available.")

        try:
            results = self.optimizer.execute_query(
                "SELECT * FROM watermarks WHERE watermark_id = ?",
                parameters=(watermark_id,),
                use_cache=True,
            )

            if results:
                row = results[0]
                watermark_data = json.loads(row["watermark_data"])
                return {
                    "watermark_id": row["watermark_id"],
                    "watermark_data": watermark_data,
                    "method": row["method"],
                    "strength": row["strength"],
                    "audio_path": row["audio_path"],
                    "created_at": row["created_at"],
                }

            return None
        except Exception as e:
            logger.error(f"Failed to retrieve watermark: {e}")
            return None

    def log_verification(
        self,
        watermark_id: str,
        result: str,
        confidence: float,
        verified_by: str | None = None,
    ):
        """
        Log watermark verification.

        Args:
            watermark_id: Watermark identifier
            result: Verification result
            confidence: Confidence score
            verified_by: Optional verifier identifier
        """
        if not self.optimizer:
            raise RuntimeError("Query optimizer not available.")

        try:
            self.optimizer.execute_query(
                """
                INSERT INTO verification_logs
                (watermark_id, result, confidence, verified_by)
                VALUES (?, ?, ?, ?)
                """,
                parameters=(watermark_id, result, confidence, verified_by),
                use_cache=False,
            )

            logger.info(f"Logged verification for watermark: {watermark_id}")
        except Exception as e:
            logger.error(f"Failed to log verification: {e}")
            raise

    def get_verification_history(self, watermark_id: str, limit: int = 100) -> list[dict]:
        """
        Get verification history for a watermark.

        Args:
            watermark_id: Watermark identifier
            limit: Maximum number of records

        Returns:
            List of verification records
        """
        if not self.optimizer:
            raise RuntimeError("Query optimizer not available.")

        try:
            results = self.optimizer.execute_query(
                """
                SELECT * FROM verification_logs
                WHERE watermark_id = ?
                ORDER BY verified_at DESC
                LIMIT ?
                """,
                parameters=(watermark_id, limit),
                use_cache=True,
            )

            return results
        except Exception as e:
            logger.error(f"Failed to get verification history: {e}")
            return []

    def close(self):
        """Close database connections."""
        if self.optimizer:
            self.optimizer.close()
