"""
Tests for protocol module.
"""

from __future__ import annotations

import json

from voicestudio_plugin_sdk.protocol import (
    ErrorCode,
    HostMethods,
    MessageType,
    Notification,
    Request,
    Response,
    RPCError,
    decode_message_header,
    encode_message,
)


class TestMessageType:
    """Tests for MessageType enum."""

    def test_request(self):
        """Test request type."""
        assert MessageType.REQUEST == "request"

    def test_response(self):
        """Test response type."""
        assert MessageType.RESPONSE == "response"

    def test_notification(self):
        """Test notification type."""
        assert MessageType.NOTIFICATION == "notification"


class TestErrorCode:
    """Tests for ErrorCode enum."""

    def test_standard_codes(self):
        """Test standard JSON-RPC error codes."""
        assert ErrorCode.PARSE_ERROR == -32700
        assert ErrorCode.INVALID_REQUEST == -32600
        assert ErrorCode.METHOD_NOT_FOUND == -32601
        assert ErrorCode.INVALID_PARAMS == -32602
        assert ErrorCode.INTERNAL_ERROR == -32603

    def test_custom_codes(self):
        """Test VoiceStudio custom error codes."""
        assert ErrorCode.PERMISSION_DENIED == -32000
        assert ErrorCode.PLUGIN_ERROR == -32002
        assert ErrorCode.TIMEOUT == -32001
        assert ErrorCode.RESOURCE_LIMIT == -32003


class TestRPCError:
    """Tests for RPCError dataclass."""

    def test_creation(self):
        """Test creating an error."""
        err = RPCError(
            code=ErrorCode.INTERNAL_ERROR,
            message="Something went wrong",
        )
        assert err.code == -32603
        assert err.message == "Something went wrong"
        assert err.data is None

    def test_with_data(self):
        """Test error with additional data."""
        err = RPCError(
            code=ErrorCode.INVALID_PARAMS,
            message="Invalid parameter",
            data={"field": "name", "expected": "string"},
        )
        assert err.data["field"] == "name"

    def test_to_dict(self):
        """Test converting to dictionary."""
        err = RPCError(
            code=ErrorCode.METHOD_NOT_FOUND,
            message="Method not found",
        )
        data = err.to_dict()
        assert data["code"] == -32601
        assert data["message"] == "Method not found"
        assert "data" not in data  # None should be omitted

    def test_from_dict(self):
        """Test creating from dictionary."""
        err = RPCError.from_dict({
            "code": -32000,
            "message": "Plugin error",
            "data": {"stack": "..."},
        })
        assert err.code == -32000
        assert err.data["stack"] == "..."

    def test_factory_methods(self):
        """Test factory methods for common errors."""
        err = RPCError.parse_error()
        assert err.code == ErrorCode.PARSE_ERROR

        err = RPCError.method_not_found("test.method")
        assert err.code == ErrorCode.METHOD_NOT_FOUND
        assert "test.method" in err.message

        err = RPCError.invalid_params("missing required field")
        assert err.code == ErrorCode.INVALID_PARAMS


class TestRequest:
    """Tests for Request dataclass."""

    def test_creation(self):
        """Test creating a request."""
        req = Request(
            id="123",
            method="plugin.invoke",
            params={"capability": "test"},
        )
        assert req.id == "123"
        assert req.method == "plugin.invoke"
        assert req.jsonrpc == "2.0"

    def test_to_dict(self):
        """Test converting to dictionary."""
        req = Request(
            id="456",
            method="host.audio.play",
            params={"path": "/audio.wav"},
        )
        data = req.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "456"
        assert data["method"] == "host.audio.play"

    def test_from_dict(self):
        """Test creating from dictionary."""
        req = Request.from_dict({
            "jsonrpc": "2.0",
            "id": "789",
            "method": "test.method",
        })
        assert req.id == "789"
        assert req.params is None  # No params provided


class TestResponse:
    """Tests for Response dataclass."""

    def test_success_response(self):
        """Test creating success response."""
        resp = Response(
            id="123",
            result={"status": "ok"},
        )
        assert resp.id == "123"
        assert resp.result == {"status": "ok"}
        assert resp.error is None
        assert resp.jsonrpc == "2.0"

    def test_error_response(self):
        """Test creating error response."""
        err = RPCError(
            code=ErrorCode.INTERNAL_ERROR,
            message="Failed",
        )
        resp = Response(
            id="456",
            error=err,
        )
        assert resp.result is None
        assert resp.error is not None

    def test_to_dict_success(self):
        """Test converting success response to dictionary."""
        resp = Response(
            id="123",
            result={"data": 42},
        )
        data = resp.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == "123"
        assert data["result"] == {"data": 42}
        assert "error" not in data

    def test_to_dict_error(self):
        """Test converting error response to dictionary."""
        resp = Response(
            id="456",
            error=RPCError(ErrorCode.PERMISSION_DENIED, "Error"),
        )
        data = resp.to_dict()
        assert "result" not in data
        assert data["error"]["code"] == -32000

    def test_from_dict(self):
        """Test creating from dictionary."""
        resp = Response.from_dict({
            "jsonrpc": "2.0",
            "id": "789",
            "result": {"success": True},
        })
        assert resp.result["success"] is True

    def test_factory_methods(self):
        """Test Response factory methods."""
        resp = Response.success("req-1", {"data": 42})
        assert resp.id == "req-1"
        assert resp.result == {"data": 42}
        assert not resp.is_error

        resp = Response.failure("req-2", RPCError.parse_error())
        assert resp.id == "req-2"
        assert resp.is_error


class TestNotification:
    """Tests for Notification dataclass."""

    def test_creation(self):
        """Test creating a notification."""
        notif = Notification(
            method="notify.progress",
            params={"percent": 50},
        )
        assert notif.method == "notify.progress"
        assert notif.jsonrpc == "2.0"

    def test_to_dict(self):
        """Test converting to dictionary."""
        notif = Notification(
            method="notify.log",
            params={"level": "info", "message": "Hello"},
        )
        data = notif.to_dict()
        assert data["jsonrpc"] == "2.0"
        assert "id" not in data
        assert data["method"] == "notify.log"

    def test_from_dict(self):
        """Test creating from dictionary."""
        notif = Notification.from_dict({
            "jsonrpc": "2.0",
            "method": "notify.event",
            "params": {"event": "ready"},
        })
        assert notif.params["event"] == "ready"


class TestHostMethods:
    """Tests for HostMethods constants."""

    def test_lifecycle_methods(self):
        """Test lifecycle method names."""
        assert HostMethods.INITIALIZE == "plugin.initialize"
        assert HostMethods.SHUTDOWN == "plugin.shutdown"

    def test_audio_methods(self):
        """Test audio method names."""
        assert HostMethods.AUDIO_PLAY == "host.audio.play"
        assert HostMethods.AUDIO_STOP == "host.audio.stop"

    def test_notification_methods(self):
        """Test notification method names."""
        assert HostMethods.LOG == "notify.log"
        assert HostMethods.PROGRESS == "notify.progress"


class TestMessageEncoding:
    """Tests for message encoding/decoding."""

    def test_encode_request(self):
        """Test encoding a request."""
        req = Request(
            id="test-1",
            method="test.method",
            params={"key": "value"},
        )
        encoded = encode_message(req)
        assert isinstance(encoded, bytes)

        # Decode to verify format (4-byte length prefix + JSON)
        length = int.from_bytes(encoded[:4], byteorder="big")
        json_data = encoded[4:]
        assert len(json_data) == length

        parsed = json.loads(json_data)
        assert parsed["id"] == "test-1"

    def test_encode_response(self):
        """Test encoding a response."""
        resp = Response(
            id="test-2",
            result={"status": "ok"},
        )
        encoded = encode_message(resp)
        int.from_bytes(encoded[:4], byteorder="big")
        json_data = encoded[4:]
        parsed = json.loads(json_data)
        assert parsed["result"]["status"] == "ok"

    def test_encode_notification(self):
        """Test encoding a notification."""
        notif = Notification(
            method="notify.event",
            params={"type": "test"},
        )
        encoded = encode_message(notif)
        int.from_bytes(encoded[:4], byteorder="big")
        json_data = encoded[4:]
        parsed = json.loads(json_data)
        assert "id" not in parsed

    def test_decode_header(self):
        """Test decoding message header."""
        # Create a sample message with known length
        length = 42
        data = length.to_bytes(4, byteorder="big") + b"x" * 100
        decoded_length = decode_message_header(data)
        assert decoded_length == 42

    def test_roundtrip(self):
        """Test encoding and parsing roundtrip."""
        original = Request(
            id="roundtrip-test",
            method="test.roundtrip",
            params={"nested": {"value": 123}},
        )
        encoded = encode_message(original)

        # Parse back
        length = int.from_bytes(encoded[:4], byteorder="big")
        json_data = encoded[4:4 + length]
        parsed_dict = json.loads(json_data)
        restored = Request.from_dict(parsed_dict)

        assert restored.id == original.id
        assert restored.method == original.method
        assert restored.params["nested"]["value"] == 123
