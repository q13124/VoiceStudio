"""
Phase 9: User Feedback System
Task 9.6: Collect and manage user feedback.
"""

from __future__ import annotations

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """Types of feedback."""
    BUG_REPORT = "bug_report"
    FEATURE_REQUEST = "feature_request"
    IMPROVEMENT = "improvement"
    QUESTION = "question"
    PRAISE = "praise"
    OTHER = "other"


class FeedbackPriority(Enum):
    """Feedback priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackStatus(Enum):
    """Feedback status."""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    WONT_FIX = "wont_fix"


@dataclass
class FeedbackAttachment:
    """An attachment to feedback."""
    attachment_id: str
    filename: str
    content_type: str
    size_bytes: int
    path: str


@dataclass
class Feedback:
    """A feedback submission."""
    feedback_id: str
    type: FeedbackType
    priority: FeedbackPriority
    status: FeedbackStatus
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    user_id: str | None = None
    user_email: str | None = None
    app_version: str = ""
    os_version: str = ""
    attachments: list[FeedbackAttachment] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    responses: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class FeedbackStats:
    """Feedback statistics."""
    total: int = 0
    by_type: dict[str, int] = field(default_factory=dict)
    by_status: dict[str, int] = field(default_factory=dict)
    by_priority: dict[str, int] = field(default_factory=dict)
    average_resolution_hours: float = 0.0


class FeedbackService:
    """Service for managing user feedback."""

    def __init__(
        self,
        storage_path: Path | None = None
    ):
        self._storage_path = storage_path or Path.home() / ".voicestudio" / "feedback"
        self._feedback: dict[str, Feedback] = {}
        self._load_feedback()

    def submit(
        self,
        feedback_type: FeedbackType,
        title: str,
        description: str,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM,
        user_id: str | None = None,
        user_email: str | None = None,
        attachments: list[FeedbackAttachment] | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> Feedback:
        """Submit new feedback."""
        feedback = Feedback(
            feedback_id=str(uuid.uuid4()),
            type=feedback_type,
            priority=priority,
            status=FeedbackStatus.NEW,
            title=title,
            description=description,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            user_id=user_id,
            user_email=user_email,
            app_version=self._get_app_version(),
            os_version=self._get_os_version(),
            attachments=attachments or [],
            tags=tags or [],
            metadata=metadata or {},
        )

        self._feedback[feedback.feedback_id] = feedback
        self._save_feedback()

        logger.info(f"Feedback submitted: {feedback.feedback_id} - {title}")

        return feedback

    def get(self, feedback_id: str) -> Feedback | None:
        """Get feedback by ID."""
        return self._feedback.get(feedback_id)

    def list_feedback(
        self,
        feedback_type: FeedbackType | None = None,
        status: FeedbackStatus | None = None,
        priority: FeedbackPriority | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[Feedback]:
        """List feedback with optional filters."""
        items = list(self._feedback.values())

        if feedback_type:
            items = [f for f in items if f.type == feedback_type]

        if status:
            items = [f for f in items if f.status == status]

        if priority:
            items = [f for f in items if f.priority == priority]

        # Sort by created_at, newest first
        items.sort(key=lambda f: f.created_at, reverse=True)

        return items[offset:offset + limit]

    def update_status(
        self,
        feedback_id: str,
        status: FeedbackStatus,
        comment: str | None = None
    ) -> Feedback | None:
        """Update feedback status."""
        feedback = self._feedback.get(feedback_id)
        if not feedback:
            return None

        feedback.status = status
        feedback.updated_at = datetime.now()

        if comment:
            feedback.responses.append({
                "type": "status_change",
                "status": status.value,
                "comment": comment,
                "timestamp": datetime.now().isoformat(),
            })

        self._save_feedback()

        return feedback

    def add_response(
        self,
        feedback_id: str,
        message: str,
        responder: str
    ) -> Feedback | None:
        """Add a response to feedback."""
        feedback = self._feedback.get(feedback_id)
        if not feedback:
            return None

        feedback.responses.append({
            "type": "response",
            "message": message,
            "responder": responder,
            "timestamp": datetime.now().isoformat(),
        })
        feedback.updated_at = datetime.now()

        self._save_feedback()

        return feedback

    def add_attachment(
        self,
        feedback_id: str,
        filename: str,
        content: bytes,
        content_type: str
    ) -> FeedbackAttachment | None:
        """Add an attachment to feedback."""
        feedback = self._feedback.get(feedback_id)
        if not feedback:
            return None

        # Save attachment
        attachments_dir = self._storage_path / "attachments" / feedback_id
        attachments_dir.mkdir(parents=True, exist_ok=True)

        attachment_id = str(uuid.uuid4())
        attachment_path = attachments_dir / f"{attachment_id}_{filename}"
        attachment_path.write_bytes(content)

        attachment = FeedbackAttachment(
            attachment_id=attachment_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(content),
            path=str(attachment_path),
        )

        feedback.attachments.append(attachment)
        feedback.updated_at = datetime.now()
        self._save_feedback()

        return attachment

    def get_stats(self) -> FeedbackStats:
        """Get feedback statistics."""
        stats = FeedbackStats()

        items = list(self._feedback.values())
        stats.total = len(items)

        # Count by type
        for ft in FeedbackType:
            count = len([f for f in items if f.type == ft])
            if count > 0:
                stats.by_type[ft.value] = count

        # Count by status
        for fs in FeedbackStatus:
            count = len([f for f in items if f.status == fs])
            if count > 0:
                stats.by_status[fs.value] = count

        # Count by priority
        for fp in FeedbackPriority:
            count = len([f for f in items if f.priority == fp])
            if count > 0:
                stats.by_priority[fp.value] = count

        # Calculate average resolution time
        resolved = [f for f in items if f.status == FeedbackStatus.RESOLVED]
        if resolved:
            total_hours = sum(
                (f.updated_at - f.created_at).total_seconds() / 3600
                for f in resolved
            )
            stats.average_resolution_hours = total_hours / len(resolved)

        return stats

    def delete(self, feedback_id: str) -> bool:
        """Delete feedback."""
        if feedback_id in self._feedback:
            del self._feedback[feedback_id]
            self._save_feedback()
            return True
        return False

    def _get_app_version(self) -> str:
        """Get application version."""
        return "1.0.0"

    def _get_os_version(self) -> str:
        """Get OS version."""
        import platform
        return platform.platform()

    def _load_feedback(self) -> None:
        """Load feedback from storage."""
        feedback_file = self._storage_path / "feedback.json"

        if not feedback_file.exists():
            return

        try:
            data = json.loads(feedback_file.read_text())

            for item in data.get("feedback", []):
                feedback = Feedback(
                    feedback_id=item["feedback_id"],
                    type=FeedbackType(item["type"]),
                    priority=FeedbackPriority(item["priority"]),
                    status=FeedbackStatus(item["status"]),
                    title=item["title"],
                    description=item["description"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"]),
                    user_id=item.get("user_id"),
                    user_email=item.get("user_email"),
                    app_version=item.get("app_version", ""),
                    os_version=item.get("os_version", ""),
                    tags=item.get("tags", []),
                    metadata=item.get("metadata", {}),
                    responses=item.get("responses", []),
                )
                self._feedback[feedback.feedback_id] = feedback

        except Exception as e:
            logger.error(f"Failed to load feedback: {e}")

    def _save_feedback(self) -> None:
        """Save feedback to storage."""
        self._storage_path.mkdir(parents=True, exist_ok=True)
        feedback_file = self._storage_path / "feedback.json"

        try:
            data = {
                "feedback": [
                    {
                        "feedback_id": f.feedback_id,
                        "type": f.type.value,
                        "priority": f.priority.value,
                        "status": f.status.value,
                        "title": f.title,
                        "description": f.description,
                        "created_at": f.created_at.isoformat(),
                        "updated_at": f.updated_at.isoformat(),
                        "user_id": f.user_id,
                        "user_email": f.user_email,
                        "app_version": f.app_version,
                        "os_version": f.os_version,
                        "tags": f.tags,
                        "metadata": f.metadata,
                        "responses": f.responses,
                    }
                    for f in self._feedback.values()
                ]
            }

            feedback_file.write_text(json.dumps(data, indent=2))

        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
