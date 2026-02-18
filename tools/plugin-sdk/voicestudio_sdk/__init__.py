"""
VoiceStudio Plugin SDK.

A Python SDK for developing VoiceStudio plugins with full type safety
and access to the host API.

Quick Start:
    from voicestudio_sdk import Plugin, PluginContext
    from voicestudio_sdk.audio import AudioBuffer

    class MyPlugin(Plugin):
        async def process(self, ctx: PluginContext, audio: AudioBuffer) -> AudioBuffer:
            # Process audio
            return audio

Features:
- Type-safe plugin development
- Host API client for VoiceStudio integration
- Audio processing utilities
- Configuration management
- Testing utilities
"""

__version__ = "1.0.0"

# Core plugin classes
# Audio utilities
from voicestudio_sdk.audio import AudioBuffer, AudioFormat

# Configuration
from voicestudio_sdk.config import ConfigField, ConfigType, PluginConfig

# Host API
from voicestudio_sdk.host import HostAPI, HostConnection
from voicestudio_sdk.plugin import (
    AnalysisPlugin,
    EnhancementPlugin,
    Plugin,
    PluginContext,
    PluginMetadata,
    PluginType,
    ProcessingPlugin,
    SynthesisPlugin,
    TranscriptionPlugin,
    register_plugin,
)

# Testing utilities
from voicestudio_sdk.testing import (
    MockHost,
    PluginTestCase,
    create_test_manifest,
    create_test_plugin_directory,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "Plugin",
    "PluginContext",
    "PluginMetadata",
    "PluginType",
    # Specialized plugins
    "SynthesisPlugin",
    "TranscriptionPlugin",
    "ProcessingPlugin",
    "EnhancementPlugin",
    "AnalysisPlugin",
    "register_plugin",
    # Audio
    "AudioBuffer",
    "AudioFormat",
    # Config
    "PluginConfig",
    "ConfigField",
    "ConfigType",
    # Host
    "HostAPI",
    "HostConnection",
    # Testing
    "MockHost",
    "PluginTestCase",
    "create_test_manifest",
    "create_test_plugin_directory",
]
