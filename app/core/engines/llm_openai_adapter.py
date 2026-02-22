"""
OpenAI LLM Adapter for VoiceStudio (Phase 9.1.3)

Implements LLM provider using OpenAI's chat completions API.
This is an optional cloud adapter -- local providers (Ollama) are preferred
per the local-first policy. Only use when local models are insufficient.

Requires: OPENAI_API_KEY environment variable.
"""

from __future__ import annotations

import json
import logging
import os
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
    LLMConfig,
    LLMResponse,
    Message,
)


class OpenAILLMProvider(BaseLLMProvider):
    """
    Cloud LLM provider using OpenAI's chat completions API.

    Note: Per project policy (free-only, local-first), this adapter is
    optional and only used when explicitly enabled by the user.
    The API key is never stored in code -- it must be set via environment
    variable OPENAI_API_KEY or passed in LLMConfig.api_key.
    """

    DEFAULT_MODEL = "gpt-4o-mini"
    DEFAULT_BASE_URL = "https://api.openai.com"

    def __init__(self, config: LLMConfig | None = None):
        super().__init__(config)
        if not self._config.model:
            self._config.model = self.DEFAULT_MODEL
        if not self._config.base_url:
            self._config.base_url = self.DEFAULT_BASE_URL
        if not self._config.api_key:
            self._config.api_key = os.getenv("OPENAI_API_KEY", "")
        self._client: Any | None = None

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def is_available(self) -> bool:
        """Check if API key is configured."""
        return bool(self._config.api_key)

    def _get_client(self) -> Any:
        if self._client is None:
            if not _HAS_HTTPX:
                raise RuntimeError("httpx is required. Install with: pip install httpx")
            if not self._config.api_key:
                raise RuntimeError(
                    "OpenAI API key not configured. " "Set OPENAI_API_KEY environment variable."
                )
            import httpx as hx

            self._client = hx.AsyncClient(
                base_url=self._config.base_url,
                headers={
                    "Authorization": f"Bearer {self._config.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=hx.Timeout(self._config.timeout_seconds),
            )
        return self._client

    async def generate(
        self,
        messages: list[Message],
        config: LLMConfig | None = None,
        functions: list[FunctionSpec] | None = None,
    ) -> LLMResponse:
        """Generate a response using OpenAI chat completions."""
        cfg = self._merge_config(config)
        msgs = self._prepend_system_prompt(messages, cfg)

        payload: dict[str, Any] = {
            "model": cfg.model,
            "messages": [m.to_dict() for m in msgs],
            "temperature": cfg.temperature,
            "max_tokens": cfg.max_tokens,
            "top_p": cfg.top_p,
            "frequency_penalty": cfg.frequency_penalty,
            "presence_penalty": cfg.presence_penalty,
            "stream": False,
        }

        if cfg.stop_sequences:
            payload["stop"] = cfg.stop_sequences

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
                content=message_data.get("content", "") or "",
                finish_reason=choice.get("finish_reason", "stop"),
                function_call=message_data.get("function_call"),
                tool_calls=message_data.get("tool_calls"),
                model=data.get("model", cfg.model),
                latency_ms=latency_ms,
                usage=data.get("usage"),
            )
        except Exception as exc:
            logger.error(f"OpenAI generate failed: {exc}")
            raise

    async def generate_stream(
        self,
        messages: list[Message],
        config: LLMConfig | None = None,
        functions: list[FunctionSpec] | None = None,
    ) -> AsyncIterator[str]:
        """Stream tokens from OpenAI."""
        cfg = self._merge_config(config)
        msgs = self._prepend_system_prompt(messages, cfg)

        payload: dict[str, Any] = {
            "model": cfg.model,
            "messages": [m.to_dict() for m in msgs],
            "temperature": cfg.temperature,
            "max_tokens": cfg.max_tokens,
            "stream": True,
        }

        if functions:
            payload["tools"] = [f.to_dict() for f in functions]

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
            logger.error(f"OpenAI stream failed: {exc}")
            raise

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
