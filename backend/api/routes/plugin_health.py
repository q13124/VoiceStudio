"""
Plugin Health REST API — Phase 5D M3.

Provides REST endpoints for plugin health metrics and audit visualization.
Supports querying plugin performance, viewing audit trails, and exporting data.

Architecture: Routes -> Metrics/Audit Services -> SQLite Persistence
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/plugins/health", tags=["plugin-health"])


# =============================================================================
# Request/Response Models
# =============================================================================


class HealthStatus(str, Enum):
    """Plugin health status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MetricSummary(BaseModel):
    """Summary of a metric type."""

    count: int = 0
    sum: float = 0.0
    min: float = 0.0
    max: float = 0.0
    avg: float = 0.0


class PluginHealthResponse(BaseModel):
    """Health status for a single plugin."""

    plugin_id: str
    status: HealthStatus
    uptime_seconds: float = 0.0
    total_calls: int = 0
    total_errors: int = 0
    error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    memory_bytes: int = 0
    last_active: str | None = None
    metrics: dict[str, MetricSummary] = {}


class SystemHealthResponse(BaseModel):
    """System-wide plugin health status."""

    total_plugins: int = 0
    healthy_plugins: int = 0
    degraded_plugins: int = 0
    unhealthy_plugins: int = 0
    total_calls: int = 0
    total_errors: int = 0
    system_error_rate: float = 0.0
    avg_latency_ms: float = 0.0
    total_memory_bytes: int = 0
    timestamp: str


class MetricRecord(BaseModel):
    """A single metric record."""

    id: int | None = None
    plugin_id: str
    metric_type: str
    value: float
    timestamp: str
    labels: dict[str, str] = {}
    session_id: str | None = None


class MetricsQueryResponse(BaseModel):
    """Response for metrics query."""

    count: int
    metrics: list[MetricRecord]
    filters: dict[str, Any] = {}


class AuditEvent(BaseModel):
    """An audit log event."""

    id: int | None = None
    timestamp: str
    event_type: str
    plugin_id: str | None = None
    severity: str = "INFO"
    message: str
    details: dict[str, Any] = {}
    actor: str | None = None


class AuditQueryResponse(BaseModel):
    """Response for audit query."""

    count: int
    events: list[AuditEvent]
    filters: dict[str, Any] = {}


class StorageStats(BaseModel):
    """Metrics storage statistics."""

    total_records: int = 0
    file_size_bytes: int = 0
    file_size_mb: float = 0.0
    date_range: dict[str, str | None] = {}
    records_by_plugin: dict[str, int] = {}
    records_by_type: dict[str, int] = {}
    retention_policy: str = "30_days"


class ExportFormat(str, Enum):
    """Supported export formats."""

    JSON = "json"
    CSV = "csv"
    PROMETHEUS = "prometheus"


# =============================================================================
# Helper Functions
# =============================================================================


def _get_persistence():
    """Get the metrics persistence instance."""
    try:
        from backend.plugins.metrics.persistence import get_metrics_persistence

        return get_metrics_persistence()
    except ImportError:
        logger.warning("Metrics persistence not available")
        return None


def _get_audit_logger():
    """Get the audit logger instance."""
    try:
        from backend.plugins.supply_chain.audit import get_audit_logger

        return get_audit_logger()
    except ImportError:
        logger.warning("Audit logger not available")
        return None


def _get_metrics_aggregator():
    """Get the metrics aggregator instance."""
    try:
        from backend.plugins.metrics.aggregator import get_aggregator

        return get_aggregator()
    except ImportError:
        logger.warning("Metrics aggregator not available")
        return None


def _calculate_health_status(error_rate: float, crash_count: int) -> HealthStatus:
    """Calculate health status from metrics."""
    if error_rate > 10.0 or crash_count > 0:
        return HealthStatus.UNHEALTHY
    elif error_rate > 5.0:
        return HealthStatus.DEGRADED
    else:
        return HealthStatus.HEALTHY


# =============================================================================
# Health Endpoints
# =============================================================================


@router.get("/system", response_model=SystemHealthResponse)
async def get_system_health() -> SystemHealthResponse:
    """
    Get system-wide plugin health status.

    Returns aggregated health metrics across all plugins.
    """
    aggregator = _get_metrics_aggregator()

    if aggregator:
        try:
            health = aggregator.get_system_health()
            return SystemHealthResponse(
                total_plugins=health.total_plugins,
                healthy_plugins=health.healthy_plugins,
                degraded_plugins=health.degraded_plugins,
                unhealthy_plugins=health.unhealthy_plugins,
                total_calls=health.total_calls,
                total_errors=health.total_errors,
                system_error_rate=health.system_error_rate,
                avg_latency_ms=health.avg_latency_ms,
                total_memory_bytes=health.total_memory_bytes,
                timestamp=datetime.now().isoformat(),
            )
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")

    # Return empty response if aggregator not available
    return SystemHealthResponse(timestamp=datetime.now().isoformat())


@router.get("/plugins", response_model=list[PluginHealthResponse])
async def list_plugin_health() -> list[PluginHealthResponse]:
    """
    Get health status for all plugins.

    Returns health metrics for each active plugin.
    """
    aggregator = _get_metrics_aggregator()
    results: list[PluginHealthResponse] = []

    if aggregator:
        try:
            plugin_health_list = aggregator.get_all_plugin_health()
            for ph in plugin_health_list:
                results.append(
                    PluginHealthResponse(
                        plugin_id=ph.plugin_id,
                        status=_calculate_health_status(ph.error_rate, ph.crash_count),
                        uptime_seconds=ph.uptime_seconds,
                        total_calls=ph.total_calls,
                        total_errors=ph.total_errors,
                        error_rate=ph.error_rate,
                        avg_latency_ms=ph.avg_latency_ms,
                        memory_bytes=ph.memory_bytes,
                        last_active=ph.last_active.isoformat() if ph.last_active else None,
                    )
                )
        except Exception as e:
            logger.error(f"Failed to get plugin health list: {e}")

    return results


@router.get("/plugins/{plugin_id}", response_model=PluginHealthResponse)
async def get_plugin_health(plugin_id: str) -> PluginHealthResponse:
    """
    Get health status for a specific plugin.

    Args:
        plugin_id: Plugin identifier
    """
    aggregator = _get_metrics_aggregator()
    persistence = _get_persistence()

    if aggregator:
        try:
            ph = aggregator.get_plugin_health(plugin_id)
            if ph:
                # Get additional metrics from persistence if available
                metrics_summary: dict[str, MetricSummary] = {}
                if persistence:
                    summary = persistence.get_plugin_summary(
                        plugin_id, since=datetime.now() - timedelta(hours=24)
                    )
                    for metric_type, stats in summary.get("metrics", {}).items():
                        metrics_summary[metric_type] = MetricSummary(
                            count=stats["count"],
                            sum=stats["sum"],
                            min=stats["min"],
                            max=stats["max"],
                            avg=stats["avg"],
                        )

                return PluginHealthResponse(
                    plugin_id=ph.plugin_id,
                    status=_calculate_health_status(ph.error_rate, ph.crash_count),
                    uptime_seconds=ph.uptime_seconds,
                    total_calls=ph.total_calls,
                    total_errors=ph.total_errors,
                    error_rate=ph.error_rate,
                    avg_latency_ms=ph.avg_latency_ms,
                    memory_bytes=ph.memory_bytes,
                    last_active=ph.last_active.isoformat() if ph.last_active else None,
                    metrics=metrics_summary,
                )
        except Exception as e:
            logger.error(f"Failed to get plugin health for {plugin_id}: {e}")

    raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_id}")


@router.get("/unhealthy", response_model=list[PluginHealthResponse])
async def list_unhealthy_plugins() -> list[PluginHealthResponse]:
    """
    Get list of unhealthy or degraded plugins.

    Returns only plugins that need attention.
    """
    aggregator = _get_metrics_aggregator()
    results: list[PluginHealthResponse] = []

    if aggregator:
        try:
            unhealthy = aggregator.get_unhealthy_plugins()
            for ph in unhealthy:
                results.append(
                    PluginHealthResponse(
                        plugin_id=ph.plugin_id,
                        status=_calculate_health_status(ph.error_rate, ph.crash_count),
                        uptime_seconds=ph.uptime_seconds,
                        total_calls=ph.total_calls,
                        total_errors=ph.total_errors,
                        error_rate=ph.error_rate,
                        avg_latency_ms=ph.avg_latency_ms,
                        memory_bytes=ph.memory_bytes,
                        last_active=ph.last_active.isoformat() if ph.last_active else None,
                    )
                )
        except Exception as e:
            logger.error(f"Failed to get unhealthy plugins: {e}")

    return results


# =============================================================================
# Metrics Endpoints
# =============================================================================


@router.get("/metrics", response_model=MetricsQueryResponse)
async def query_metrics(
    plugin_id: str | None = Query(None, description="Filter by plugin ID"),
    metric_type: str | None = Query(None, description="Filter by metric type"),
    start_time: str | None = Query(None, description="Start time (ISO format)"),
    end_time: str | None = Query(None, description="End time (ISO format)"),
    limit: int = Query(100, ge=1, le=10000, description="Maximum records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
) -> MetricsQueryResponse:
    """
    Query stored metrics with filtering.

    Args:
        plugin_id: Filter by plugin ID
        metric_type: Filter by metric type
        start_time: Start time (ISO format)
        end_time: End time (ISO format)
        limit: Maximum records to return
        offset: Number of records to skip
    """
    persistence = _get_persistence()

    if not persistence:
        return MetricsQueryResponse(count=0, metrics=[], filters={})

    try:
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None

        records = persistence.query_metrics(
            plugin_id=plugin_id,
            metric_type=metric_type,
            start_time=start_dt,
            end_time=end_dt,
            limit=limit,
            offset=offset,
        )

        return MetricsQueryResponse(
            count=len(records),
            metrics=[
                MetricRecord(
                    id=r.id,
                    plugin_id=r.plugin_id,
                    metric_type=r.metric_type,
                    value=r.value,
                    timestamp=r.timestamp.isoformat(),
                    labels=r.labels,
                    session_id=r.session_id,
                )
                for r in records
            ],
            filters={
                "plugin_id": plugin_id,
                "metric_type": metric_type,
                "start_time": start_time,
                "end_time": end_time,
                "limit": limit,
                "offset": offset,
            },
        )
    except Exception as e:
        logger.error(f"Failed to query metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/aggregated")
async def get_aggregated_metrics(
    plugin_id: str | None = Query(None, description="Filter by plugin ID"),
    metric_type: str | None = Query(None, description="Filter by metric type"),
    hours: int = Query(24, ge=1, le=168, description="Hours of history to aggregate"),
) -> dict[str, Any]:
    """
    Get aggregated metrics over time windows.

    Args:
        plugin_id: Filter by plugin ID
        metric_type: Filter by metric type
        hours: Hours of history to aggregate (1-168)
    """
    persistence = _get_persistence()

    if not persistence:
        return {"aggregations": [], "filters": {}}

    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        aggregated = persistence.get_aggregated_metrics(
            plugin_id=plugin_id,
            metric_type=metric_type,
            start_time=start_time,
            end_time=end_time,
        )

        return {
            "aggregations": [agg.to_dict() for agg in aggregated],
            "filters": {
                "plugin_id": plugin_id,
                "metric_type": metric_type,
                "hours": hours,
            },
        }
    except Exception as e:
        logger.error(f"Failed to get aggregated metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/export")
async def export_metrics(
    format: ExportFormat = Query(ExportFormat.JSON, description="Export format"),
    plugin_id: str | None = Query(None, description="Filter by plugin ID"),
    hours: int = Query(24, ge=1, le=168, description="Hours of history to export"),
) -> Response:
    """
    Export metrics in various formats.

    Args:
        format: Export format (json, csv, prometheus)
        plugin_id: Filter by plugin ID
        hours: Hours of history to export
    """
    persistence = _get_persistence()

    if not persistence:
        raise HTTPException(status_code=503, detail="Metrics persistence not available")

    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        if format == ExportFormat.JSON:
            content = persistence.export_json(
                plugin_id=plugin_id,
                start_time=start_time,
                end_time=end_time,
            )
            return Response(content=content, media_type="application/json")

        elif format == ExportFormat.CSV:
            content = persistence.export_csv(
                plugin_id=plugin_id,
                start_time=start_time,
                end_time=end_time,
            )
            return PlainTextResponse(content=content, media_type="text/csv")

        elif format == ExportFormat.PROMETHEUS:
            content = persistence.export_prometheus(
                plugin_id=plugin_id,
                start_time=start_time,
                end_time=end_time,
            )
            return PlainTextResponse(content=content, media_type="text/plain; version=0.0.4")

    except Exception as e:
        logger.error(f"Failed to export metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics/storage", response_model=StorageStats)
async def get_storage_stats() -> StorageStats:
    """
    Get metrics storage statistics.

    Returns information about the metrics database.
    """
    persistence = _get_persistence()

    if not persistence:
        return StorageStats()

    try:
        stats = persistence.get_storage_stats()
        return StorageStats(
            total_records=stats["total_records"],
            file_size_bytes=stats["file_size_bytes"],
            file_size_mb=stats["file_size_mb"],
            date_range=stats["date_range"],
            records_by_plugin=stats["records_by_plugin"],
            records_by_type=stats["records_by_type"],
            retention_policy=stats["retention_policy"],
        )
    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics/prune")
async def prune_old_metrics() -> dict[str, Any]:
    """
    Apply retention policy and prune old metrics.

    Returns the number of records deleted.
    """
    persistence = _get_persistence()

    if not persistence:
        raise HTTPException(status_code=503, detail="Metrics persistence not available")

    try:
        deleted = persistence.apply_retention_policy()
        return {
            "deleted_records": deleted,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to prune metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Audit Endpoints
# =============================================================================


@router.get("/audit", response_model=AuditQueryResponse)
async def query_audit_events(
    plugin_id: str | None = Query(None, description="Filter by plugin ID"),
    event_type: str | None = Query(None, description="Filter by event type"),
    severity: str | None = Query(None, description="Filter by severity"),
    hours: int = Query(24, ge=1, le=168, description="Hours of history"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum events to return"),
) -> AuditQueryResponse:
    """
    Query audit log events.

    Args:
        plugin_id: Filter by plugin ID
        event_type: Filter by event type
        severity: Filter by severity (INFO, WARNING, ERROR)
        hours: Hours of history to query
        limit: Maximum events to return
    """
    audit_logger = _get_audit_logger()

    if not audit_logger:
        return AuditQueryResponse(count=0, events=[], filters={})

    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        events = audit_logger.query_events(
            plugin_id=plugin_id,
            event_type=event_type,
            severity=severity,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

        return AuditQueryResponse(
            count=len(events),
            events=[
                AuditEvent(
                    id=e.id,
                    timestamp=e.timestamp.isoformat(),
                    event_type=(
                        e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type)
                    ),
                    plugin_id=e.plugin_id,
                    severity=e.severity.value if hasattr(e.severity, "value") else str(e.severity),
                    message=e.message,
                    details=e.details or {},
                    actor=e.actor,
                )
                for e in events
            ],
            filters={
                "plugin_id": plugin_id,
                "event_type": event_type,
                "severity": severity,
                "hours": hours,
                "limit": limit,
            },
        )
    except Exception as e:
        logger.error(f"Failed to query audit events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/plugins/{plugin_id}")
async def get_plugin_audit_trail(
    plugin_id: str,
    hours: int = Query(24, ge=1, le=168, description="Hours of history"),
    limit: int = Query(50, ge=1, le=500, description="Maximum events to return"),
) -> AuditQueryResponse:
    """
    Get audit trail for a specific plugin.

    Args:
        plugin_id: Plugin identifier
        hours: Hours of history
        limit: Maximum events to return
    """
    return await query_audit_events(
        plugin_id=plugin_id, event_type=None, severity=None, hours=hours, limit=limit
    )


@router.get("/audit/recent")
async def get_recent_audit_events(
    limit: int = Query(20, ge=1, le=100, description="Number of recent events"),
) -> AuditQueryResponse:
    """
    Get most recent audit events across all plugins.

    Args:
        limit: Number of recent events to return
    """
    return await query_audit_events(
        plugin_id=None, event_type=None, severity=None, hours=24, limit=limit
    )


@router.get("/audit/summary")
async def get_audit_summary(
    hours: int = Query(24, ge=1, le=168, description="Hours of history"),
) -> dict[str, Any]:
    """
    Get summary of audit events.

    Args:
        hours: Hours of history to summarize
    """
    audit_logger = _get_audit_logger()

    if not audit_logger:
        return {
            "total_events": 0,
            "by_severity": {},
            "by_event_type": {},
            "by_plugin": {},
            "hours": hours,
        }

    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        events = audit_logger.query_events(
            start_time=start_time,
            end_time=end_time,
            limit=10000,
        )

        by_severity: dict[str, int] = {}
        by_event_type: dict[str, int] = {}
        by_plugin: dict[str, int] = {}

        for e in events:
            severity_key = e.severity.value if hasattr(e.severity, "value") else str(e.severity)
            by_severity[severity_key] = by_severity.get(severity_key, 0) + 1

            type_key = e.event_type.value if hasattr(e.event_type, "value") else str(e.event_type)
            by_event_type[type_key] = by_event_type.get(type_key, 0) + 1

            if e.plugin_id:
                by_plugin[e.plugin_id] = by_plugin.get(e.plugin_id, 0) + 1

        return {
            "total_events": len(events),
            "by_severity": by_severity,
            "by_event_type": by_event_type,
            "by_plugin": by_plugin,
            "hours": hours,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to get audit summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
