"""
Engine Adapter Implementation.

Implements the engine port interfaces by delegating to concrete engine
implementations. This adapter provides:

- Unified engine access through dependency injection
- Lazy loading of engines on first use
- Resource management (loading/unloading)
- Graceful degradation when engines unavailable
- Caching of engine instances

Usage:
    from backend.adapters.engine_adapter import get_engine_service

    engine_service = get_engine_service()
    tts_engine = engine_service.get_synthesis_engine("xtts")
    result = await tts_engine.synthesize(request)
"""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from typing import Any

import numpy as np

from backend.interfaces.engine_port import (
    EngineCapability,
    EngineInfo,
    EngineStatus,
    SynthesisRequest,
    SynthesisResult,
    TranscriptionRequest,
    TranscriptionResult,
    VoiceConversionRequest,
    VoiceConversionResult,
)

logger = logging.getLogger(__name__)


class SynthesisEngineAdapter:
    """Adapter for TTS engines implementing ISynthesisEngine."""

    def __init__(self, engine_id: str = "xtts"):
        self._engine_id = engine_id
        self._engine = None
        self._loaded = False

    @property
    def engine_id(self) -> str:
        return self._engine_id

    @property
    def is_loaded(self) -> bool:
        return self._loaded and self._engine is not None

    async def _ensure_loaded(self) -> None:
        """Lazy load the engine on first use."""
        if self._loaded:
            return

        try:
            if self._engine_id == "xtts":
                from app.core.engines.xtts_engine import XTTSEngine

                self._engine = XTTSEngine()
                await self._engine.load()
            elif self._engine_id == "piper":
                from app.core.engines.piper_engine import PiperEngine

                self._engine = PiperEngine()
                await self._engine.load()
            else:
                # Try to load from engine registry
                from backend.ml.models.engine_service import get_engine_by_id

                self._engine = get_engine_by_id(self._engine_id)
                if self._engine and hasattr(self._engine, "load"):
                    await self._engine.load()

            self._loaded = self._engine is not None

        except ImportError as e:
            logger.warning(f"Engine {self._engine_id} not available: {e}")
            self._loaded = False
        except Exception as e:
            logger.error(f"Failed to load engine {self._engine_id}: {e}")
            self._loaded = False

    async def synthesize(self, request: SynthesisRequest) -> SynthesisResult:
        """Synthesize speech from text."""
        await self._ensure_loaded()

        start_time = time.time()

        if not self._loaded or self._engine is None:
            # Return empty result on failure
            return SynthesisResult(
                audio_data=np.zeros(16000),  # 1 second of silence
                sample_rate=16000,
                duration_seconds=1.0,
                engine_used=self._engine_id,
                latency_ms=(time.time() - start_time) * 1000,
                metadata={"error": "Engine not loaded"},
            )

        try:
            # Call the underlying engine
            if hasattr(self._engine, "synthesize"):
                result = await self._engine.synthesize(
                    text=request.text,
                    speaker_wav=request.speaker_embedding,
                    language=request.language,
                )

                audio_data = result.get("audio", np.zeros(16000))
                sample_rate = result.get("sample_rate", 22050)

            elif hasattr(self._engine, "process"):
                audio_data = await self._engine.process(
                    {
                        "text": request.text,
                        "language": request.language,
                    }
                )
                sample_rate = 22050
            else:
                raise RuntimeError(f"Engine {self._engine_id} has no synthesize method")

            latency_ms = (time.time() - start_time) * 1000
            duration = len(audio_data) / sample_rate if sample_rate > 0 else 0

            return SynthesisResult(
                audio_data=audio_data,
                sample_rate=sample_rate,
                duration_seconds=duration,
                engine_used=self._engine_id,
                latency_ms=latency_ms,
            )

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return SynthesisResult(
                audio_data=np.zeros(16000),
                sample_rate=16000,
                duration_seconds=1.0,
                engine_used=self._engine_id,
                latency_ms=(time.time() - start_time) * 1000,
                metadata={"error": str(e)},
            )

    async def synthesize_streaming(
        self,
        request: SynthesisRequest,
    ) -> AsyncIterator[np.ndarray]:
        """Synthesize speech with streaming output."""
        # For now, synthesize and yield in chunks
        result = await self.synthesize(request)

        chunk_size = 4096
        audio = result.audio_data

        for i in range(0, len(audio), chunk_size):
            yield audio[i : i + chunk_size]

    def get_voices(self) -> list[dict[str, Any]]:
        """Get available voices for this engine."""
        if self._engine and hasattr(self._engine, "get_voices"):
            return self._engine.get_voices()
        return [{"id": "default", "name": "Default Voice"}]

    def get_languages(self) -> list[str]:
        """Get supported languages."""
        if self._engine and hasattr(self._engine, "get_languages"):
            return self._engine.get_languages()
        return ["en", "es", "fr", "de", "it", "pt", "pl", "ru", "zh", "ja", "ko"]


class TranscriptionEngineAdapter:
    """Adapter for STT engines implementing ITranscriptionEngine."""

    def __init__(self, engine_id: str = "whisper"):
        self._engine_id = engine_id
        self._engine = None
        self._loaded = False

    @property
    def engine_id(self) -> str:
        return self._engine_id

    @property
    def is_loaded(self) -> bool:
        return self._loaded and self._engine is not None

    async def _ensure_loaded(self) -> None:
        """Lazy load the engine on first use."""
        if self._loaded:
            return

        try:
            if self._engine_id == "whisper":
                from app.core.engines.whisper_engine import WhisperEngine

                self._engine = WhisperEngine()
                await self._engine.load()
            else:
                from backend.ml.models.engine_service import get_engine_by_id

                self._engine = get_engine_by_id(self._engine_id)
                if self._engine and hasattr(self._engine, "load"):
                    await self._engine.load()

            self._loaded = self._engine is not None

        except ImportError as e:
            logger.warning(f"Engine {self._engine_id} not available: {e}")
        except Exception as e:
            logger.error(f"Failed to load engine {self._engine_id}: {e}")

    async def transcribe(self, request: TranscriptionRequest) -> TranscriptionResult:
        """Transcribe audio to text."""
        await self._ensure_loaded()

        start_time = time.time()

        if not self._loaded or self._engine is None:
            return TranscriptionResult(
                text="",
                language="en",
                confidence=0.0,
                engine_used=self._engine_id,
                latency_ms=(time.time() - start_time) * 1000,
            )

        try:
            if hasattr(self._engine, "transcribe"):
                result = await self._engine.transcribe(
                    audio=request.audio_data,
                    language=request.language,
                    task=request.task,
                )

                return TranscriptionResult(
                    text=result.get("text", ""),
                    language=result.get("language", "en"),
                    confidence=result.get("confidence", 0.9),
                    word_timestamps=result.get("word_timestamps"),
                    engine_used=self._engine_id,
                    latency_ms=(time.time() - start_time) * 1000,
                )
            else:
                raise RuntimeError(f"Engine {self._engine_id} has no transcribe method")

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return TranscriptionResult(
                text="",
                language="en",
                confidence=0.0,
                engine_used=self._engine_id,
                latency_ms=(time.time() - start_time) * 1000,
            )

    async def transcribe_streaming(
        self,
        audio_stream: AsyncIterator[np.ndarray],
        sample_rate: int,
    ) -> AsyncIterator[TranscriptionResult]:
        """Transcribe streaming audio."""
        buffer = []
        async for chunk in audio_stream:
            buffer.append(chunk)

            if len(buffer) >= 10:  # Process every ~10 chunks
                combined = np.concatenate(buffer)
                result = await self.transcribe(
                    TranscriptionRequest(
                        audio_data=combined,
                        sample_rate=sample_rate,
                    )
                )
                buffer = []
                yield result

    def get_languages(self) -> list[str]:
        """Get supported languages."""
        return ["en", "es", "fr", "de", "it", "pt", "ru", "zh", "ja", "ko", "ar", "hi"]


class VoiceConversionEngineAdapter:
    """Adapter for voice conversion engines implementing IVoiceConversionEngine."""

    def __init__(self, engine_id: str = "rvc"):
        self._engine_id = engine_id
        self._engine = None
        self._loaded = False

    @property
    def engine_id(self) -> str:
        return self._engine_id

    @property
    def is_loaded(self) -> bool:
        return self._loaded and self._engine is not None

    async def _ensure_loaded(self) -> None:
        """Lazy load the engine on first use."""
        if self._loaded:
            return

        try:
            from backend.voice.rvc.engine import RVCEngine

            self._engine = RVCEngine()
            self._loaded = True

        except ImportError as e:
            logger.warning(f"RVC engine not available: {e}")
        except Exception as e:
            logger.error(f"Failed to load RVC engine: {e}")

    async def convert(self, request: VoiceConversionRequest) -> VoiceConversionResult:
        """Convert voice in audio."""
        await self._ensure_loaded()

        start_time = time.time()

        if not self._loaded or self._engine is None:
            return VoiceConversionResult(
                audio_data=request.audio_data,
                sample_rate=request.sample_rate,
                engine_used=self._engine_id,
                latency_ms=(time.time() - start_time) * 1000,
            )

        try:
            result = await self._engine.convert(
                audio_data=request.audio_data,
                sample_rate=request.sample_rate,
                pitch_shift=request.pitch_shift,
            )

            return VoiceConversionResult(
                audio_data=result.audio_data,
                sample_rate=result.sample_rate,
                engine_used=self._engine_id,
                latency_ms=(time.time() - start_time) * 1000,
                quality_score=0.85,
            )

        except Exception as e:
            logger.error(f"Voice conversion failed: {e}")
            return VoiceConversionResult(
                audio_data=request.audio_data,
                sample_rate=request.sample_rate,
                engine_used=self._engine_id,
                latency_ms=(time.time() - start_time) * 1000,
            )

    async def load_model(self, model_path: str, index_path: str | None = None) -> bool:
        """Load a voice model."""
        await self._ensure_loaded()

        if self._engine is None:
            return False

        return await self._engine.load_model(model_path, index_path)

    def get_models(self) -> list[dict[str, Any]]:
        """Get available voice models."""
        return [
            {"id": "default", "name": "Default RVC Model"},
        ]


class EmotionEngineAdapter:
    """Adapter for emotion engine implementing IEmotionEngine."""

    def __init__(self):
        self._engine = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded and self._engine is not None

    async def _ensure_loaded(self) -> None:
        """Lazy load the engine on first use."""
        if self._loaded:
            return

        try:
            from backend.voice.emotion.engine import EmotionEngine

            self._engine = EmotionEngine()
            await self._engine.load()
            self._loaded = True

        except ImportError as e:
            logger.warning(f"Emotion engine not available: {e}")
        except Exception as e:
            logger.error(f"Failed to load emotion engine: {e}")

    async def detect(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
    ) -> dict[str, Any]:
        """Detect emotion in audio."""
        await self._ensure_loaded()

        if not self._loaded or self._engine is None:
            return {"emotion": "neutral", "confidence": 0.5}

        result = await self._engine.detect(audio_data, sample_rate)
        return {
            "emotion": result.detected_emotion.value,
            "confidence": result.confidence,
            "scores": result.emotion_scores,
        }

    async def apply_emotion(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        emotion: str,
        intensity: float = 1.0,
    ) -> np.ndarray:
        """Apply emotion to audio."""
        await self._ensure_loaded()

        if not self._loaded or self._engine is None:
            return audio_data

        from backend.voice.emotion.types import EmotionType

        emotion_type = (
            EmotionType(emotion)
            if emotion in [e.value for e in EmotionType]
            else EmotionType.NEUTRAL
        )

        return await self._engine.apply_emotion(audio_data, sample_rate, emotion_type, intensity)

    def get_emotions(self) -> list[str]:
        """Get supported emotions."""
        return ["neutral", "happy", "sad", "angry", "fearful", "surprised"]


class TranslationEngineAdapter:
    """Adapter for translation engine implementing ITranslationEngine."""

    def __init__(self):
        self._engine = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded and self._engine is not None

    async def _ensure_loaded(self) -> None:
        """Lazy load the engine on first use."""
        if self._loaded:
            return

        try:
            from backend.voice.translation.engine import TranslationEngine

            self._engine = TranslationEngine()
            await self._engine.load()
            self._loaded = True

        except ImportError as e:
            logger.warning(f"Translation engine not available: {e}")
        except Exception as e:
            logger.error(f"Failed to load translation engine: {e}")

    async def translate(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        target_language: str,
        source_language: str | None = None,
    ) -> dict[str, Any]:
        """Translate voice to target language."""
        await self._ensure_loaded()

        if not self._loaded or self._engine is None:
            return {
                "audio_data": audio_data,
                "sample_rate": sample_rate,
                "source_text": "",
                "translated_text": "",
            }

        result = await self._engine.translate(
            audio_data,
            sample_rate,
            target_language=target_language,
            source_language=source_language,
        )

        return {
            "audio_data": result.audio_data,
            "sample_rate": result.sample_rate,
            "source_text": result.source_text,
            "translated_text": result.translated_text,
            "source_language": result.source_language,
            "target_language": result.target_language,
        }

    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str | None = None,
    ) -> str:
        """Translate text to target language."""
        try:
            from backend.voice.translation.translation_service import TranslationService

            service = TranslationService()
            return await service._translate_text(
                None, text, source_language or "en", target_language
            )
        except Exception as e:
            logger.error(f"Text translation failed: {e}")
            return text

    def get_languages(self) -> list[str]:
        """Get supported languages."""
        return [
            "en",
            "es",
            "fr",
            "de",
            "it",
            "pt",
            "ru",
            "zh",
            "ja",
            "ko",
            "ar",
            "hi",
            "nl",
            "pl",
            "tr",
            "vi",
            "th",
            "id",
        ]


class EngineAdapter:
    """
    Main engine adapter implementing IEnginePort.

    Provides unified access to all engine types with lazy loading
    and resource management.
    """

    def __init__(self):
        self._synthesis_engines: dict[str, SynthesisEngineAdapter] = {}
        self._transcription_engines: dict[str, TranscriptionEngineAdapter] = {}
        self._voice_conversion_engines: dict[str, VoiceConversionEngineAdapter] = {}
        self._emotion_engine: EmotionEngineAdapter | None = None
        self._translation_engine: TranslationEngineAdapter | None = None

    def get_available_engines(self) -> list[EngineInfo]:
        """Get list of available engines with their status."""
        engines = [
            EngineInfo(
                engine_id="xtts",
                name="XTTS v2",
                version="2.0",
                capabilities=[EngineCapability.TTS, EngineCapability.CLONING],
                status=(
                    EngineStatus.READY
                    if "xtts" in self._synthesis_engines
                    else EngineStatus.UNLOADED
                ),
            ),
            EngineInfo(
                engine_id="whisper",
                name="Whisper",
                version="large-v3",
                capabilities=[EngineCapability.STT],
                status=(
                    EngineStatus.READY
                    if "whisper" in self._transcription_engines
                    else EngineStatus.UNLOADED
                ),
            ),
            EngineInfo(
                engine_id="rvc",
                name="RVC v2",
                version="2.0",
                capabilities=[EngineCapability.VOICE_CONVERSION],
                status=(
                    EngineStatus.READY
                    if "rvc" in self._voice_conversion_engines
                    else EngineStatus.UNLOADED
                ),
            ),
            EngineInfo(
                engine_id="emotion",
                name="Emotion Engine",
                version="1.0",
                capabilities=[EngineCapability.EMOTION],
                status=EngineStatus.READY if self._emotion_engine else EngineStatus.UNLOADED,
            ),
            EngineInfo(
                engine_id="translation",
                name="Translation Engine",
                version="1.0",
                capabilities=[EngineCapability.TRANSLATION],
                status=EngineStatus.READY if self._translation_engine else EngineStatus.UNLOADED,
            ),
        ]
        return engines

    def get_engine_status(self, engine_id: str) -> EngineStatus:
        """Get status of a specific engine."""
        if engine_id in self._synthesis_engines:
            return (
                EngineStatus.READY
                if self._synthesis_engines[engine_id].is_loaded
                else EngineStatus.UNLOADED
            )
        if engine_id in self._transcription_engines:
            return (
                EngineStatus.READY
                if self._transcription_engines[engine_id].is_loaded
                else EngineStatus.UNLOADED
            )
        if engine_id in self._voice_conversion_engines:
            return (
                EngineStatus.READY
                if self._voice_conversion_engines[engine_id].is_loaded
                else EngineStatus.UNLOADED
            )
        return EngineStatus.UNLOADED

    async def load_engine(self, engine_id: str) -> bool:
        """Load an engine into memory."""
        try:
            if engine_id in ["xtts", "piper"]:
                engine = self.get_synthesis_engine(engine_id)
                await engine._ensure_loaded()
                return engine.is_loaded
            elif engine_id == "whisper":
                engine = self.get_transcription_engine(engine_id)
                await engine._ensure_loaded()
                return engine.is_loaded
            elif engine_id == "rvc":
                engine = self.get_voice_conversion_engine(engine_id)
                await engine._ensure_loaded()
                return engine.is_loaded
            elif engine_id == "emotion":
                engine = self.get_emotion_engine()
                await engine._ensure_loaded()
                return engine.is_loaded
            elif engine_id == "translation":
                engine = self.get_translation_engine()
                await engine._ensure_loaded()
                return engine.is_loaded
            return False
        except Exception as e:
            logger.error(f"Failed to load engine {engine_id}: {e}")
            return False

    async def unload_engine(self, engine_id: str) -> bool:
        """Unload an engine from memory."""
        try:
            if engine_id in self._synthesis_engines:
                del self._synthesis_engines[engine_id]
            if engine_id in self._transcription_engines:
                del self._transcription_engines[engine_id]
            if engine_id in self._voice_conversion_engines:
                del self._voice_conversion_engines[engine_id]
            if engine_id == "emotion":
                self._emotion_engine = None
            if engine_id == "translation":
                self._translation_engine = None
            return True
        except Exception as e:
            logger.error(f"Failed to unload engine {engine_id}: {e}")
            return False

    def get_synthesis_engine(self, engine_id: str | None = None) -> SynthesisEngineAdapter:
        """Get a synthesis engine instance."""
        engine_id = engine_id or "xtts"
        if engine_id not in self._synthesis_engines:
            self._synthesis_engines[engine_id] = SynthesisEngineAdapter(engine_id)
        return self._synthesis_engines[engine_id]

    def get_transcription_engine(self, engine_id: str | None = None) -> TranscriptionEngineAdapter:
        """Get a transcription engine instance."""
        engine_id = engine_id or "whisper"
        if engine_id not in self._transcription_engines:
            self._transcription_engines[engine_id] = TranscriptionEngineAdapter(engine_id)
        return self._transcription_engines[engine_id]

    def get_voice_conversion_engine(
        self, engine_id: str | None = None
    ) -> VoiceConversionEngineAdapter:
        """Get a voice conversion engine instance."""
        engine_id = engine_id or "rvc"
        if engine_id not in self._voice_conversion_engines:
            self._voice_conversion_engines[engine_id] = VoiceConversionEngineAdapter(engine_id)
        return self._voice_conversion_engines[engine_id]

    def get_emotion_engine(self) -> EmotionEngineAdapter:
        """Get the emotion engine instance."""
        if self._emotion_engine is None:
            self._emotion_engine = EmotionEngineAdapter()
        return self._emotion_engine

    def get_translation_engine(self) -> TranslationEngineAdapter:
        """Get the translation engine instance."""
        if self._translation_engine is None:
            self._translation_engine = TranslationEngineAdapter()
        return self._translation_engine


# Singleton instance
_engine_adapter: EngineAdapter | None = None


def get_engine_service() -> EngineAdapter:
    """
    Get the singleton engine adapter instance.

    This is the primary entry point for routes to access engines.

    Usage:
        from backend.adapters.engine_adapter import get_engine_service

        engine_service = get_engine_service()
        tts_engine = engine_service.get_synthesis_engine()
        result = await tts_engine.synthesize(request)
    """
    global _engine_adapter
    if _engine_adapter is None:
        _engine_adapter = EngineAdapter()
    return _engine_adapter
