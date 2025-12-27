"""
Job Progress Routes

Unified job progress monitoring for all job types.
Supports batch jobs, training jobs, synthesis jobs, etc.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..optimization import cache_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

# In-memory job storage (replace with database in production)
_jobs: Dict[str, Dict] = {}


class JobType(str):
    """Job type enumeration."""

    BATCH = "batch"
    TRAINING = "training"
    SYNTHESIS = "synthesis"
    EXPORT = "export"
    IMPORT = "import"
    OTHER = "other"


class JobStatus(str):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class JobProgress(BaseModel):
    """Unified job progress information."""

    id: str
    name: str
    type: str  # JobType
    status: str  # JobStatus
    progress: float  # 0.0 to 1.0
    current_step: Optional[str] = None
    total_steps: Optional[int] = None
    current_step_index: Optional[int] = None
    created: str  # ISO datetime string
    started: Optional[str] = None
    completed: Optional[str] = None
    estimated_time_remaining: Optional[int] = None  # seconds
    error_message: Optional[str] = None
    result_id: Optional[str] = None
    metadata: Dict = {}


class JobSummary(BaseModel):
    """Summary of all jobs."""

    total: int
    pending: int
    running: int
    completed: int
    failed: int
    cancelled: int
    by_type: Dict[str, int] = {}


@router.get("", response_model=List[JobProgress])
@cache_response(ttl=5)  # Cache for 5 seconds (job status changes frequently)
async def get_jobs(
    job_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get all jobs, optionally filtered."""
    jobs = list(_jobs.values())

    if job_type:
        jobs = [j for j in jobs if j.get("type") == job_type]

    if status:
        jobs = [j for j in jobs if j.get("status") == status]

    # Sort by creation date (newest first)
    jobs.sort(key=lambda j: j.get("created", ""), reverse=True)

    # Convert to JobProgress models
    result = []
    for job in jobs[:limit]:
        result.append(
            JobProgress(
                id=job.get("id", ""),
                name=job.get("name", ""),
                type=job.get("type", "other"),
                status=job.get("status", "pending"),
                progress=job.get("progress", 0.0),
                current_step=job.get("current_step"),
                total_steps=job.get("total_steps"),
                current_step_index=job.get("current_step_index"),
                created=job.get("created", ""),
                started=job.get("started"),
                completed=job.get("completed"),
                estimated_time_remaining=job.get("estimated_time_remaining"),
                error_message=job.get("error_message"),
                result_id=job.get("result_id"),
                metadata=job.get("metadata", {}),
            )
        )

    return result


@router.get("/{job_id}", response_model=JobProgress)
@cache_response(ttl=5)  # Cache for 5 seconds (job status changes frequently)
async def get_job(job_id: str):
    """Get a specific job."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _jobs[job_id]
    return JobProgress(
        id=job.get("id", ""),
        name=job.get("name", ""),
        type=job.get("type", "other"),
        status=job.get("status", "pending"),
        progress=job.get("progress", 0.0),
        current_step=job.get("current_step"),
        total_steps=job.get("total_steps"),
        current_step_index=job.get("current_step_index"),
        created=job.get("created", ""),
        started=job.get("started"),
        completed=job.get("completed"),
        estimated_time_remaining=job.get("estimated_time_remaining"),
        error_message=job.get("error_message"),
        result_id=job.get("result_id"),
        metadata=job.get("metadata", {}),
    )


@router.get("/summary", response_model=JobSummary)
@cache_response(ttl=10)  # Cache for 10 seconds (summary updates frequently)
async def get_job_summary():
    """Get summary of all jobs."""
    total = len(_jobs)
    pending = len([j for j in _jobs.values() if j.get("status") == "pending"])
    running = len([j for j in _jobs.values() if j.get("status") == "running"])
    completed = len([j for j in _jobs.values() if j.get("status") == "completed"])
    failed = len([j for j in _jobs.values() if j.get("status") == "failed"])
    cancelled = len([j for j in _jobs.values() if j.get("status") == "cancelled"])

    # Count by type
    by_type: Dict[str, int] = {}
    for job in _jobs.values():
        job_type = job.get("type", "other")
        by_type[job_type] = by_type.get(job_type, 0) + 1

    return JobSummary(
        total=total,
        pending=pending,
        running=running,
        completed=completed,
        failed=failed,
        cancelled=cancelled,
        by_type=by_type,
    )


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a job."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _jobs[job_id]
    current_status = job.get("status", "pending")

    if current_status in ("completed", "failed", "cancelled"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job with status: {current_status}",
        )

    job["status"] = "cancelled"
    job["completed"] = datetime.utcnow().isoformat()
    _jobs[job_id] = job

    return {"success": True, "message": "Job cancelled"}


@router.post("/{job_id}/pause")
async def pause_job(job_id: str):
    """Pause a running job."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _jobs[job_id]
    if job.get("status") != "running":
        raise HTTPException(status_code=400, detail="Can only pause running jobs")

    job["status"] = "paused"
    _jobs[job_id] = job

    return {"success": True, "message": "Job paused"}


@router.post("/{job_id}/resume")
async def resume_job(job_id: str):
    """Resume a paused job."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _jobs[job_id]
    if job.get("status") != "paused":
        raise HTTPException(status_code=400, detail="Can only resume paused jobs")

    job["status"] = "running"
    _jobs[job_id] = job

    return {"success": True, "message": "Job resumed"}


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Delete a job (only if completed, failed, or cancelled)."""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _jobs[job_id]
    status = job.get("status", "pending")

    if status in ("pending", "running", "paused"):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete active job. Cancel it first.",
        )

    del _jobs[job_id]
    return {"success": True, "message": "Job deleted"}


@router.delete("")
async def clear_completed_jobs():
    """Clear all completed, failed, and cancelled jobs."""
    to_delete = [
        job_id
        for job_id, job in _jobs.items()
        if job.get("status") in ("completed", "failed", "cancelled")
    ]

    for job_id in to_delete:
        del _jobs[job_id]

    return {"success": True, "deleted_count": len(to_delete)}
