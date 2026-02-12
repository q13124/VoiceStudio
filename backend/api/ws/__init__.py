"""
WebSocket events package

Provides standardized WebSocket messaging for VoiceStudio.

Usage:
    from backend.api.ws.protocol import (
        create_message, create_error, create_ack,
        create_progress, create_complete, MessageType, ErrorCode
    )
"""

from .protocol import (
    create_message,
    create_error,
    create_ack,
    create_progress,
    create_complete,
    create_pong,
    create_data,
    generate_request_id,
    MessageType,
    ErrorCode,
)

__all__ = [
    "create_message",
    "create_error",
    "create_ack",
    "create_progress",
    "create_complete",
    "create_pong",
    "create_data",
    "generate_request_id",
    "MessageType",
    "ErrorCode",
]