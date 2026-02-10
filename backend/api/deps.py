"""
FastAPI Dependency Injection Wrappers (Phase 2.3)

Provides type-safe dependency injection for services using FastAPI's Depends().
This improves testability by allowing services to be easily mocked in tests.

Usage:
    from backend.api.deps import EngineServiceDep, EngineConfigServiceDep

    @router.get("/engines")
    async def list_engines(engine_service: EngineServiceDep):
        return engine_service.list_engines()

    @router.get("/engines/config")
    async def get_config(config_service: EngineConfigServiceDep):
        return config_service.get_default_engine("tts")
"""

from typing import Annotated, Optional, TYPE_CHECKING

from fastapi import Depends

if TYPE_CHECKING:
    from backend.services.EngineConfigService import EngineConfigService
    from backend.services.engine_service import IEngineService
    from backend.services.AudioArtifactRegistry import AudioArtifactRegistry
    from backend.services.ContentAddressedAudioCache import ContentAddressedAudioCache
    from backend.services.JobStateStore import JobStateStore
    from backend.services.ProjectStoreService import ProjectStoreService
    from backend.services.profile_store import ProfileStore
    from backend.services.track_store import TrackStore
    from backend.services.artifact_ref_counter import ArtifactRefCounter
    from backend.services.edit_history import EditHistory


# EngineConfigService dependency
def get_engine_config_service_dep():
    """Get the EngineConfigService singleton."""
    from backend.services.EngineConfigService import get_engine_config_service
    return get_engine_config_service()


try:
    from backend.services.EngineConfigService import (
        EngineConfigService as _EngineConfigService,
    )
    EngineConfigServiceDep: Optional[type] = Annotated[
        _EngineConfigService, Depends(get_engine_config_service_dep)
    ]
except ImportError:
    EngineConfigServiceDep = None


# EngineService dependency
def get_engine_service_dep():
    """Get the EngineService singleton."""
    from backend.services.engine_service import get_engine_service
    return get_engine_service()


try:
    from backend.services.engine_service import IEngineService as _IEngineService
    EngineServiceDep: Optional[type] = Annotated[
        _IEngineService, Depends(get_engine_service_dep)
    ]
except ImportError:
    EngineServiceDep = None


# AudioArtifactRegistry dependency
def get_audio_registry_dep():
    """Get the AudioArtifactRegistry singleton."""
    from backend.services.AudioArtifactRegistry import get_audio_registry
    return get_audio_registry()


try:
    from backend.services.AudioArtifactRegistry import (
        AudioArtifactRegistry as _AudioArtifactRegistry,
    )
    AudioRegistryDep: Optional[type] = Annotated[
        _AudioArtifactRegistry, Depends(get_audio_registry_dep)
    ]
except ImportError:
    AudioRegistryDep = None


# ContentAddressedAudioCache dependency
def get_audio_cache_dep():
    """Get the ContentAddressedAudioCache singleton."""
    from backend.services.ContentAddressedAudioCache import get_audio_cache
    return get_audio_cache()


try:
    from backend.services.ContentAddressedAudioCache import (
        ContentAddressedAudioCache as _ContentAddressedAudioCache,
    )
    AudioCacheDep: Optional[type] = Annotated[
        _ContentAddressedAudioCache, Depends(get_audio_cache_dep)
    ]
except ImportError:
    AudioCacheDep = None


# JobStateStore dependency
def get_job_state_store_dep():
    """Get the JobStateStore singleton."""
    from backend.services.JobStateStore import get_job_state_store
    return get_job_state_store()


try:
    from backend.services.JobStateStore import JobStateStore as _JobStateStore
    JobStateStoreDep: Optional[type] = Annotated[
        _JobStateStore, Depends(get_job_state_store_dep)
    ]
except ImportError:
    JobStateStoreDep = None


# CircuitBreaker dependency (per-engine)
def get_circuit_breaker_dep(engine_id: str):
    """Get circuit breaker for a specific engine."""
    from backend.services.circuit_breaker import get_engine_breaker
    return get_engine_breaker(engine_id)


# ProjectStoreService dependency
def get_project_store_service_dep():
    """Get the ProjectStoreService singleton."""
    from backend.services.ProjectStoreService import get_project_store_service
    return get_project_store_service()


try:
    from backend.services.ProjectStoreService import (
        ProjectStoreService as _ProjectStoreService,
    )
    ProjectStoreServiceDep: Optional[type] = Annotated[
        _ProjectStoreService, Depends(get_project_store_service_dep)
    ]
except ImportError:
    ProjectStoreServiceDep = None


# ProfileStore dependency
def get_profile_store_dep():
    """Get the ProfileStore singleton."""
    from backend.services.profile_store import get_profile_store
    return get_profile_store()


try:
    from backend.services.profile_store import ProfileStore as _ProfileStore
    ProfileStoreDep: Optional[type] = Annotated[
        _ProfileStore, Depends(get_profile_store_dep)
    ]
except ImportError:
    ProfileStoreDep = None


# TrackStore dependency
def get_track_store_dep():
    """Get the TrackStore singleton."""
    from backend.services.track_store import get_track_store
    return get_track_store()


try:
    from backend.services.track_store import TrackStore as _TrackStore
    TrackStoreDep: Optional[type] = Annotated[
        _TrackStore, Depends(get_track_store_dep)
    ]
except ImportError:
    TrackStoreDep = None


# ArtifactRefCounter dependency
def get_ref_counter_dep():
    """Get the ArtifactRefCounter singleton."""
    from backend.services.artifact_ref_counter import get_ref_counter
    return get_ref_counter()


try:
    from backend.services.artifact_ref_counter import (
        ArtifactRefCounter as _ArtifactRefCounter,
    )
    ArtifactRefCounterDep: Optional[type] = Annotated[
        _ArtifactRefCounter, Depends(get_ref_counter_dep)
    ]
except ImportError:
    ArtifactRefCounterDep = None


# EditHistory dependency
def get_edit_history_dep():
    """Get a project-scoped EditHistory instance."""
    from backend.services.edit_history import EditHistory
    return EditHistory()


try:
    from backend.services.edit_history import EditHistory as _EditHistory
    EditHistoryDep: Optional[type] = Annotated[
        _EditHistory, Depends(get_edit_history_dep)
    ]
except ImportError:
    EditHistoryDep = None


# Export all dependencies
__all__ = [
    "EngineServiceDep",
    "EngineConfigServiceDep",
    "AudioRegistryDep",
    "AudioCacheDep",
    "JobStateStoreDep",
    "ProjectStoreServiceDep",
    "ProfileStoreDep",
    "TrackStoreDep",
    "ArtifactRefCounterDep",
    "EditHistoryDep",
    "get_engine_service_dep",
    "get_engine_config_service_dep",
    "get_audio_registry_dep",
    "get_audio_cache_dep",
    "get_job_state_store_dep",
    "get_project_store_service_dep",
    "get_profile_store_dep",
    "get_track_store_dep",
    "get_ref_counter_dep",
    "get_edit_history_dep",
    "get_circuit_breaker_dep",
]
