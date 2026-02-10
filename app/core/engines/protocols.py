"""
Engine Protocol Definitions for VoiceStudio

This module re-exports the canonical EngineProtocol from base.py
for backward compatibility. New code should import from base.py directly.

All engines must implement this protocol/interface.
"""

# Canonical definition is in base.py - re-export for backward compatibility
from .base import (
    EngineProtocol,
    CancellationToken,
    OperationCancelledError,
    _get_torch,
)

__all__ = ["EngineProtocol", "CancellationToken", "OperationCancelledError"]
