"""
Phase 9: Feedback API Routes
Task 9.10: API routes for user feedback.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

# Import feedback service at module level - fail fast at startup if not available
from backend.feedback import (
    FeedbackPriority,
    FeedbackService,
    FeedbackStatus,
    FeedbackType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/feedback", tags=["feedback"])


class FeedbackSubmission(BaseModel):
    """Feedback submission request."""

    type: str  # bug_report, feature_request, improvement, question, praise, other
    title: str
    description: str
    priority: str = "medium"  # low, medium, high, critical
    user_email: str | None = None
    tags: list[str] = []
    metadata: dict[str, Any] = {}


class FeedbackResponse(BaseModel):
    """Feedback response."""

    feedback_id: str
    type: str
    priority: str
    status: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime


class FeedbackStatsResponse(BaseModel):
    """Feedback statistics response."""

    total: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    by_priority: dict[str, int]
    average_resolution_hours: float


@router.post("/submit", response_model=FeedbackResponse)
async def submit_feedback(submission: FeedbackSubmission):
    """Submit user feedback."""
    try:
        service = FeedbackService()

        # Map string to enum
        feedback_type = FeedbackType(submission.type)
        priority = FeedbackPriority(submission.priority)

        feedback = service.submit(
            feedback_type=feedback_type,
            title=submission.title,
            description=submission.description,
            priority=priority,
            user_email=submission.user_email,
            tags=submission.tags,
            metadata=submission.metadata,
        )

        return FeedbackResponse(
            feedback_id=feedback.feedback_id,
            type=feedback.type.value,
            priority=feedback.priority.value,
            status=feedback.status.value,
            title=feedback.title,
            description=feedback.description,
            created_at=feedback.created_at,
            updated_at=feedback.updated_at,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[FeedbackResponse])
async def list_feedback(
    type: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    """List feedback with optional filters."""
    try:
        service = FeedbackService()

        # Convert string filters to enums
        ft = FeedbackType(type) if type else None
        fs = FeedbackStatus(status) if status else None
        fp = FeedbackPriority(priority) if priority else None

        items = service.list_feedback(
            feedback_type=ft,
            status=fs,
            priority=fp,
            limit=limit,
            offset=offset,
        )

        return [
            FeedbackResponse(
                feedback_id=f.feedback_id,
                type=f.type.value,
                priority=f.priority.value,
                status=f.status.value,
                title=f.title,
                description=f.description,
                created_at=f.created_at,
                updated_at=f.updated_at,
            )
            for f in items
        ]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(feedback_id: str):
    """Get feedback by ID."""
    service = FeedbackService()
    feedback = service.get(feedback_id)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return FeedbackResponse(
        feedback_id=feedback.feedback_id,
        type=feedback.type.value,
        priority=feedback.priority.value,
        status=feedback.status.value,
        title=feedback.title,
        description=feedback.description,
        created_at=feedback.created_at,
        updated_at=feedback.updated_at,
    )


@router.patch("/{feedback_id}/status")
async def update_feedback_status(feedback_id: str, status: str, comment: str | None = None):
    """Update feedback status."""
    try:
        service = FeedbackService()

        new_status = FeedbackStatus(status)
        feedback = service.update_status(feedback_id, new_status, comment)

        if not feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")

        return {"status": "updated", "new_status": status}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{feedback_id}/respond")
async def add_response(
    feedback_id: str, message: str = Form(...), responder: str = Form(default="support")
):
    """Add a response to feedback."""
    service = FeedbackService()
    feedback = service.add_response(feedback_id, message, responder)

    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return {"status": "response_added"}


@router.post("/{feedback_id}/attachments")
async def add_attachment(feedback_id: str, file: UploadFile = File(...)):
    """Add an attachment to feedback."""
    service = FeedbackService()

    content = await file.read()
    attachment = service.add_attachment(
        feedback_id,
        file.filename or "attachment",
        content,
        file.content_type or "application/octet-stream",
    )

    if not attachment:
        raise HTTPException(status_code=404, detail="Feedback not found")

    return {
        "attachment_id": attachment.attachment_id,
        "filename": attachment.filename,
        "size_bytes": attachment.size_bytes,
    }


@router.get("/stats/summary", response_model=FeedbackStatsResponse)
async def get_feedback_stats():
    """Get feedback statistics."""
    service = FeedbackService()
    stats = service.get_stats()

    return FeedbackStatsResponse(
        total=stats.total,
        by_type=stats.by_type,
        by_status=stats.by_status,
        by_priority=stats.by_priority,
        average_resolution_hours=stats.average_resolution_hours,
    )


@router.delete("/{feedback_id}")
async def delete_feedback(feedback_id: str):
    """Delete feedback."""
    service = FeedbackService()

    if service.delete(feedback_id):
        return {"status": "deleted"}

    raise HTTPException(status_code=404, detail="Feedback not found")
