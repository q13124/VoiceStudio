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
    ErrorCode,
    MessageType,
    create_ack,
    create_complete,
    create_data,
    create_error,
    create_message,
    create_pong,
    create_progress,
    generate_request_id,
)

__all__ = [
    "ErrorCode",
    "MessageType",
    "create_ack",
    "create_complete",
    "create_data",
    "create_error",
    "create_message",
    "create_pong",
    "create_progress",
    "generate_request_id",
]
