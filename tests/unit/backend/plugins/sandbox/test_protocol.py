"""
Tests for Plugin Subprocess Protocol.

Phase 4 Enhancement: Tests for JSON-RPC message format and utilities.
"""

import json
import time

import pytest

from backend.plugins.sandbox.protocol import (
    ErrorCode,
    HostMethods,
    Message,
    MessageType,
    Notification,
    Request,
    Response,
    RPCError,
    decode_message_header,
    encode_message,
)


class TestMessageType:
    """Test MessageType enum."""

    def test_message_types(self):
        """All expected message types are defined."""
        assert MessageType.REQUEST == "request"
        assert MessageType.RESPONSE == "response"
        assert MessageType.NOTIFICATION == "notification"
        assert MessageType.ERROR == "error"


class TestErrorCode:
    """Test ErrorCode enum."""

    def test_standard_errors(self):
        """Standard JSON-RPC error codes are defined."""
        assert ErrorCode.PARSE_ERROR == -32700
        assert ErrorCode.INVALID_REQUEST == -32600
        assert ErrorCode.METHOD_NOT_FOUND == -32601
        assert ErrorCode.INVALID_PARAMS == -32602
        assert ErrorCode.INTERNAL_ERROR == -32603

    def test_voicestudio_errors(self):
        """VoiceStudio-specific error codes are defined."""
        assert ErrorCode.PERMISSION_DENIED == -32000
        assert ErrorCode.TIMEOUT == -32001
        assert ErrorCode.PLUGIN_ERROR == -32002
        assert ErrorCode.RESOURCE_LIMIT == -32003


class TestRPCError:
    """Test RPCError class."""

    def test_create_error(self):
        """Create an error with code and message."""
        error = RPCError(code=-32600, message="Invalid request")
        assert error.code == -32600
        assert error.message == "Invalid request"
        assert error.data is None

    def test_create_error_with_data(self):
        """Create an error with additional data."""
        error = RPCError(
            code=-32602,
            message="Invalid params",
            data={"param": "value"},
        )
        assert error.data == {"param": "value"}

    def test_to_dict(self):
        """Convert error to dictionary."""
        error = RPCError(code=-32600, message="Invalid request")
        d = error.to_dict()
        assert d == {"code": -32600, "message": "Invalid request"}

    def test_to_dict_with_data(self):
        """Convert error with data to dictionary."""
        error = RPCError(code=-32600, message="Invalid request", data={"key": "val"})
        d = error.to_dict()
        assert d["data"] == {"key": "val"}

    def test_from_dict(self):
        """Create error from dictionary."""
        data = {"code": -32600, "message": "Invalid request", "data": {"key": "val"}}
        error = RPCError.from_dict(data)
        assert error.code == -32600
        assert error.message == "Invalid request"
        assert error.data == {"key": "val"}

    def test_factory_methods(self):
        """Test factory methods for common errors."""
        assert RPCError.parse_error().code == ErrorCode.PARSE_ERROR
        assert RPCError.invalid_request().code == ErrorCode.INVALID_REQUEST
        assert RPCError.method_not_found("test").code == ErrorCode.METHOD_NOT_FOUND
        assert "test" in RPCError.method_not_found("test").message
        assert RPCError.invalid_params().code == ErrorCode.INVALID_PARAMS
        assert RPCError.internal_error().code == ErrorCode.INTERNAL_ERROR
        assert RPCError.permission_denied("audio").code == ErrorCode.PERMISSION_DENIED
        assert RPCError.timeout(5000).code == ErrorCode.TIMEOUT


class TestRequest:
    """Test Request message class."""

    def test_create_request(self):
        """Create a request message."""
        request = Request(id=1, method="test.method")
        assert request.id == 1
        assert request.method == "test.method"
        assert request.params is None
        assert request.jsonrpc == "2.0"

    def test_create_request_with_params(self):
        """Create a request with parameters."""
        request = Request(id=1, method="test.method", params={"key": "value"})
        assert request.params == {"key": "value"}

    def test_to_dict(self):
        """Convert request to dictionary."""
        request = Request(id=1, method="test.method", params={"key": "value"})
        d = request.to_dict()
        assert d["jsonrpc"] == "2.0"
        assert d["id"] == 1
        assert d["method"] == "test.method"
        assert d["params"] == {"key": "value"}
        assert "_timestamp" in d

    def test_to_dict_without_params(self):
        """Convert request without params to dictionary."""
        request = Request(id=1, method="test.method")
        d = request.to_dict()
        assert "params" not in d

    def test_from_dict(self):
        """Create request from dictionary."""
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "test.method",
            "params": {"key": "value"},
        }
        request = Request.from_dict(data)
        assert request.id == 1
        assert request.method == "test.method"
        assert request.params == {"key": "value"}

    def test_to_json(self):
        """Serialize request to JSON."""
        request = Request(id=1, method="test.method")
        json_str = request.to_json()
        parsed = json.loads(json_str)
        assert parsed["id"] == 1
        assert parsed["method"] == "test.method"


class TestResponse:
    """Test Response message class."""

    def test_create_success_response(self):
        """Create a success response."""
        response = Response.success(1, {"result": "value"})
        assert response.id == 1
        assert response.result == {"result": "value"}
        assert response.error is None

    def test_create_error_response(self):
        """Create an error response."""
        error = RPCError.internal_error("Something failed")
        response = Response.failure(1, error)
        assert response.id == 1
        assert response.result is None
        assert response.error == error

    def test_to_dict_success(self):
        """Convert success response to dictionary."""
        response = Response.success(1, "result")
        d = response.to_dict()
        assert d["jsonrpc"] == "2.0"
        assert d["id"] == 1
        assert d["result"] == "result"
        assert "error" not in d

    def test_to_dict_error(self):
        """Convert error response to dictionary."""
        error = RPCError.internal_error()
        response = Response.failure(1, error)
        d = response.to_dict()
        assert "error" in d
        assert d["error"]["code"] == ErrorCode.INTERNAL_ERROR

    def test_from_dict_success(self):
        """Create response from success dictionary."""
        data = {"jsonrpc": "2.0", "id": 1, "result": {"key": "value"}}
        response = Response.from_dict(data)
        assert response.id == 1
        assert response.result == {"key": "value"}
        assert response.error is None

    def test_from_dict_error(self):
        """Create response from error dictionary."""
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32600, "message": "Invalid"},
        }
        response = Response.from_dict(data)
        assert response.id == 1
        assert response.error is not None
        assert response.error.code == -32600


class TestNotification:
    """Test Notification message class."""

    def test_create_notification(self):
        """Create a notification message."""
        notification = Notification(method="notify.log")
        assert notification.method == "notify.log"
        assert notification.params is None

    def test_create_notification_with_params(self):
        """Create a notification with parameters."""
        notification = Notification(method="notify.log", params={"level": "info"})
        assert notification.params == {"level": "info"}

    def test_to_dict(self):
        """Convert notification to dictionary."""
        notification = Notification(method="notify.log", params={"level": "info"})
        d = notification.to_dict()
        assert d["jsonrpc"] == "2.0"
        assert d["method"] == "notify.log"
        assert d["params"] == {"level": "info"}
        assert "id" not in d  # Notifications don't have id

    def test_from_dict(self):
        """Create notification from dictionary."""
        data = {"jsonrpc": "2.0", "method": "notify.log", "params": {"level": "info"}}
        notification = Notification.from_dict(data)
        assert notification.method == "notify.log"
        assert notification.params == {"level": "info"}


class TestMessageParsing:
    """Test Message.from_dict type detection."""

    def test_parse_request(self):
        """Detect and parse request message."""
        data = {"jsonrpc": "2.0", "id": 1, "method": "test"}
        message = Message.from_dict(data)
        assert isinstance(message, Request)

    def test_parse_notification(self):
        """Detect and parse notification message."""
        data = {"jsonrpc": "2.0", "method": "test"}
        message = Message.from_dict(data)
        assert isinstance(message, Notification)

    def test_parse_success_response(self):
        """Detect and parse success response message."""
        data = {"jsonrpc": "2.0", "id": 1, "result": "value"}
        message = Message.from_dict(data)
        assert isinstance(message, Response)

    def test_parse_error_response(self):
        """Detect and parse error response message."""
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "error": {"code": -32600, "message": "Invalid"},
        }
        message = Message.from_dict(data)
        assert isinstance(message, Response)

    def test_parse_from_json(self):
        """Parse message from JSON string."""
        json_str = '{"jsonrpc": "2.0", "id": 1, "method": "test"}'
        message = Message.from_json(json_str)
        assert isinstance(message, Request)

    def test_parse_invalid_json(self):
        """Raise error for invalid JSON."""
        with pytest.raises(ValueError):
            Message.from_json("not valid json")


class TestMessageEncoding:
    """Test message encoding/decoding utilities."""

    def test_encode_message(self):
        """Encode message with length prefix."""
        request = Request(id=1, method="test")
        encoded = encode_message(request)

        # First 4 bytes are length prefix
        length = int.from_bytes(encoded[:4], byteorder="big")
        body = encoded[4:]

        assert length == len(body)
        parsed = json.loads(body.decode("utf-8"))
        assert parsed["method"] == "test"

    def test_decode_message_header(self):
        """Decode length prefix from header."""
        # Create a header with length 100
        header = (100).to_bytes(4, byteorder="big")
        length = decode_message_header(header)
        assert length == 100

    def test_decode_header_insufficient_data(self):
        """Raise error for insufficient header data."""
        with pytest.raises(ValueError):
            decode_message_header(b"\x00\x00")


class TestHostMethods:
    """Test HostMethods constants."""

    def test_lifecycle_methods(self):
        """Lifecycle method names are defined."""
        assert HostMethods.INITIALIZE == "plugin.initialize"
        assert HostMethods.SHUTDOWN == "plugin.shutdown"
        assert HostMethods.ACTIVATE == "plugin.activate"
        assert HostMethods.DEACTIVATE == "plugin.deactivate"

    def test_audio_methods(self):
        """Audio method names are defined."""
        assert HostMethods.AUDIO_PLAY == "host.audio.play"
        assert HostMethods.AUDIO_STOP == "host.audio.stop"
        assert HostMethods.AUDIO_GET_DEVICES == "host.audio.getDevices"

    def test_ui_methods(self):
        """UI method names are defined."""
        assert HostMethods.UI_NOTIFY == "host.ui.notify"
        assert HostMethods.UI_SHOW_DIALOG == "host.ui.showDialog"

    def test_storage_methods(self):
        """Storage method names are defined."""
        assert HostMethods.STORAGE_GET == "host.storage.get"
        assert HostMethods.STORAGE_SET == "host.storage.set"
        assert HostMethods.STORAGE_DELETE == "host.storage.delete"

    def test_notification_methods(self):
        """Notification method names are defined."""
        assert HostMethods.LOG == "notify.log"
        assert HostMethods.PROGRESS == "notify.progress"
        assert HostMethods.HEARTBEAT == "notify.heartbeat"
