"""
LLM Provider Interface for VoiceStudio (Phase 9.1.1)

Defines the abstract protocol that all LLM providers must implement.
Supports both local (Ollama) and cloud (OpenAI) providers through
a unified interface with streaming and function-calling support.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    AsyncIterator,
    Dict,
    List,
    Optional,
    Protocol,
    runtime_checkable,
)
import logging

logger = logging.getLogger(__name__)


class MessageRole(str, Enum):
    """Role in a conversation message."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


@dataclass
class Message:
    """A single message in a conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for API calls."""
        result: Dict[str, Any] = {
            "role": self.role.value,
            "content": self.content,
        }
        if self.name:
            result["name"] = self.name
        if self.function_call:
            result["function_call"] = self.function_call
        if self.tool_calls:
            result["tool_calls"] = self.tool_calls
        if self.tool_call_id:
            result["tool_call_id"] = self.tool_call_id
        return result


@dataclass
class FunctionSpec:
    """Specification for a callable function the LLM can invoke."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema for parameters

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for API calls."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    finish_reason: str = "stop"
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, int]] = None  # prompt_tokens, completion_tokens, total_tokens
    model: str = ""
    latency_ms: float = 0.0


@dataclass
class LLMConfig:
    """Configuration for LLM provider."""
    model: str = ""
    temperature: float = 0.7
    max_tokens: int = 1024
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    system_prompt: Optional[str] = None
    timeout_seconds: float = 30.0
    # Provider-specific
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)


class IntentType(str, Enum):
    """Types of user intent detected from text."""
    CASUAL = "casual"
    COMPLEX_REASONING = "complex_reasoning"
    TOOL_CALL = "tool_call"
    VOICE_COMMAND = "voice_command"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Detected intent from user text."""
    intent_type: IntentType
    confidence: float  # 0.0 to 1.0
    entities: Dict[str, Any] = field(default_factory=dict)
    raw_text: str = ""


@runtime_checkable
class LLMProviderProtocol(Protocol):
    """
    Protocol that all LLM providers must implement.

    Supports synchronous responses, streaming, and function calling.
    Local-first: Ollama/LocalAI adapters are primary; cloud adapters optional.
    """

    @property
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'ollama', 'openai')."""
        ...

    @property
    def is_available(self) -> bool:
        """Check if the provider is currently available."""
        ...

    async def generate(
        self,
        messages: List[Message],
        config: Optional[LLMConfig] = None,
        functions: Optional[List[FunctionSpec]] = None,
    ) -> LLMResponse:
        """
        Generate a single response from the LLM.

        Args:
            messages: Conversation history.
            config: Optional configuration overrides.
            functions: Optional function specifications for tool calling.

        Returns:
            LLMResponse with content and metadata.
        """
        ...

    async def generate_stream(
        self,
        messages: List[Message],
        config: Optional[LLMConfig] = None,
        functions: Optional[List[FunctionSpec]] = None,
    ) -> AsyncIterator[str]:
        """
        Stream tokens from the LLM as they are generated.

        Args:
            messages: Conversation history.
            config: Optional configuration overrides.
            functions: Optional function specifications for tool calling.

        Yields:
            Token strings as they are generated.
        """
        ...

    async def classify_intent(self, text: str) -> Intent:
        """
        Classify user intent from text input.

        Used by the supervisor to route between pipeline modes.

        Args:
            text: Raw user text.

        Returns:
            Intent with type and confidence.
        """
        ...


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Provides common functionality like configuration management,
    conversation history formatting, and intent classification fallback.
    """

    def __init__(self, config: Optional[LLMConfig] = None):
        self._config = config or LLMConfig()
        self._initialized = False
        logger.info(f"{self.__class__.__name__} provider created")

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        ...

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is currently available."""
        ...

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        config: Optional[LLMConfig] = None,
        functions: Optional[List[FunctionSpec]] = None,
    ) -> LLMResponse:
        """Generate a single response."""
        ...

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        config: Optional[LLMConfig] = None,
        functions: Optional[List[FunctionSpec]] = None,
    ) -> AsyncIterator[str]:
        """Stream tokens from the LLM."""
        ...

    async def classify_intent(self, text: str) -> Intent:
        """
        Default intent classification using keyword heuristics.

        Override in subclasses for model-based classification.
        """
        text_lower = text.lower().strip()

        # Simple heuristic classification
        tool_keywords = [
            "generate", "synthesize", "clone", "convert", "create",
            "adjust", "change", "set", "apply", "export", "import",
            "train", "process", "render",
        ]
        complex_keywords = [
            "explain", "analyze", "compare", "why", "how does",
            "what if", "recommend", "optimize", "debug", "calculate",
        ]

        for keyword in tool_keywords:
            if keyword in text_lower:
                return Intent(
                    intent_type=IntentType.TOOL_CALL,
                    confidence=0.7,
                    raw_text=text,
                )

        for keyword in complex_keywords:
            if keyword in text_lower:
                return Intent(
                    intent_type=IntentType.COMPLEX_REASONING,
                    confidence=0.6,
                    raw_text=text,
                )

        # Default to casual
        return Intent(
            intent_type=IntentType.CASUAL,
            confidence=0.5,
            raw_text=text,
        )

    def _merge_config(self, override: Optional[LLMConfig] = None) -> LLMConfig:
        """Merge override config with default config."""
        if override is None:
            return self._config

        return LLMConfig(
            model=override.model or self._config.model,
            temperature=override.temperature,
            max_tokens=override.max_tokens,
            top_p=override.top_p,
            frequency_penalty=override.frequency_penalty,
            presence_penalty=override.presence_penalty,
            stop_sequences=override.stop_sequences or self._config.stop_sequences,
            system_prompt=override.system_prompt or self._config.system_prompt,
            timeout_seconds=override.timeout_seconds,
            api_key=override.api_key or self._config.api_key,
            base_url=override.base_url or self._config.base_url,
            extra={**self._config.extra, **override.extra},
        )

    def _prepend_system_prompt(
        self, messages: List[Message], config: LLMConfig
    ) -> List[Message]:
        """Prepend system prompt if configured and not already present."""
        if not config.system_prompt:
            return messages

        if messages and messages[0].role == MessageRole.SYSTEM:
            return messages

        system_msg = Message(
            role=MessageRole.SYSTEM,
            content=config.system_prompt,
        )
        return [system_msg] + list(messages)
