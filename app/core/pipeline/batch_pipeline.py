"""
Batch Pipeline Mode for VoiceStudio (Phase 9.2.3)

High-quality sequential processing for non-real-time scenarios.
Prioritizes quality over latency -- full transcription, complete
LLM response, then full synthesis.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BatchResult:
    """Result from batch pipeline processing."""
    input_text: str
    transcription: str | None = None
    llm_response: str = ""
    audio_data: bytes | None = None
    audio_path: str | None = None
    metrics: dict[str, float] | None = None
    error: str | None = None


class BatchPipeline:
    """
    Batch pipeline for high-quality sequential processing.

    Use this mode when latency is not critical and quality is paramount.
    Processes the complete STT → LLM → TTS chain sequentially with
    full context and highest quality settings.
    """

    def __init__(
        self,
        llm_provider=None,
        stt_engine: str = "whisper",
        tts_engine: str = "xtts_v2",
        language: str = "en",
    ):
        self._llm_provider = llm_provider
        self._stt_engine = stt_engine
        self._tts_engine = tts_engine
        self._language = language

    async def process_audio(
        self,
        audio_data: bytes,
        sample_rate: int = 16000,
        context: list[dict[str, str]] | None = None,
    ) -> BatchResult:
        """
        Process audio through the complete batch pipeline.

        Args:
            audio_data: Complete audio input.
            sample_rate: Sample rate of the audio.
            context: Optional conversation context.

        Returns:
            BatchResult with all pipeline outputs.
        """
        total_start = time.perf_counter()
        metrics: dict[str, float] = {}

        # Stage 1: Full STT
        stt_start = time.perf_counter()
        try:
            transcription = await self._transcribe(audio_data, sample_rate)
            metrics["stt_ms"] = (time.perf_counter() - stt_start) * 1000
        except Exception as exc:
            return BatchResult(
                input_text="",
                error=f"STT failed: {exc}",
                metrics=metrics,
            )

        if not transcription.strip():
            return BatchResult(input_text="", transcription="", metrics=metrics)

        # Stage 2: Full LLM response
        llm_start = time.perf_counter()
        try:
            llm_response = await self._generate(transcription, context)
            metrics["llm_ms"] = (time.perf_counter() - llm_start) * 1000
        except Exception as exc:
            return BatchResult(
                input_text=transcription,
                transcription=transcription,
                error=f"LLM failed: {exc}",
                metrics=metrics,
            )

        # Stage 3: Full TTS synthesis
        tts_start = time.perf_counter()
        try:
            audio_output = await self._synthesize(llm_response)
            metrics["tts_ms"] = (time.perf_counter() - tts_start) * 1000
        except Exception as exc:
            return BatchResult(
                input_text=transcription,
                transcription=transcription,
                llm_response=llm_response,
                error=f"TTS failed: {exc}",
                metrics=metrics,
            )

        metrics["total_ms"] = (time.perf_counter() - total_start) * 1000

        return BatchResult(
            input_text=transcription,
            transcription=transcription,
            llm_response=llm_response,
            audio_data=audio_output,
            metrics=metrics,
        )

    async def process_text(
        self,
        text: str,
        context: list[dict[str, str]] | None = None,
        synthesize: bool = True,
    ) -> BatchResult:
        """
        Process text through LLM → TTS pipeline.

        Args:
            text: Input text.
            context: Conversation context.
            synthesize: Whether to synthesize TTS output.

        Returns:
            BatchResult with response and optional audio.
        """
        total_start = time.perf_counter()
        metrics: dict[str, float] = {}

        # LLM
        llm_start = time.perf_counter()
        try:
            llm_response = await self._generate(text, context)
            metrics["llm_ms"] = (time.perf_counter() - llm_start) * 1000
        except Exception as exc:
            return BatchResult(input_text=text, error=f"LLM failed: {exc}", metrics=metrics)

        # TTS (optional)
        audio_output = None
        if synthesize and llm_response.strip():
            tts_start = time.perf_counter()
            try:
                audio_output = await self._synthesize(llm_response)
                metrics["tts_ms"] = (time.perf_counter() - tts_start) * 1000
            except Exception as exc:
                logger.warning(f"TTS synthesis failed (non-fatal): {exc}")

        metrics["total_ms"] = (time.perf_counter() - total_start) * 1000

        return BatchResult(
            input_text=text,
            llm_response=llm_response,
            audio_data=audio_output,
            metrics=metrics,
        )

    async def process_batch(
        self,
        items: list[str],
        synthesize: bool = True,
    ) -> list[BatchResult]:
        """Process multiple text items through the pipeline."""
        results = []
        for item in items:
            result = await self.process_text(item, synthesize=synthesize)
            results.append(result)
        return results

    async def _transcribe(self, audio_data: bytes, sample_rate: int = 16000) -> str:
        """Full transcription using STT engine."""
        try:
            from backend.services.engine_service import get_engine_service
            service = get_engine_service()
            result = await service.transcribe(
                audio_data=audio_data,
                sample_rate=sample_rate,
                engine=self._stt_engine,
                language=self._language,
            )
            return result.get("text", "")
        except Exception as exc:
            raise RuntimeError(f"Transcription failed: {exc}") from exc

    async def _generate(
        self, text: str, context: list[dict[str, str]] | None = None
    ) -> str:
        """Generate full LLM response."""
        if self._llm_provider is None:
            raise RuntimeError("No LLM provider available")

        from app.core.engines.llm_interface import Message, MessageRole

        messages = []
        if context:
            for msg in context:
                role = MessageRole.USER if msg.get("role") == "user" else MessageRole.ASSISTANT
                messages.append(Message(role=role, content=msg.get("content", "")))
        messages.append(Message(role=MessageRole.USER, content=text))

        response = await self._llm_provider.generate(messages)
        return response.content

    async def _synthesize(self, text: str) -> bytes | None:
        """Full TTS synthesis."""
        if not text.strip():
            return None
        try:
            from backend.services.engine_service import get_engine_service
            service = get_engine_service()
            result = await service.synthesize(
                text=text,
                engine=self._tts_engine,
                language=self._language,
            )
            return result.get("audio_data")
        except Exception as exc:
            raise RuntimeError(f"Synthesis failed: {exc}") from exc
