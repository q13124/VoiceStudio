"""
OpenAI Realtime API Adapter for VoiceStudio (Phase 10.2.1)

Integrates OpenAI's Realtime API for end-to-end speech-to-speech
conversation. Supports bidirectional audio streaming, barge-in,
and function calling.

Note: Requires OPENAI_API_KEY. Per local-first policy, this is
optional -- local S2S alternatives are preferred when available.
"""

import asyncio
import base64
import json
import logging
import os
import time
from typing import Any, AsyncIterator, Dict, List, Optional

logger = logging.getLogger(__name__)

from app.core.engines.s2s_protocol import (
    BaseS2SProvider,
    S2SConfig,
    S2SConnectionState,
    S2SResponse,
)


class OpenAIRealtimeProvider(BaseS2SProvider):
    """
    Speech-to-speech provider using OpenAI's Realtime API.

    Uses WebSocket connection for bidirectional audio streaming.
    The API processes audio input directly and returns audio output,
    preserving tone, emotion, and speaker characteristics.
    """

    DEFAULT_MODEL = "gpt-4o-realtime-preview"
    WS_URL = "wss://api.openai.com/v1/realtime"

    def __init__(self, config: Optional[S2SConfig] = None):
        super().__init__(config)
        if not self._config.model:
            self._config.model = self.DEFAULT_MODEL
        if not self._config.api_key:
            self._config.api_key = os.getenv("OPENAI_API_KEY", "")
        self._ws_connection = None
        self._response_buffer: list = []

    @property
    def provider_name(self) -> str:
        return "openai_realtime"

    @property
    def is_available(self) -> bool:
        return bool(self._config.api_key)

    async def connect(self, config: Optional[S2SConfig] = None) -> bool:
        """Connect to OpenAI Realtime API via WebSocket."""
        if config:
            self._config = config

        if not self._config.api_key:
            logger.error("OpenAI API key not configured")
            return False

        try:
            from app.core.infrastructure.s2s_connection import S2SWebSocketConnection

            url = f"{self.WS_URL}?model={self._config.model}"
            headers = {
                "Authorization": f"Bearer {self._config.api_key}",
                "OpenAI-Beta": "realtime=v1",
            }

            self._ws_connection = S2SWebSocketConnection(url=url, headers=headers)
            connected = await self._ws_connection.connect()

            if connected:
                self._state = S2SConnectionState.CONNECTED

                # Configure session
                await self._ws_connection.send_json({
                    "type": "session.update",
                    "session": {
                        "modalities": self._config.modalities,
                        "voice": self._config.voice,
                        "input_audio_format": self._config.input_format,
                        "output_audio_format": self._config.output_format,
                        "turn_detection": {
                            "type": self._config.turn_detection,
                            "threshold": 0.5,
                            "silence_duration_ms": self._config.silence_threshold_ms,
                        },
                        "temperature": self._config.temperature,
                        "max_response_output_tokens": self._config.max_response_tokens,
                    },
                })

                logger.info("OpenAI Realtime connected and configured")
                return True
            return False

        except Exception as exc:
            logger.error(f"OpenAI Realtime connection failed: {exc}")
            self._state = S2SConnectionState.ERROR
            return False

    async def disconnect(self) -> None:
        """Disconnect from OpenAI Realtime API."""
        if self._ws_connection:
            await self._ws_connection.disconnect()
        self._state = S2SConnectionState.DISCONNECTED

    async def send_audio(self, audio_data: bytes) -> None:
        """Send audio data to the Realtime API."""
        if not self._ws_connection or not self._ws_connection.is_connected:
            raise ConnectionError("Not connected to OpenAI Realtime")

        # Encode as base64 for the API
        encoded = base64.b64encode(audio_data).decode("utf-8")
        await self._ws_connection.send_json({
            "type": "input_audio_buffer.append",
            "audio": encoded,
        })
        self._state = S2SConnectionState.ACTIVE

    async def receive_audio(self) -> AsyncIterator[S2SResponse]:
        """Receive audio responses from the Realtime API."""
        if not self._ws_connection or not self._ws_connection.is_connected:
            raise ConnectionError("Not connected")

        try:
            async for message in self._ws_connection.receive():
                if isinstance(message, dict):
                    msg_type = message.get("type", "")

                    if msg_type == "response.audio.delta":
                        audio_b64 = message.get("delta", "")
                        if audio_b64:
                            audio_data = base64.b64decode(audio_b64)
                            yield S2SResponse(
                                audio_data=audio_data,
                                is_final=False,
                            )

                    elif msg_type == "response.audio_transcript.delta":
                        yield S2SResponse(
                            response_text=message.get("delta", ""),
                            is_final=False,
                        )

                    elif msg_type == "response.done":
                        response_data = message.get("response", {})
                        usage = response_data.get("usage", {})
                        if usage:
                            self._total_input_tokens += usage.get("input_tokens", 0)
                            self._total_output_tokens += usage.get("output_tokens", 0)
                        self._turn_count += 1

                        yield S2SResponse(
                            is_final=True,
                            usage=usage,
                            metadata={"response_id": response_data.get("id", "")},
                        )

                    elif msg_type == "error":
                        error = message.get("error", {})
                        logger.error(f"OpenAI Realtime error: {error}")
                        yield S2SResponse(
                            is_final=True,
                            metadata={"error": error},
                        )

        except Exception as exc:
            logger.error(f"Receive error: {exc}")
            self._state = S2SConnectionState.ERROR

    async def respond(
        self, audio_data: bytes, context: Optional[str] = None
    ) -> S2SResponse:
        """
        Send audio and get a complete response.

        For simple request-response pattern (non-streaming).
        """
        start_time = time.perf_counter()

        if not self._ws_connection or not self._ws_connection.is_connected:
            raise ConnectionError("Not connected")

        # Send audio
        await self.send_audio(audio_data)

        # Commit the audio buffer
        await self._ws_connection.send_json({
            "type": "input_audio_buffer.commit",
        })

        # Request response
        await self._ws_connection.send_json({
            "type": "response.create",
        })

        # Collect response
        audio_chunks = []
        transcript_parts = []
        final_usage = None

        async for response in self.receive_audio():
            if response.audio_data:
                audio_chunks.append(response.audio_data)
            if response.response_text:
                transcript_parts.append(response.response_text)
            if response.is_final:
                final_usage = response.usage
                break

        latency = (time.perf_counter() - start_time) * 1000
        combined_audio = b"".join(audio_chunks) if audio_chunks else None

        return S2SResponse(
            audio_data=combined_audio,
            response_text="".join(transcript_parts),
            is_final=True,
            usage=final_usage,
            latency_ms=latency,
        )

    async def interrupt(self) -> None:
        """Cancel the current response."""
        if self._ws_connection and self._ws_connection.is_connected:
            await self._ws_connection.send_json({
                "type": "response.cancel",
            })
            logger.info("OpenAI Realtime: response cancelled")
