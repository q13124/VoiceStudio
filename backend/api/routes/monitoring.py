"""
Phase 9: Monitoring API Routes
Task 9.9: API routes for monitoring endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    uptime_seconds: float
    version: str
    checks: list[dict[str, Any]] = []


class MetricsResponse(BaseModel):
    """Metrics response."""
    timestamp: datetime
    metrics: dict[str, Any]


class AlertResponse(BaseModel):
    """Alert response."""
    alert_id: str
    severity: str
    status: str
    title: str
    message: str
    triggered_at: datetime


class DiagnosticsResponse(BaseModel):
    """Diagnostics response."""
    timestamp: datetime
    overall_status: str
    system_info: dict[str, Any]
    checks: list[dict[str, Any]]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Get application health status."""
    try:
        from backend.monitoring import HealthCheckService
        
        service = HealthCheckService()
        report = await service.run_all()
        
        return HealthResponse(
            status=report.overall_status.value,
            timestamp=report.timestamp,
            uptime_seconds=report.uptime_seconds,
            version=report.version,
            checks=[
                {
                    "component": c.component,
                    "status": c.status.value,
                    "message": c.message,
                    "latency_ms": c.latency_ms,
                }
                for c in report.checks
            ],
        )
    except ImportError:
        # Fallback if monitoring module not available
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now(),
            uptime_seconds=0,
            version="1.0.0",
            checks=[],
        )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """Get application metrics."""
    try:
        from backend.monitoring import get_collector
        
        collector = get_collector()
        
        return MetricsResponse(
            timestamp=datetime.now(),
            metrics=collector.get_all_metrics(),
        )
    except ImportError:
        return MetricsResponse(
            timestamp=datetime.now(),
            metrics={},
        )


@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    """Get metrics in Prometheus format."""
    try:
        from backend.monitoring import get_collector
        from fastapi.responses import PlainTextResponse
        
        collector = get_collector()
        
        return PlainTextResponse(
            content=collector.export_prometheus(),
            media_type="text/plain; charset=utf-8",
        )
    except ImportError:
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            content="# No metrics available\n",
            media_type="text/plain; charset=utf-8",
        )


@router.get("/alerts", response_model=list[AlertResponse])
async def get_active_alerts():
    """Get active alerts."""
    try:
        from backend.monitoring import AlertManager
        
        manager = AlertManager()
        alerts = manager.get_active_alerts()
        
        return [
            AlertResponse(
                alert_id=a.alert_id,
                severity=a.severity.value,
                status=a.status.value,
                title=a.title,
                message=a.message,
                triggered_at=a.triggered_at,
            )
            for a in alerts
        ]
    except ImportError:
        return []


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user: str = "system"):
    """Acknowledge an alert."""
    try:
        from backend.monitoring import AlertManager
        
        manager = AlertManager()
        if manager.acknowledge(alert_id, user):
            return {"status": "acknowledged"}
        
        raise HTTPException(status_code=404, detail="Alert not found")
        
    except ImportError:
        raise HTTPException(status_code=501, detail="Alerting not available")


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert."""
    try:
        from backend.monitoring import AlertManager
        
        manager = AlertManager()
        if manager.resolve(alert_id):
            return {"status": "resolved"}
        
        raise HTTPException(status_code=404, detail="Alert not found")
        
    except ImportError:
        raise HTTPException(status_code=501, detail="Alerting not available")


@router.get("/diagnostics", response_model=DiagnosticsResponse)
async def run_diagnostics():
    """Run system diagnostics."""
    try:
        from backend.diagnostics.system_diagnostics import SystemDiagnostics
        
        diagnostics = SystemDiagnostics()
        report = await diagnostics.run_diagnostics()
        
        return DiagnosticsResponse(
            timestamp=report.timestamp,
            overall_status=report.overall_status.value,
            system_info={
                "os": report.system_info.os_name,
                "version": report.system_info.os_version,
                "cpu": report.system_info.cpu_model,
                "ram_gb": report.system_info.ram_total_gb,
                "gpu": report.system_info.gpu_name,
            },
            checks=[
                {
                    "name": r.name,
                    "category": r.category.value,
                    "status": r.status.value,
                    "message": r.message,
                    "details": r.details,
                }
                for r in report.results
            ],
        )
    except ImportError:
        return DiagnosticsResponse(
            timestamp=datetime.now(),
            overall_status="unknown",
            system_info={},
            checks=[],
        )


@router.get("/performance")
async def get_performance_stats():
    """Get performance statistics."""
    try:
        from backend.monitoring import get_monitor
        
        monitor = get_monitor()
        stats = monitor.get_stats()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "stats": [
                {
                    "operation": s.operation_type,
                    "count": s.count,
                    "avg_ms": s.avg_duration_ms,
                    "p95_ms": s.p95_ms,
                    "p99_ms": s.p99_ms,
                    "error_rate": s.error_rate,
                }
                for s in stats
            ],
        }
    except ImportError:
        return {"timestamp": datetime.now().isoformat(), "stats": []}


@router.get("/errors")
async def get_recent_errors(limit: int = 20):
    """Get recent errors."""
    try:
        from backend.monitoring import get_tracker
        
        tracker = get_tracker()
        errors = tracker.get_errors(limit=limit)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "errors": [
                {
                    "error_id": e.error_id,
                    "type": e.exception_type,
                    "message": e.message,
                    "severity": e.severity.value,
                    "category": e.category.value,
                    "count": e.occurrence_count,
                    "first_seen": e.first_seen.isoformat(),
                    "last_seen": e.last_seen.isoformat(),
                }
                for e in errors
            ],
        }
    except ImportError:
        return {"timestamp": datetime.now().isoformat(), "errors": []}
