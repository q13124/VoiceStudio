"""
Mock LLM/S2S Providers for Testing (Phase 14.1.4)

Test doubles for pipeline and supervisor tests that don't
require actual LLM or S2S service connections.
"""

import asyncio
from collections.abc import AsyncIterator

from app.core.engines.llm_interface import (
    BaseLLMProvider,
    FunctionSpec,
    Intent,
    IntentType,
    LLMConfig,
    LLMResponse,
    Message,
)
from app.core.engines.s2s_protocol import (
    BaseS2SProvider,
    S2SConfig,
    S2SConnectionState,
    S2SResponse,
)


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing pipeline and supervisor."""

    def __init__(
        self,
        response_text: str = "This is a mock response.",
        config: LLMConfig | None = None,
        latency_ms: float = 10.0,
        stream_tokens: list[str] | None = None,
    ):
        super().__init__(config)
        self._response_text = response_text
        self._latency_ms = latency_ms
        self._stream_tokens = stream_tokens or response_text.split()
        self._call_count = 0

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def is_available(self) -> bool:
        return True

    async def generate(
        self,
        messages: list[Message],
        config: LLMConfig | None = None,
        functions: list[FunctionSpec] | None = None,
    ) -> LLMResponse:
        self._call_count += 1
        await asyncio.sleep(self._latency_ms / 1000.0)
        return LLMResponse(
            content=self._response_text,
            finish_reason="stop",
            model="mock-model",
            latency_ms=self._latency_ms,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        )

    async def generate_stream(
        self,
        messages: list[Message],
        config: LLMConfig | None = None,
        functions: list[FunctionSpec] | None = None,
    ) -> AsyncIterator[str]:
        self._call_count += 1
        for token in self._stream_tokens:
            await asyncio.sleep(1 / 1000.0)  # 1ms per token
            yield token + " "

    async def classify_intent(self, text: str) -> Intent:
        return Intent(
            intent_type=IntentType.CASUAL,
            confidence=0.9,
            raw_text=text,
        )

    @property
    def call_count(self) -> int:
        return self._call_count


class MockS2SProvider(BaseS2SProvider):
    """Mock S2S provider for testing supervisor routing."""

    def __init__(
        self,
        response_audio: bytes = b"\x00" * 4800,  # 100ms at 24kHz, 16-bit
        response_text: str = "Mock S2S response",
        config: S2SConfig | None = None,
        latency_ms: float = 50.0,
    ):
        super().__init__(config)
        self._response_audio = response_audio
        self._response_text = response_text
        self._latency_ms = latency_ms
        self._call_count = 0

    @property
    def provider_name(self) -> str:
        return "mock_s2s"

    @property
    def is_available(self) -> bool:
        return True

    async def connect(self, config: S2SConfig | None = None) -> bool:
        self._state = S2SConnectionState.CONNECTED
        return True

    async def disconnect(self) -> None:
        self._state = S2SConnectionState.DISCONNECTED

    async def send_audio(self, audio_data: bytes) -> None:
        self._state = S2SConnectionState.ACTIVE

    async def receive_audio(self) -> AsyncIterator[S2SResponse]:
        yield S2SResponse(
            audio_data=self._response_audio,
            response_text=self._response_text,
            is_final=True,
            latency_ms=self._latency_ms,
        )

    async def respond(
        self, audio_data: bytes, context: str | None = None
    ) -> S2SResponse:
        self._call_count += 1
        await asyncio.sleep(self._latency_ms / 1000.0)
        self._turn_count += 1
        return S2SResponse(
            audio_data=self._response_audio,
            response_text=self._response_text,
            is_final=True,
            latency_ms=self._latency_ms,
            usage={"input_tokens": 100, "output_tokens": 50},
        )

    async def interrupt(self) -> None:
        """Interrupt current generation."""
        self._state = S2SConnectionState.CONNECTED
        # No-op for mock

    @property
    def connection_state(self) -> S2SConnectionState:
        """Get current connection state."""
        return self._state

    @property
    def call_count(self) -> int:
        return self._call_count
