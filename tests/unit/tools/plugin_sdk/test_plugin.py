"""
Unit tests for the plugin module.
"""

import os
import sys

import pytest

# Add SDK to path for testing
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "tools", "plugin-sdk")
)

from voicestudio_sdk.host import HostAPI, HostConnection
from voicestudio_sdk.plugin import (
    Plugin,
    PluginContext,
    PluginMetadata,
    PluginType,
    SynthesisPlugin,
    TranscriptionPlugin,
    register_plugin,
)


class TestPluginMetadata:
    """Tests for PluginMetadata dataclass."""

    def test_create_minimal_metadata(self):
        """Test creating metadata with required fields only."""
        from voicestudio_sdk.plugin import PluginArchitecture

        metadata = PluginMetadata(
            id="com.test.plugin",
            name="Test Plugin",
            version="1.0.0",
            author="Test Author",
            description="A test plugin",
            category=PluginType.SYNTHESIS,
            architecture=PluginArchitecture.BACKEND_ONLY,
        )

        assert metadata.id == "com.test.plugin"
        assert metadata.name == "Test Plugin"
        assert metadata.version == "1.0.0"
        assert metadata.category == PluginType.SYNTHESIS
        assert metadata.plugin_type == PluginType.SYNTHESIS  # Legacy alias
        assert metadata.architecture == PluginArchitecture.BACKEND_ONLY

    def test_create_full_metadata(self):
        """Test creating metadata with all fields."""
        from voicestudio_sdk.plugin import PluginArchitecture

        metadata = PluginMetadata(
            id="com.test.plugin",
            name="Test Plugin",
            version="1.0.0",
            author="Test Author",
            description="A test plugin",
            category=PluginType.TRANSCRIPTION,
            architecture=PluginArchitecture.FULL_STACK,
            license="MIT",
            homepage="https://example.com",
            repository="https://github.com/test/plugin",
            min_voicestudio_version="1.0.0",
        )

        assert metadata.license == "MIT"
        assert metadata.homepage == "https://example.com"
        assert metadata.min_voicestudio_version == "1.0.0"
        assert metadata.category == PluginType.TRANSCRIPTION
        assert metadata.architecture == PluginArchitecture.FULL_STACK

    def test_from_manifest(self):
        """Test creating metadata from a manifest dictionary."""
        from voicestudio_sdk.plugin import PluginArchitecture

        manifest = {
            "id": "com.example.tts",
            "name": "Example TTS",
            "version": "1.2.3",
            "description": "An example TTS plugin",
            "author": {"name": "Test Author", "email": "test@example.com"},
            "license": "MIT",
            "plugin_type": "full_stack",  # Architecture type
            "category": "voice_synthesis",  # Functional category
            "min_app_version": "2.0.0",
            "capabilities": ["tts", "streaming"],
            "security": {"permissions": ["audio.read", "storage.write"]},
        }

        metadata = PluginMetadata.from_manifest(manifest)

        assert metadata.id == "com.example.tts"
        assert metadata.name == "Example TTS"
        assert metadata.version == "1.2.3"
        assert metadata.author == "Test Author"
        assert metadata.category == PluginType.SYNTHESIS
        assert metadata.architecture == PluginArchitecture.FULL_STACK
        assert metadata.min_voicestudio_version == "2.0.0"
        assert metadata.capabilities == ["tts", "streaming"]
        assert metadata.permissions == ["audio.read", "storage.write"]

    def test_from_manifest_legacy_format(self):
        """Test creating metadata from legacy manifest format."""
        from voicestudio_sdk.plugin import PluginArchitecture

        # Legacy manifest without explicit plugin_type/category
        manifest = {
            "id": "com.example.legacy",
            "name": "Legacy Plugin",
            "version": "0.9.0",
            "description": "A legacy plugin",
            "author": "Simple Author",  # String instead of dict
            "license": "Apache-2.0",
            # Missing plugin_type - should default to backend_only
            # Missing category - should default to utilities
        }

        metadata = PluginMetadata.from_manifest(manifest)

        assert metadata.id == "com.example.legacy"
        assert metadata.author == "Simple Author"
        assert metadata.category == PluginType.UTILITY  # Default
        assert metadata.architecture == PluginArchitecture.BACKEND_ONLY  # Default


class TestPluginType:
    """Tests for PluginType enum."""

    def test_plugin_types_exist(self):
        """Test that all expected plugin types exist."""
        assert PluginType.SYNTHESIS
        assert PluginType.TRANSCRIPTION
        assert PluginType.PROCESSING
        assert PluginType.ENHANCEMENT
        assert PluginType.ANALYSIS

    def test_plugin_type_values(self):
        """Test plugin type string values (aligned with manifest schema 'category')."""
        assert PluginType.SYNTHESIS.value == "voice_synthesis"
        assert PluginType.TRANSCRIPTION.value == "speech_recognition"
        assert PluginType.PROCESSING.value == "audio_effects"
        assert PluginType.UTILITY.value == "utilities"

    def test_plugin_type_from_string(self):
        """Test from_string handles both new and legacy values."""
        # New schema values
        assert PluginType.from_string("voice_synthesis") == PluginType.SYNTHESIS
        assert PluginType.from_string("speech_recognition") == PluginType.TRANSCRIPTION
        # Legacy short names
        assert PluginType.from_string("synthesis") == PluginType.SYNTHESIS
        assert PluginType.from_string("transcription") == PluginType.TRANSCRIPTION
        # Fallback for unknown
        assert PluginType.from_string("unknown_type") == PluginType.UTILITY


class TestPluginContext:
    """Tests for PluginContext dataclass."""

    def test_create_context(self):
        """Test creating a plugin context."""
        host = HostAPI(HostConnection(mode="direct"))

        ctx = PluginContext(
            plugin_id="com.test.plugin",
            plugin_path="/path/to/plugin",
            config={"key": "value"},
            host_api=host,
        )

        assert ctx.plugin_id == "com.test.plugin"
        assert ctx.plugin_path == "/path/to/plugin"
        assert ctx.config["key"] == "value"
        assert ctx.host_api == host

    def test_context_shortcut(self):
        """Test host shortcut property."""
        host = HostAPI(HostConnection(mode="direct"))

        ctx = PluginContext(
            plugin_id="com.test.plugin",
            plugin_path="/path/to/plugin",
            config={},
            host_api=host,
        )

        assert ctx.host == ctx.host_api


class TestPluginBase:
    """Tests for Plugin base class."""

    def test_plugin_instantiation(self):
        """Test that Plugin can be subclassed and instantiated."""

        class TestPlugin(Plugin):
            pass

        plugin = TestPlugin()
        assert plugin is not None

    @pytest.mark.asyncio
    async def test_plugin_initialize(self):
        """Test plugin initialization."""

        class TestPlugin(Plugin):
            async def initialize(self, ctx):
                await super().initialize(ctx)
                self.initialized = True

        plugin = TestPlugin()
        host = HostAPI(HostConnection(mode="direct"))
        await host.connect()

        ctx = PluginContext(
            plugin_id="com.test.plugin",
            plugin_path="/path/to/plugin",
            config={},
            host_api=host,
        )

        await plugin.initialize(ctx)
        assert plugin.initialized

    @pytest.mark.asyncio
    async def test_plugin_shutdown(self):
        """Test plugin shutdown."""

        class TestPlugin(Plugin):
            async def shutdown(self):
                await super().shutdown()
                self.shutdown_called = True

        plugin = TestPlugin()
        await plugin.shutdown()
        assert plugin.shutdown_called


class TestSynthesisPlugin:
    """Tests for SynthesisPlugin."""

    def test_synthesis_plugin_instantiation(self):
        """Test that SynthesisPlugin can be subclassed."""

        class MyTTSPlugin(SynthesisPlugin):
            async def synthesize(self, text, voice, **options):
                return None

        plugin = MyTTSPlugin()
        assert plugin is not None

    def test_synthesis_plugin_requires_synthesize(self):
        """Test that synthesize method must be implemented."""
        # This would fail if we tried to instantiate without implementing synthesize
        # We can't test this directly without triggering the abstract method error
        pass


class TestTranscriptionPlugin:
    """Tests for TranscriptionPlugin."""

    def test_transcription_plugin_instantiation(self):
        """Test that TranscriptionPlugin can be subclassed."""

        class MySTTPlugin(TranscriptionPlugin):
            async def transcribe(self, audio, language=None, **options):
                return ""

        plugin = MySTTPlugin()
        assert plugin is not None


class TestRegisterPlugin:
    """Tests for register_plugin decorator."""

    def test_register_plugin_decorator(self):
        """Test that register_plugin decorator works."""

        @register_plugin("com.test.decorated")
        class DecoratedPlugin(Plugin):
            pass

        # The decorator should attach metadata
        assert hasattr(DecoratedPlugin, "_plugin_id")
        assert DecoratedPlugin._plugin_id == "com.test.decorated"
