"""
Google Gemini Live Adapter for VoiceStudio (Phase 10.2.2)

Integrates Google's Gemini Live API for speech-to-speech conversation.
Supports real-time audio streaming with low latency.

Note: Requires GOOGLE_API_KEY. Optional cloud adapter.
"""

from __future__ import annotations

import base64
import logging
import os
import time
from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)

from app.core.engines.s2s_protocol import (
    BaseS2SProvider,
    S2SConfig,
    S2SConnectionState,
    S2SResponse,
)


class GeminiLiveProvider(BaseS2SProvider):
    """
    Speech-to-speech provider using Google Gemini Live.

    Gemini Live supports real-time conversational AI with
    audio input/output, preserving emotion and speaker identity.
    """

    DEFAULT_MODEL = "gemini-2.0-flash-exp"
    WS_URL = "wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1alpha.GenerativeService.BidiGenerateContent"

    def __init__(self, config: S2SConfig | None = None):
        super().__init__(config)
        if not self._config.model:
            self._config.model = self.DEFAULT_MODEL
        if not self._config.api_key:
            self._config.api_key = os.getenv("GOOGLE_API_KEY", "")
        self._ws_connection = None

    @property
    def provider_name(self) -> str:
        return "gemini_live"

    @property
    def is_available(self) -> bool:
        return bool(self._config.api_key)

    async def connect(self, config: S2SConfig | None = None) -> bool:
        """Connect to Gemini Live API."""
        if config:
            self._config = config

        if not self._config.api_key:
            logger.error("Google API key not configured")
            return False

        try:
            from app.core.infrastructure.s2s_connection import S2SWebSocketConnection

            url = f"{self.WS_URL}?key={self._config.api_key}"
            self._ws_connection = S2SWebSocketConnection(url=url)
            connected = await self._ws_connection.connect()

            if connected:
                # Send setup message
                await self._ws_connection.send_json(
                    {
                        "setup": {
                            "model": f"models/{self._config.model}",
                            "generation_config": {
                                "response_modalities": ["AUDIO"],
                                "speech_config": {
                                    "voice_config": {
                                        "prebuilt_voice_config": {
                                            "voice_name": self._config.voice or "Puck",
                                        }
                                    }
                                },
                            },
                        }
                    }
                )

                self._state = S2SConnectionState.CONNECTED
                logger.info("Gemini Live connected and configured")
                return True
            return False

        except Exception as exc:
            logger.error(f"Gemini Live connection failed: {exc}")
            self._state = S2SConnectionState.ERROR
            return False

    async def disconnect(self) -> None:
        """Disconnect from Gemini Live."""
        if self._ws_connection:
            await self._ws_connection.disconnect()
        self._state = S2SConnectionState.DISCONNECTED

    async def send_audio(self, audio_data: bytes) -> None:
        """Send audio to Gemini Live."""
        if not self._ws_connection or not self._ws_connection.is_connected:
            raise ConnectionError("Not connected to Gemini Live")

        encoded = base64.b64encode(audio_data).decode("utf-8")
        await self._ws_connection.send_json(
            {
                "realtime_input": {
                    "media_chunks": [
                        {
                            "data": encoded,
                            "mime_type": "audio/pcm",
                        }
                    ]
                }
            }
        )
        self._state = S2SConnectionState.ACTIVE

    async def receive_audio(self) -> AsyncIterator[S2SResponse]:
        """Receive audio from Gemini Live."""
        if not self._ws_connection or not self._ws_connection.is_connected:
            raise ConnectionError("Not connected")

        try:
            async for message in self._ws_connection.receive():
                if isinstance(message, dict):
                    # Handle server content (audio response)
                    server_content = message.get("serverContent", {})
                    parts = server_content.get("modelTurn", {}).get("parts", [])

                    for part in parts:
                        if "inlineData" in part:
                            inline = part["inlineData"]
                            audio_b64 = inline.get("data", "")
                            if audio_b64:
                                audio_data = base64.b64decode(audio_b64)
                                yield S2SResponse(
                                    audio_data=audio_data,
                                    is_final=False,
                                )
                        elif "text" in part:
                            yield S2SResponse(
                                response_text=part["text"],
                                is_final=False,
                            )

                    # Check if turn is complete
                    if server_content.get("turnComplete", False):
                        self._turn_count += 1
                        yield S2SResponse(is_final=True)

        except Exception as exc:
            logger.error(f"Gemini Live receive error: {exc}")
            self._state = S2SConnectionState.ERROR

    async def respond(self, audio_data: bytes, context: str | None = None) -> S2SResponse:
        """Send audio and get a complete response."""
        start_time = time.perf_counter()

        await self.send_audio(audio_data)

        # Collect response
        audio_chunks = []
        text_parts = []

        async for response in self.receive_audio():
            if response.audio_data:
                audio_chunks.append(response.audio_data)
            if response.response_text:
                text_parts.append(response.response_text)
            if response.is_final:
                break

        latency = (time.perf_counter() - start_time) * 1000

        return S2SResponse(
            audio_data=b"".join(audio_chunks) if audio_chunks else None,
            response_text="".join(text_parts),
            is_final=True,
            latency_ms=latency,
        )

    async def interrupt(self) -> None:
        """Interrupt current response."""
        if self._ws_connection and self._ws_connection.is_connected:
            # Gemini uses end_of_turn signal
            await self._ws_connection.send_json({"client_content": {"turn_complete": True}})
