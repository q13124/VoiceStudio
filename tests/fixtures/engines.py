"""
Engine Test Fixtures

Provides mock engine fixtures for testing without requiring real engine instances:
- Mock TTS engines (XTTS, Chatterbox, Piper, etc.)
- Mock transcription engines (Whisper)
- Mock quality analysis engines
- Engine response simulators
"""

import asyncio
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union
from unittest.mock import AsyncMock, MagicMock, Mock, patch

# Import factories
try:
    from tests.fixtures.factories import AudioFactory, AudioSpec, random_id, random_string
except ImportError:
    from .factories import AudioFactory, AudioSpec, random_id, random_string


# =============================================================================
# ENGINE MOCK CONFIGURATIONS
# =============================================================================

@dataclass
class MockEngineConfig:
    """Configuration for mock engine behavior."""
    engine_id: str
    name: str
    type: str = "audio"
    subtype: str = "tts"
    latency_ms: float = 100.0
    latency_variance: float = 0.2
    success_rate: float = 1.0  # 1.0 = 100% success
    capabilities: List[str] = field(default_factory=list)
    supported_languages: List[str] = field(default_factory=lambda: ["en"])
    sample_rate: int = 22050
    
    @property
    def simulated_latency(self) -> float:
        """Get simulated latency with variance."""
        variance = self.latency_ms * self.latency_variance
        return (self.latency_ms + random.uniform(-variance, variance)) / 1000
    
    def should_succeed(self) -> bool:
        """Determine if this request should succeed."""
        return random.random() < self.success_rate


# Pre-defined engine configurations
ENGINE_CONFIGS = {
    "xtts_v2": MockEngineConfig(
        engine_id="xtts_v2",
        name="XTTS v2",
        subtype="tts",
        latency_ms=500.0,
        capabilities=["voice_cloning", "multi_language_tts", "emotion_control"],
        supported_languages=["en", "es", "fr", "de", "it", "pt", "ja", "zh-cn"],
        sample_rate=24000,
    ),
    "chatterbox": MockEngineConfig(
        engine_id="chatterbox",
        name="Chatterbox TTS",
        subtype="tts",
        latency_ms=400.0,
        capabilities=["voice_cloning", "zero_shot_cloning", "emotion_control", "high_quality_synthesis"],
        supported_languages=["en", "es", "fr", "de", "it", "pt", "ja", "zh-cn", "ko"],
        sample_rate=22050,
    ),
    "piper": MockEngineConfig(
        engine_id="piper",
        name="Piper TTS",
        subtype="tts",
        latency_ms=50.0,
        capabilities=["multi_language_tts", "streaming"],
        supported_languages=["en", "es", "de", "fr"],
        sample_rate=22050,
    ),
    "silero": MockEngineConfig(
        engine_id="silero",
        name="Silero TTS",
        subtype="tts",
        latency_ms=100.0,
        capabilities=["multi_language_tts"],
        supported_languages=["en", "ru", "de", "es"],
        sample_rate=48000,
    ),
    "tortoise": MockEngineConfig(
        engine_id="tortoise",
        name="Tortoise TTS",
        subtype="tts",
        latency_ms=5000.0,  # Very slow
        capabilities=["voice_cloning", "high_quality_synthesis"],
        supported_languages=["en"],
        sample_rate=24000,
    ),
    "whisper": MockEngineConfig(
        engine_id="whisper",
        name="Whisper",
        type="audio",
        subtype="stt",
        latency_ms=200.0,
        capabilities=["transcription", "multi_language"],
        supported_languages=["en", "es", "fr", "de", "it", "pt", "ja", "zh", "ko", "ru"],
        sample_rate=16000,
    ),
    "whisper_cpp": MockEngineConfig(
        engine_id="whisper_cpp",
        name="Whisper.cpp",
        type="audio",
        subtype="stt",
        latency_ms=100.0,
        capabilities=["transcription", "streaming"],
        supported_languages=["en", "es", "fr", "de"],
        sample_rate=16000,
    ),
    "rvc": MockEngineConfig(
        engine_id="rvc",
        name="RVC",
        subtype="voice_conversion",
        latency_ms=300.0,
        capabilities=["voice_conversion", "singing_voice"],
        supported_languages=["en"],
        sample_rate=48000,
    ),
}


# =============================================================================
# MOCK ENGINE BASE
# =============================================================================

class MockEngine:
    """Base mock engine that simulates engine behavior."""
    
    def __init__(self, config: MockEngineConfig):
        self.config = config
        self.call_count = 0
        self.last_call_time = None
        self.is_initialized = False
        self.is_healthy = True
        self._error_message: Optional[str] = None
    
    @property
    def engine_id(self) -> str:
        return self.config.engine_id
    
    @property
    def name(self) -> str:
        return self.config.name
    
    def initialize(self) -> bool:
        """Simulate engine initialization."""
        time.sleep(self.config.simulated_latency * 0.5)
        self.is_initialized = True
        return True
    
    def shutdown(self) -> None:
        """Simulate engine shutdown."""
        self.is_initialized = False
    
    def health_check(self) -> Dict[str, Any]:
        """Return health status."""
        return {
            "engine_id": self.engine_id,
            "status": "healthy" if self.is_healthy else "unhealthy",
            "initialized": self.is_initialized,
            "call_count": self.call_count,
        }
    
    def set_error(self, message: str) -> None:
        """Set engine to error state."""
        self._error_message = message
        self.is_healthy = False
    
    def clear_error(self) -> None:
        """Clear error state."""
        self._error_message = None
        self.is_healthy = True
    
    def _simulate_latency(self) -> None:
        """Simulate processing latency."""
        time.sleep(self.config.simulated_latency)
    
    def _check_should_fail(self) -> None:
        """Check if operation should fail and raise error."""
        if self._error_message:
            raise RuntimeError(self._error_message)
        if not self.config.should_succeed():
            raise RuntimeError(f"Simulated failure for {self.engine_id}")
    
    def _record_call(self) -> None:
        """Record that a call was made."""
        self.call_count += 1
        self.last_call_time = time.time()


class MockTTSEngine(MockEngine):
    """Mock TTS engine for synthesis testing."""
    
    def synthesize(
        self,
        text: str,
        profile_id: Optional[str] = None,
        language: str = "en",
        **kwargs
    ) -> bytes:
        """Simulate text-to-speech synthesis."""
        self._record_call()
        self._check_should_fail()
        self._simulate_latency()
        
        # Generate fake audio based on text length
        duration = len(text) * 0.05  # ~50ms per character
        spec = AudioSpec(
            sample_rate=self.config.sample_rate,
            duration_seconds=min(duration, 30.0),
        )
        
        return AudioFactory.create_wav_bytes(spec)
    
    async def synthesize_async(
        self,
        text: str,
        profile_id: Optional[str] = None,
        language: str = "en",
        **kwargs
    ) -> bytes:
        """Async version of synthesize."""
        self._record_call()
        self._check_should_fail()
        await asyncio.sleep(self.config.simulated_latency)
        
        duration = len(text) * 0.05
        spec = AudioSpec(
            sample_rate=self.config.sample_rate,
            duration_seconds=min(duration, 30.0),
        )
        
        return AudioFactory.create_wav_bytes(spec)
    
    def clone_voice(
        self,
        reference_audio: bytes,
        text: str,
        **kwargs
    ) -> bytes:
        """Simulate voice cloning."""
        self._record_call()
        self._check_should_fail()
        self._simulate_latency()
        
        # Double latency for cloning
        time.sleep(self.config.simulated_latency)
        
        duration = len(text) * 0.05
        spec = AudioSpec(
            sample_rate=self.config.sample_rate,
            duration_seconds=min(duration, 30.0),
        )
        
        return AudioFactory.create_wav_bytes(spec)


class MockSTTEngine(MockEngine):
    """Mock STT engine for transcription testing."""
    
    SAMPLE_TRANSCRIPTS = [
        "Hello, this is a test transcription.",
        "The quick brown fox jumps over the lazy dog.",
        "Welcome to VoiceStudio voice processing.",
        "Testing one two three.",
    ]
    
    def transcribe(
        self,
        audio: bytes,
        language: str = "en",
        **kwargs
    ) -> Dict[str, Any]:
        """Simulate audio transcription."""
        self._record_call()
        self._check_should_fail()
        self._simulate_latency()
        
        # Return simulated transcription
        return {
            "text": random.choice(self.SAMPLE_TRANSCRIPTS),
            "language": language,
            "confidence": random.uniform(0.85, 0.99),
            "segments": [
                {
                    "start": 0.0,
                    "end": 3.0,
                    "text": "Sample segment",
                    "confidence": 0.95,
                }
            ],
        }
    
    async def transcribe_async(
        self,
        audio: bytes,
        language: str = "en",
        **kwargs
    ) -> Dict[str, Any]:
        """Async version of transcribe."""
        self._record_call()
        self._check_should_fail()
        await asyncio.sleep(self.config.simulated_latency)
        
        return {
            "text": random.choice(self.SAMPLE_TRANSCRIPTS),
            "language": language,
            "confidence": random.uniform(0.85, 0.99),
        }


class MockQualityEngine(MockEngine):
    """Mock quality analysis engine."""
    
    def analyze(
        self,
        audio: bytes,
        reference_audio: Optional[bytes] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Simulate quality analysis."""
        self._record_call()
        self._check_should_fail()
        self._simulate_latency()
        
        return {
            "mos_score": random.uniform(3.5, 5.0),
            "similarity_score": random.uniform(0.7, 0.95) if reference_audio else None,
            "naturalness": random.uniform(0.7, 0.95),
            "clarity": random.uniform(0.8, 0.98),
            "noise_level": random.uniform(0.01, 0.1),
            "metrics": {
                "snr_db": random.uniform(20, 40),
                "f0_stability": random.uniform(0.8, 0.98),
                "articulation_rate": random.uniform(3.0, 5.0),
            },
        }


# =============================================================================
# ENGINE FACTORY
# =============================================================================

class MockEngineFactory:
    """Factory for creating mock engine instances."""
    
    @staticmethod
    def create(engine_id: str, **overrides) -> MockEngine:
        """Create a mock engine by ID."""
        if engine_id not in ENGINE_CONFIGS:
            # Create generic config
            config = MockEngineConfig(
                engine_id=engine_id,
                name=engine_id.replace("_", " ").title(),
                **overrides
            )
        else:
            config = ENGINE_CONFIGS[engine_id]
            # Apply overrides
            for key, value in overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)
        
        # Create appropriate engine type
        if config.subtype == "stt" or "transcription" in config.capabilities:
            return MockSTTEngine(config)
        elif config.subtype in ["tts", "voice_clone", "voice_conversion"]:
            return MockTTSEngine(config)
        else:
            return MockEngine(config)
    
    @staticmethod
    def create_xtts(**overrides) -> MockTTSEngine:
        """Create XTTS mock engine."""
        return MockEngineFactory.create("xtts_v2", **overrides)
    
    @staticmethod
    def create_chatterbox(**overrides) -> MockTTSEngine:
        """Create Chatterbox mock engine."""
        return MockEngineFactory.create("chatterbox", **overrides)
    
    @staticmethod
    def create_piper(**overrides) -> MockTTSEngine:
        """Create Piper mock engine."""
        return MockEngineFactory.create("piper", **overrides)
    
    @staticmethod
    def create_whisper(**overrides) -> MockSTTEngine:
        """Create Whisper mock engine."""
        return MockEngineFactory.create("whisper", **overrides)
    
    @staticmethod
    def create_quality_analyzer(**overrides) -> MockQualityEngine:
        """Create quality analysis mock engine."""
        config = MockEngineConfig(
            engine_id="quality_analyzer",
            name="Quality Analyzer",
            subtype="analysis",
            latency_ms=200.0,
            capabilities=["quality_analysis", "similarity_scoring"],
            **overrides
        )
        return MockQualityEngine(config)
    
    @staticmethod
    def create_all_tts() -> Dict[str, MockTTSEngine]:
        """Create all TTS mock engines."""
        tts_ids = ["xtts_v2", "chatterbox", "piper", "silero", "tortoise"]
        return {eid: MockEngineFactory.create(eid) for eid in tts_ids}


# =============================================================================
# ENGINE SERVICE MOCK
# =============================================================================

class MockEngineService:
    """Mock engine service for testing engine management."""
    
    def __init__(self):
        self._engines: Dict[str, MockEngine] = {}
        self._default_engine = "xtts_v2"
    
    def register_engine(self, engine: MockEngine) -> None:
        """Register a mock engine."""
        self._engines[engine.engine_id] = engine
    
    def get_engine(self, engine_id: str) -> Optional[MockEngine]:
        """Get engine by ID."""
        return self._engines.get(engine_id)
    
    def list_engines(self) -> List[Dict[str, Any]]:
        """List all registered engines."""
        return [
            {
                "id": e.engine_id,
                "name": e.name,
                "status": "available" if e.is_healthy else "unavailable",
                "capabilities": e.config.capabilities,
            }
            for e in self._engines.values()
        ]
    
    def is_available(self, engine_id: str) -> bool:
        """Check if engine is available."""
        engine = self._engines.get(engine_id)
        return engine is not None and engine.is_healthy
    
    def synthesize(
        self,
        text: str,
        engine_id: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """Synthesize using specified or default engine."""
        engine_id = engine_id or self._default_engine
        engine = self.get_engine(engine_id)
        
        if not engine:
            raise ValueError(f"Engine {engine_id} not found")
        
        if not isinstance(engine, MockTTSEngine):
            raise TypeError(f"Engine {engine_id} is not a TTS engine")
        
        return engine.synthesize(text, **kwargs)
    
    def transcribe(
        self,
        audio: bytes,
        engine_id: str = "whisper",
        **kwargs
    ) -> Dict[str, Any]:
        """Transcribe using specified engine."""
        engine = self.get_engine(engine_id)
        
        if not engine:
            raise ValueError(f"Engine {engine_id} not found")
        
        if not isinstance(engine, MockSTTEngine):
            raise TypeError(f"Engine {engine_id} is not an STT engine")
        
        return engine.transcribe(audio, **kwargs)
    
    @classmethod
    def create_with_engines(cls, engine_ids: Optional[List[str]] = None) -> "MockEngineService":
        """Create service with pre-registered engines."""
        service = cls()
        
        if engine_ids is None:
            engine_ids = ["xtts_v2", "chatterbox", "piper", "whisper"]
        
        for engine_id in engine_ids:
            engine = MockEngineFactory.create(engine_id)
            service.register_engine(engine)
        
        return service


# =============================================================================
# PYTEST FIXTURES
# =============================================================================

def pytest_fixture_mock_xtts():
    """Pytest fixture for XTTS mock engine."""
    return MockEngineFactory.create_xtts()


def pytest_fixture_mock_chatterbox():
    """Pytest fixture for Chatterbox mock engine."""
    return MockEngineFactory.create_chatterbox()


def pytest_fixture_mock_whisper():
    """Pytest fixture for Whisper mock engine."""
    return MockEngineFactory.create_whisper()


def pytest_fixture_mock_engine_service():
    """Pytest fixture for mock engine service."""
    return MockEngineService.create_with_engines()


def pytest_fixture_all_mock_engines():
    """Pytest fixture for all mock engines."""
    return {
        "tts": MockEngineFactory.create_all_tts(),
        "stt": {"whisper": MockEngineFactory.create_whisper()},
        "quality": {"analyzer": MockEngineFactory.create_quality_analyzer()},
    }
