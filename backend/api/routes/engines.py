"""
Engine management and recommendation routes.
Implements IDEA 47: Quality-Based Engine Recommendation System.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.engines.router import router as engine_router_instance

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
    """List all available engines."""
    if not ENGINE_AVAILABLE or not engine_router:
        return {"engines": [], "available": False}

    try:
        engines = engine_router.list_engines()
        return {"engines": engines, "available": True, "count": len(engines)}
    except Exception as e:
        logger.error(f"Error listing engines: {e}")
        return {"engines": [], "available": False, "error": str(e)}


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
                    pass

            # Parse similarity estimate
            if "similarity_estimate" in quality_features:
                try:
                    similarity_estimate = float(quality_features["similarity_estimate"])
                except (ValueError, TypeError):
                    pass

            # Parse naturalness estimate
            if "naturalness_estimate" in quality_features:
                try:
                    naturalness_estimate = float(
                        quality_features["naturalness_estimate"]
                    )
                except (ValueError, TypeError):
                    pass

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
    fallback_to_cpu: Optional[bool] = Field(None, description="Fallback to CPU if GPU unavailable")
    memory_fraction: Optional[float] = Field(None, ge=0.0, le=1.0, description="GPU memory fraction (0.0-1.0)")


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
        raise HTTPException(status_code=503, detail="Engine configuration service not available")
    
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
        raise HTTPException(status_code=503, detail="Engine configuration service not available")
    
    try:
        config_service = get_engine_config_service()
        config = config_service.get_engine_config(engine_id)
        return EngineConfigResponse(engine_id=engine_id, config=config)
    except Exception as e:
        logger.error(f"Error getting engine configuration for {engine_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get engine configuration: {str(e)}"
        )


@router.put("/config/{engine_id}")
async def update_engine_config(
    engine_id: str,
    request: EngineConfigUpdateRequest
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
        raise HTTPException(status_code=503, detail="Engine configuration service not available")
    
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
        logger.error(f"Error updating engine configuration for {engine_id}: {e}", exc_info=True)
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
        raise HTTPException(status_code=503, detail="Engine configuration service not available")
    
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
        raise HTTPException(status_code=503, detail="Engine configuration service not available")
    
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
        raise HTTPException(status_code=503, detail="Engine configuration service not available")
    
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
        raise HTTPException(status_code=503, detail="Engine configuration service not available")
    
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
        raise HTTPException(status_code=503, detail="Engine configuration service not available")
    
    try:
        config_service = get_engine_config_service()
        is_valid, errors = config_service.validate_config()
        
        return {
            "valid": is_valid,
            "errors": errors
        }
    except Exception as e:
        logger.error(f"Error validating configuration: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to validate configuration: {str(e)}"
        )
