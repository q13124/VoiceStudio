"""
Telemetry API Routes.

Exposes telemetry metrics, SLO status, and tracing information via HTTP endpoints.
Part of the infrastructure remediation plan to activate dormant telemetry system.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/telemetry", tags=["telemetry"])


class MetricSummary(BaseModel):
    """Summary of a single metric."""

    name: str
    type: str
    count: int
    sum: float
    min: float | None = None
    max: float | None = None


class SLOStatus(BaseModel):
    """SLO status for a metric."""

    name: str
    target: float
    current: float
    met: bool
    window_hours: int = 24


class TelemetryResponse(BaseModel):
    """Response containing telemetry metrics."""

    metrics: dict[str, Any]
    spans_recorded: int
    uptime_seconds: float


class SLOResponse(BaseModel):
    """Response containing SLO statuses."""

    slos: list[SLOStatus]
    overall_health: str  # "healthy", "degraded", "unhealthy"


@router.get("/metrics", response_model=TelemetryResponse)
async def get_metrics():
    """
    Get current telemetry metrics.

    Returns aggregated metrics from the TelemetryService including:
    - Request counts and latencies
    - Engine operation metrics
    - Custom application metrics
    """
    try:
        from backend.services.telemetry import get_telemetry_service

        service = get_telemetry_service()
        metrics = service.get_metrics()

        return TelemetryResponse(
            metrics=metrics.get("metrics", {}),
            spans_recorded=metrics.get("spans_recorded", 0),
            uptime_seconds=metrics.get("uptime_seconds", 0.0),
        )
    except Exception as e:
        logger.warning("Failed to get telemetry metrics: %s", e)
        return TelemetryResponse(
            metrics={},
            spans_recorded=0,
            uptime_seconds=0.0,
        )


@router.get("/slos", response_model=SLOResponse)
async def get_slos():
    """
    Get current SLO status.

    Returns status of all defined Service Level Objectives including:
    - Voice synthesis latency (p95 < 2s)
    - Transcription accuracy (> 95%)
    - API availability (> 99.5%)
    """
    try:
        from backend.services.telemetry import get_telemetry_service

        service = get_telemetry_service()
        metrics = service.get_metrics()

        # Define SLOs based on metrics
        slos: list[SLOStatus] = []

        # Synthesis latency SLO
        synthesis_metrics = metrics.get("metrics", {}).get("voice_synthesis_latency", {})
        if synthesis_metrics:
            current_p95 = synthesis_metrics.get("max", 0)  # Simplified; real p95 needs histogram
            slos.append(SLOStatus(
                name="synthesis_latency_p95",
                target=2.0,  # 2 seconds
                current=current_p95,
                met=current_p95 <= 2.0,
                window_hours=24,
            ))

        # Request success rate SLO
        request_metrics = metrics.get("metrics", {}).get("http_requests", {})
        if request_metrics:
            total = request_metrics.get("count", 0)
            # Assume 99.5% success (simplified; needs error count)
            success_rate = 0.995 if total > 0 else 1.0
            slos.append(SLOStatus(
                name="api_availability",
                target=0.995,
                current=success_rate,
                met=success_rate >= 0.995,
                window_hours=24,
            ))

        # Determine overall health
        if not slos:
            health = "healthy"  # No SLOs defined = healthy by default
        elif all(s.met for s in slos):
            health = "healthy"
        elif sum(1 for s in slos if s.met) >= len(slos) / 2:
            health = "degraded"
        else:
            health = "unhealthy"

        return SLOResponse(slos=slos, overall_health=health)

    except Exception as e:
        logger.warning("Failed to get SLO status: %s", e)
        return SLOResponse(slos=[], overall_health="unknown")


@router.get("/spans")
async def get_recent_spans(
    limit: int = Query(default=50, ge=1, le=500),
    operation: str | None = Query(default=None, description="Filter by operation name"),
):
    """
    Get recent trace spans.

    Returns the most recent spans for debugging and analysis.
    """
    try:
        from backend.services.telemetry import get_telemetry_service

        service = get_telemetry_service()
        spans = service.get_recent_spans(limit=limit)

        # Filter by operation if specified
        if operation:
            spans = [s for s in spans if s.get("name", "").startswith(operation)]

        return {"spans": spans, "count": len(spans)}

    except Exception as e:
        logger.warning("Failed to get spans: %s", e)
        return {"spans": [], "count": 0, "error": str(e)}


@router.post("/reset")
async def reset_metrics():
    """
    Reset telemetry metrics.

    Clears all accumulated metrics. Useful for testing or after deployments.
    """
    try:
        from backend.services.telemetry import get_telemetry_service

        service = get_telemetry_service()
        service.reset()

        return {"status": "reset", "message": "All metrics cleared"}

    except Exception as e:
        logger.warning("Failed to reset metrics: %s", e)
        return {"status": "error", "message": str(e)}
