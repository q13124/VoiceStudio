"""
Local LLM Adapter for VoiceStudio (Phase 9.1.2)

Implements LLM provider using Ollama for local-first, offline-capable
language model inference. No API keys or cloud services required.

Ollama must be running locally (default: http://localhost:11434).
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import AsyncIterator
from typing import Any

logger = logging.getLogger(__name__)

try:
    import httpx

    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False

from .llm_interface import (
    BaseLLMProvider,
    FunctionSpec,
    Intent,
    IntentType,
    LLMConfig,
    LLMResponse,
    Message,
    MessageRole,
)


class OllamaLLMProvider(BaseLLMProvider):
    """
    Local LLM provider using Ollama.

    Ollama provides local model inference without cloud dependencies.
    Supports streaming, multiple models, and runs fully offline.

    Default model: llama3.2 (or configurable via LLMConfig.model)
    Default URL: http://localhost:11434 (or via LLMConfig.base_url)
    """

    DEFAULT_MODEL = "llama3.2"
    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, config: LLMConfig | None = None):
        super().__init__(config)
        if not self._config.model:
            self._config.model = self.DEFAULT_MODEL
        if not self._config.base_url:
            self._config.base_url = self.DEFAULT_BASE_URL
        self._client: Any | None = None

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def is_available(self) -> bool:
        """Check if Ollama is running locally."""
        if not _HAS_HTTPX:
            return False
        try:
            import httpx as hx

            with hx.Client(timeout=2.0) as client:
                resp = client.get(f"{self._config.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    def _get_client(self) -> Any:
        """Get or create httpx async client."""
        if self._client is None:
            if not _HAS_HTTPX:
                raise RuntimeError(
                    "httpx is required for Ollama integration. " "Install with: pip install httpx"
                )
            import httpx as hx

            self._client = hx.AsyncClient(
                base_url=self._config.base_url or "http://localhost:11434",
                timeout=hx.Timeout(self._config.timeout_seconds),
            )
        return self._client

    async def generate(
        self,
        messages: list[Message],
        config: LLMConfig | None = None,
        functions: list[FunctionSpec] | None = None,
    ) -> LLMResponse:
        """Generate a response using Ollama's chat API."""
        cfg = self._merge_config(config)
        msgs = self._prepend_system_prompt(messages, cfg)

        payload: dict[str, Any] = {
            "model": cfg.model,
            "messages": [m.to_dict() for m in msgs],
            "stream": False,
            "options": {
                "temperature": cfg.temperature,
                "num_predict": cfg.max_tokens,
                "top_p": cfg.top_p,
            },
        }

        if functions:
            payload["tools"] = [f.to_dict() for f in functions]

        start_time = time.perf_counter()
        client = self._get_client()

        try:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            tool_calls = None
            message_data = data.get("message", {})
            if message_data.get("tool_calls"):
                tool_calls = message_data["tool_calls"]

            return LLMResponse(
                content=message_data.get("content", ""),
                finish_reason="stop",
                tool_calls=tool_calls,
                model=cfg.model,
                latency_ms=latency_ms,
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": (data.get("prompt_eval_count", 0) + data.get("eval_count", 0)),
                },
            )
        except Exception as exc:
            logger.error(f"Ollama generate failed: {exc}")
            raise

    async def generate_stream(
        self,
        messages: list[Message],
        config: LLMConfig | None = None,
        functions: list[FunctionSpec] | None = None,
    ) -> AsyncIterator[str]:
        """Stream tokens from Ollama."""
        cfg = self._merge_config(config)
        msgs = self._prepend_system_prompt(messages, cfg)

        payload: dict[str, Any] = {
            "model": cfg.model,
            "messages": [m.to_dict() for m in msgs],
            "stream": True,
            "options": {
                "temperature": cfg.temperature,
                "num_predict": cfg.max_tokens,
                "top_p": cfg.top_p,
            },
        }

        if functions:
            payload["tools"] = [f.to_dict() for f in functions]

        client = self._get_client()

        try:
            async with client.stream("POST", "/api/chat", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    try:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
                        if chunk.get("done", False):
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception as exc:
            logger.error(f"Ollama stream failed: {exc}")
            raise

    async def classify_intent(self, text: str) -> Intent:
        """
        Classify intent using the local LLM for higher accuracy.

        Falls back to keyword heuristics if the model is unavailable.
        """
        if not self.is_available:
            return await super().classify_intent(text)

        try:
            classification_prompt = Message(
                role=MessageRole.USER,
                content=(
                    f"Classify the following user message into one category: "
                    f"'casual', 'complex_reasoning', 'tool_call', or 'voice_command'. "
                    f"Respond with ONLY the category name, nothing else.\n\n"
                    f"Message: {text}"
                ),
            )
            # Use a very short config for classification
            fast_config = LLMConfig(
                model=self._config.model,
                temperature=0.0,
                max_tokens=20,
                base_url=self._config.base_url,
            )

            response = await self.generate(
                [classification_prompt],
                config=fast_config,
            )

            category = response.content.strip().lower()
            intent_map = {
                "casual": IntentType.CASUAL,
                "complex_reasoning": IntentType.COMPLEX_REASONING,
                "tool_call": IntentType.TOOL_CALL,
                "voice_command": IntentType.VOICE_COMMAND,
            }

            intent_type = intent_map.get(category, IntentType.UNKNOWN)
            return Intent(
                intent_type=intent_type,
                confidence=0.85 if intent_type != IntentType.UNKNOWN else 0.3,
                raw_text=text,
            )
        except Exception as exc:
            logger.warning(f"LLM-based classification failed, using heuristics: {exc}")
            return await super().classify_intent(text)

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None


class LocalAILLMProvider(BaseLLMProvider):
    """
    Local LLM provider using LocalAI (OpenAI-compatible local server).

    LocalAI provides an OpenAI-compatible API for local inference.
    Default URL: http://localhost:8080
    """

    DEFAULT_MODEL = "gpt-3.5-turbo"  # LocalAI model alias
    DEFAULT_BASE_URL = "http://localhost:8080"

    def __init__(self, config: LLMConfig | None = None):
        super().__init__(config)
        if not self._config.model:
            self._config.model = self.DEFAULT_MODEL
        if not self._config.base_url:
            self._config.base_url = self.DEFAULT_BASE_URL
        self._client: Any | None = None

    @property
    def provider_name(self) -> str:
        return "localai"

    @property
    def is_available(self) -> bool:
        if not _HAS_HTTPX:
            return False
        try:
            import httpx as hx

            with hx.Client(timeout=2.0) as client:
                resp = client.get(f"{self._config.base_url}/v1/models")
                return resp.status_code == 200
        except Exception:
            return False

    def _get_client(self) -> Any:
        if self._client is None:
            if not _HAS_HTTPX:
                raise RuntimeError("httpx is required. Install with: pip install httpx")
            import httpx as hx

            self._client = hx.AsyncClient(
                base_url=self._config.base_url or "http://localhost:11434",
                timeout=hx.Timeout(self._config.timeout_seconds),
            )
        return self._client

    async def generate(
        self,
        messages: list[Message],
        config: LLMConfig | None = None,
        functions: list[FunctionSpec] | None = None,
    ) -> LLMResponse:
        """Generate using OpenAI-compatible chat completions API."""
        cfg = self._merge_config(config)
        msgs = self._prepend_system_prompt(messages, cfg)

        payload: dict[str, Any] = {
            "model": cfg.model,
            "messages": [m.to_dict() for m in msgs],
            "temperature": cfg.temperature,
            "max_tokens": cfg.max_tokens,
            "top_p": cfg.top_p,
            "stream": False,
        }

        if functions:
            payload["tools"] = [f.to_dict() for f in functions]

        start_time = time.perf_counter()
        client = self._get_client()

        try:
            response = await client.post("/v1/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000
            choice = data.get("choices", [{}])[0]
            message_data = choice.get("message", {})

            return LLMResponse(
                content=message_data.get("content", ""),
                finish_reason=choice.get("finish_reason", "stop"),
                tool_calls=message_data.get("tool_calls"),
                model=data.get("model", cfg.model),
                latency_ms=latency_ms,
                usage=data.get("usage"),
            )
        except Exception as exc:
            logger.error(f"LocalAI generate failed: {exc}")
            raise

    async def generate_stream(
        self,
        messages: list[Message],
        config: LLMConfig | None = None,
        functions: list[FunctionSpec] | None = None,
    ) -> AsyncIterator[str]:
        """Stream tokens using OpenAI-compatible SSE endpoint."""
        cfg = self._merge_config(config)
        msgs = self._prepend_system_prompt(messages, cfg)

        payload: dict[str, Any] = {
            "model": cfg.model,
            "messages": [m.to_dict() for m in msgs],
            "temperature": cfg.temperature,
            "max_tokens": cfg.max_tokens,
            "stream": True,
        }

        client = self._get_client()

        try:
            async with client.stream("POST", "/v1/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
        except Exception as exc:
            logger.error(f"LocalAI stream failed: {exc}")
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
