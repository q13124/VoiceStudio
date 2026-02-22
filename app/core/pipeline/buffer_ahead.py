"""
Buffer-Ahead Synthesis for VoiceStudio (Phase 9.3.2)

Implements the buffer-ahead pattern where TTS synthesis begins
before the LLM has completed generating its response.
Tokens are accumulated until a sentence boundary, then sent to
TTS for synthesis while the LLM continues generating.
"""

import asyncio
import logging
import time
from collections import deque
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AudioSegment:
    """A synthesized audio segment ready for playback."""

    text: str
    audio_data: bytes
    segment_index: int
    latency_ms: float = 0.0


class SentenceDetector:
    """
    Detects sentence boundaries in streaming text.

    Accumulates tokens and flushes when a complete sentence
    is detected, enabling buffer-ahead TTS synthesis.
    """

    SENTENCE_ENDINGS = {".", "!", "?", "\n"}
    MIN_SENTENCE_LENGTH = 10  # Minimum chars before flushing

    def __init__(self):
        self._buffer = ""
        self._sentences: deque[str] = deque()

    def add_token(self, token: str) -> str | None:
        """
        Add a token and return a complete sentence if available.

        Returns:
            Complete sentence string, or None if still accumulating.
        """
        self._buffer += token

        # Check for sentence boundary
        for ending in self.SENTENCE_ENDINGS:
            if self._buffer.rstrip().endswith(ending):
                if len(self._buffer.strip()) >= self.MIN_SENTENCE_LENGTH:
                    sentence: str = self._buffer.strip()
                    self._buffer = ""
                    return sentence

        return None

    def flush(self) -> str | None:
        """Flush any remaining text in the buffer."""
        if self._buffer.strip():
            sentence: str = self._buffer.strip()
            self._buffer = ""
            return sentence
        return None

    def reset(self) -> None:
        """Reset the detector."""
        self._buffer = ""
        self._sentences.clear()


class BufferAheadSynthesizer:
    """
    Coordinates buffer-ahead TTS synthesis with LLM streaming.

    As the LLM streams tokens, this component:
    1. Detects sentence boundaries
    2. Queues sentences for TTS synthesis
    3. Manages a synthesis queue for playback
    4. Enables audio playback to begin before LLM finishes
    """

    def __init__(
        self,
        synthesize_fn: Callable[[str], Any],
        max_queue_size: int = 5,
    ):
        self._synthesize_fn = synthesize_fn
        self._sentence_detector = SentenceDetector()
        self._audio_queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._segment_index = 0
        self._synthesis_tasks: list = []

    async def process_token_stream(
        self,
        token_stream: AsyncIterator[str],
    ) -> AsyncIterator[AudioSegment]:
        """
        Process a stream of LLM tokens and yield audio segments.

        Args:
            token_stream: Async iterator of LLM tokens.

        Yields:
            AudioSegment objects as sentences are synthesized.
        """
        try:
            async for token in token_stream:
                sentence = self._sentence_detector.add_token(token)
                if sentence:
                    start = time.perf_counter()
                    audio_data = await self._synthesize_fn(sentence)
                    latency = (time.perf_counter() - start) * 1000

                    if audio_data:
                        segment = AudioSegment(
                            text=sentence,
                            audio_data=audio_data,
                            segment_index=self._segment_index,
                            latency_ms=latency,
                        )
                        self._segment_index += 1
                        yield segment

            # Flush remaining text
            remaining = self._sentence_detector.flush()
            if remaining:
                start = time.perf_counter()
                audio_data = await self._synthesize_fn(remaining)
                latency = (time.perf_counter() - start) * 1000

                if audio_data:
                    yield AudioSegment(
                        text=remaining,
                        audio_data=audio_data,
                        segment_index=self._segment_index,
                        latency_ms=latency,
                    )

        except Exception as exc:
            logger.error(f"Buffer-ahead synthesis error: {exc}")
            raise

    def reset(self) -> None:
        """Reset the synthesizer state."""
        self._sentence_detector.reset()
        self._segment_index = 0
        self._synthesis_tasks.clear()
