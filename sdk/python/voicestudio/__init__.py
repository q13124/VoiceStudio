"""
VoiceStudio Python SDK

A Python client library for VoiceStudio voice synthesis API.

Phase 12.1: Python SDK

Example:
    from voicestudio import VoiceStudioClient
    
    async with VoiceStudioClient() as client:
        voices = await client.list_voices()
        audio = await client.synthesize("Hello, world!", voice_id="en-US-Neural")
        audio.save("output.wav")
"""

from .client import (
    VoiceStudioClient,
    Voice,
    AudioResult,
    SynthesisOptions,
    CloneResult,
    OutputFormat,
    SynthesisEngine,
    VoiceStudioError,
    ConnectionError,
    SynthesisError,
    VoiceNotFoundError,
    synthesize_sync,
    list_voices_sync,
    __version__,
)

__all__ = [
    "VoiceStudioClient",
    "Voice",
    "AudioResult",
    "SynthesisOptions",
    "CloneResult",
    "OutputFormat",
    "SynthesisEngine",
    "VoiceStudioError",
    "ConnectionError",
    "SynthesisError",
    "VoiceNotFoundError",
    "synthesize_sync",
    "list_voices_sync",
    "__version__",
]
