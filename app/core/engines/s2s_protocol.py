"""
Speech-to-Speech Protocol for VoiceStudio (Phase 10.1.1)

Defines the interface for end-to-end speech-to-speech models
that convert audio directly to audio without intermediate text.
"""

from __future__ import annotations

import logging
from abc import abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from .base import EngineProtocol

logger = logging.getLogger(__name__)


class S2SConnectionState(str, Enum):
    """Connection state for S2S providers."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ACTIVE = "active"  # Audio flowing
    ERROR = "error"


@dataclass
class S2SConfig:
    """Configuration for S2S provider."""
    model: str = ""
    voice: str = "alloy"
    language: str = "en"
    modalities: list[str] = field(default_factory=lambda: ["text", "audio"])
    temperature: float = 0.8
    max_response_tokens: int = 4096
    # Connection
    api_key: str | None = None
    base_url: str | None = None
    # Audio format
    input_format: str = "pcm16"
    output_format: str = "pcm16"
    sample_rate: int = 24000
    # Behavior
    turn_detection: str = "server_vad"
    silence_threshold_ms: int = 500
    enable_interruption: bool = True
    # Cost management
    token_ceiling: int = 0  # 0 = unlimited
    context_window_tokens: int = 128000


@dataclass
class S2SResponse:
    """Response from an S2S provider."""
    audio_data: bytes | None = None
    transcript: str | None = None  # If provider generates transcript
    response_text: str | None = None
    is_final: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, int] | None = None
    latency_ms: float = 0.0


@runtime_checkable
class S2SProviderProtocol(Protocol):
    """
    Protocol for speech-to-speech providers.

    Supports persistent WebSocket connections for real-time
    bidirectional audio streaming.
    """

    @property
    def provider_name(self) -> str: ...

    @property
    def connection_state(self) -> S2SConnectionState: ...

    @property
    def is_available(self) -> bool: ...

    async def connect(self, config: S2SConfig | None = None) -> bool: ...

    async def disconnect(self) -> None: ...

    async def send_audio(self, audio_data: bytes) -> None: ...

    async def receive_audio(self) -> AsyncIterator[S2SResponse]: ...

    async def respond(
        self, audio_data: bytes, context: str | None = None
    ) -> S2SResponse: ...

    async def interrupt(self) -> None: ...


class BaseS2SProvider(EngineProtocol):
    """
    Abstract base class for speech-to-speech providers.

    Provides common connection management, audio buffering, and
    metrics tracking for S2S implementations.

    Inherits from EngineProtocol to integrate with VoiceStudio's
    engine router and lifecycle management.
    """

    def __init__(self, config: S2SConfig | None = None, device: str | None = None, gpu: bool = False):
        # S2S providers are typically cloud-based, so default to cpu (no local GPU needed)
        super().__init__(device=device, gpu=gpu)
        self._config = config or S2SConfig()
        self._state = S2SConnectionState.DISCONNECTED
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._turn_count = 0
        logger.info(f"{self.__class__.__name__} provider created")

    def initialize(self) -> bool:
        """
        Initialize the S2S provider.

        For S2S providers, initialization is minimal since actual
        connection happens via connect(). This marks the provider as ready.

        Returns:
            True (S2S providers are always initializable)
        """
        self._initialized = True
        logger.info(f"{self.__class__.__name__} initialized")
        return True

    def cleanup(self) -> None:
        """
        Clean up S2S provider resources.

        For async disconnect, use disconnect() directly. This provides
        synchronous cleanup for the engine lifecycle.
        """
        self._state = S2SConnectionState.DISCONNECTED
        self._initialized = False
        logger.info(f"{self.__class__.__name__} cleaned up")

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    def connection_state(self) -> S2SConnectionState:
        return self._state

    @property
    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    async def connect(self, config: S2SConfig | None = None) -> bool: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def send_audio(self, audio_data: bytes) -> None: ...

    @abstractmethod
    async def receive_audio(self) -> AsyncIterator[S2SResponse]: ...

    @abstractmethod
    async def respond(
        self, audio_data: bytes, context: str | None = None
    ) -> S2SResponse: ...

    async def interrupt(self) -> None:
        """Interrupt current generation. Override for provider-specific logic."""
        logger.info(f"{self.provider_name}: Interrupt requested")

    def get_usage(self) -> dict[str, Any]:
        """Get token usage statistics."""
        return {
            "provider": self.provider_name,
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "turn_count": self._turn_count,
            "token_ceiling": self._config.token_ceiling,
            "at_ceiling": (
                self._config.token_ceiling > 0
                and (self._total_input_tokens + self._total_output_tokens) >= self._config.token_ceiling
            ),
        }

    def _check_token_ceiling(self) -> bool:
        """Check if the token ceiling has been reached."""
        if self._config.token_ceiling <= 0:
            return False
        total = self._total_input_tokens + self._total_output_tokens
        return total >= self._config.token_ceiling

    def _enforce_token_ceiling(self) -> None:
        """
        Enforce the token ceiling by raising an exception if reached.

        Implementations should call this in send_audio() and respond()
        before processing to prevent cost overruns.

        Raises:
            TokenCeilingExceeded: If the token ceiling has been reached.
        """
        if self._check_token_ceiling():
            logger.warning(
                f"{self.provider_name}: Token ceiling reached "
                f"({self._total_input_tokens + self._total_output_tokens} >= "
                f"{self._config.token_ceiling})"
            )
            raise TokenCeilingExceeded(
                f"Token ceiling of {self._config.token_ceiling} reached for "
                f"{self.provider_name}"
            )

    def _update_token_counts(
        self, input_tokens: int = 0, output_tokens: int = 0
    ) -> None:
        """Update token counts after a turn."""
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens
        self._turn_count += 1


class TokenCeilingExceeded(Exception):
    """Raised when S2S token ceiling is exceeded."""
    pass
