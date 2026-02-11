"""
Engine management and recommendation routes.
Implements IDEA 47: Quality-Based Engine Recommendation System.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.engines.router import router as engine_router_instance
from backend.services.model_preflight import run_preflight

from ..optimization import cache_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/engines", tags=["engines"])

# Get engine router instance
try:
    engine_router = engine_router_instance
    ENGINE_AVAILABLE = True
except Exception as e:
    logger.warning(f"Engine router not available: {e}")
    engine_router = None
    ENGINE_AVAILABLE = False


class PreflightResult(BaseModel):
    """Result of a single engine preflight check."""
    ok: bool
    downloaded: bool = False
    message: Optional[str] = None
    path: Optional[str] = None


class PreflightResponse(BaseModel):
    """Response model for preflight checks."""
    results: Dict[str, PreflightResult]
    all_ready: bool
    ready_count: int
    total_count: int


class EngineRecommendationRequest(BaseModel):
    """Request for engine recommendation."""

    task_type: str = Field(
        default="tts", description="Task type (e.g., 'tts', 'voice_cloning')"
    )
    min_mos_score: Optional[float] = Field(
        default=None, ge=1.0, le=5.0, description="Minimum MOS score required (1.0-5.0)"
    )
    min_similarity: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum similarity required (0.0-1.0)",
    )
    min_naturalness: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum naturalness required (0.0-1.0)",
    )
    prefer_speed: bool = Field(
        default=False, description="If True, prefer faster engines over highest quality"
    )
    quality_tier: Optional[str] = Field(
        default=None,
        description="Quality tier preference: 'fast', 'standard', 'high', 'ultra'",
    )


class EngineQualityEstimate(BaseModel):
    """Quality estimate for an engine."""

    mos_score: Optional[float] = Field(
        default=None, description="Estimated MOS score (1.0-5.0)"
    )
    similarity: Optional[float] = Field(
        default=None, description="Estimated similarity (0.0-1.0)"
    )
    naturalness: Optional[float] = Field(
        default=None, description="Estimated naturalness (0.0-1.0)"
    )
    speed_estimate: Optional[str] = Field(
        default=None, description="Speed estimate (e.g., 'fast', 'medium', 'slow')"
    )


class EngineRecommendation(BaseModel):
    """Engine recommendation result."""

    engine_id: str = Field(description="Engine identifier")
    engine_name: str = Field(description="Display name of the engine")
    recommendation_score: float = Field(
        ge=0.0, le=1.0, description="Recommendation score (0.0-1.0, higher is better)"
    )
    quality_estimate: EngineQualityEstimate = Field(
        description="Estimated quality metrics"
    )
    meets_requirements: bool = Field(
        description="Whether engine meets all minimum requirements"
    )
    reasoning: str = Field(
        description="Explanation for why this engine was recommended"
    )


class EngineRecommendationResponse(BaseModel):
    """Response containing engine recommendations."""

    recommendations: List[EngineRecommendation] = Field(
        description="List of engine recommendations, sorted by score"
    )
    total_engines: int = Field(description="Total number of engines evaluated")
    matching_engines: int = Field(
        description="Number of engines that meet requirements"
    )


@router.get("/list")
@cache_response(ttl=60)  # Cache for 60 seconds (engine list may change)
async def list_engines() -> dict:
    """List all available engines (detailed endpoint)."""
    if not ENGINE_AVAILABLE or not engine_router:
        return {"engines": [], "available": False}

    try:
        engines = engine_router.list_engines()
        return {"engines": engines, "available": True, "count": len(engines)}
    except Exception as e:
        logger.error(f"Error listing engines: {e}")
        return {"engines": [], "available": False, "error": str(e)}


@router.get("")
@cache_response(ttl=60)  # Root listing for host EngineManager compatibility
async def get_engines() -> dict:
    """
    Root engine listing endpoint.

    This provides the same payload shape as `/api/engines/list` so that
    host-side clients (e.g. `EngineManager` in the desktop app) can call
    `GET /api/engines` and receive:
      { "engines": [...], "available": bool, "count": int }.
    """
    return await list_engines()


@router.get("/preflight", response_model=PreflightResponse)
async def preflight(auto_download: bool = True) -> PreflightResponse:
    """
    Run model pre-flight checks (and optional auto-downloads for HF-backed models).

    Returns a summary per engine with paths and download status.
    """
    raw_results = run_preflight(auto_download=auto_download)
    
    # Convert to structured response
    results = {}
    ready_count = 0
    for name, result in raw_results.items():
        if isinstance(result, dict):
            is_ok = result.get("ok", False)
            results[name] = PreflightResult(
                ok=is_ok,
                downloaded=result.get("downloaded", False),
                message=result.get("message"),
                path=result.get("path"),
            )
            if is_ok:
                ready_count += 1
        else:
            # Handle non-dict results
            results[name] = PreflightResult(ok=False, message=str(result))
    
    return PreflightResponse(
        results=results,
        all_ready=ready_count == len(results),
        ready_count=ready_count,
        total_count=len(results),
    )


@router.post("/recommend", response_model=EngineRecommendationResponse)
async def recommend_engine(
    request: EngineRecommendationRequest,
) -> EngineRecommendationResponse:
    """
    Get engine recommendations based on quality requirements.

    Implements IDEA 47: Quality-Based Engine Recommendation System.

    Returns a list of engines sorted by recommendation score, with quality
    estimates and reasoning for each recommendation.
    """
    if not ENGINE_AVAILABLE or not engine_router:
        raise HTTPException(status_code=503, detail="Engine router not available")

    try:
        # Get all available engines for the task type
        available_engines = engine_router.list_engines()
        recommendations = []

        for engine_id in available_engines:
            manifest = engine_router.get_manifest(engine_id)
            if not manifest:
                continue

            # Check task type match
            manifest_type = manifest.get("type", "")
            manifest_subtype = manifest.get("subtype", "")

            # Match task type
            if manifest_type != "audio":
                continue

            if request.task_type == "tts" and manifest_subtype not in [
                "tts",
                "voice_cloning",
            ]:
                continue
            elif (
                request.task_type == "voice_cloning"
                and manifest_subtype != "voice_cloning"
            ):
                continue

            # Get quality features from manifest
            quality_features = manifest.get("quality_features", {})

            # Parse quality estimates
            mos_estimate = None
            similarity_estimate = None
            naturalness_estimate = None
            speed_estimate = None

            # Parse MOS estimate (e.g., "4.5-5.0" -> 4.5)
            if "mos_estimate" in quality_features:
                mos_str = str(quality_features["mos_estimate"])
                try:
                    if "-" in mos_str:
                        mos_estimate = float(mos_str.split("-")[0])
                    else:
                        mos_estimate = float(mos_str)
                except (ValueError, AttributeError):
                    ...

            # Parse similarity estimate
            if "similarity_estimate" in quality_features:
                try:
                    similarity_estimate = float(quality_features["similarity_estimate"])
                except (ValueError, TypeError):
                    ...

            # Parse naturalness estimate
            if "naturalness_estimate" in quality_features:
                try:
                    naturalness_estimate = float(
                        quality_features["naturalness_estimate"]
                    )
                except (ValueError, TypeError):
                    ...

            # Get speed estimate
            speed_estimate = quality_features.get("speed_estimate", "medium")

            # Check if engine meets minimum requirements
            meets_requirements = True
            reasoning_parts = []

            if request.min_mos_score is not None:
                if mos_estimate is None or mos_estimate < request.min_mos_score:
                    meets_requirements = False
                    reasoning_parts.append(
                        f"MOS score {mos_estimate or 'unknown'} below required {request.min_mos_score}"
                    )

            if request.min_similarity is not None:
                if (
                    similarity_estimate is None
                    or similarity_estimate < request.min_similarity
                ):
                    meets_requirements = False
                    reasoning_parts.append(
                        f"Similarity {similarity_estimate or 'unknown'} below required {request.min_similarity}"
                    )

            if request.min_naturalness is not None:
                if (
                    naturalness_estimate is None
                    or naturalness_estimate < request.min_naturalness
                ):
                    meets_requirements = False
                    reasoning_parts.append(
                        f"Naturalness {naturalness_estimate or 'unknown'} below required {request.min_naturalness}"
                    )

            # Calculate recommendation score
            score = 0.0
            score_factors = []

            # Quality tier matching
            if request.quality_tier:
                tier = quality_features.get("quality_tier", "standard")
                if tier == request.quality_tier:
                    score += 0.3
                    score_factors.append(
                        f"Matches quality tier '{request.quality_tier}'"
                    )
                elif tier in ["high", "ultra"] and request.quality_tier in [
                    "high",
                    "ultra",
                ]:
                    score += 0.2
                    score_factors.append(f"High quality tier match")

            # MOS score contribution
            if mos_estimate is not None:
                # Normalize to 0-1 scale (1.0-5.0 -> 0.0-1.0)
                mos_normalized = (mos_estimate - 1.0) / 4.0
                score += mos_normalized * 0.3
                score_factors.append(f"MOS: {mos_estimate:.2f}")

            # Similarity contribution
            if similarity_estimate is not None:
                score += similarity_estimate * 0.2
                score_factors.append(f"Similarity: {similarity_estimate:.2f}")

            # Naturalness contribution
            if naturalness_estimate is not None:
                score += naturalness_estimate * 0.2
                score_factors.append(f"Naturalness: {naturalness_estimate:.2f}")

            # Speed preference
            if request.prefer_speed:
                if speed_estimate in ["fast", "ultra_fast"]:
                    score += 0.2
                    score_factors.append("Fast engine preferred")
                elif speed_estimate in ["slow", "very_slow"]:
                    score -= 0.1
                    score_factors.append("Slower than preferred")
            else:
                # Prefer quality over speed
                if speed_estimate in ["slow", "very_slow"]:
                    score += 0.1
                    score_factors.append("High quality (slower)")

            # Clamp score to 0-1
            score = max(0.0, min(1.0, score))

            # Build reasoning
            if not reasoning_parts:
                reasoning = f"Recommended: {', '.join(score_factors)}"
            else:
                reasoning = f"Does not meet requirements: {'; '.join(reasoning_parts)}"

            recommendations.append(
                EngineRecommendation(
                    engine_id=engine_id,
                    engine_name=manifest.get("name", engine_id),
                    recommendation_score=score,
                    quality_estimate=EngineQualityEstimate(
                        mos_score=mos_estimate,
                        similarity=similarity_estimate,
                        naturalness=naturalness_estimate,
                        speed_estimate=speed_estimate,
                    ),
                    meets_requirements=meets_requirements,
                    reasoning=reasoning,
                )
            )

        # Sort by recommendation score (descending)
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)

        # Count matching engines
        matching_count = sum(1 for r in recommendations if r.meets_requirements)

        return EngineRecommendationResponse(
            recommendations=recommendations,
            total_engines=len(recommendations),
            matching_engines=matching_count,
        )

    except Exception as e:
        logger.error(f"Error getting engine recommendations: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get engine recommendations: {str(e)}"
        )


@router.get("/compare")
@cache_response(ttl=60)  # Cache for 60 seconds (engine comparison may change)
async def compare_engines(
    engines: str = Query(..., description="Comma-separated list of engine IDs"),
    task_type: str = Query(default="tts", description="Task type"),
) -> dict:
    """
    Compare multiple engines side-by-side.

    Returns quality estimates and capabilities for each engine.
    """
    if not ENGINE_AVAILABLE or not engine_router:
        raise HTTPException(status_code=503, detail="Engine router not available")

    try:
        engine_ids = [e.strip() for e in engines.split(",")]
        comparison = []

        for engine_id in engine_ids:
            manifest = engine_router.get_manifest(engine_id)
            if not manifest:
                continue

            quality_features = manifest.get("quality_features", {})

            comparison.append(
                {
                    "engine_id": engine_id,
                    "engine_name": manifest.get("name", engine_id),
                    "quality_features": quality_features,
                    "capabilities": manifest.get("capabilities", []),
                }
            )

        return {"engines": comparison, "count": len(comparison)}

    except Exception as e:
        logger.error(f"Error comparing engines: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to compare engines: {str(e)}"
        )


# Engine Configuration Management Endpoints

try:
    from backend.services.EngineConfigService import get_engine_config_service

    HAS_CONFIG_SERVICE = True
except ImportError:
    HAS_CONFIG_SERVICE = False
    logger.warning("EngineConfigService not available")


class EngineConfigResponse(BaseModel):
    """Response for engine configuration."""

    engine_id: str = Field(description="Engine ID")
    config: Dict[str, Any] = Field(description="Engine configuration")


class GPUSettingsRequest(BaseModel):
    """Request to update GPU settings."""

    enabled: Optional[bool] = Field(None, description="Enable GPU")
    device: Optional[str] = Field(None, description="Device (cuda, cpu, auto)")
    fallback_to_cpu: Optional[bool] = Field(
        None, description="Fallback to CPU if GPU unavailable"
    )
    memory_fraction: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="GPU memory fraction (0.0-1.0)"
    )


class EngineConfigUpdateRequest(BaseModel):
    """Request to update engine configuration."""

    model_paths: Optional[Dict[str, str]] = Field(None, description="Model paths")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Engine parameters")


@router.get("/config")
@cache_response(ttl=300)  # Cache for 5 minutes (config doesn't change often)
async def get_engine_configuration() -> dict:
    """
    Get complete engine configuration.

    Returns:
        Complete engine configuration including defaults, GPU settings, and engine-specific configs
    """
    if not HAS_CONFIG_SERVICE:
        raise HTTPException(
            status_code=503, detail="Engine configuration service not available"
        )

    try:
        config_service = get_engine_config_service()
        config = config_service.get_all_config()
        return config
    except Exception as e:
        logger.error(f"Error getting engine configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get engine configuration: {str(e)}"
        )


@router.get("/config/{engine_id}")
@cache_response(ttl=300)
async def get_engine_config(engine_id: str) -> EngineConfigResponse:
    """
    Get configuration for a specific engine.

    Args:
        engine_id: Engine ID

    Returns:
        Engine configuration
    """
    if not HAS_CONFIG_SERVICE:
        raise HTTPException(
            status_code=503, detail="Engine configuration service not available"
        )

    try:
        config_service = get_engine_config_service()
        config = config_service.get_engine_config(engine_id)
        return EngineConfigResponse(engine_id=engine_id, config=config)
    except Exception as e:
        logger.error(
            f"Error getting engine configuration for {engine_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to get engine configuration: {str(e)}"
        )


@router.put("/config/{engine_id}")
async def update_engine_config(
    engine_id: str, request: EngineConfigUpdateRequest
) -> EngineConfigResponse:
    """
    Update configuration for a specific engine.

    Args:
        engine_id: Engine ID
        request: Configuration update request

    Returns:
        Updated engine configuration
    """
    if not HAS_CONFIG_SERVICE:
        raise HTTPException(
            status_code=503, detail="Engine configuration service not available"
        )

    try:
        config_service = get_engine_config_service()

        # Build update config
        update_config = {}
        if request.model_paths:
            update_config["model_paths"] = request.model_paths
        if request.parameters:
            update_config["parameters"] = request.parameters

        config_service.set_engine_config(engine_id, update_config)
        config = config_service.get_engine_config(engine_id)

        return EngineConfigResponse(engine_id=engine_id, config=config)
    except Exception as e:
        logger.error(
            f"Error updating engine configuration for {engine_id}: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to update engine configuration: {str(e)}"
        )


@router.get("/config/gpu/settings")
@cache_response(ttl=60)
async def get_gpu_settings() -> dict:
    """
    Get global GPU settings.

    Returns:
        GPU settings dictionary
    """
    if not HAS_CONFIG_SERVICE:
        raise HTTPException(
            status_code=503, detail="Engine configuration service not available"
        )

    try:
        config_service = get_engine_config_service()
        gpu_settings = config_service.get_gpu_settings()
        return gpu_settings
    except Exception as e:
        logger.error(f"Error getting GPU settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get GPU settings: {str(e)}"
        )


@router.put("/config/gpu/settings")
async def update_gpu_settings(request: GPUSettingsRequest) -> dict:
    """
    Update global GPU settings.

    Args:
        request: GPU settings update request

    Returns:
        Updated GPU settings
    """
    if not HAS_CONFIG_SERVICE:
        raise HTTPException(
            status_code=503, detail="Engine configuration service not available"
        )

    try:
        config_service = get_engine_config_service()

        # Build update dict (only include non-None values)
        update_settings = {}
        if request.enabled is not None:
            update_settings["enabled"] = request.enabled
        if request.device is not None:
            update_settings["device"] = request.device
        if request.fallback_to_cpu is not None:
            update_settings["fallback_to_cpu"] = request.fallback_to_cpu
        if request.memory_fraction is not None:
            update_settings["memory_fraction"] = request.memory_fraction

        config_service.set_gpu_settings(update_settings)
        gpu_settings = config_service.get_gpu_settings()

        return gpu_settings
    except Exception as e:
        logger.error(f"Error updating GPU settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to update GPU settings: {str(e)}"
        )


@router.get("/config/defaults")
@cache_response(ttl=300)
async def get_default_engines() -> dict:
    """
    Get default engines for each task type.

    Returns:
        Dictionary of task types to default engine IDs
    """
    if not HAS_CONFIG_SERVICE:
        raise HTTPException(
            status_code=503, detail="Engine configuration service not available"
        )

    try:
        config_service = get_engine_config_service()
        defaults = config_service.config.get("defaults", {})
        return {"defaults": defaults}
    except Exception as e:
        logger.error(f"Error getting default engines: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get default engines: {str(e)}"
        )


@router.put("/config/defaults/{task_type}")
async def set_default_engine(task_type: str, engine_id: str) -> dict:
    """
    Set default engine for a task type.

    Args:
        task_type: Task type (e.g., "tts", "image_gen", "video_gen")
        engine_id: Engine ID to set as default

    Returns:
        Updated defaults
    """
    if not HAS_CONFIG_SERVICE:
        raise HTTPException(
            status_code=503, detail="Engine configuration service not available"
        )

    try:
        config_service = get_engine_config_service()
        config_service.set_default_engine(task_type, engine_id)
        defaults = config_service.config.get("defaults", {})
        return {"defaults": defaults}
    except Exception as e:
        logger.error(f"Error setting default engine: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to set default engine: {str(e)}"
        )


@router.post("/config/validate")
async def validate_configuration() -> dict:
    """
    Validate engine configuration.

    Returns:
        Validation result with any errors
    """
    if not HAS_CONFIG_SERVICE:
        raise HTTPException(
            status_code=503, detail="Engine configuration service not available"
        )

    try:
        config_service = get_engine_config_service()
        is_valid, errors = config_service.validate_config()

        return {"valid": is_valid, "errors": errors}
    except Exception as e:
        logger.error(f"Error validating configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to validate configuration: {str(e)}"
        )


# Engine Lifecycle Management


@router.post("/{engine_id}/start")
async def start_engine(engine_id: str, job_id: Optional[str] = None):
    """
    Start an engine instance.
    """
    if not ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Engine system not available")

    try:
        from app.core.runtime.engine_lifecycle import get_lifecycle_manager

        lifecycle = get_lifecycle_manager()

        # Check if engine is registered (or try to register from manifest via router)
        # Note: Ideally engine should be registered. If not, we might need to load it.
        # For now, assume it's registered or we can't start it.

        engine = lifecycle.acquire_engine(engine_id, job_id=job_id, auto_start=True)
        if not engine:
            # Try to register via engine router if not found
            if engine_router:
                manifest = engine_router.get_manifest(engine_id)
                if manifest:
                    lifecycle.register_engine(engine_id, manifest)
                    engine = lifecycle.acquire_engine(
                        engine_id, job_id=job_id, auto_start=True
                    )

        if not engine:
            raise HTTPException(
                status_code=500, detail=f"Failed to acquire/start engine {engine_id}"
            )

        return {"status": "started", "engine_id": engine_id, "port": engine.port}
    except Exception as e:
        logger.error(f"Error starting engine {engine_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start engine: {str(e)}")


@router.post("/{engine_id}/stop")
async def stop_engine(engine_id: str, job_id: Optional[str] = None):
    """
    Stop an engine instance.
    """
    if not ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Engine system not available")

    try:
        from app.core.runtime.engine_lifecycle import get_lifecycle_manager

        lifecycle = get_lifecycle_manager()

        if job_id:
            lifecycle.release_engine(engine_id, job_id)
        else:
            # Administrative stop: request graceful drain.
            # If the engine is leased, it will stop after the lease is released.
            # If unleased, it will drain/stop immediately.
            lifecycle._request_drain(engine_id)  # noqa: SLF001 (internal lifecycle API)
            return {"status": "drain_requested", "engine_id": engine_id}

        return {"status": "released", "engine_id": engine_id, "job_id": job_id}

    except Exception as e:
        logger.error(f"Error stopping engine {engine_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to stop engine: {str(e)}")


@router.get("/{engine_id}/status")
async def get_engine_status(engine_id: str):
    """
    Get engine status.
    """
    if not ENGINE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Engine system not available")

    try:
        from app.core.runtime.engine_lifecycle import EngineState, get_lifecycle_manager

        lifecycle = get_lifecycle_manager()

        state = lifecycle.get_engine_state(engine_id)
        status_str = state.name.lower() if state else "unknown"

        # Map BUSY to RUNNING for frontend compatibility
        if status_str == "busy":
            status_str = "running"

        return {
            "engine_id": engine_id,
            "state": status_str,
            "available": status_str in ["healthy", "idle", "running", "busy"],
        }
    except Exception as e:
        logger.error(f"Error getting engine status {engine_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get engine status: {str(e)}"
        )


@router.get("/{engine_id}/voices")
async def get_engine_voices(engine_id: str):
    """
    Get voices available for an engine.
    """
    if not ENGINE_AVAILABLE or not engine_router:
        return []

    try:
        # Get engine instance
        # Note: We need to use get_engine_stats or similar, or just list voices if engine supports it.
        # engine_router.get_engine returns the engine instance/adapter.

        # Since get_engine might fail if engine is not running/loaded, we might need to load it first.
        # But listing voices shouldn't require starting the engine process if possible (metadata).
        # However, many engines need to be loaded to list voices.

        # We can try to check if engine is running via lifecycle.
        from app.core.runtime.engine_lifecycle import get_lifecycle_manager

        lifecycle = get_lifecycle_manager()

        # If engine is not running, we might check if we can get voices from manifest or cache?
        # Typically engines expose get_voices.

        # Let's try to get it. If it fails, return empty.
        engine = engine_router.get_engine(
            engine_id
        )  # This might start it? No, router usually manages instances.

        if engine and hasattr(engine, "get_voices"):
            return engine.get_voices()

        return []
    except Exception as e:
        logger.error(f"Error getting voices for {engine_id}: {e}")
        return []


class ParameterDefinitionModel(BaseModel):
    """Definition of a single engine parameter."""
    name: str
    display_name: str = ""
    description: str = ""
    type: str  # string, integer, number, boolean, enum, array, object, filepath
    default_value: Optional[Any] = None
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    step: Optional[float] = None
    enum_options: Optional[List[Dict[str, str]]] = None
    group_id: Optional[str] = None
    order: int = 0
    is_advanced: bool = False
    is_required: bool = False


class ParameterGroupModel(BaseModel):
    """Group for organizing parameters in UI."""
    id: str
    display_name: str
    description: str = ""
    order: int = 0
    is_collapsed: bool = False


class EngineParameterSchemaResponse(BaseModel):
    """Response model for engine parameter schema."""
    engine_id: str
    schema_version: str = "1.0"
    parameters: List[ParameterDefinitionModel]
    groups: List[ParameterGroupModel] = []


@router.get("/{engine_id}/schema", response_model=EngineParameterSchemaResponse)
async def get_engine_schema(engine_id: str):
    """
    Get the configuration schema for an engine.
    Used for capability-driven dynamic UI generation.
    """
    import json
    from pathlib import Path

    # Search for engine manifest in known locations
    engine_dirs = [
        Path("engines/audio"),
        Path("engines/video"),
        Path("engines"),
    ]

    manifest = None
    for engine_dir in engine_dirs:
        manifest_path = engine_dir / engine_id / "engine.manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                break
            except Exception as e:
                logger.warning(f"Error reading manifest {manifest_path}: {e}")

    if manifest is None:
        # Try to find by searching all subdirectories
        for engine_dir in engine_dirs:
            if not engine_dir.exists():
                continue
            for subdir in engine_dir.iterdir():
                if subdir.is_dir():
                    manifest_path = subdir / "engine.manifest.json"
                    if manifest_path.exists():
                        try:
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                if data.get("engine_id") == engine_id:
                                    manifest = data
                                    break
                        # ALLOWED: bare except - skip invalid manifests gracefully
                        except Exception:
                            pass
            if manifest:
                break

    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Engine '{engine_id}' not found")

    config_schema = manifest.get("config_schema", {})

    # Convert manifest config_schema to ParameterDefinitionModel list
    parameters = []
    for idx, (param_name, param_def) in enumerate(config_schema.items()):
        if not isinstance(param_def, dict):
            continue

        param_type = param_def.get("type", "string")
        enum_options = None

        if "enum" in param_def:
            enum_options = [
                {"value": str(v), "display_name": str(v)}
                for v in param_def.get("enum", [])
            ]
            param_type = "enum"

        parameters.append(ParameterDefinitionModel(
            name=param_name,
            display_name=param_def.get("display_name", param_name.replace("_", " ").title()),
            description=param_def.get("description", ""),
            type=param_type,
            default_value=param_def.get("default"),
            min_value=param_def.get("minimum"),
            max_value=param_def.get("maximum"),
            step=param_def.get("step"),
            enum_options=enum_options,
            group_id=param_def.get("ui_group"),
            order=param_def.get("ui_order", idx),
            is_advanced=param_def.get("advanced", False),
            is_required=param_def.get("required", False),
        ))

    # Extract groups from parameters
    groups_seen = set()
    groups = []
    for param in parameters:
        if param.group_id and param.group_id not in groups_seen:
            groups_seen.add(param.group_id)
            groups.append(ParameterGroupModel(
                id=param.group_id,
                display_name=param.group_id.replace("_", " ").title(),
                order=len(groups),
            ))

    return EngineParameterSchemaResponse(
        engine_id=engine_id,
        parameters=parameters,
        groups=groups,
    )
