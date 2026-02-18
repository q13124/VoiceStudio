"""
IPC Bridge for Plugin Subprocess Communication.

Phase 4 Enhancement: Bidirectional JSON-RPC communication bridge
between VoiceStudio host and plugin subprocess.

The bridge handles:
    - Message serialization/deserialization
    - Request/response correlation
    - Timeout management
    - Async send/receive operations
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from .protocol import (
    ErrorCode,
    Message,
    Notification,
    Request,
    Response,
    RPCError,
    decode_message_header,
    encode_message,
)

logger = logging.getLogger(__name__)


class BridgeState(str, Enum):
    """States of the IPC bridge."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CLOSING = "closing"
    ERROR = "error"


@dataclass
class PendingRequest:
    """Tracks a pending RPC request awaiting response."""

    request_id: Union[int, str]
    method: str
    future: asyncio.Future
    timeout_task: Optional[asyncio.Task] = None
    sent_at: float = 0.0


@dataclass
class IPCBridge:
    """
    Bidirectional JSON-RPC communication bridge.

    Handles message passing between host and plugin subprocess
    via stdin/stdout streams.
    """

    # Stream handles
    reader: Optional[asyncio.StreamReader] = None
    writer: Optional[asyncio.StreamWriter] = None

    # State
    state: BridgeState = BridgeState.DISCONNECTED
    _next_id: int = field(default=0, repr=False)
    _pending: Dict[Union[int, str], PendingRequest] = field(default_factory=dict, repr=False)
    _handlers: Dict[str, Callable[..., Awaitable[Any]]] = field(
        default_factory=dict, repr=False
    )
    _notification_handlers: Dict[str, Callable[..., Awaitable[None]]] = field(
        default_factory=dict, repr=False
    )

    # Configuration
    default_timeout_ms: int = 30000
    max_message_size: int = 10 * 1024 * 1024  # 10 MB

    # Event loop reference
    _loop: Optional[asyncio.AbstractEventLoop] = field(default=None, repr=False)
    _read_task: Optional[asyncio.Task] = field(default=None, repr=False)

    def __post_init__(self):
        """Initialize internal state."""
        self._pending = {}
        self._handlers = {}
        self._notification_handlers = {}

    def connect(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        """
        Connect the bridge to stream handles.

        Args:
            reader: Input stream (subprocess stdout or stdin)
            writer: Output stream (subprocess stdin or stdout)
        """
        if self.state != BridgeState.DISCONNECTED:
            raise RuntimeError(f"Cannot connect in state {self.state}")

        self.reader = reader
        self.writer = writer
        self.state = BridgeState.CONNECTED
        self._loop = asyncio.get_event_loop()

        logger.debug("IPC bridge connected")

    async def start_reading(self) -> None:
        """Start the background message reading task."""
        if self.state != BridgeState.CONNECTED:
            raise RuntimeError(f"Cannot start reading in state {self.state}")

        self._read_task = asyncio.create_task(self._read_loop())
        logger.debug("IPC bridge read loop started")

    async def close(self) -> None:
        """Close the bridge and clean up resources."""
        if self.state == BridgeState.DISCONNECTED:
            return

        self.state = BridgeState.CLOSING
        logger.debug("IPC bridge closing")

        # Cancel read task
        if self._read_task and not self._read_task.done():
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass

        # Cancel pending requests
        for pending in list(self._pending.values()):
            if pending.timeout_task:
                pending.timeout_task.cancel()
            if not pending.future.done():
                pending.future.set_exception(
                    RuntimeError("Bridge closed while request pending")
                )
        self._pending.clear()

        # Close writer
        if self.writer:
            self.writer.close()
            try:
                await self.writer.wait_closed()
            except Exception:
                # SAFETY: During cleanup, if wait_closed() fails (e.g., connection
                # already closed or broken pipe), we proceed with cleanup since
                # the resource is already being torn down and errors are expected.
                pass

        self.reader = None
        self.writer = None
        self.state = BridgeState.DISCONNECTED
        logger.debug("IPC bridge closed")

    def register_handler(
        self,
        method: str,
        handler: Callable[..., Awaitable[Any]],
    ) -> None:
        """
        Register a handler for incoming requests.

        Args:
            method: The RPC method name
            handler: Async function to handle the request
        """
        self._handlers[method] = handler
        logger.debug(f"Registered handler for method: {method}")

    def register_notification_handler(
        self,
        method: str,
        handler: Callable[..., Awaitable[None]],
    ) -> None:
        """
        Register a handler for incoming notifications.

        Args:
            method: The notification method name
            handler: Async function to handle the notification
        """
        self._notification_handlers[method] = handler
        logger.debug(f"Registered notification handler for method: {method}")

    async def send_request(
        self,
        method: str,
        params: Optional[Union[Dict[str, Any], List[Any]]] = None,
        timeout_ms: Optional[int] = None,
    ) -> Any:
        """
        Send an RPC request and await response.

        Args:
            method: The RPC method name
            params: Optional parameters
            timeout_ms: Request timeout in milliseconds (default: 30000)

        Returns:
            The result from the response

        Raises:
            RPCError: If the remote returns an error
            TimeoutError: If the request times out
            RuntimeError: If the bridge is not connected
        """
        if self.state != BridgeState.CONNECTED:
            raise RuntimeError(f"Cannot send request in state {self.state}")

        request_id = self._get_next_id()
        request = Request(id=request_id, method=method, params=params)

        timeout = timeout_ms or self.default_timeout_ms
        future: asyncio.Future[Response] = asyncio.Future()

        pending = PendingRequest(
            request_id=request_id,
            method=method,
            future=future,
        )
        self._pending[request_id] = pending

        # Set up timeout
        async def timeout_handler():
            await asyncio.sleep(timeout / 1000.0)
            if request_id in self._pending:
                del self._pending[request_id]
                if not future.done():
                    future.set_exception(
                        TimeoutError(f"Request {method} timed out after {timeout}ms")
                    )

        pending.timeout_task = asyncio.create_task(timeout_handler())

        try:
            await self._send_message(request)
            response = await future

            if response.error:
                raise Exception(
                    f"RPC error {response.error.code}: {response.error.message}"
                )

            return response.result

        finally:
            if pending.timeout_task and not pending.timeout_task.done():
                pending.timeout_task.cancel()

    async def send_notification(
        self,
        method: str,
        params: Optional[Union[Dict[str, Any], List[Any]]] = None,
    ) -> None:
        """
        Send a notification (no response expected).

        Args:
            method: The notification method name
            params: Optional parameters
        """
        if self.state != BridgeState.CONNECTED:
            raise RuntimeError(f"Cannot send notification in state {self.state}")

        notification = Notification(method=method, params=params)
        await self._send_message(notification)

    async def _send_message(self, message: Message) -> None:
        """Send a message over the wire."""
        if not self.writer:
            raise RuntimeError("Writer not available")

        data = encode_message(message)

        if len(data) > self.max_message_size:
            raise ValueError(
                f"Message size {len(data)} exceeds maximum {self.max_message_size}"
            )

        self.writer.write(data)
        await self.writer.drain()
        logger.debug(f"Sent message: {message.to_dict().get('method', 'response')}")

    async def _read_loop(self) -> None:
        """Background task to read incoming messages."""
        if not self.reader:
            return

        while self.state == BridgeState.CONNECTED:
            try:
                # Read length prefix
                header = await self.reader.readexactly(4)
                length = decode_message_header(header)

                if length > self.max_message_size:
                    logger.error(f"Message size {length} exceeds maximum")
                    continue

                # Read message body
                body = await self.reader.readexactly(length)
                json_str = body.decode("utf-8")

                # Parse and dispatch
                message = Message.from_json(json_str)
                await self._dispatch_message(message)

            except asyncio.IncompleteReadError:
                logger.info("Connection closed by remote")
                self.state = BridgeState.DISCONNECTED
                break
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in read loop: {e}")
                self.state = BridgeState.ERROR
                break

    async def _dispatch_message(self, message: Message) -> None:
        """Dispatch an incoming message to the appropriate handler."""
        if isinstance(message, Response):
            await self._handle_response(message)
        elif isinstance(message, Request):
            await self._handle_request(message)
        elif isinstance(message, Notification):
            await self._handle_notification(message)
        else:
            logger.warning(f"Unknown message type: {type(message)}")

    async def _handle_response(self, response: Response) -> None:
        """Handle an incoming response."""
        pending = self._pending.pop(response.id, None)
        if pending:
            if pending.timeout_task:
                pending.timeout_task.cancel()
            if not pending.future.done():
                pending.future.set_result(response)
        else:
            logger.warning(f"Received response for unknown request: {response.id}")

    async def _handle_request(self, request: Request) -> None:
        """Handle an incoming request."""
        handler = self._handlers.get(request.method)

        if handler is None:
            error = RPCError.method_not_found(request.method)
            response = Response.failure(request.id, error)
        else:
            try:
                if request.params is None:
                    result = await handler()
                elif isinstance(request.params, dict):
                    result = await handler(**request.params)
                else:
                    result = await handler(*request.params)

                response = Response.success(request.id, result)

            except TypeError as e:
                error = RPCError.invalid_params(str(e))
                response = Response.failure(request.id, error)
            except PermissionError as e:
                error = RPCError(
                    code=ErrorCode.PERMISSION_DENIED,
                    message=str(e),
                )
                response = Response.failure(request.id, error)
            except Exception as e:
                logger.exception(f"Error handling request {request.method}")
                error = RPCError.internal_error(str(e))
                response = Response.failure(request.id, error)

        await self._send_message(response)

    async def _handle_notification(self, notification: Notification) -> None:
        """Handle an incoming notification."""
        handler = self._notification_handlers.get(notification.method)

        if handler is None:
            logger.debug(f"No handler for notification: {notification.method}")
            return

        try:
            if notification.params is None:
                await handler()
            elif isinstance(notification.params, dict):
                await handler(**notification.params)
            else:
                await handler(*notification.params)
        except Exception as e:
            logger.exception(f"Error handling notification {notification.method}: {e}")

    def _get_next_id(self) -> int:
        """Generate the next request ID."""
        self._next_id += 1
        return self._next_id
