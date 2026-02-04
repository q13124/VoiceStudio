"""
FastAPI Dependency Injection Wrappers (Phase 2.3)

Provides type-safe dependency injection for services using FastAPI's Depends() pattern.
This improves testability by allowing services to be easily mocked in tests.

Usage:
    from backend.api.deps import EngineServiceDep, EngineConfigServiceDep, AudioRegistryDep

    @router.get("/engines")
    async def list_engines(engine_service: EngineServiceDep):
        return engine_service.list_engines()

    @router.get("/engines/config")
    async def get_config(config_service: EngineConfigServiceDep):
        return config_service.get_default_engine("tts")
"""

from typing import Annotated

from fastapi import Depends


# EngineConfigService dependency (for engine configuration, defaults, etc.)
# VS-0038 fix: Renamed from EngineServiceDep to avoid confusion
def get_engine_config_service_dep():
    """Get the EngineConfigService singleton."""
    from backend.services.EngineConfigService import get_engine_config_service
    return get_engine_config_service()


try:
    from backend.services.EngineConfigService import EngineConfigService
    EngineConfigServiceDep = Annotated[EngineConfigService, Depends(get_engine_config_service_dep)]
except ImportError:
    EngineConfigServiceDep = None


# EngineService dependency (for list_engines, get_engine, etc.)
# VS-0038 fix: Added proper EngineService dependency
def get_engine_service_dep():
    """Get the EngineService singleton."""
    from backend.services.engine_service import get_engine_service
    return get_engine_service()


try:
    from backend.services.engine_service import IEngineService
    EngineServiceDep = Annotated[IEngineService, Depends(get_engine_service_dep)]
except ImportError:
    EngineServiceDep = None


# AudioArtifactRegistry dependency
def get_audio_registry_dep():
    """Get the AudioArtifactRegistry singleton."""
    from backend.services.AudioArtifactRegistry import get_audio_registry
    return get_audio_registry()


try:
    from backend.services.AudioArtifactRegistry import AudioArtifactRegistry
    AudioRegistryDep = Annotated[AudioArtifactRegistry, Depends(get_audio_registry_dep)]
except ImportError:
    AudioRegistryDep = None


# ContentAddressedAudioCache dependency
def get_audio_cache_dep():
    """Get the ContentAddressedAudioCache singleton."""
    from backend.services.ContentAddressedAudioCache import get_audio_cache
    return get_audio_cache()


try:
    from backend.services.ContentAddressedAudioCache import ContentAddressedAudioCache
    AudioCacheDep = Annotated[ContentAddressedAudioCache, Depends(get_audio_cache_dep)]
except ImportError:
    AudioCacheDep = None


# JobStateStore dependency
def get_job_state_store_dep():
    """Get the JobStateStore singleton."""
    from backend.services.JobStateStore import get_job_state_store
    return get_job_state_store()


try:
    from backend.services.JobStateStore import JobStateStore
    JobStateStoreDep = Annotated[JobStateStore, Depends(get_job_state_store_dep)]
except ImportError:
    JobStateStoreDep = None


# CircuitBreaker dependency (per-engine)
def get_circuit_breaker_dep(engine_id: str):
    """Get circuit breaker for a specific engine."""
    from backend.services.circuit_breaker import get_engine_breaker
    return get_engine_breaker(engine_id)


# Export all dependencies
__all__ = [
    "EngineServiceDep",
    "EngineConfigServiceDep",
    "AudioRegistryDep", 
    "AudioCacheDep",
    "JobStateStoreDep",
    "get_engine_service_dep",
    "get_engine_config_service_dep",
    "get_audio_registry_dep",
    "get_audio_cache_dep",
    "get_job_state_store_dep",
    "get_circuit_breaker_dep",
]
