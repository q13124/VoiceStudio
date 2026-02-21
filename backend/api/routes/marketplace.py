"""
Plugin Marketplace API Routes.

Phase 7 Sprint 1: REST API for publisher registration, plugin submission,
review queue, ratings/reviews, and download tracking.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


# ============================================================================
# Request/Response Models
# ============================================================================


class PublisherRegisterRequest(BaseModel):
    """Publisher registration request."""

    name: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., min_length=1, max_length=320)
    website: str = Field(default="", max_length=500)
    description: str = Field(default="", max_length=2000)


class PublisherResponse(BaseModel):
    """Publisher profile response."""

    publisher_id: str
    name: str
    email: str
    website: str
    description: str
    verification_status: str
    created_at: str
    updated_at: str


class SubmissionRequest(BaseModel):
    """Plugin submission request."""

    plugin_id: str = Field(..., min_length=1, max_length=200)
    publisher_id: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., min_length=1, max_length=50)
    manifest_url: str = Field(default="", max_length=500)
    package_url: str = Field(default="", max_length=500)


class SubmissionResponse(BaseModel):
    """Plugin submission response."""

    submission_id: str
    plugin_id: str
    publisher_id: str
    version: str
    status: str
    created_at: str


class ReviewRequest(BaseModel):
    """Plugin review/rating request."""

    rating: int = Field(..., ge=1, le=5, description="Star rating 1-5")
    review: str = Field(default="", max_length=2000)
    version: str = Field(default="", max_length=50)


class ReviewResponse(BaseModel):
    """Review response."""

    rating_id: str
    plugin_id: str
    version: str
    rating: int
    review: str
    created_at: str
    updated_at: str


class SubmissionReviewRequest(BaseModel):
    """Admin review request."""

    action: str = Field(..., pattern="^(approve|reject)$")
    reason: str = Field(default="", max_length=1000)


# ============================================================================
# Publisher Endpoints
# ============================================================================


@router.post("/publishers", response_model=PublisherResponse)
async def register_publisher(request: PublisherRegisterRequest) -> dict[str, Any]:
    """
    Register a new publisher.

    Returns:
        Publisher profile with verification status.
    """
    try:
        from backend.services.marketplace_service import get_marketplace_service

        service = get_marketplace_service()
        publisher = service.register_publisher(
            name=request.name,
            email=request.email,
            website=request.website,
            description=request.description,
        )
        return publisher.to_dict()
    except Exception as e:
        logger.error("Publisher registration failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/publishers/{publisher_id}", response_model=PublisherResponse)
async def get_publisher(publisher_id: str) -> dict[str, Any]:
    """Get publisher profile by ID."""
    if not publisher_id:
        raise HTTPException(status_code=400, detail="publisher_id required")
    from backend.services.marketplace_service import get_marketplace_service

    service = get_marketplace_service()
    publisher = service.get_publisher(publisher_id)
    if not publisher:
        raise HTTPException(status_code=404, detail=f"Publisher '{publisher_id}' not found")
    return publisher.to_dict()


# ============================================================================
# Submission Endpoints
# ============================================================================


@router.post("/submissions", response_model=SubmissionResponse)
async def submit_plugin(request: SubmissionRequest) -> dict[str, Any]:
    """
    Submit a plugin for review.

    Triggers automated vetting (SBOM check, sandbox test, signing).
    """
    try:
        from backend.services.marketplace_service import get_marketplace_service

        service = get_marketplace_service()
        submission = service.submit_plugin(
            plugin_id=request.plugin_id,
            publisher_id=request.publisher_id,
            version=request.version,
            manifest_url=request.manifest_url,
            package_url=request.package_url,
        )
        service.run_automated_vetting(submission.submission_id)
        return {
            "submission_id": submission.submission_id,
            "plugin_id": submission.plugin_id,
            "publisher_id": submission.publisher_id,
            "version": submission.version,
            "status": "vetting",
            "created_at": submission.created_at,
        }
    except Exception as e:
        logger.error("Plugin submission failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/review-queue")
async def get_review_queue() -> list[dict[str, Any]]:
    """
    Get the admin review queue (pending and flagged submissions).

    Requires admin role in production.
    """
    try:
        from backend.services.marketplace_service import get_marketplace_service

        service = get_marketplace_service()
        items = service.get_review_queue()
        return [s.to_dict() for s in items]
    except Exception as e:
        logger.error("Failed to get review queue: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/review-queue/{submission_id}/review")
async def review_submission(submission_id: str, request: SubmissionReviewRequest) -> dict[str, Any]:
    """
    Approve or reject a submission (admin).

    action: "approve" or "reject"
    reason: Required for reject.
    """
    if not submission_id:
        raise HTTPException(status_code=400, detail="submission_id required")
    try:
        from backend.services.marketplace_service import get_marketplace_service

        service = get_marketplace_service()
        if request.action == "approve":
            success = service.approve_submission(submission_id, reviewed_by="admin")
        else:
            if not request.reason:
                raise HTTPException(status_code=400, detail="Rejection reason required")
            success = service.reject_submission(
                submission_id, reason=request.reason, reviewed_by="admin"
            )
        return {
            "success": success,
            "submission_id": submission_id,
            "action": request.action,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Review failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================================
# Ratings and Reviews Endpoints
# ============================================================================


@router.post("/reviews/{plugin_id}", response_model=ReviewResponse)
async def submit_review(plugin_id: str, request: ReviewRequest) -> dict[str, Any]:
    """
    Submit or update a rating/review for a plugin.

    rating: 1-5 stars
    review: Optional text review
    version: Plugin version (optional, defaults to latest)
    """
    if not plugin_id:
        raise HTTPException(status_code=400, detail="plugin_id required")
    try:
        from backend.services.marketplace_service import get_marketplace_service

        service = get_marketplace_service()
        version = request.version or "latest"
        result = service.add_review(
            plugin_id=plugin_id,
            version=version,
            rating=request.rating,
            review=request.review,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Review submission failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/reviews/{plugin_id}")
async def get_plugin_reviews(plugin_id: str) -> list[dict[str, Any]]:
    """Get reviews for a plugin."""
    if not plugin_id:
        raise HTTPException(status_code=400, detail="plugin_id required")
    try:
        from backend.services.marketplace_service import get_marketplace_service

        service = get_marketplace_service()
        return service.get_reviews(plugin_id)
    except Exception as e:
        logger.error("Failed to get reviews: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/reviews/{plugin_id}/mine")
async def get_my_review(plugin_id: str) -> dict[str, Any] | None:
    """Get current user's review for a plugin."""
    if not plugin_id:
        raise HTTPException(status_code=400, detail="plugin_id required")
    try:
        from backend.services.marketplace_service import get_marketplace_service

        service = get_marketplace_service()
        return service.get_my_review(plugin_id)
    except Exception as e:
        logger.error("Failed to get my review: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


# ============================================================================
# Download Tracking Endpoints
# ============================================================================


@router.post("/downloads/{plugin_id}/record")
async def record_download(plugin_id: str) -> dict[str, Any]:
    """
    Record a plugin download (called on install).

    Returns new download count.
    """
    if not plugin_id:
        raise HTTPException(status_code=400, detail="plugin_id required")
    try:
        from backend.services.marketplace_service import get_marketplace_service

        service = get_marketplace_service()
        count = service.record_download(plugin_id)
        return {"plugin_id": plugin_id, "download_count": count}
    except Exception as e:
        logger.error("Download recording failed: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/downloads/{plugin_id}")
async def get_download_count(plugin_id: str) -> dict[str, Any]:
    """Get download count for a plugin."""
    if not plugin_id:
        raise HTTPException(status_code=400, detail="plugin_id required")
    try:
        from backend.services.marketplace_service import get_marketplace_service

        service = get_marketplace_service()
        count = service.get_download_count(plugin_id)
        return {"plugin_id": plugin_id, "download_count": count}
    except Exception as e:
        logger.error("Failed to get download count: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e
