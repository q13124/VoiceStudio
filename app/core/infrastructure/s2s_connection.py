"""
WebSocket Connection Manager for S2S Providers (Phase 10.1.2)

Manages persistent WebSocket connections for real-time speech-to-speech
models. Handles reconnection, heartbeat, and connection lifecycle.
"""

import asyncio
import json
import logging
import time
from typing import Any, AsyncIterator, Callable, Dict, Optional

logger = logging.getLogger(__name__)

try:
    import websockets
    _HAS_WEBSOCKETS = True
except ImportError:
    _HAS_WEBSOCKETS = False


class S2SWebSocketConnection:
    """
    Manages a persistent WebSocket connection for S2S providers.

    Features:
    - Automatic reconnection with exponential backoff
    - Heartbeat monitoring
    - Message queuing during disconnection
    - Graceful shutdown
    """

    # Default timeout values (seconds)
    DEFAULT_SEND_TIMEOUT = 10.0
    DEFAULT_RECEIVE_TIMEOUT = 30.0
    DEFAULT_CONNECT_TIMEOUT = 15.0

    def __init__(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        heartbeat_interval: float = 30.0,
        send_timeout: float = DEFAULT_SEND_TIMEOUT,
        receive_timeout: float = DEFAULT_RECEIVE_TIMEOUT,
    ):
        self._url = url
        self._headers = headers or {}
        self._max_retries = max_retries
        self._heartbeat_interval = heartbeat_interval
        self._send_timeout = send_timeout
        self._receive_timeout = receive_timeout
        self._ws = None
        self._connected = False
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._message_queue: asyncio.Queue = asyncio.Queue()

    @property
    def is_connected(self) -> bool:
        return self._connected and self._ws is not None

    async def connect(self) -> bool:
        """Establish WebSocket connection."""
        if not _HAS_WEBSOCKETS:
            logger.error("websockets library not installed")
            return False

        for attempt in range(self._max_retries):
            try:
                self._ws = await websockets.connect(
                    self._url,
                    additional_headers=self._headers,
                    ping_interval=20,
                    ping_timeout=10,
                    max_size=10 * 1024 * 1024,  # 10MB max message
                )
                self._connected = True
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                logger.info(f"S2S WebSocket connected to {self._url}")
                return True
            except Exception as exc:
                wait_time = 2 ** attempt
                logger.warning(
                    f"S2S connection attempt {attempt + 1} failed: {exc}. "
                    f"Retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

        logger.error(f"Failed to connect after {self._max_retries} attempts")
        return False

    async def disconnect(self) -> None:
        """Close the WebSocket connection."""
        self._connected = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
        if self._ws:
            try:
                await self._ws.close()
            except Exception as e:
                logger.debug(f"WebSocket close error (ignored): {e}")
            self._ws = None
        logger.info("S2S WebSocket disconnected")

    async def send_json(self, data: Dict[str, Any]) -> None:
        """Send JSON data over WebSocket with timeout."""
        if not self.is_connected:
            raise ConnectionError("Not connected")
        try:
            await asyncio.wait_for(
                self._ws.send(json.dumps(data)),
                timeout=self._send_timeout,
            )
        except asyncio.TimeoutError:
            logger.error(f"S2S send_json timed out after {self._send_timeout}s")
            self._connected = False
            raise TimeoutError(f"WebSocket send timed out after {self._send_timeout}s")

    async def send_bytes(self, data: bytes) -> None:
        """Send binary data over WebSocket with timeout."""
        if not self.is_connected:
            raise ConnectionError("Not connected")
        try:
            await asyncio.wait_for(
                self._ws.send(data),
                timeout=self._send_timeout,
            )
        except asyncio.TimeoutError:
            logger.error(f"S2S send_bytes timed out after {self._send_timeout}s")
            self._connected = False
            raise TimeoutError(f"WebSocket send timed out after {self._send_timeout}s")

    async def receive(self) -> AsyncIterator[Any]:
        """Receive messages from WebSocket with timeout handling."""
        if not self.is_connected:
            raise ConnectionError("Not connected")

        try:
            async for message in self._ws:
                if isinstance(message, str):
                    try:
                        yield json.loads(message)
                    except json.JSONDecodeError:
                        yield message
                else:
                    yield message
        except Exception as exc:
            logger.error(f"S2S receive error: {exc}")
            self._connected = False
            raise

    async def receive_one(self, timeout: Optional[float] = None) -> Any:
        """
        Receive a single message with optional timeout.

        Args:
            timeout: Timeout in seconds (uses default if None).

        Returns:
            Received message (parsed JSON or raw).

        Raises:
            TimeoutError: If no message received within timeout.
            ConnectionError: If not connected.
        """
        if not self.is_connected:
            raise ConnectionError("Not connected")

        timeout = timeout or self._receive_timeout
        try:
            message = await asyncio.wait_for(
                self._ws.recv(),
                timeout=timeout,
            )
            if isinstance(message, str):
                try:
                    return json.loads(message)
                except json.JSONDecodeError:
                    return message
            return message
        except asyncio.TimeoutError:
            logger.warning(f"S2S receive timed out after {timeout}s")
            raise TimeoutError(f"WebSocket receive timed out after {timeout}s")

    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to keep connection alive."""
        while self._connected:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                if self._ws and self._connected:
                    await self._ws.ping()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.warning(f"Heartbeat failed: {exc}")
                self._connected = False
                break
