"""
Monitoring and Metrics Routes

Provides API endpoints for metrics, error tracking, and monitoring data.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter

from app.core.monitoring.error_tracking import get_error_tracker
from app.core.monitoring.metrics import get_metrics_collector

from ..optimization import cache_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/metrics")
@cache_response(ttl=5)  # Cache for 5 seconds (metrics change frequently)
def get_metrics() -> Dict[str, Any]:
    """
    Get all metrics.

    Returns:
        All collected metrics
    """
    collector = get_metrics_collector()
    return collector.get_all_metrics()


@router.get("/metrics/counters")
@cache_response(ttl=5)  # Cache for 5 seconds (counters change frequently)
def get_counters() -> Dict[str, float]:
    """
    Get all counter metrics.

    Returns:
        Counter metrics
    """
    collector = get_metrics_collector()
    return {name: collector.get_counter(name) for name in collector.counters.keys()}


@router.get("/metrics/gauges")
@cache_response(ttl=5)  # Cache for 5 seconds (gauges change frequently)
def get_gauges() -> Dict[str, float]:
    """
    Get all gauge metrics.

    Returns:
        Gauge metrics
    """
    collector = get_metrics_collector()
    return {
        name: collector.get_gauge(name)
        for name in collector.gauges.keys()
        if collector.get_gauge(name) is not None
    }


@router.get("/metrics/timers/{name}")
@cache_response(ttl=5)  # Cache for 5 seconds (timer stats change frequently)
def get_timer_stats(name: str) -> Dict[str, float]:
    """
    Get timer statistics.

    Args:
        name: Timer name

    Returns:
        Timer statistics
    """
    collector = get_metrics_collector()
    stats = collector.get_timer_stats(name)
    if stats is None:
        return {"error": f"Timer '{name}' not found"}
    return stats


@router.get("/metrics/histograms/{name}")
@cache_response(ttl=5)  # Cache for 5 seconds (histogram stats change frequently)
def get_histogram_stats(name: str) -> Dict[str, float]:
    """
    Get histogram statistics.

    Args:
        name: Histogram name

    Returns:
        Histogram statistics
    """
    collector = get_metrics_collector()
    stats = collector.get_histogram_stats(name)
    if stats is None:
        return {"error": f"Histogram '{name}' not found"}
    return stats


@router.post("/metrics/clear")
def clear_metrics() -> Dict[str, str]:
    """
    Clear all metrics.

    Returns:
        Success message
    """
    collector = get_metrics_collector()
    collector.clear()
    return {"message": "Metrics cleared"}


@router.get("/errors")
@cache_response(ttl=10)  # Cache for 10 seconds (errors may accumulate)
def get_errors() -> Dict[str, Any]:
    """
    Get error summary.

    Returns:
        Error summary
    """
    tracker = get_error_tracker()
    return tracker.get_error_summary()


@router.get("/errors/{error_type}")
@cache_response(ttl=10)  # Cache for 10 seconds (errors may accumulate)
def get_errors_by_type(error_type: str) -> Dict[str, Any]:
    """
    Get errors by type.

    Args:
        error_type: Error type name

    Returns:
        Errors of specified type
    """
    tracker = get_error_tracker()
    errors = tracker.get_errors_by_type(error_type)

    return {
        "error_type": error_type,
        "count": len(errors),
        "errors": [
            {
                "message": err.message,
                "severity": err.severity.value,
                "count": err.count,
                "first_occurrence": err.first_occurrence.isoformat(),
                "last_occurrence": err.last_occurrence.isoformat(),
            }
            for err in errors
        ],
    }


@router.post("/errors/clear")
def clear_errors() -> Dict[str, str]:
    """
    Clear all error records.

    Returns:
        Success message
    """
    tracker = get_error_tracker()
    tracker.clear()
    return {"message": "Errors cleared"}
