"""
Training Job Repository.

Backend-Frontend Integration Plan - Phase 1.
Replaces in-memory storage in backend/api/routes/training.py.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from backend.data.repository_base import (
    BaseEntity,
    BaseRepository,
    ConnectionConfig,
)

logger = logging.getLogger(__name__)


class TrainingStatus(str, Enum):
    """Training job status."""
    PENDING = "pending"
    PREPARING = "preparing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TrainingJobEntity(BaseEntity):
    """
    Training job entity for persistent storage.

    Maps to training_jobs table.
    """
    dataset_id: str | None = None
    engine_id: str | None = None
    model_name: str | None = None
    status: str = TrainingStatus.PENDING.value
    progress: float = 0.0
    current_epoch: int = 0
    total_epochs: int | None = None
    current_step: int = 0
    total_steps: int | None = None
    learning_rate: float | None = None
    loss: float | None = None
    validation_loss: float | None = None
    best_loss: float | None = None
    metrics: str = "{}"  # JSON
    hyperparameters: str = "{}"  # JSON
    checkpoints: str = "[]"  # JSON array
    error: str | None = None
    output_path: str | None = None
    user_id: str | None = None
    started_at: str | None = None
    completed_at: str | None = None

    def get_metrics(self) -> dict[str, Any]:
        """Parse metrics JSON."""
        try:
            return json.loads(self.metrics) if self.metrics else {}
        except json.JSONDecodeError:
            return {}

    def set_metrics(self, data: dict[str, Any]) -> None:
        """Set metrics as JSON string."""
        self.metrics = json.dumps(data)

    def get_hyperparameters(self) -> dict[str, Any]:
        """Parse hyperparameters JSON."""
        try:
            return json.loads(self.hyperparameters) if self.hyperparameters else {}
        except json.JSONDecodeError:
            return {}

    def set_hyperparameters(self, data: dict[str, Any]) -> None:
        """Set hyperparameters as JSON string."""
        self.hyperparameters = json.dumps(data)

    def get_checkpoints(self) -> list[str]:
        """Parse checkpoints JSON."""
        try:
            return json.loads(self.checkpoints) if self.checkpoints else []
        except json.JSONDecodeError:
            return []

    def add_checkpoint(self, checkpoint_path: str) -> None:
        """Add a checkpoint path."""
        checkpoints = self.get_checkpoints()
        checkpoints.append(checkpoint_path)
        self.checkpoints = json.dumps(checkpoints)


@dataclass
class TrainingLogEntity:
    """Training log entry."""
    id: int | None = None
    job_id: str = ""
    level: str = "info"
    message: str = ""
    data: str = "{}"  # JSON
    timestamp: str = ""

    def get_data(self) -> dict[str, Any]:
        """Parse data JSON."""
        try:
            return json.loads(self.data) if self.data else {}
        except json.JSONDecodeError:
            return {}


@dataclass
class TrainingQualityEntry:
    """Training quality history entry."""
    id: int | None = None
    job_id: str = ""
    epoch: int = 0
    step: int | None = None
    mos_score: float | None = None
    similarity_score: float | None = None
    naturalness_score: float | None = None
    intelligibility_score: float | None = None
    metrics: str = "{}"  # JSON
    timestamp: str = ""


class TrainingJobRepository(BaseRepository[TrainingJobEntity]):
    """
    Repository for training job persistence.

    Replaces the in-memory _training_jobs dict with database-backed storage.
    """

    def __init__(self, config: ConnectionConfig | None = None):
        super().__init__(
            entity_type=TrainingJobEntity,
            table_name="training_jobs",
            config=config,
        )

    def _entity_to_dict(self, entity: TrainingJobEntity) -> dict[str, Any]:
        """Convert TrainingJobEntity to database row dict."""
        return {
            "id": entity.id,
            "dataset_id": entity.dataset_id,
            "engine_id": entity.engine_id,
            "model_name": entity.model_name,
            "status": entity.status,
            "progress": entity.progress,
            "current_epoch": entity.current_epoch,
            "total_epochs": entity.total_epochs,
            "current_step": entity.current_step,
            "total_steps": entity.total_steps,
            "learning_rate": entity.learning_rate,
            "loss": entity.loss,
            "validation_loss": entity.validation_loss,
            "best_loss": entity.best_loss,
            "metrics": entity.metrics,
            "hyperparameters": entity.hyperparameters,
            "checkpoints": entity.checkpoints,
            "error": entity.error,
            "output_path": entity.output_path,
            "user_id": entity.user_id,
            "created_at": entity.created_at.isoformat() if isinstance(entity.created_at, datetime) else entity.created_at,
            "updated_at": entity.updated_at.isoformat() if isinstance(entity.updated_at, datetime) else entity.updated_at,
            "started_at": entity.started_at,
            "completed_at": entity.completed_at,
            "deleted_at": entity.deleted_at.isoformat() if entity.deleted_at else None,
        }

    def _row_to_entity(self, row: dict[str, Any]) -> TrainingJobEntity:
        """Convert database row to TrainingJobEntity."""
        return TrainingJobEntity(
            id=row["id"],
            dataset_id=row.get("dataset_id"),
            engine_id=row.get("engine_id"),
            model_name=row.get("model_name"),
            status=row.get("status", TrainingStatus.PENDING.value),
            progress=row.get("progress", 0.0),
            current_epoch=row.get("current_epoch", 0),
            total_epochs=row.get("total_epochs"),
            current_step=row.get("current_step", 0),
            total_steps=row.get("total_steps"),
            learning_rate=row.get("learning_rate"),
            loss=row.get("loss"),
            validation_loss=row.get("validation_loss"),
            best_loss=row.get("best_loss"),
            metrics=row.get("metrics", "{}"),
            hyperparameters=row.get("hyperparameters", "{}"),
            checkpoints=row.get("checkpoints", "[]"),
            error=row.get("error"),
            output_path=row.get("output_path"),
            user_id=row.get("user_id"),
            created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.now(),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row.get("updated_at") else datetime.now(),
            started_at=row.get("started_at"),
            completed_at=row.get("completed_at"),
            deleted_at=datetime.fromisoformat(row["deleted_at"]) if row.get("deleted_at") else None,
        )

    async def get_active_jobs(self) -> list[TrainingJobEntity]:
        """Get all active training jobs."""
        await self.connect()

        query = f"""
            SELECT * FROM {self.table_name}
            WHERE status IN ('pending', 'preparing', 'running', 'paused')
            AND deleted_at IS NULL
            ORDER BY created_at DESC
        """

        async with self._connection.execute(query) as cursor:
            rows = await cursor.fetchall()
            return [self._row_to_entity(dict(row)) for row in rows]

    async def update_progress(
        self,
        job_id: str,
        progress: float,
        current_epoch: int | None = None,
        current_step: int | None = None,
        loss: float | None = None,
    ) -> TrainingJobEntity | None:
        """Update training progress."""
        data: dict[str, Any] = {"progress": progress}
        if current_epoch is not None:
            data["current_epoch"] = current_epoch
        if current_step is not None:
            data["current_step"] = current_step
        if loss is not None:
            data["loss"] = loss
        return await self.update(job_id, data)

    async def mark_started(self, job_id: str) -> TrainingJobEntity | None:
        """Mark training job as started."""
        return await self.update(job_id, {
            "status": TrainingStatus.RUNNING.value,
            "started_at": datetime.now().isoformat(),
        })

    async def mark_completed(
        self,
        job_id: str,
        output_path: str | None = None,
    ) -> TrainingJobEntity | None:
        """Mark training job as completed."""
        data = {
            "status": TrainingStatus.COMPLETED.value,
            "progress": 1.0,
            "completed_at": datetime.now().isoformat(),
        }
        if output_path:
            data["output_path"] = output_path
        return await self.update(job_id, data)

    async def mark_failed(self, job_id: str, error: str) -> TrainingJobEntity | None:
        """Mark training job as failed."""
        return await self.update(job_id, {
            "status": TrainingStatus.FAILED.value,
            "error": error,
            "completed_at": datetime.now().isoformat(),
        })

    async def add_log(
        self,
        job_id: str,
        level: str,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """Add a log entry for a training job."""
        await self.connect()

        query = """
            INSERT INTO training_logs (job_id, level, message, data, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """

        await self._connection.execute(query, (
            job_id,
            level,
            message,
            json.dumps(data) if data else "{}",
            datetime.now().isoformat(),
        ))
        await self._connection.commit()

    async def get_logs(
        self,
        job_id: str,
        limit: int = 100,
    ) -> list[TrainingLogEntity]:
        """Get logs for a training job."""
        await self.connect()

        query = """
            SELECT * FROM training_logs
            WHERE job_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """

        async with self._connection.execute(query, (job_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return [
                TrainingLogEntity(
                    id=row["id"],
                    job_id=row["job_id"],
                    level=row["level"],
                    message=row["message"],
                    data=row["data"],
                    timestamp=row["timestamp"],
                )
                for row in rows
            ]

    async def add_quality_entry(
        self,
        job_id: str,
        epoch: int,
        step: int | None = None,
        mos_score: float | None = None,
        similarity_score: float | None = None,
        naturalness_score: float | None = None,
        intelligibility_score: float | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> None:
        """Add a quality history entry."""
        await self.connect()

        query = """
            INSERT INTO training_quality_history
            (job_id, epoch, step, mos_score, similarity_score, naturalness_score, intelligibility_score, metrics, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        await self._connection.execute(query, (
            job_id,
            epoch,
            step,
            mos_score,
            similarity_score,
            naturalness_score,
            intelligibility_score,
            json.dumps(metrics) if metrics else "{}",
            datetime.now().isoformat(),
        ))
        await self._connection.commit()

    async def get_quality_history(
        self,
        job_id: str,
        limit: int = 100,
    ) -> list[TrainingQualityEntry]:
        """Get quality history for a training job."""
        await self.connect()

        query = """
            SELECT * FROM training_quality_history
            WHERE job_id = ?
            ORDER BY epoch ASC, step ASC
            LIMIT ?
        """

        async with self._connection.execute(query, (job_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return [
                TrainingQualityEntry(
                    id=row["id"],
                    job_id=row["job_id"],
                    epoch=row["epoch"],
                    step=row["step"],
                    mos_score=row["mos_score"],
                    similarity_score=row["similarity_score"],
                    naturalness_score=row["naturalness_score"],
                    intelligibility_score=row["intelligibility_score"],
                    metrics=row["metrics"],
                    timestamp=row["timestamp"],
                )
                for row in rows
            ]


# Singleton instance
_training_repository: TrainingJobRepository | None = None


def get_training_repository() -> TrainingJobRepository:
    """Get or create TrainingJobRepository singleton."""
    global _training_repository
    if _training_repository is None:
        _training_repository = TrainingJobRepository()
    return _training_repository
