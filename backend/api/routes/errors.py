"""
Error Tracking API Routes — Phase 5.4

Provides API endpoints for error tracking and analysis.
All operations are local-first and require no external dependencies.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.services.error_tracker import (
    ErrorAggregate,
    ErrorCategory,
    ErrorSeverity,
    ErrorSummary,
    TrackedError,
    get_error_tracker,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/errors", tags=["errors"])


# =============================================================================
# Response Models
# =============================================================================


class ErrorContextResponse(BaseModel):
    """Response model for error context."""

    request_id: str | None = None
    user_id: str | None = None
    endpoint: str | None = None
    method: str | None = None


class TrackedErrorResponse(BaseModel):
    """Response model for a tracked error."""

    error_id: str
    fingerprint: str
    timestamp: str
    severity: str
    category: str
    message: str
    exception_type: str
    stacktrace: str | None = None
    context: ErrorContextResponse | None = None
    tags: list[str] = []
    resolved: bool = False


class ErrorAggregateResponse(BaseModel):
    """Response model for error aggregate."""

    fingerprint: str
    first_seen: str
    last_seen: str
    count: int
    severity: str
    category: str
    message: str
    exception_type: str
    affected_endpoints: list[str] = []


class ErrorSummaryResponse(BaseModel):
    """Response model for error summary."""

    total_errors: int
    unique_errors: int
    errors_by_severity: dict[str, int]
    errors_by_category: dict[str, int]
    error_rate: float
    top_errors: list[ErrorAggregateResponse]


class ResolveRequest(BaseModel):
    """Request model for resolving an error."""

    resolution_notes: str = ""


class ResolveResponse(BaseModel):
    """Response model for resolve operation."""

    success: bool
    error_id: str
    message: str


class ExportResponse(BaseModel):
    """Response model for export operation."""

    success: bool
    filepath: str
    message: str


# =============================================================================
# Helper Functions
# =============================================================================


def _convert_error(error: TrackedError) -> TrackedErrorResponse:
    """Convert internal error to response model."""
    return TrackedErrorResponse(
        error_id=error.error_id,
        fingerprint=error.fingerprint,
        timestamp=error.timestamp,
        severity=error.severity.value,
        category=error.category.value,
        message=error.message,
        exception_type=error.exception_type,
        stacktrace=error.stacktrace,
        context=(
            ErrorContextResponse(
                request_id=error.context.request_id,
                user_id=error.context.user_id,
                endpoint=error.context.endpoint,
                method=error.context.method,
            )
            if error.context
            else None
        ),
        tags=error.tags,
        resolved=error.resolved,
    )


def _convert_aggregate(agg: ErrorAggregate) -> ErrorAggregateResponse:
    """Convert internal aggregate to response model."""
    return ErrorAggregateResponse(
        fingerprint=agg.fingerprint,
        first_seen=agg.first_seen,
        last_seen=agg.last_seen,
        count=agg.count,
        severity=agg.severity.value,
        category=agg.category.value,
        message=agg.message,
        exception_type=agg.exception_type,
        affected_endpoints=agg.affected_endpoints,
    )


def _convert_summary(summary: ErrorSummary) -> ErrorSummaryResponse:
    """Convert internal summary to response model."""
    return ErrorSummaryResponse(
        total_errors=summary.total_errors,
        unique_errors=summary.unique_errors,
        errors_by_severity=summary.errors_by_severity,
        errors_by_category=summary.errors_by_category,
        error_rate=summary.error_rate,
        top_errors=[_convert_aggregate(a) for a in summary.top_errors],
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get("/summary", response_model=ErrorSummaryResponse)
async def get_error_summary():
    """
    Get error summary statistics.

    Returns aggregated error statistics including:
    - Total error count
    - Unique error count
    - Errors by severity and category
    - Error rate
    - Top errors by frequency
    """
    try:
        tracker = get_error_tracker()
        summary = tracker.get_summary()
        return _convert_summary(summary)
    except Exception as e:
        logger.error(f"Error getting error summary: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/recent", response_model=list[TrackedErrorResponse])
async def get_recent_errors(
    limit: int = Query(100, ge=1, le=500, description="Maximum errors to return"),
    severity: str | None = Query(None, description="Filter by severity"),
    category: str | None = Query(None, description="Filter by category"),
):
    """
    Get recent errors with optional filtering.

    Returns the most recent tracked errors, optionally filtered by severity
    or category.
    """
    try:
        tracker = get_error_tracker()

        # Convert string to enum if provided
        severity_enum = None
        if severity:
            try:
                severity_enum = ErrorSeverity(severity)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")

        category_enum = None
        if category:
            try:
                category_enum = ErrorCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

        errors = tracker.get_errors(
            limit=limit,
            severity=severity_enum,
            category=category_enum,
        )

        return [_convert_error(e) for e in errors]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recent errors: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/aggregates", response_model=list[ErrorAggregateResponse])
async def get_error_aggregates(
    limit: int = Query(50, ge=1, le=200, description="Maximum aggregates to return"),
    sort_by: str = Query("count", description="Sort by: count or recent"),
):
    """
    Get aggregated error statistics.

    Returns unique errors grouped by fingerprint with occurrence counts.
    """
    try:
        if sort_by not in ("count", "recent"):
            raise HTTPException(status_code=400, detail="sort_by must be 'count' or 'recent'")

        tracker = get_error_tracker()
        aggregates = tracker.get_aggregates(limit=limit, sort_by=sort_by)
        return [_convert_aggregate(a) for a in aggregates]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting error aggregates: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/categories")
async def get_error_categories():
    """
    Get available error categories.
    """
    return {
        "categories": [c.value for c in ErrorCategory],
        "severities": [s.value for s in ErrorSeverity],
    }


@router.post("/{error_id}/resolve", response_model=ResolveResponse)
async def resolve_error(
    error_id: str,
    request: ResolveRequest,
):
    """
    Mark an error as resolved.

    Resolving an error removes it from active tracking but keeps it in
    history for analysis.
    """
    try:
        tracker = get_error_tracker()
        success = tracker.resolve_error(error_id, request.resolution_notes)

        if not success:
            raise HTTPException(status_code=404, detail=f"Error not found: {error_id}")

        return ResolveResponse(
            success=True,
            error_id=error_id,
            message="Error marked as resolved",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/export", response_model=ExportResponse)
async def export_error_report(
    filename: str | None = Query(None, description="Custom filename"),
    include_stacktraces: bool = Query(False, description="Include stacktraces"),
):
    """
    Export error report to JSON file.

    The report is saved to .buildlogs/errors/ directory.
    """
    try:
        tracker = get_error_tracker()
        filepath = tracker.export_report(
            filename=filename,
            include_stacktraces=include_stacktraces,
        )

        return ExportResponse(
            success=True,
            filepath=str(filepath),
            message=f"Error report exported to {filepath}",
        )
    except Exception as e:
        logger.error(f"Error exporting error report: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/resolved")
async def clear_resolved_errors():
    """
    Clear all resolved errors from tracking.

    Returns the number of errors removed.
    """
    try:
        tracker = get_error_tracker()
        removed = tracker.clear_resolved()

        return {
            "success": True,
            "removed": removed,
            "message": f"Cleared {removed} resolved errors",
        }
    except Exception as e:
        logger.error(f"Error clearing resolved errors: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/rate")
async def get_error_rate():
    """
    Get current error rate.

    Returns the error rate as a percentage of total requests.
    """
    try:
        tracker = get_error_tracker()
        summary = tracker.get_summary()

        return {
            "error_rate": summary.error_rate,
            "total_errors": summary.total_errors,
            "unique_errors": summary.unique_errors,
        }
    except Exception as e:
        logger.error(f"Error getting error rate: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
