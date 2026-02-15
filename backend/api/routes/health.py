"""
Enhanced Health Check Routes

Provides comprehensive health checking for the API and system components.
"""

from __future__ import annotations

import logging
import os
import shutil
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.resilience.health_check import (
    HealthCheckResult,
    HealthStatus,
    get_health_checker,
)
from backend.config.path_config import get_models_path
from backend.services.circuit_breaker import get_engine_breaker_stats
from backend.services.engine_service import get_engine_service
from backend.settings import config

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


def _check_gpu() -> dict[str, Any]:
    """Check GPU availability."""
    try:
        # NOTE: Importing torch (and friends) can hard-crash the process on some machines
        # due to native DLL/ABI mismatches. Keep this check safe-by-default.
        if not config.health.enable_torch_check:
            return {
                "status": "degraded",
                "available": False,
                "message": (
                    "GPU check skipped (set VOICESTUDIO_HEALTH_ENABLE_TORCH=1 "
                    "to enable torch-based GPU detection)"
                ),
            }

        import torch  # type: ignore

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

        return {
            "status": "degraded",
            "available": False,
            "message": "GPU not available, using CPU",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "available": False,
            "error": str(e),
        }


def _check_engines() -> dict[str, Any]:
    """Check engine availability with detailed information (enhanced)."""
    try:
        # Safe engine availability check: enumerate engine manifests
        # without importing engine modules. Importing full engine packages
        # can hard-crash the process on machines with incompatible native
        # dependencies (torch/torchvision/etc.).
        import json
        from pathlib import Path

        repo_root = Path(__file__).resolve().parents[3]
        engines_root = repo_root / "engines"
        manifests = (
            list(engines_root.rglob("engine.manifest.json"))
            if engines_root.exists()
            else []
        )

        engine_ids = []
        for p in manifests[:2000]:
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                engine_id = data.get("engine_id") or data.get("id")
                if engine_id:
                    engine_ids.append(str(engine_id))
            except Exception as e:
                logger.warning(f"Failed to parse engine manifest {p}: {e}")
                continue

        engine_ids = sorted(set(engine_ids))
        return {
            "status": "healthy" if engine_ids else "degraded",
            "available_engines": len(engine_ids),
            "initialized_engines": 0,
            "total_engines": len(engine_ids),
            "engines": engine_ids[:10],
            "initialized": [],
            "message": "Engine availability derived from manifests (safe mode)",
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
async def health_check() -> dict[str, Any]:
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
    except Exception as e:
        logger.debug(f"Failed to collect system metrics: {e}")

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
def simple_health_check() -> dict[str, str]:
    """
    Simple health check endpoint (fast, no detailed checks).

    Returns:
        Simple status
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
    }


def _get_system_metrics() -> dict[str, Any]:
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
        except Exception as e:
            logger.debug(f"Failed to collect network metrics: {e}")

    except Exception as e:
        logger.warning(f"Failed to get system metrics: {e}")
        metrics["error"] = str(e)

    return metrics


def _get_resource_usage() -> dict[str, Any]:
    """Get resource usage information (enhanced)."""
    resources = {}

    # Safe-by-default: avoid importing app.core.* modules that may pull in native ML stacks.
    # These imports can hard-crash the process on some machines due to DLL/ABI mismatches.
    if config.health.safe_mode:
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

        return resources

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

    # Engine performance metrics (via EngineService - ADR-008 compliant)
    try:
        engine_service = get_engine_service()
        metrics = engine_service.get_engine_performance_metrics()
        if "error" not in metrics:
            resources["engine_metrics"] = {
                "summary": metrics.get("summary", {}),
                "total_engines": len(metrics.get("all_stats", [])),
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
async def detailed_health_check() -> dict[str, Any]:
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
async def readiness_check() -> dict[str, Any]:
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

    def _is_healthy(result: Any) -> bool:
        try:
            status = getattr(result, "status", None)
            if status is None:
                return False
            if status == HealthStatus.HEALTHY:
                return True
            value = getattr(status, "value", None)
            return value == HealthStatus.HEALTHY.value
        except Exception as e:
            logger.warning(f"Readiness health check evaluation failed: {e}")
            return False

    critical_healthy = all(
        _is_healthy(
            results.get(
                name,
                HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message="Check not run",
                ),
            )
        )
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


@router.get("/ready")
async def ready_check() -> dict[str, Any]:
    """Alias for readiness check."""
    return await readiness_check()


@router.get("/liveness")
def liveness_check() -> dict[str, Any]:
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


@router.get("/live")
def live_check() -> dict[str, Any]:
    """Alias for liveness check."""
    return liveness_check()


def get_performance_middleware():
    """
    Wrapper for performance monitoring middleware lookup.

    Exposed as a function so unit tests can patch it without importing middleware modules.
    """
    try:
        from backend.api.middleware.performance_monitoring import (
            get_performance_middleware as _get_performance_middleware,
        )  # type: ignore

        return _get_performance_middleware()
    except Exception as e:
        logger.warning(f"Performance middleware unavailable: {e}")
        return None


@router.get("/preflight")
def preflight_check() -> dict[str, Any]:
    """
    Operator-readable preflight report for local-first readiness.

    Validates:
    - storage roots (projects/cache/jobs)
    - model root (VOICESTUDIO_MODELS_PATH)
    - engine config model path consistency
    - audio registry durability path
    - job state persistence path
    - basic native tool presence (ffmpeg)
    """

    def ensure_dir(path: str) -> dict[str, Any]:
        try:
            os.makedirs(path, exist_ok=True)
            # Write test
            test_file = os.path.join(path, ".write_test.tmp")
            with open(test_file, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(test_file)
            return {"ok": True, "path": path}
        except Exception as e:
            return {"ok": False, "path": path, "error": str(e)}

    # Resolve core roots
    from backend.services.AudioArtifactRegistry import get_audio_registry
    from backend.services.ContentAddressedAudioCache import get_audio_cache
    from backend.services.EngineConfigService import get_engine_config_service
    from backend.services.JobStateStore import get_job_state_store
    from backend.services.ProjectStoreService import get_project_store_service

    projects_root = str(get_project_store_service().projects_dir)
    cache_root = str(get_audio_cache().cache_dir)
    model_root = str(get_models_path())
    audio_registry_path = str(get_audio_registry().registry_path)
    jobs_root = str(get_job_state_store("voice_cloning_wizard").jobs_root)

    # Ensure dirs exist / writable
    checks: dict[str, Any] = {
        "projects_root": ensure_dir(projects_root),
        "cache_root": ensure_dir(cache_root),
        "model_root": ensure_dir(model_root),
        "audio_registry_dir": ensure_dir(
            os.path.dirname(audio_registry_path) or cache_root
        ),
        "jobs_root": ensure_dir(jobs_root),
    }

    # EngineConfigService consistency
    try:
        engine_config = get_engine_config_service()
        base_path = engine_config.config.get("model_paths", {}).get("base")
        checks["engine_config"] = {
            "ok": True,
            "model_paths.base": base_path,
            "expected_model_root": model_root,
            "consistent_with_model_root": (
                (os.path.abspath(str(base_path)) == os.path.abspath(str(model_root)))
                if base_path
                else False
            ),
        }
    except Exception as e:
        checks["engine_config"] = {"ok": False, "error": str(e)}

    # XTTS preflight (deps + assets)
    try:
        from backend.services.model_preflight import PreflightError, ensure_xtts

        checks["xtts_v2"] = ensure_xtts(auto_download=False)
    except PreflightError as exc:
        detail = exc.detail
        message = None
        if isinstance(detail, dict):
            msg = detail.get("message")
            if isinstance(msg, str):
                message = msg
        checks["xtts_v2"] = {
            "ok": False,
            "downloaded": False,
            "message": message or str(detail),
            "status_code": exc.status_code,
        }
        if isinstance(detail, dict):
            for key, value in detail.items():
                if key != "message":
                    checks["xtts_v2"][key] = value
    except Exception as e:
        checks["xtts_v2"] = {
            "ok": False,
            "downloaded": False,
            "message": f"{type(e).__name__}: {e}",
            "status_code": 500,
        }

    # So-VITS-SVC preflight (checkpoint + config)
    try:
        from backend.services.model_preflight import PreflightError as PreflightErr
        from backend.services.model_preflight import ensure_sovits

        checks["sovits_svc"] = ensure_sovits(auto_download=False)
    except PreflightErr as exc:
        detail = exc.detail
        message = None
        if isinstance(detail, dict):
            msg = detail.get("message")
            if isinstance(msg, str):
                message = msg
        checks["sovits_svc"] = {
            "ok": False,
            "downloaded": False,
            "message": message or str(detail),
            "status_code": exc.status_code,
        }
        if isinstance(detail, dict):
            for key, value in detail.items():
                if key != "message":
                    checks["sovits_svc"][key] = value
    except Exception as e:
        checks["sovits_svc"] = {
            "ok": False,
            "downloaded": False,
            "message": f"{type(e).__name__}: {e}",
            "status_code": 500,
        }

    # Native tool discovery (report-only; hardening handled in
    # dedicated task)
    ffmpeg_env = os.getenv("VOICESTUDIO_FFMPEG_PATH")
    ffmpeg = (
        ffmpeg_env
        if (ffmpeg_env and os.path.exists(ffmpeg_env))
        else shutil.which("ffmpeg")
    )
    checks["ffmpeg"] = {
        "ok": bool(ffmpeg),
        "path": ffmpeg or None,
        "message": (
            "ffmpeg found"
            if ffmpeg
            else (
                "ffmpeg not found (set VOICESTUDIO_FFMPEG_PATH or "
                "install ffmpeg on PATH)"
            )
        ),
    }

    overall_ok = all(v.get("ok", False) for v in checks.values() if isinstance(v, dict))
    return {
        "ok": overall_ok,
        "timestamp": datetime.utcnow().isoformat(),
        "env": {
            "VOICESTUDIO_MODELS_PATH": os.getenv("VOICESTUDIO_MODELS_PATH"),
            "VOICESTUDIO_PROJECTS_DIR": os.getenv("VOICESTUDIO_PROJECTS_DIR"),
            "VOICESTUDIO_CACHE_DIR": os.getenv("VOICESTUDIO_CACHE_DIR"),
            "VOICESTUDIO_JOBS_DIR": os.getenv("VOICESTUDIO_JOBS_DIR"),
            "HF_HOME": os.getenv("HF_HOME"),
            "HUGGINGFACE_HUB_CACHE": os.getenv("HUGGINGFACE_HUB_CACHE"),
            "TRANSFORMERS_CACHE": os.getenv("TRANSFORMERS_CACHE"),
            "HF_DATASETS_CACHE": os.getenv("HF_DATASETS_CACHE"),
            "TTS_HOME": os.getenv("TTS_HOME"),
            "TORCH_HOME": os.getenv("TORCH_HOME"),
        },
        "checks": checks,
    }


@router.get("/resources")
@cache_response(ttl=5)  # Cache for 5 seconds
def resource_usage() -> dict[str, Any]:
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
@cache_response(ttl=10)  # Cache for 10 seconds
def engine_health() -> dict[str, Any]:
    """
    Get detailed engine availability and health information.

    Returns:
        Engine availability, status, and statistics
    """
    engine_info = _check_engines()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        **engine_info,
    }


@router.get("/circuit-breakers")
@cache_response(ttl=5)
def circuit_breaker_health() -> dict[str, Any]:
    """
    Get circuit breaker status for all engines (TD-014).

    Returns per-engine breaker state (closed/open/half_open), failure counts,
    and blocked request counts for monitoring and debugging.
    """
    try:
        stats = get_engine_breaker_stats()
        breakers = {}
        for name, s in stats.items():
            breakers[name] = {
                "name": s.name,
                "state": s.state.name,
                "failure_count": s.failure_count,
                "success_count": s.success_count,
                "last_failure_time": s.last_failure_time,
                "last_success_time": s.last_success_time,
                "open_count": s.open_count,
                "total_calls": s.total_calls,
                "total_failures": s.total_failures,
                "total_blocked": s.total_blocked,
            }
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "breakers": breakers,
        }
    except Exception as e:
        logger.warning("Failed to get circuit breaker stats: %s", e)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "breakers": {},
            "error": str(e),
        }


@router.get("/performance")
def performance_metrics() -> dict[str, Any]:
    """
    Get API endpoint performance metrics.

    Returns:
        Comprehensive performance metrics including:
        - Overall statistics
        - Top endpoints by time, calls, average time, error rate
        - Per-endpoint metrics
    """
    try:
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
                "message": ("Performance monitoring middleware not initialized"),
            }
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get performance metrics: {e!s}",
        )


@router.get("/performance/{endpoint:path}")
def endpoint_performance_metrics(endpoint: str) -> dict[str, Any]:
    """
    Get performance metrics for a specific endpoint.

    Args:
        endpoint: Endpoint key (format: METHOD:PATH)

    Returns:
        Detailed metrics for the specified endpoint
    """
    try:
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
            detail=f"Failed to get endpoint metrics: {e!s}",
        )


@router.get("/features")
@cache_response(ttl=30)
async def get_feature_status() -> dict[str, Any]:
    """
    Get feature availability status for frontend display.

    Reports which features are fully functional vs running in placeholder mode.
    This enables graceful UI degradation when models are not loaded.

    Architecture note (GAP-ARCH-001): This endpoint uses a service layer abstraction
    rather than direct engine imports to maintain API-Engine boundary separation.

    Returns:
        Feature status dictionary with:
        - feature name
        - availability (fully_functional, placeholder, unavailable)
        - message explaining status
    """
    from backend.services.feature_status_service import get_all_feature_statuses

    features = await get_all_feature_statuses()

    # Lip sync
    try:
        from backend.services.lip_sync_service import LipSyncService
        LipSyncService()
        # LipSyncService uses multiple backends; check if any are available
        features["lip_sync"] = {
            "status": "placeholder",  # Most installations won't have these models
            "message": "Lip sync uses fallback mode - Wav2Lip/SadTalker not loaded",
            "requires_model": True,
        }
    except Exception as e:
        features["lip_sync"] = {
            "status": "unavailable",
            "message": f"Lip sync service unavailable: {e!s}",
            "requires_model": True,
        }

    # TTS (core functionality - should always be available)
    try:
        engine_service = get_engine_service()
        engines = engine_service.list_engines()
        tts_engines = [e for e in engines if e.get("type") == "tts"]
        features["text_to_speech"] = {
            "status": "fully_functional" if tts_engines else "unavailable",
            "message": f"{len(tts_engines)} TTS engines available" if tts_engines
                       else "No TTS engines loaded",
            "requires_model": True,
            "available_engines": [e.get("id") for e in tts_engines[:5]],
        }
    except Exception as e:
        features["text_to_speech"] = {
            "status": "unavailable",
            "message": f"TTS engine unavailable: {e!s}",
            "requires_model": True,
        }

    # Count status summary
    summary = {
        "fully_functional": sum(1 for f in features.values() if f.get("status") == "fully_functional"),
        "placeholder": sum(1 for f in features.values() if f.get("status") == "placeholder"),
        "unavailable": sum(1 for f in features.values() if f.get("status") == "unavailable"),
        "total": len(features),
    }

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "features": features,
        "summary": summary,
    }
