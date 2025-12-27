"""
Enhanced Health Check Routes

Provides comprehensive health checking for the API and system components.
"""

import logging
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.core.resilience.health_check import (
    HealthCheckResult,
    HealthStatus,
    get_health_checker,
)

from ..optimization import cache_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["health"])


# Create main health checker
_health_checker = get_health_checker("api", timeout=5.0)


def _check_database() -> bool:
    """Check database connectivity."""
    try:
        # Try to import and check database
        from app.core.security.database import WatermarkDatabase

        _ = WatermarkDatabase()
        # Simple check - try to query
        return True
    except Exception as e:
        logger.warning(f"Database health check failed: {e}")
        return False


def _check_gpu() -> Dict[str, Any]:
    """Check GPU availability."""
    try:
        import torch

        if torch.cuda.is_available():
            return {
                "status": "healthy",
                "available": True,
                "device_count": torch.cuda.device_count(),
                "device_name": (
                    torch.cuda.get_device_name(0)
                    if torch.cuda.device_count() > 0
                    else None
                ),
            }
        else:
            return {
                "status": "degraded",
                "available": False,
                "message": "GPU not available, using CPU",
            }
    except ImportError:
        return {
            "status": "degraded",
            "available": False,
            "message": "PyTorch not installed",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "available": False,
            "error": str(e),
        }


def _check_engines() -> Dict[str, Any]:
    """Check engine availability with detailed information (enhanced)."""
    try:
        from app.core.engines.router import EngineRouter

        router = EngineRouter()
        engines = router.list_engines()
        stats = router.get_engine_stats()

        # Get initialized engines with details
        initialized_engines = []
        engine_details = {}
        for name, engine_info in stats.get("engines", {}).items():
            if engine_info.get("initialized", False):
                initialized_engines.append(name)
                engine_details[name] = {
                    "initialized": True,
                    "memory_usage_mb": engine_info.get("memory_usage_mb", 0.0),
                    "gpu_memory_mb": engine_info.get("gpu_memory_mb", 0.0),
                }

        # Get engine performance metrics
        try:
            from app.core.engines.performance_metrics import get_engine_metrics

            metrics = get_engine_metrics()
            all_stats = metrics.get_all_stats()
            for engine_name, engine_stats in all_stats.items():
                if engine_name not in engine_details:
                    engine_details[engine_name] = {}
                engine_details[engine_name]["performance"] = {
                    "avg_synthesis_time_ms": engine_stats.get(
                        "avg_synthesis_time_ms", 0.0
                    ),
                    "total_syntheses": engine_stats.get("total_syntheses", 0),
                    "cache_hit_rate": engine_stats.get("cache_hit_rate", 0.0),
                    "error_rate": engine_stats.get("error_rate", 0.0),
                }
        except Exception as e:
            logger.debug(f"Failed to get engine performance metrics: {e}")

        return {
            "status": "healthy",
            "available_engines": len(engines),
            "initialized_engines": len(initialized_engines),
            "total_engines": len(engines),
            "engines": engines[:10],  # First 10 engines
            "initialized": initialized_engines[:10],
            "memory_usage_mb": stats.get("total_memory_usage_mb", 0.0),
            "gpu_memory_usage_mb": stats.get("total_gpu_memory_usage_mb", 0.0),
            "system_memory_pressure": stats.get("system_memory_pressure", False),
            "engine_details": {
                k: v for k, v in list(engine_details.items())[:10]
            },  # First 10 engine details
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
        }


# Register health checks
_health_checker.register_check("database", _check_database, critical=True)
_health_checker.register_check(
    "gpu", lambda: _check_gpu()["status"] == "healthy", critical=False
)
_health_checker.register_check(
    "engines", lambda: _check_engines()["status"] == "healthy", critical=False
)


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.

    Returns:
        Health status with detailed information including:
        - System health checks
        - Resource usage
        - Engine availability
        - Component status
    """
    results = await _health_checker.run_all_checks()
    overall_status = _health_checker.get_overall_status()

    # Get detailed information
    details = {}

    # Database
    db_result = results.get("database")
    if db_result:
        details["database"] = {
            "status": db_result.status.value,
            "message": db_result.message,
            "response_time_ms": db_result.response_time_ms,
        }

    # GPU
    try:
        gpu_info = _check_gpu()
        details["gpu"] = gpu_info
    except Exception as e:
        details["gpu"] = {"status": "unknown", "error": str(e)}

    # Engines
    try:
        engine_info = _check_engines()
        details["engines"] = engine_info
    except Exception as e:
        details["engines"] = {"status": "unknown", "error": str(e)}

    # System metrics (lightweight)
    try:
        import os

        import psutil

        process = psutil.Process(os.getpid())
        details["system"] = {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
        }
    except Exception:
        pass

    # Resource usage summary
    try:
        resource_summary = _get_resource_usage()
        details["resources"] = {
            "gpu": resource_summary.get("gpu", {}),
            "tasks": {
                "active": resource_summary.get("tasks", {}).get("active_tasks", 0),
                "running": resource_summary.get("tasks", {}).get("running_tasks", 0),
            },
            "validation": {
                "cache_size": resource_summary.get("validation", {})
                .get("schema_cache_stats", {})
                .get("cache_size", 0),
            },
        }
    except Exception as e:
        logger.debug(f"Failed to get resource summary: {e}")

    return {
        "status": overall_status.value,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            name: {
                "status": result.status.value,
                "message": result.message,
                "response_time_ms": result.response_time_ms,
            }
            for name, result in results.items()
        },
        "details": details,
    }


@router.get("/simple")
def simple_health_check() -> Dict[str, str]:
    """
    Simple health check endpoint (fast, no detailed checks).

    Returns:
        Simple status
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }


def _get_system_metrics() -> Dict[str, Any]:
    """Get comprehensive system metrics."""
    metrics = {}
    try:
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Process metrics
        process_info = process.as_dict(
            attrs=["cpu_percent", "memory_info", "memory_percent", "num_threads"]
        )
        metrics["process"] = {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_mb": process_info["memory_info"].rss / 1024 / 1024,
            "memory_percent": process_info.get("memory_percent", 0.0),
            "num_threads": process_info.get("num_threads", 0),
        }

        # System-wide metrics
        metrics["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
            "memory_available_gb": psutil.virtual_memory().available / (1024**3),
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
            "memory_percent": psutil.virtual_memory().percent,
        }

        # Disk metrics
        disk = psutil.disk_usage("/")
        metrics["disk"] = {
            "total_gb": disk.total / (1024**3),
            "used_gb": disk.used / (1024**3),
            "free_gb": disk.free / (1024**3),
            "percent": (disk.used / disk.total) * 100,
        }

        # Network metrics (if available)
        try:
            net_io = psutil.net_io_counters()
            metrics["network"] = {
                "bytes_sent_mb": net_io.bytes_sent / (1024**2),
                "bytes_recv_mb": net_io.bytes_recv / (1024**2),
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            }
        except Exception:
            pass

    except Exception as e:
        logger.warning(f"Failed to get system metrics: {e}")
        metrics["error"] = str(e)

    return metrics


def _get_resource_usage() -> Dict[str, Any]:
    """Get resource usage information (enhanced)."""
    resources = {}

    # GPU information
    try:
        from app.core.runtime.resource_manager import ResourceManager

        resource_manager = ResourceManager()
        gpu_monitor = getattr(resource_manager, "gpu_monitor", None)
        if gpu_monitor:
            resources["gpu"] = gpu_monitor.get_gpu_info()
            resources["vram"] = gpu_monitor.get_vram_info()
    except Exception as e:
        logger.debug(f"Failed to get GPU info: {e}")
        resources["gpu"] = {"available": False, "error": str(e)}

    # Task scheduler statistics
    try:
        from app.core.tasks.scheduler import get_scheduler

        scheduler = get_scheduler()
        resources["tasks"] = scheduler.get_stats()
    except Exception as e:
        logger.debug(f"Failed to get task scheduler stats: {e}")

    # Validation optimizer statistics
    try:
        from backend.api.validation_optimizer import (
            get_cache_stats,
            get_validation_stats,
        )

        resources["validation"] = {
            "cache_stats": get_cache_stats(),
            "validation_stats": get_validation_stats(),
        }
    except Exception as e:
        logger.debug(f"Failed to get validation optimizer stats: {e}")

    # Database connection pool statistics
    try:
        from app.core.database.query_optimizer import DatabaseQueryOptimizer

        # Use default database path
        db_path = ":memory:"  # Default SQLite in-memory
        optimizer = DatabaseQueryOptimizer(db_path=db_path)
        resources["database"] = optimizer.get_query_stats()
    except Exception as e:
        logger.debug(f"Failed to get database pool stats: {e}")

    # WebSocket connection statistics
    try:
        from backend.api.ws.realtime import get_connection_stats

        resources["websocket"] = get_connection_stats()
    except Exception as e:
        logger.debug(f"Failed to get WebSocket stats: {e}")

    # Engine performance metrics
    try:
        from app.core.engines.performance_metrics import get_engine_metrics

        metrics = get_engine_metrics()
        resources["engine_metrics"] = {
            "summary": metrics.get_summary(),
            "total_engines": len(metrics.get_all_stats()),
        }
    except Exception as e:
        logger.debug(f"Failed to get engine performance metrics: {e}")

    # API endpoint performance metrics
    try:
        from backend.api.middleware.performance_monitoring import (
            get_performance_middleware,
        )

        middleware = get_performance_middleware()
        if middleware:
            resources["api_performance"] = middleware.get_stats()
    except Exception as e:
        logger.debug(f"Failed to get API performance metrics: {e}")

    # Temp file manager statistics
    try:
        from app.core.utils.temp_file_manager import get_temp_file_manager

        temp_manager = get_temp_file_manager()
        stats = temp_manager.get_stats()
        resources["temp_files"] = {
            "active_files": stats.get("total_files", 0),
            "total_size_mb": stats.get("total_size_mb", 0.0),
        }
    except Exception as e:
        logger.debug(f"Failed to get temp file manager stats: {e}")

    return resources


@router.get("/detailed")
async def detailed_health_check() -> Dict[str, Any]:
    """
    Detailed health check with all system information.

    Returns:
        Detailed health information including system metrics,
        resource usage, and component status
    """
    results = await _health_checker.run_all_checks()
    overall_status = _health_checker.get_overall_status()

    # Get comprehensive system metrics
    system_metrics = _get_system_metrics()

    # Get resource usage
    resource_usage = _get_resource_usage()

    # Enhanced engine information
    engine_info = _check_engines()

    return {
        "status": overall_status.value,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {
            name: {
                "status": result.status.value,
                "message": result.message,
                "response_time_ms": result.response_time_ms,
                "error": result.error,
                "details": result.details,
            }
            for name, result in results.items()
        },
        "system": system_metrics,
        "resources": resource_usage,
        "engines": engine_info,
    }


@router.get("/readiness")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check (for Kubernetes, etc.).

    Returns:
        Readiness status
    """
    results = await _health_checker.run_all_checks()

    # Only check critical services for readiness
    # Get critical check names from registered checks
    critical_check_names = []
    for name, check_info in _health_checker.checks.items():
        if isinstance(check_info, dict) and check_info.get("critical", False):
            critical_check_names.append(name)

    critical_healthy = all(
        results.get(
            name,
            HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message="Check not run",
            ),
        ).status
        == HealthStatus.HEALTHY
        for name in critical_check_names
    )

    if critical_healthy:
        return {
            "ready": True,
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
        }
    else:
        raise HTTPException(
            status_code=503, detail="Service not ready - critical checks failed"
        )


@router.get("/liveness")
def liveness_check() -> Dict[str, str]:
    """
    Liveness check (for Kubernetes, etc.).

    Returns:
        Liveness status
    """
    return {
        "alive": True,
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/resources")
@cache_response(ttl=5)  # Cache for 5 seconds (resource usage changes frequently)
def resource_usage() -> Dict[str, Any]:
    """
    Get detailed resource usage information.

    Returns:
        Comprehensive resource usage metrics including:
        - System resources (CPU, memory, disk, network)
        - GPU/VRAM information
        - Task scheduler statistics
        - Validation optimizer statistics
        - Database connection pool statistics
        - WebSocket connection statistics
    """
    system_metrics = _get_system_metrics()
    resource_usage = _get_resource_usage()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system": system_metrics,
        "resources": resource_usage,
    }


@router.get("/engines")
@cache_response(ttl=10)  # Cache for 10 seconds (engine health changes moderately)
def engine_health() -> Dict[str, Any]:
    """
    Get detailed engine availability and health information.

    Returns:
        Engine availability, status, and statistics
    """
    engine_info = _check_engines()

    # Get additional engine statistics
    try:
        from app.core.engines.router import EngineRouter

        router = EngineRouter()
        stats = router.get_engine_stats()
        engine_info["statistics"] = {
            "total_engines": stats.get("total_engines", 0),
            "initialized_engines": stats.get("initialized_engines", 0),
            "total_memory_usage_mb": stats.get("total_memory_usage_mb", 0.0),
        }
    except Exception as e:
        logger.debug(f"Failed to get engine statistics: {e}")

    return {
        "timestamp": datetime.utcnow().isoformat(),
        **engine_info,
    }


@router.get("/performance")
@cache_response(ttl=10)  # Cache for 10 seconds (performance metrics change moderately)
def performance_metrics() -> Dict[str, Any]:
    """
    Get API endpoint performance metrics.

    Returns:
        Comprehensive performance metrics including:
        - Overall statistics
        - Top endpoints by time, calls, average time, error rate
        - Per-endpoint metrics
    """
    try:
        from backend.api.middleware.performance_monitoring import (
            get_performance_middleware,
        )

        middleware = get_performance_middleware()
        if middleware:
            stats = middleware.get_stats()
            return {
                "timestamp": datetime.utcnow().isoformat(),
                **stats,
            }
        else:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "enabled": False,
                "message": "Performance monitoring middleware not initialized",
            }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get performance metrics: {str(e)}"
        )


@router.get("/performance/{endpoint:path}")
def endpoint_performance_metrics(endpoint: str) -> Dict[str, Any]:
    """
    Get performance metrics for a specific endpoint.

    Args:
        endpoint: Endpoint key (format: METHOD:PATH)

    Returns:
        Detailed metrics for the specified endpoint
    """
    try:
        from backend.api.middleware.performance_monitoring import (
            get_performance_middleware,
        )

        middleware = get_performance_middleware()
        if middleware:
            metrics = middleware.get_metrics(endpoint)
            if metrics:
                return {
                    "timestamp": datetime.utcnow().isoformat(),
                    "endpoint": endpoint,
                    **metrics,
                }
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Metrics not found for endpoint: {endpoint}",
                )
        else:
            raise HTTPException(
                status_code=503,
                detail="Performance monitoring middleware not initialized",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get endpoint performance metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get endpoint metrics: {str(e)}",
        )
