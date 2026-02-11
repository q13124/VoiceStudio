"""
WebSocket Message Protocol Standardization

GAP-INT-002: Standardized WebSocket message format for VoiceStudio.

All WebSocket messages should follow this standardized format:

    {
        "type": "<message_type>",
        "topic": "<optional_topic>",
        "payload": { ... },
        "timestamp": "<ISO8601>",
        "request_id": "<optional_correlation_id>"
    }

Message Types:
    - "data": Regular data messages
    - "error": Error messages
    - "ack": Acknowledgments
    - "ping"/"pong": Heartbeat
    - "subscribe"/"unsubscribe": Topic management
    - "start"/"stop": Stream control
    - "complete": Operation complete
    - "progress": Progress updates

Usage:
    from backend.api.ws.protocol import (
        create_message, create_error, create_ack,
        create_progress, create_complete
    )
    
    # Send a data message
    await ws.send_json(create_message("audio_chunk", {"data": chunk}))
    
    # Send an error
    await ws.send_json(create_error("Synthesis failed", code="ENGINE_ERROR"))
    
    # Send progress
    await ws.send_json(create_progress(50, "Processing audio..."))
"""

from datetime import datetime
from typing import Any, Dict, Optional
import uuid


def create_message(
    message_type: str,
    payload: Optional[Dict[str, Any]] = None,
    topic: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a standardized WebSocket message.
    
    Args:
        message_type: Type of message (e.g., "data", "audio_chunk", "status")
        payload: Message payload data
        topic: Optional topic for pub/sub patterns
        request_id: Optional correlation ID for request/response patterns
    
    Returns:
        Standardized message dictionary
    """
    msg: Dict[str, Any] = {
        "type": message_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    if payload is not None:
        msg["payload"] = payload
    
    if topic is not None:
        msg["topic"] = topic
    
    if request_id is not None:
        msg["request_id"] = request_id
    
    return msg


def create_error(
    message: str,
    code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a standardized error message.
    
    Args:
        message: Human-readable error message
        code: Optional error code (e.g., "ENGINE_ERROR", "VALIDATION_ERROR")
        details: Optional additional error details
        request_id: Optional correlation ID
    
    Returns:
        Standardized error message dictionary
    """
    payload: Dict[str, Any] = {"message": message}
    
    if code is not None:
        payload["code"] = code
    
    if details is not None:
        payload["details"] = details
    
    return create_message("error", payload, request_id=request_id)


def create_ack(
    action: str,
    success: bool = True,
    message: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create an acknowledgment message.
    
    Args:
        action: The action being acknowledged (e.g., "subscribe", "reset")
        success: Whether the action succeeded
        message: Optional status message
        request_id: Optional correlation ID
    
    Returns:
        Standardized ack message dictionary
    """
    payload: Dict[str, Any] = {"action": action, "success": success}
    
    if message is not None:
        payload["message"] = message
    
    return create_message("ack", payload, request_id=request_id)


def create_progress(
    percent: float,
    message: Optional[str] = None,
    stage: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a progress update message.
    
    Args:
        percent: Progress percentage (0-100)
        message: Optional status message
        stage: Optional stage name (e.g., "loading", "processing", "encoding")
        request_id: Optional correlation ID
    
    Returns:
        Standardized progress message dictionary
    """
    payload: Dict[str, Any] = {"percent": min(100, max(0, percent))}
    
    if message is not None:
        payload["message"] = message
    
    if stage is not None:
        payload["stage"] = stage
    
    return create_message("progress", payload, request_id=request_id)


def create_complete(
    message: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a completion message.
    
    Args:
        message: Optional completion message
        result: Optional result data
        request_id: Optional correlation ID
    
    Returns:
        Standardized complete message dictionary
    """
    payload: Dict[str, Any] = {}
    
    if message is not None:
        payload["message"] = message
    
    if result is not None:
        payload["result"] = result
    
    return create_message("complete", payload, request_id=request_id)


def create_pong() -> Dict[str, Any]:
    """Create a pong response to a ping."""
    return create_message("pong")


def create_data(
    data: Dict[str, Any],
    topic: Optional[str] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a data message.
    
    Args:
        data: The data payload
        topic: Optional topic
        request_id: Optional correlation ID
    
    Returns:
        Standardized data message dictionary
    """
    return create_message("data", data, topic=topic, request_id=request_id)


def generate_request_id() -> str:
    """Generate a unique request ID for correlation."""
    return str(uuid.uuid4())


# Message type constants for consistency
class MessageType:
    """Standard message type constants."""
    
    DATA = "data"
    ERROR = "error"
    ACK = "ack"
    PING = "ping"
    PONG = "pong"
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    START = "start"
    STOP = "stop"
    COMPLETE = "complete"
    PROGRESS = "progress"
    
    # Audio-specific
    AUDIO_CHUNK = "audio_chunk"
    AUDIO_COMPLETE = "audio_complete"
    
    # Conversion-specific
    CONVERTED_CHUNK = "converted_chunk"
    
    # Training-specific
    TRAINING_UPDATE = "training_update"
    TRAINING_COMPLETE = "training_complete"
    
    # Visualization
    VISUALIZATION_FRAME = "visualization_frame"
    METERS_UPDATE = "meters_update"


# Error code constants
class ErrorCode:
    """Standard error codes for WebSocket errors."""
    
    VALIDATION_ERROR = "VALIDATION_ERROR"
    ENGINE_ERROR = "ENGINE_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAVAILABLE = "UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    UNAUTHORIZED = "UNAUTHORIZED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    TIMEOUT = "TIMEOUT"
