"""
Core plugin classes and protocols.

This module provides the base classes for VoiceStudio plugin development.
"""

import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, TypeVar

T = TypeVar("T")


class PluginType(str, Enum):
    """Plugin functional type classification (maps to manifest 'category')."""

    SYNTHESIS = "voice_synthesis"
    TRANSCRIPTION = "speech_recognition"
    PROCESSING = "audio_effects"
    ENHANCEMENT = "audio_effects"
    ANALYSIS = "audio_analysis"
    VOICE_CONVERSION = "voice_conversion"
    VIDEO_PROCESSING = "video_processing"
    INTEGRATION = "integrations"
    UTILITY = "utilities"
    DEVELOPER_TOOL = "developer_tools"

    # Legacy aliases for backward compatibility
    @classmethod
    def from_string(cls, value: str) -> "PluginType":
        """Convert a string to PluginType, handling legacy values."""
        # Try direct match first
        for member in cls:
            if member.value == value:
                return member
        # Handle legacy short names
        legacy_map = {
            "synthesis": cls.SYNTHESIS,
            "transcription": cls.TRANSCRIPTION,
            "processing": cls.PROCESSING,
            "enhancement": cls.ENHANCEMENT,
            "analysis": cls.ANALYSIS,
            "utility": cls.UTILITY,
        }
        if value in legacy_map:
            return legacy_map[value]
        return cls.UTILITY


class PluginArchitecture(str, Enum):
    """Plugin architecture type (maps to manifest 'plugin_type')."""

    BACKEND_ONLY = "backend_only"
    FRONTEND_ONLY = "frontend_only"
    FULL_STACK = "full_stack"


@dataclass
class PluginMetadata:
    """Plugin metadata extracted from manifest."""

    id: str
    name: str
    version: str
    author: str = ""
    description: str = ""
    category: PluginType = PluginType.UTILITY  # Functional category (voice_synthesis, etc.)
    architecture: PluginArchitecture = PluginArchitecture.BACKEND_ONLY  # Architecture type
    license: str = ""
    homepage: str = ""
    repository: str = ""
    min_voicestudio_version: str = ""
    capabilities: list[str] = field(default_factory=list)
    permissions: list[str] = field(default_factory=list)

    # Legacy alias for backward compatibility
    @property
    def plugin_type(self) -> PluginType:
        """Legacy alias for category."""
        return self.category

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> "PluginMetadata":
        """Create metadata from a parsed manifest dictionary."""
        author = manifest.get("author", {})
        if isinstance(author, dict):
            author_name = author.get("name", "Unknown")
        else:
            author_name = str(author) if author else ""

        # Parse category (functional type)
        category_str = manifest.get("category", "utilities")
        category = PluginType.from_string(category_str)

        # Parse architecture (plugin_type in manifest)
        arch_str = manifest.get("plugin_type", "backend_only")
        try:
            architecture = PluginArchitecture(arch_str)
        except ValueError:
            architecture = PluginArchitecture.BACKEND_ONLY

        # Handle distribution section for catalog plugins
        distribution = manifest.get("distribution", {})

        return cls(
            id=manifest.get("id", ""),
            name=manifest.get("name", ""),
            version=manifest.get("version", "0.0.0"),
            author=author_name,
            description=manifest.get("description", ""),
            category=category,
            architecture=architecture,
            license=manifest.get("license", ""),
            homepage=manifest.get("homepage", distribution.get("homepage", "")),
            repository=manifest.get("repository", distribution.get("repository", "")),
            min_voicestudio_version=manifest.get("min_app_version", ""),
            capabilities=manifest.get("capabilities", []),
            permissions=manifest.get("security", {}).get("permissions", []),
        )


@dataclass
class PluginContext:
    """
    Context provided to plugin operations.

    Contains runtime information and access to host services.

    Can be created in two ways:
    1. With metadata object: PluginContext(metadata=metadata, config={})
    2. With simple fields: PluginContext(plugin_id="...", plugin_path="...", host_api=host)
    """

    # Simple creation fields (alternative to metadata)
    plugin_id: str = ""
    plugin_path: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    host_api: Optional[Any] = field(default=None, repr=False)

    # Full metadata (optional)
    metadata: Optional[PluginMetadata] = None
    session_id: str = ""
    workspace_path: Optional[str] = None

    def __post_init__(self):
        """Initialize derived fields."""
        # If metadata provided, extract plugin_id from it
        if self.metadata and not self.plugin_id:
            self.plugin_id = self.metadata.id

    @property
    def host(self) -> Any:
        """Get the host API for communicating with VoiceStudio."""
        if self.host_api is None:
            raise RuntimeError("Host API not available in this context")
        return self.host_api

    def get_config(self, key: str, default: T = None) -> T:
        """Get a configuration value with optional default."""
        return self.config.get(key, default)

    def require_config(self, key: str) -> Any:
        """Get a required configuration value, raising if not present."""
        if key not in self.config:
            raise ValueError(f"Required configuration '{key}' not found")
        return self.config[key]


class Plugin(abc.ABC):
    """
    Base class for VoiceStudio plugins.

    All plugins must inherit from this class and implement the required
    abstract methods based on their plugin type.

    Example:
        class MySynthesisPlugin(Plugin):
            async def synthesize(self, ctx: PluginContext, text: str) -> bytes:
                # Generate audio from text
                return audio_bytes
    """

    def __init__(self) -> None:
        """Initialize the plugin."""
        self._metadata: Optional[PluginMetadata] = None
        self._initialized: bool = False

    @property
    def metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        if self._metadata is None:
            raise RuntimeError("Plugin not yet initialized")
        return self._metadata

    @property
    def is_initialized(self) -> bool:
        """Check if the plugin has been initialized."""
        return self._initialized

    async def initialize(self, ctx: PluginContext) -> None:
        """
        Initialize the plugin.

        Called once when the plugin is first loaded. Override to perform
        setup tasks like loading models or establishing connections.

        Args:
            ctx: The plugin context with metadata and configuration.
        """
        # Store metadata if provided, otherwise create minimal metadata
        if ctx.metadata:
            self._metadata = ctx.metadata
        elif ctx.plugin_id:
            self._metadata = PluginMetadata(
                id=ctx.plugin_id,
                name=ctx.plugin_id,
                version="0.0.0",
            )
        self._initialized = True

    async def shutdown(self) -> None:
        """
        Shutdown the plugin.

        Called when the plugin is being unloaded. Override to clean up
        resources like closing connections or unloading models.
        """
        self._initialized = False

    def get_capabilities(self) -> list[str]:
        """
        Get the list of capabilities this plugin provides.

        Returns:
            List of capability identifiers.
        """
        if self._metadata:
            return self._metadata.capabilities
        return []

    def supports_capability(self, capability: str) -> bool:
        """
        Check if this plugin supports a specific capability.

        Args:
            capability: The capability identifier to check.

        Returns:
            True if the capability is supported.
        """
        return capability in self.get_capabilities()


class SynthesisPlugin(Plugin):
    """Base class for text-to-speech synthesis plugins."""

    @abc.abstractmethod
    async def synthesize(
        self,
        ctx: PluginContext,
        text: str,
        voice: Optional[str] = None,
        **kwargs: Any,
    ) -> bytes:
        """
        Synthesize speech from text.

        Args:
            ctx: The plugin context.
            text: The text to synthesize.
            voice: Optional voice identifier.
            **kwargs: Additional synthesis parameters.

        Returns:
            Audio data as bytes.
        """
        ...

    async def list_voices(self, ctx: PluginContext) -> list[dict[str, Any]]:
        """
        List available voices.

        Returns:
            List of voice dictionaries with 'id' and 'name' keys.
        """
        return []


class TranscriptionPlugin(Plugin):
    """Base class for speech-to-text transcription plugins."""

    @abc.abstractmethod
    async def transcribe(
        self,
        ctx: PluginContext,
        audio: bytes,
        language: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """
        Transcribe audio to text.

        Args:
            ctx: The plugin context.
            audio: Audio data as bytes.
            language: Optional language code.
            **kwargs: Additional transcription parameters.

        Returns:
            Transcribed text.
        """
        ...

    async def list_languages(self, ctx: PluginContext) -> list[str]:
        """
        List supported languages.

        Returns:
            List of language codes.
        """
        return []


class ProcessingPlugin(Plugin):
    """Base class for audio processing plugins."""

    @abc.abstractmethod
    async def process(
        self,
        ctx: PluginContext,
        audio: bytes,
        **kwargs: Any,
    ) -> bytes:
        """
        Process audio data.

        Args:
            ctx: The plugin context.
            audio: Input audio data.
            **kwargs: Additional processing parameters.

        Returns:
            Processed audio data.
        """
        ...


class EnhancementPlugin(Plugin):
    """Base class for audio enhancement plugins."""

    @abc.abstractmethod
    async def enhance(
        self,
        ctx: PluginContext,
        audio: bytes,
        **kwargs: Any,
    ) -> bytes:
        """
        Enhance audio quality.

        Args:
            ctx: The plugin context.
            audio: Input audio data.
            **kwargs: Additional enhancement parameters.

        Returns:
            Enhanced audio data.
        """
        ...


class AnalysisPlugin(Plugin):
    """Base class for audio analysis plugins."""

    @abc.abstractmethod
    async def analyze(
        self,
        ctx: PluginContext,
        audio: bytes,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Analyze audio data.

        Args:
            ctx: The plugin context.
            audio: Input audio data.
            **kwargs: Additional analysis parameters.

        Returns:
            Analysis results as a dictionary.
        """
        ...


# Plugin registry for discovery
_plugin_registry: dict[str, type[Plugin]] = {}


def register_plugin(plugin_id: str):
    """
    Decorator to register a plugin class.

    Example:
        @register_plugin("com.example.my-plugin")
        class MyPlugin(Plugin):
            ...
    """
    def decorator(cls: type[Plugin]) -> type[Plugin]:
        cls._plugin_id = plugin_id
        _plugin_registry[plugin_id] = cls
        return cls
    return decorator


def get_registered_plugins() -> dict[str, type[Plugin]]:
    """Get all registered plugin classes."""
    return _plugin_registry.copy()
