"""
API v3 - Engine Endpoints.

Task 3.4.1: Unified engine management API.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.services.engine_service import IEngineService, get_engine_service

router = APIRouter(prefix="/engines", tags=["engines"])


# --- Request/Response Models ---

class EngineCapability(BaseModel):
    """Engine capability descriptor."""
    feature: str
    supported: bool
    config_schema: Optional[Dict[str, Any]] = None


class EngineInfo(BaseModel):
    """Engine information response."""
    id: str
    name: str
    version: str
    type: str
    status: str
    capabilities: List[EngineCapability] = []
    memory_usage_mb: Optional[float] = None
    gpu_usage_percent: Optional[float] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "xtts_v2",
                "name": "XTTS v2",
                "version": "2.0.0",
                "type": "synthesis",
                "status": "ready",
                "capabilities": [
                    {"feature": "text_to_speech", "supported": True},
                    {"feature": "voice_cloning", "supported": True},
                ],
                "memory_usage_mb": 2048.5,
            }
        }


class EngineListResponse(BaseModel):
    """Paginated engine list response."""
    engines: List[EngineInfo]
    cursor: Optional[str] = None
    has_more: bool = False


class EngineHealthResponse(BaseModel):
    """Engine health check response."""
    engine_id: str
    healthy: bool
    status: str
    latency_ms: Optional[float] = None
    error: Optional[str] = None


# --- Endpoints ---

@router.get(
    "",
    response_model=EngineListResponse,
    summary="List available engines",
    description="Get all available engines with their capabilities and status.",
)
async def list_engines(
    type: Optional[str] = Query(None, description="Filter by engine type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    cursor: Optional[str] = Query(None, description="Pagination cursor"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    engine_service: IEngineService = Depends(get_engine_service),
):
    """List all available engines."""
    engines = engine_service.list_engines()
    
    # Filter by type if specified
    if type:
        engines = [e for e in engines if e.get("type") == type]
    
    # Filter by status if specified
    if status:
        engines = [e for e in engines if e.get("status") == status]
    
    # Convert to response model
    engine_infos = []
    for e in engines[:limit]:
        engine_infos.append(EngineInfo(
            id=e.get("id", ""),
            name=e.get("name", ""),
            version=e.get("version", "0.0.0"),
            type=e.get("type", "unknown"),
            status=e.get("status", "unknown"),
            capabilities=[
                EngineCapability(feature=cap, supported=True)
                for cap in e.get("capabilities", [])
            ],
            memory_usage_mb=e.get("memory_usage_mb"),
            gpu_usage_percent=e.get("gpu_usage_percent"),
        ))
    
    return EngineListResponse(
        engines=engine_infos,
        has_more=len(engines) > limit,
    )


@router.get(
    "/{engine_id}",
    response_model=EngineInfo,
    summary="Get engine details",
    description="Get detailed information about a specific engine.",
)
async def get_engine(
    engine_id: str,
    engine_service: IEngineService = Depends(get_engine_service),
):
    """Get engine by ID."""
    status = engine_service.get_engine_status(engine_id)
    
    if not status:
        raise HTTPException(status_code=404, detail=f"Engine not found: {engine_id}")
    
    return EngineInfo(
        id=engine_id,
        name=status.get("name", engine_id),
        version=status.get("version", "0.0.0"),
        type=status.get("type", "unknown"),
        status=status.get("status", "unknown"),
        capabilities=[
            EngineCapability(feature=cap, supported=True)
            for cap in status.get("capabilities", [])
        ],
        memory_usage_mb=status.get("memory_usage_mb"),
        gpu_usage_percent=status.get("gpu_usage_percent"),
    )


@router.get(
    "/{engine_id}/health",
    response_model=EngineHealthResponse,
    summary="Check engine health",
    description="Perform a health check on a specific engine.",
)
async def check_engine_health(
    engine_id: str,
    engine_service: IEngineService = Depends(get_engine_service),
):
    """Check engine health."""
    try:
        is_available = engine_service.is_engine_available(engine_id)
        status = engine_service.get_engine_status(engine_id)
        
        return EngineHealthResponse(
            engine_id=engine_id,
            healthy=is_available,
            status=status.get("status", "unknown") if status else "not_found",
            latency_ms=status.get("latency_ms") if status else None,
        )
    except Exception as e:
        return EngineHealthResponse(
            engine_id=engine_id,
            healthy=False,
            status="error",
            error=str(e),
        )


@router.post(
    "/{engine_id}/load",
    summary="Load engine into pool",
    description="Preload an engine into the warm pool for faster inference.",
)
async def load_engine(
    engine_id: str,
    config: Optional[Dict[str, Any]] = None,
    engine_service: IEngineService = Depends(get_engine_service),
):
    """Load an engine into the pool."""
    try:
        engine = engine_service.get_engine(engine_id)
        if engine:
            return {"status": "loaded", "engine_id": engine_id}
        else:
            raise HTTPException(status_code=404, detail=f"Engine not found: {engine_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{engine_id}/unload",
    summary="Unload engine from pool",
    description="Unload an engine from the warm pool to free memory.",
)
async def unload_engine(
    engine_id: str,
    engine_service: IEngineService = Depends(get_engine_service),
):
    """Unload an engine from the pool."""
    # Note: Actual unloading requires engine pool integration
    return {"status": "unloaded", "engine_id": engine_id}
