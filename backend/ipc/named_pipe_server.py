"""
Named Pipe IPC Server.

Task 1.4.1: Alternative IPC for firewall scenarios.
Provides named pipe communication as fallback for HTTP.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import sys
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of IPC messages."""

    REQUEST = 0
    RESPONSE = 1
    EVENT = 2
    ERROR = 3
    PING = 4
    PONG = 5


@dataclass
class IPCMessage:
    """An IPC message."""

    msg_type: MessageType
    msg_id: str
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PipeConfig:
    """Configuration for named pipe server."""

    pipe_name: str = "voicestudio_ipc"
    max_connections: int = 10
    buffer_size: int = 65536
    timeout_seconds: float = 30.0
    enable_auth: bool = True


class NamedPipeServer:
    """
    Named pipe IPC server for Windows.

    Features:
    - Bidirectional communication
    - Message framing
    - Multiple client support
    - Request-response pattern
    - Event broadcasting
    """

    def __init__(self, config: PipeConfig | None = None):
        self.config = config or PipeConfig()

        self._pipe_path = f"\\\\.\\pipe\\{self.config.pipe_name}"
        self._handlers: dict[str, Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]] = {}
        self._clients: dict[str, Any] = {}
        self._running = False
        self._server_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        self._msg_counter = 0

    def register_handler(
        self,
        method: str,
        handler: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]],
    ) -> None:
        """Register a method handler."""
        self._handlers[method] = handler
        logger.debug(f"Registered IPC handler: {method}")

    def handler(
        self,
        method: str,
    ) -> Callable[[Callable], Callable]:
        """Decorator to register a handler."""

        def decorator(func: Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]) -> Callable:
            self.register_handler(method, func)
            return func

        return decorator

    async def start(self) -> None:
        """Start the named pipe server."""
        if sys.platform != "win32":
            logger.warning("Named pipes are only supported on Windows")
            return

        self._running = True
        self._server_task = asyncio.create_task(self._server_loop())
        logger.info(f"Named pipe server started: {self._pipe_path}")

    async def stop(self) -> None:
        """Stop the named pipe server."""
        self._running = False

        # Close all client connections
        for client_id in list(self._clients.keys()):
            await self._close_client(client_id)

        if self._server_task:
            self._server_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._server_task

        logger.info("Named pipe server stopped")

    async def _server_loop(self) -> None:
        """Main server loop."""
        if sys.platform != "win32":
            return

        try:
            import pywintypes
            import win32file
            import win32pipe

            while self._running:
                try:
                    # Create pipe instance
                    pipe = win32pipe.CreateNamedPipe(
                        self._pipe_path,
                        win32pipe.PIPE_ACCESS_DUPLEX,
                        win32pipe.PIPE_TYPE_MESSAGE
                        | win32pipe.PIPE_READMODE_MESSAGE
                        | win32pipe.PIPE_WAIT,
                        self.config.max_connections,
                        self.config.buffer_size,
                        self.config.buffer_size,
                        0,
                        None,
                    )

                    # Wait for client connection
                    win32pipe.ConnectNamedPipe(pipe, None)

                    # Handle client in background
                    client_id = f"client_{len(self._clients)}"
                    self._clients[client_id] = pipe
                    asyncio.create_task(self._handle_client(client_id, pipe))

                except pywintypes.error as e:
                    if e.winerror == 232:  # Pipe closed
                        continue
                    logger.error(f"Pipe error: {e}")
                    await asyncio.sleep(1.0)
                except Exception as e:
                    logger.error(f"Server loop error: {e}")
                    await asyncio.sleep(1.0)

        except ImportError:
            logger.error("pywin32 required for named pipe support")
        except asyncio.CancelledError:
            pass

    async def _handle_client(self, client_id: str, pipe: Any) -> None:
        """Handle a client connection."""
        logger.info(f"Client connected: {client_id}")

        try:
            import win32file

            while self._running and client_id in self._clients:
                try:
                    # Read message
                    _result, data = win32file.ReadFile(pipe, self.config.buffer_size)

                    if not data:
                        break

                    # Parse message
                    message = self._parse_message(data)

                    if message.msg_type == MessageType.PING:
                        response = IPCMessage(
                            msg_type=MessageType.PONG,
                            msg_id=message.msg_id,
                            payload={},
                        )
                    elif message.msg_type == MessageType.REQUEST:
                        response = await self._handle_request(message)
                    else:
                        continue

                    # Send response
                    response_data = self._serialize_message(response)
                    win32file.WriteFile(pipe, response_data)

                except Exception as e:
                    logger.error(f"Client handler error: {e}")
                    break

        except ImportError:
            logger.debug(
                "win32file not available - Windows named pipes not supported on this platform"
            )
        finally:
            await self._close_client(client_id)

    async def _handle_request(self, message: IPCMessage) -> IPCMessage:
        """Handle a request message."""
        method = message.payload.get("method", "")
        params = message.payload.get("params", {})

        handler = self._handlers.get(method)

        if not handler:
            return IPCMessage(
                msg_type=MessageType.ERROR,
                msg_id=message.msg_id,
                payload={"error": f"Unknown method: {method}"},
            )

        try:
            result = await handler(params)
            return IPCMessage(
                msg_type=MessageType.RESPONSE,
                msg_id=message.msg_id,
                payload={"result": result},
            )
        except Exception as e:
            logger.error(f"Handler error for {method}: {e}")
            return IPCMessage(
                msg_type=MessageType.ERROR,
                msg_id=message.msg_id,
                payload={"error": str(e)},
            )

    async def _close_client(self, client_id: str) -> None:
        """Close a client connection."""
        pipe = self._clients.pop(client_id, None)
        if pipe:
            try:
                import win32file

                win32file.CloseHandle(pipe)
            except Exception as close_err:
                logger.debug(f"Failed to close pipe handle for client {client_id}: {close_err}")
        logger.info(f"Client disconnected: {client_id}")

    def _parse_message(self, data: bytes) -> IPCMessage:
        """Parse a message from bytes."""
        try:
            payload = json.loads(data.decode("utf-8"))
            return IPCMessage(
                msg_type=MessageType(payload.get("type", 0)),
                msg_id=payload.get("id", ""),
                payload=payload.get("payload", {}),
            )
        except Exception as e:
            logger.error(f"Message parse error: {e}")
            return IPCMessage(
                msg_type=MessageType.ERROR,
                msg_id="",
                payload={"error": "Invalid message format"},
            )

    def _serialize_message(self, message: IPCMessage) -> bytes:
        """Serialize a message to bytes."""
        data = {
            "type": message.msg_type.value,
            "id": message.msg_id,
            "payload": message.payload,
            "timestamp": message.timestamp.isoformat(),
        }
        return json.dumps(data).encode("utf-8")

    async def broadcast(self, event: str, data: dict[str, Any]) -> int:
        """
        Broadcast an event to all connected clients.

        Returns number of clients notified.
        """
        if sys.platform != "win32":
            return 0

        try:
            import win32file

            message = IPCMessage(
                msg_type=MessageType.EVENT,
                msg_id=f"event_{self._msg_counter}",
                payload={"event": event, "data": data},
            )
            self._msg_counter += 1

            message_data = self._serialize_message(message)
            sent = 0

            for client_id, pipe in list(self._clients.items()):
                try:
                    win32file.WriteFile(pipe, message_data)
                    sent += 1
                except Exception:
                    await self._close_client(client_id)

            return sent

        except ImportError:
            return 0

    def get_stats(self) -> dict[str, Any]:
        """Get server statistics."""
        return {
            "pipe_path": self._pipe_path,
            "connected_clients": len(self._clients),
            "registered_handlers": list(self._handlers.keys()),
            "running": self._running,
        }
