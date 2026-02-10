"""
Engine Service - Abstraction layer for engine operations.

This service provides a clean architecture boundary between API routes and the engine layer.
Routes should inject EngineService instead of importing from app.core.engines directly.

Architecture:
    Routes (API) -> EngineService (Service) -> Engine Layer (app.core.engines)

This follows the Clean Architecture principle of dependency inversion.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import logging

from backend.services.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerOpenError,
)

logger = logging.getLogger(__name__)

# Type definitions for engine operations
EngineId = str
AudioPath = Union[str, Path]
MetricsResult = Dict[str, Any]
SynthesisResult = Dict[str, Any]


class IEngineService(ABC):
    """Abstract interface for engine operations.
    
    This interface defines the contract that all engine service implementations
    must follow. Routes should depend on this interface, not concrete implementations.
    """

    # -------------------------------------------------------------------------
    # Engine Discovery and Management
    # -------------------------------------------------------------------------

    @abstractmethod
    def list_engines(self) -> List[Dict[str, Any]]:
        """List all available engines with their metadata."""
        ...

    @abstractmethod
    def get_engine(self, engine_id: EngineId) -> Optional[Any]:
        """Get an engine instance by ID."""
        ...

    @abstractmethod
    def is_engine_available(self, engine_id: EngineId) -> bool:
        """Check if an engine is available and ready to use."""
        ...

    @abstractmethod
    def get_engine_status(self, engine_id: EngineId) -> Dict[str, Any]:
        """Get the current status of an engine."""
        ...

    # -------------------------------------------------------------------------
    # Voice Synthesis Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def synthesize(
        self,
        engine_id: EngineId,
        text: str,
        voice_id: Optional[str] = None,
        **kwargs: Any,
    ) -> SynthesisResult:
        """Synthesize speech from text using the specified engine."""
        ...

    @abstractmethod
    def clone_voice(
        self,
        engine_id: EngineId,
        reference_audio: AudioPath,
        text: str,
        **kwargs: Any,
    ) -> SynthesisResult:
        """Clone a voice using reference audio."""
        ...

    # -------------------------------------------------------------------------
    # Transcription Operations
    # -------------------------------------------------------------------------

    @abstractmethod
    def transcribe(
        self,
        engine_id: EngineId,
        audio_path: AudioPath,
        language: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transcribe audio to text using the specified engine."""
        ...

    # -------------------------------------------------------------------------
    # Quality Metrics
    # -------------------------------------------------------------------------

    @abstractmethod
    def calculate_metrics(
        self,
        audio_path: AudioPath,
        reference_path: Optional[AudioPath] = None,
    ) -> MetricsResult:
        """Calculate quality metrics for an audio file."""
        ...

    @abstractmethod
    def calculate_similarity(
        self,
        audio1_path: AudioPath,
        audio2_path: AudioPath,
    ) -> float:
        """Calculate similarity between two audio files."""
        ...

    @abstractmethod
    def calculate_mos_score(self, audio: Union[AudioPath, Any]) -> float:
        """Calculate Mean Opinion Score for audio (path or numpy array)."""
        ...

    @abstractmethod
    def calculate_snr(
        self, audio: Union[AudioPath, "np.ndarray"], sample_rate: Optional[int] = None
    ) -> float:
        """Calculate Signal-to-Noise Ratio for audio (path or numpy array)."""
        ...

    @abstractmethod
    def detect_artifacts(
        self, audio_path: AudioPath, sample_rate: int = 22050
    ) -> Dict[str, Any]:
        """Detect audio artifacts (clipping, distortion, noise)."""
        ...

    @abstractmethod
    def get_engine_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all engines."""
        ...

    # -------------------------------------------------------------------------
    # Quality Optimization
    # -------------------------------------------------------------------------

    @abstractmethod
    def get_quality_presets(self) -> List[Dict[str, Any]]:
        """Get available quality presets."""
        ...

    @abstractmethod
    def get_synthesis_params_from_preset(
        self,
        preset_name: str,
        engine_id: Optional[EngineId] = None,
    ) -> Dict[str, Any]:
        """Get synthesis parameters for a quality preset."""
        ...

    # -------------------------------------------------------------------------
    # Engine Router Access
    # -------------------------------------------------------------------------

    @abstractmethod
    def route_synthesis(
        self,
        text: str,
        voice_id: Optional[str] = None,
        engine_preference: Optional[str] = None,
        **kwargs: Any,
    ) -> SynthesisResult:
        """Route synthesis to the best available engine."""
        ...

    @abstractmethod
    def get_available_voices(self, engine_id: Optional[EngineId] = None) -> List[Dict[str, Any]]:
        """Get list of available voices, optionally filtered by engine."""
        ...

    @abstractmethod
    def calculate_all_metrics(
        self,
        audio: Union[AudioPath, Any],
        reference: Optional[Union[AudioPath, Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate all quality metrics for audio."""
        ...

    @abstractmethod
    def calculate_naturalness(self, audio: Union[AudioPath, Any]) -> float:
        """Calculate naturalness score for audio."""
        ...

    @abstractmethod
    def get_whisper_engine(self) -> Optional[Any]:
        """Get Whisper transcription engine."""
        ...

    @abstractmethod
    def get_aeneas_engine(self) -> Optional[Any]:
        """Get Aeneas forced alignment engine."""
        ...

    @abstractmethod
    def get_rvc_engine(self) -> Optional[Any]:
        """Get RVC voice conversion engine."""
        ...

    @abstractmethod
    def get_realesrgan_engine(self) -> Optional[Any]:
        """Get Real-ESRGAN upscaling engine."""
        ...

    @abstractmethod
    def get_deepfacelab_engine(self) -> Optional[Any]:
        """Get DeepFaceLab engine."""
        ...

    @abstractmethod
    def get_speaker_encoder_engine(self) -> Optional[Any]:
        """Get speaker encoder engine."""
        ...


class EngineService(IEngineService):
    """Concrete implementation of the engine service.
    
    This implementation delegates to the existing engine layer (app.core.engines).
    It provides a stable interface while allowing the underlying implementation
    to evolve.
    """

    # Engine fallback priority for graceful degradation
    ENGINE_FALLBACK_CHAIN: Dict[str, List[str]] = {
        "xtts_v2": ["chatterbox", "bark", "piper"],
        "chatterbox": ["xtts_v2", "bark", "piper"],
        "bark": ["xtts_v2", "chatterbox", "piper"],
        "piper": ["xtts_v2", "chatterbox", "bark"],
        "whisper": ["faster_whisper"],
        "faster_whisper": ["whisper"],
    }

    def __init__(self):
        """Initialize the engine service with lazy loading."""
        self._engine_router = None
        self._quality_metrics = None
        self._quality_optimizer = None
        self._quality_presets = None
        self._performance_metrics = None
        self._engines_loaded = False
        
        # Circuit breakers for graceful degradation
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._circuit_breaker_config = CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            recovery_timeout=60.0,
        )
    
    def _get_circuit_breaker(self, engine_id: EngineId) -> CircuitBreaker:
        """Get or create a circuit breaker for an engine."""
        if engine_id not in self._circuit_breakers:
            self._circuit_breakers[engine_id] = CircuitBreaker(
                name=engine_id,
                failure_threshold=self._circuit_breaker_config.failure_threshold,
                success_threshold=self._circuit_breaker_config.success_threshold,
                recovery_timeout=self._circuit_breaker_config.recovery_timeout,
            )
        return self._circuit_breakers[engine_id]
    
    def _get_fallback_engines(self, engine_id: EngineId) -> List[EngineId]:
        """Get fallback engine chain for graceful degradation."""
        return self.ENGINE_FALLBACK_CHAIN.get(engine_id, [])
    
    def get_engine_health(self, engine_id: EngineId) -> Dict[str, Any]:
        """Get the health status of an engine including circuit breaker state."""
        breaker = self._get_circuit_breaker(engine_id)
        stats = breaker.get_stats()
        return {
            "engine_id": engine_id,
            "circuit_state": stats.state.name,
            "failure_count": stats.failure_count,
            "success_count": stats.success_count,
            "total_calls": stats.total_calls,
            "total_failures": stats.total_failures,
            "total_blocked": stats.total_blocked,
            "is_healthy": breaker.allow_request(),
        }
    
    def get_all_engine_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status for all engines with circuit breakers."""
        return {
            engine_id: self.get_engine_health(engine_id)
            for engine_id in self._circuit_breakers
        }

    def _ensure_engines_loaded(self):
        """Lazy load engine modules to avoid import issues at startup."""
        if self._engines_loaded:
            return

        try:
            from app.core.engines import router
            self._engine_router = router
        except ImportError:
            self._engine_router = None

        try:
            from app.core.engines import quality_metrics
            self._quality_metrics = quality_metrics
        except ImportError:
            self._quality_metrics = None

        try:
            from app.core.engines import quality_optimizer
            self._quality_optimizer = quality_optimizer
        except ImportError:
            self._quality_optimizer = None

        try:
            from app.core.engines import quality_presets
            self._quality_presets = quality_presets
        except ImportError:
            self._quality_presets = None

        self._engines_loaded = True

    # -------------------------------------------------------------------------
    # Engine Discovery and Management
    # -------------------------------------------------------------------------

    def list_engines(self) -> List[Dict[str, Any]]:
        """List all available engines with their metadata."""
        self._ensure_engines_loaded()
        if self._engine_router is None:
            return []
        
        try:
            return self._engine_router.list_engines()
        except Exception as e:
            logger.debug(f"Failed to list engines: {e}")
            return []

    def get_engine(self, engine_id: EngineId) -> Optional[Any]:
        """Get an engine instance by ID."""
        self._ensure_engines_loaded()
        if self._engine_router is None:
            return None
        
        try:
            return self._engine_router.get_engine(engine_id)
        except Exception as e:
            logger.debug(f"Failed to get engine {engine_id}: {e}")
            return None

    def is_engine_available(self, engine_id: EngineId) -> bool:
        """Check if an engine is available and ready to use."""
        engine = self.get_engine(engine_id)
        return engine is not None

    def get_engine_status(self, engine_id: EngineId) -> Dict[str, Any]:
        """Get the current status of an engine."""
        self._ensure_engines_loaded()
        if self._engine_router is None:
            return {"status": "unavailable", "error": "Engine router not loaded"}
        
        try:
            engine = self._engine_router.get_engine(engine_id)
            if engine is None:
                return {"status": "not_found", "engine_id": engine_id}
            
            return {
                "status": "available",
                "engine_id": engine_id,
                "ready": getattr(engine, "ready", True),
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # -------------------------------------------------------------------------
    # Voice Synthesis Operations
    # -------------------------------------------------------------------------

    def synthesize(
        self,
        engine_id: EngineId,
        text: str,
        voice_id: Optional[str] = None,
        **kwargs: Any,
    ) -> SynthesisResult:
        """Synthesize speech from text using the specified engine.
        
        Implements graceful degradation:
        - Uses circuit breaker to prevent cascading failures
        - Falls back to alternative engines if primary fails
        - Records success/failure metrics for health monitoring
        """
        self._ensure_engines_loaded()
        if self._engine_router is None:
            return {"error": "Engine router not available", "degraded": True}
        
        # Build engine chain: primary + fallbacks
        engines_to_try = [engine_id] + self._get_fallback_engines(engine_id)
        last_error = None
        used_fallback = False
        
        for idx, current_engine_id in enumerate(engines_to_try):
            breaker = self._get_circuit_breaker(current_engine_id)
            
            # Skip if circuit is open
            if not breaker.allow_request():
                logger.debug(f"Circuit breaker OPEN for {current_engine_id}, skipping")
                continue
            
            try:
                engine = self._engine_router.get_engine(current_engine_id)
                if engine is None:
                    continue
                
                result = engine.synthesize(text, voice_id=voice_id, **kwargs)
                breaker.record_success()
                
                output = result if isinstance(result, dict) else {"audio_path": str(result)}
                if idx > 0:
                    output["degraded"] = True
                    output["fallback_engine"] = current_engine_id
                    output["primary_engine"] = engine_id
                    logger.warning(f"Synthesize fell back from {engine_id} to {current_engine_id}")
                return output
                
            except Exception as e:
                breaker.record_failure()
                last_error = e
                logger.warning(f"Engine {current_engine_id} failed: {e}")
                continue
        
        # All engines failed
        return {
            "error": f"All engines failed. Last error: {last_error}",
            "degraded": True,
            "engines_tried": engines_to_try,
        }

    def clone_voice(
        self,
        engine_id: EngineId,
        reference_audio: AudioPath,
        text: str,
        **kwargs: Any,
    ) -> SynthesisResult:
        """Clone a voice using reference audio.
        
        Implements graceful degradation with circuit breaker and fallback.
        """
        self._ensure_engines_loaded()
        if self._engine_router is None:
            return {"error": "Engine router not available", "degraded": True}
        
        # Build engine chain: primary + fallbacks (only voice cloning capable)
        engines_to_try = [engine_id] + self._get_fallback_engines(engine_id)
        last_error = None
        
        for idx, current_engine_id in enumerate(engines_to_try):
            breaker = self._get_circuit_breaker(current_engine_id)
            
            if not breaker.allow_request():
                continue
            
            try:
                engine = self._engine_router.get_engine(current_engine_id)
                if engine is None:
                    continue
                
                # Check if engine supports voice cloning
                if not hasattr(engine, 'clone_voice'):
                    continue
                
                result = engine.clone_voice(
                    reference_audio=str(reference_audio),
                    text=text,
                    **kwargs,
                )
                breaker.record_success()
                
                output = result if isinstance(result, dict) else {"audio_path": str(result)}
                if idx > 0:
                    output["degraded"] = True
                    output["fallback_engine"] = current_engine_id
                    output["primary_engine"] = engine_id
                    logger.warning(f"clone_voice fell back from {engine_id} to {current_engine_id}")
                return output
                
            except Exception as e:
                breaker.record_failure()
                last_error = e
                logger.warning(f"Engine {current_engine_id} clone_voice failed: {e}")
                continue
        
        return {
            "error": f"All engines failed. Last error: {last_error}",
            "degraded": True,
            "engines_tried": engines_to_try,
        }

    # -------------------------------------------------------------------------
    # Transcription Operations
    # -------------------------------------------------------------------------

    def transcribe(
        self,
        engine_id: EngineId,
        audio_path: AudioPath,
        language: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transcribe audio to text using the specified engine."""
        self._ensure_engines_loaded()
        if self._engine_router is None:
            return {"error": "Engine router not available"}
        
        try:
            engine = self._engine_router.get_engine(engine_id)
            if engine is None:
                return {"error": f"Engine {engine_id} not found"}
            
            result = engine.transcribe(
                audio_path=str(audio_path),
                language=language,
                **kwargs,
            )
            return result if isinstance(result, dict) else {"text": str(result)}
        except Exception as e:
            return {"error": str(e)}

    # -------------------------------------------------------------------------
    # Quality Metrics
    # -------------------------------------------------------------------------

    def calculate_metrics(
        self,
        audio_path: AudioPath,
        reference_path: Optional[AudioPath] = None,
    ) -> MetricsResult:
        """Calculate quality metrics for an audio file."""
        self._ensure_engines_loaded()
        if self._quality_metrics is None:
            return {"error": "Quality metrics not available"}
        
        try:
            return self._quality_metrics.calculate_all_metrics(
                audio_path=str(audio_path),
                reference_path=str(reference_path) if reference_path else None,
            )
        except Exception as e:
            return {"error": str(e)}

    def calculate_similarity(
        self,
        audio1_path: AudioPath,
        audio2_path: AudioPath,
    ) -> float:
        """Calculate similarity between two audio files."""
        self._ensure_engines_loaded()
        if self._quality_metrics is None:
            return 0.0
        
        try:
            return self._quality_metrics.calculate_similarity(
                str(audio1_path),
                str(audio2_path),
            )
        except Exception as e:
            logger.debug(f"Failed to calculate similarity: {e}")
            return 0.0

    def calculate_mos_score(self, audio: Union[AudioPath, Any]) -> float:
        """Calculate Mean Opinion Score for audio (path or numpy array)."""
        self._ensure_engines_loaded()
        if self._quality_metrics is None:
            return 0.0
        
        try:
            # Check if input is a numpy array (duck typing to avoid import)
            if hasattr(audio, "shape") and hasattr(audio, "dtype"):
                return self._quality_metrics.calculate_mos_score(audio)
            # Otherwise treat as path
            return self._quality_metrics.calculate_mos_score(str(audio))
        except Exception as e:
            logger.debug(f"Failed to calculate MOS score: {e}")
            return 0.0

    def calculate_snr(
        self, audio: Union[AudioPath, Any], sample_rate: Optional[int] = None
    ) -> float:
        """Calculate Signal-to-Noise Ratio for audio (path or numpy array)."""
        self._ensure_engines_loaded()
        if self._quality_metrics is None:
            return 0.0
        
        try:
            # Check if input is a numpy array (duck typing to avoid import)
            if hasattr(audio, "shape") and hasattr(audio, "dtype"):
                return self._quality_metrics.calculate_snr(audio)
            # Otherwise treat as path
            return self._quality_metrics.calculate_snr(str(audio))
        except Exception as e:
            logger.debug(f"Failed to calculate SNR: {e}")
            return 0.0

    def detect_artifacts(
        self, audio: Union[AudioPath, Any], sample_rate: int = 22050
    ) -> Dict[str, Any]:
        """Detect audio artifacts (clipping, distortion, noise)."""
        self._ensure_engines_loaded()
        if self._quality_metrics is None:
            return {"error": "Quality metrics not available"}
        
        try:
            # Check if input is a numpy array (duck typing to avoid import)
            if hasattr(audio, "shape") and hasattr(audio, "dtype"):
                return self._quality_metrics.detect_artifacts(audio, sample_rate=sample_rate)
            # Otherwise treat as path
            return self._quality_metrics.detect_artifacts(str(audio), sample_rate=sample_rate)
        except Exception as e:
            return {"error": str(e)}

    def get_engine_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all engines."""
        self._ensure_engines_loaded()
        try:
            from app.core.engines.performance_metrics import get_engine_metrics
            metrics = get_engine_metrics()
            # Normalize to dict format for API consumption
            return {
                "summary": metrics.get_summary() if hasattr(metrics, "get_summary") else {},
                "all_stats": metrics.get_all_stats() if hasattr(metrics, "get_all_stats") else [],
            }
        except ImportError:
            return {"error": "Performance metrics not available"}
        except Exception as e:
            return {"error": str(e)}

    # -------------------------------------------------------------------------
    # Quality Optimization
    # -------------------------------------------------------------------------

    def get_quality_presets(self) -> List[Dict[str, Any]]:
        """Get available quality presets."""
        self._ensure_engines_loaded()
        if self._quality_presets is None:
            return []
        
        try:
            return self._quality_presets.list_quality_presets()
        except Exception as e:
            logger.debug(f"Failed to get quality presets: {e}")
            return []

    def get_synthesis_params_from_preset(
        self,
        preset_name: str,
        engine_id: Optional[EngineId] = None,
    ) -> Dict[str, Any]:
        """Get synthesis parameters for a quality preset."""
        self._ensure_engines_loaded()
        if self._quality_presets is None:
            return {}
        
        try:
            return self._quality_presets.get_synthesis_params_from_preset(
                preset_name,
                engine_id=engine_id,
            )
        except Exception:
            return {}

    # -------------------------------------------------------------------------
    # Engine Router Access
    # -------------------------------------------------------------------------

    def route_synthesis(
        self,
        text: str,
        voice_id: Optional[str] = None,
        engine_preference: Optional[str] = None,
        **kwargs: Any,
    ) -> SynthesisResult:
        """Route synthesis to the best available engine."""
        self._ensure_engines_loaded()
        if self._engine_router is None:
            return {"error": "Engine router not available"}
        
        try:
            return self._engine_router.synthesize(
                text=text,
                voice_id=voice_id,
                engine_preference=engine_preference,
                **kwargs,
            )
        except Exception as e:
            return {"error": str(e)}

    def get_available_voices(self, engine_id: Optional[EngineId] = None) -> List[Dict[str, Any]]:
        """Get list of available voices, optionally filtered by engine."""
        self._ensure_engines_loaded()
        if self._engine_router is None:
            return []
        
        try:
            if engine_id:
                engine = self._engine_router.get_engine(engine_id)
                if engine and hasattr(engine, "list_voices"):
                    return engine.list_voices()
                return []
            return self._engine_router.list_voices()
        except Exception:
            return []

    def calculate_all_metrics(
        self,
        audio: Union[AudioPath, Any],
        reference: Optional[Union[AudioPath, Any]] = None,
    ) -> Dict[str, Any]:
        """Calculate all quality metrics for audio."""
        self._ensure_engines_loaded()
        if self._quality_metrics is None:
            return {"error": "Quality metrics not available"}
        
        try:
            # Check if input is a numpy array
            if hasattr(audio, "shape") and hasattr(audio, "dtype"):
                if reference is not None and hasattr(reference, "shape"):
                    return self._quality_metrics.calculate_all_metrics(audio, reference)
                return self._quality_metrics.calculate_all_metrics(audio)
            # Path-based
            ref_path = str(reference) if reference else None
            return self._quality_metrics.calculate_all_metrics(str(audio), ref_path)
        except Exception as e:
            return {"error": str(e)}

    def calculate_naturalness(self, audio: Union[AudioPath, Any]) -> float:
        """Calculate naturalness score for audio."""
        self._ensure_engines_loaded()
        if self._quality_metrics is None:
            return 0.0
        
        try:
            if hasattr(audio, "shape") and hasattr(audio, "dtype"):
                return self._quality_metrics.calculate_naturalness(audio)
            return self._quality_metrics.calculate_naturalness(str(audio))
        except Exception:
            return 0.0

    # -------------------------------------------------------------------------
    # Specific Engine Accessors
    # -------------------------------------------------------------------------

    def get_whisper_engine(self) -> Optional[Any]:
        """Get Whisper transcription engine."""
        self._ensure_engines_loaded()
        try:
            from app.core.engines.whisper_engine import WhisperEngine
            return WhisperEngine()
        except ImportError:
            return None
        except Exception:
            return None

    def get_aeneas_engine(self) -> Optional[Any]:
        """Get Aeneas forced alignment engine."""
        self._ensure_engines_loaded()
        try:
            from app.core.engines.aeneas_engine import AeneasEngine
            return AeneasEngine()
        except ImportError:
            return None
        except Exception:
            return None

    def get_rvc_engine(self) -> Optional[Any]:
        """Get RVC voice conversion engine."""
        self._ensure_engines_loaded()
        try:
            from app.core.engines.rvc_engine import RVCEngine
            return RVCEngine()
        except ImportError:
            return None
        except Exception:
            return None

    def get_realesrgan_engine(self) -> Optional[Any]:
        """Get Real-ESRGAN upscaling engine."""
        self._ensure_engines_loaded()
        try:
            from app.core.engines.realesrgan_engine import RealESRGANEngine
            return RealESRGANEngine()
        except ImportError:
            return None
        except Exception:
            return None

    def get_deepfacelab_engine(self) -> Optional[Any]:
        """Get DeepFaceLab engine."""
        self._ensure_engines_loaded()
        try:
            from app.core.engines.deepfacelab_engine import DeepFaceLabEngine
            return DeepFaceLabEngine()
        except ImportError:
            return None
        except Exception:
            return None

    def get_speaker_encoder_engine(self) -> Optional[Any]:
        """Get speaker encoder engine."""
        self._ensure_engines_loaded()
        try:
            from app.core.engines.speaker_encoder_engine import SpeakerEncoderEngine
            return SpeakerEncoderEngine()
        except ImportError:
            return None
        except Exception:
            return None


# Singleton instance for dependency injection
_engine_service_instance: Optional[EngineService] = None


def get_engine_service() -> IEngineService:
    """FastAPI dependency for engine service injection.
    
    Usage in routes:
        from backend.services.engine_service import get_engine_service, IEngineService
        
        @router.get("/engines")
        async def list_engines(engine_service: IEngineService = Depends(get_engine_service)):
            return engine_service.list_engines()
    """
    global _engine_service_instance
    if _engine_service_instance is None:
        _engine_service_instance = EngineService()
    return _engine_service_instance


def get_engine_by_id(engine_id: str) -> Optional[Any]:
    """Get an engine instance by ID.
    
    This is a convenience function for use by adapters.
    
    Args:
        engine_id: The engine identifier (e.g., "xtts", "whisper", "rvc")
        
    Returns:
        The engine instance or None if not available
    """
    service = get_engine_service()
    return service.get_engine(engine_id)


def get_engine_port():
    """Get the engine port interface for Clean Architecture patterns.
    
    This provides access to the IEnginePort interface defined in
    backend.interfaces.engine_port, which offers a more granular
    interface for specific engine types.
    
    Usage in routes:
        from backend.services.engine_service import get_engine_port
        
        engine_port = get_engine_port()
        tts_engine = engine_port.get_synthesis_engine()
        result = await tts_engine.synthesize(request)
    """
    from backend.adapters.engine_adapter import get_engine_service as get_adapter
    return get_adapter()


# Type alias for FastAPI dependency
EngineServiceDep = IEngineService
