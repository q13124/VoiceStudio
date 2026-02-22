"""
SLO Monitoring API Routes — Phase 5.2

Provides API endpoints for SLO status, alerts, and management.
All operations are local-first and require no external dependencies.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.platform.monitoring.slo_monitor import SLOAlert as SLOAlertModel
from backend.platform.monitoring.slo_monitor import SLOStatus as SLOStatusModel
from backend.platform.monitoring.slo_monitor import (
    get_slo_monitor,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/slo", tags=["slo"])


# =============================================================================
# Response Models
# =============================================================================


class SLOStatusResponse(BaseModel):
    """Response model for SLO status."""

    slo_id: str
    slo_name: str
    target: float
    current_value: float
    is_met: bool
    alert_severity: str | None = None
    window_hours: int
    sample_count: int
    last_updated: str
    burn_rate: float
    error_budget_remaining: float


class SLOAlertResponse(BaseModel):
    """Response model for SLO alert."""

    alert_id: str
    slo_id: str
    slo_name: str
    severity: str
    message: str
    current_value: float
    target: float
    timestamp: str
    acknowledged: bool
    acknowledged_by: str | None = None
    acknowledged_at: str | None = None
    resolved: bool
    resolved_at: str | None = None


class SLOOverviewResponse(BaseModel):
    """Response model for SLO overview."""

    overall_health: str
    total_slos: int
    slos_met: int
    slos_breached: int
    active_alerts: int
    critical_alerts: int
    warning_alerts: int


class SLOListResponse(BaseModel):
    """Response model for SLO list."""

    overview: SLOOverviewResponse
    slos: list[SLOStatusResponse]


class AlertListResponse(BaseModel):
    """Response model for alert list."""

    active_count: int
    alerts: list[SLOAlertResponse]


class AcknowledgeRequest(BaseModel):
    """Request model for acknowledging an alert."""

    acknowledged_by: str = "api"


class AcknowledgeResponse(BaseModel):
    """Response model for acknowledge operation."""

    success: bool
    alert_id: str
    message: str


class ExportResponse(BaseModel):
    """Response model for export operation."""

    success: bool
    filepath: str
    message: str


# =============================================================================
# Helper Functions
# =============================================================================


def _convert_status(status: SLOStatusModel) -> SLOStatusResponse:
    """Convert internal SLOStatus to response model."""
    return SLOStatusResponse(
        slo_id=status.slo_id,
        slo_name=status.slo_name,
        target=status.target,
        current_value=status.current_value,
        is_met=status.is_met,
        alert_severity=status.alert_severity,
        window_hours=status.window_hours,
        sample_count=status.sample_count,
        last_updated=status.last_updated,
        burn_rate=status.burn_rate,
        error_budget_remaining=status.error_budget_remaining,
    )


def _convert_alert(alert: SLOAlertModel) -> SLOAlertResponse:
    """Convert internal SLOAlert to response model."""
    return SLOAlertResponse(
        alert_id=alert.alert_id,
        slo_id=alert.slo_id,
        slo_name=alert.slo_name,
        severity=alert.severity.value if hasattr(alert.severity, "value") else str(alert.severity),
        message=alert.message,
        current_value=alert.current_value,
        target=alert.target,
        timestamp=alert.timestamp,
        acknowledged=alert.acknowledged,
        acknowledged_by=alert.acknowledged_by,
        acknowledged_at=alert.acknowledged_at,
        resolved=alert.resolved,
        resolved_at=alert.resolved_at,
    )


# =============================================================================
# Endpoints
# =============================================================================


@router.get("", response_model=SLOListResponse)
async def get_all_slos():
    """
    Get all SLO statuses with overview.

    Returns current status of all defined SLOs along with an overview summary.
    """
    try:
        monitor = get_slo_monitor()
        statuses = monitor.get_all_slo_statuses()
        active_alerts = monitor.get_active_alerts()

        met_count = sum(1 for s in statuses if s.is_met)
        critical_count = sum(1 for a in active_alerts if a.severity.value == "critical")
        warning_count = sum(1 for a in active_alerts if a.severity.value == "warning")

        overview = SLOOverviewResponse(
            overall_health=monitor.get_overall_health(),
            total_slos=len(statuses),
            slos_met=met_count,
            slos_breached=len(statuses) - met_count,
            active_alerts=len(active_alerts),
            critical_alerts=critical_count,
            warning_alerts=warning_count,
        )

        return SLOListResponse(
            overview=overview,
            slos=[_convert_status(s) for s in statuses],
        )
    except Exception as e:
        logger.error(f"Error getting SLO statuses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_slo_health():
    """
    Get overall SLO health status.

    Returns a simple health indicator: "healthy", "degraded", or "unhealthy".
    """
    try:
        monitor = get_slo_monitor()
        return {
            "status": monitor.get_overall_health(),
            "timestamp": (
                monitor.get_all_slo_statuses()[0].last_updated
                if monitor.get_all_slo_statuses()
                else None
            ),
        }
    except Exception as e:
        logger.error(f"Error getting SLO health: {e}")
        return {"status": "unknown", "error": str(e)}


@router.get("/{slo_id}", response_model=SLOStatusResponse)
async def get_slo_status(slo_id: str):
    """
    Get status of a specific SLO.

    Args:
        slo_id: The SLO identifier

    Returns:
        Current status of the specified SLO
    """
    try:
        monitor = get_slo_monitor()
        status = monitor.get_slo_status(slo_id)

        if not status:
            raise HTTPException(status_code=404, detail=f"SLO {slo_id} not found")

        return _convert_status(status)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SLO status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/active", response_model=AlertListResponse)
async def get_active_alerts():
    """
    Get all active (unresolved) alerts.

    Returns list of alerts that have not been resolved.
    """
    try:
        monitor = get_slo_monitor()
        alerts = monitor.get_active_alerts()

        return AlertListResponse(
            active_count=len(alerts),
            alerts=[_convert_alert(a) for a in alerts],
        )
    except Exception as e:
        logger.error(f"Error getting active alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts/history", response_model=AlertListResponse)
async def get_alert_history(
    limit: int = Query(100, ge=1, le=1000, description="Maximum alerts to return"),
    slo_id: str | None = Query(None, description="Filter by SLO ID"),
):
    """
    Get alert history.

    Returns historical alerts including both active and resolved.
    """
    try:
        monitor = get_slo_monitor()
        alerts = monitor.get_alert_history(limit=limit, slo_id=slo_id)

        return AlertListResponse(
            active_count=sum(1 for a in alerts if not a.resolved),
            alerts=[_convert_alert(a) for a in alerts],
        )
    except Exception as e:
        logger.error(f"Error getting alert history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/{alert_id}/acknowledge", response_model=AcknowledgeResponse)
async def acknowledge_alert(
    alert_id: str,
    request: AcknowledgeRequest,
):
    """
    Acknowledge an alert.

    Acknowledging an alert indicates it has been seen and is being addressed.
    """
    try:
        monitor = get_slo_monitor()
        success = monitor.acknowledge_alert(alert_id, request.acknowledged_by)

        if success:
            return AcknowledgeResponse(
                success=True,
                alert_id=alert_id,
                message=f"Alert {alert_id} acknowledged by {request.acknowledged_by}",
            )
        else:
            raise HTTPException(
                status_code=404, detail=f"Alert {alert_id} not found or already acknowledged"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export", response_model=ExportResponse)
async def export_slo_status():
    """
    Export current SLO status to a JSON file.

    The file is saved to .buildlogs/slo/ directory.
    """
    try:
        monitor = get_slo_monitor()
        filepath = monitor.export_status()

        return ExportResponse(
            success=True,
            filepath=str(filepath),
            message=f"SLO status exported to {filepath}",
        )
    except Exception as e:
        logger.error(f"Error exporting SLO status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record/{metric_name}")
async def record_metric(
    metric_name: str,
    value: float = Query(..., description="Metric value to record"),
):
    """
    Record a metric value for SLO tracking.

    This endpoint allows external systems to record metrics that are
    tracked by SLOs.
    """
    try:
        monitor = get_slo_monitor()
        monitor.record_metric(metric_name, value)

        return {
            "success": True,
            "metric_name": metric_name,
            "value": value,
            "message": f"Recorded {metric_name}={value}",
        }
    except Exception as e:
        logger.error(f"Error recording metric: {e}")
        raise HTTPException(status_code=500, detail=str(e))
