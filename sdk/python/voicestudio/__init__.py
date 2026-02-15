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
    AudioResult,
    CloneResult,
    ConnectionError,
    OutputFormat,
    SynthesisEngine,
    SynthesisError,
    SynthesisOptions,
    Voice,
    VoiceNotFoundError,
    VoiceStudioClient,
    VoiceStudioError,
    __version__,
    list_voices_sync,
    synthesize_sync,
)

__all__ = [
    "AudioResult",
    "CloneResult",
    "ConnectionError",
    "OutputFormat",
    "SynthesisEngine",
    "SynthesisError",
    "SynthesisOptions",
    "Voice",
    "VoiceNotFoundError",
    "VoiceStudioClient",
    "VoiceStudioError",
    "__version__",
    "list_voices_sync",
    "synthesize_sync",
]
