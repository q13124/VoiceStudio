"""
Plugin Mixins for VoiceStudio (Phase 4)

Mixins provide type-specific contracts for plugins. Use these with the
base Plugin class to define the expected interface for your plugin type.

Example:
    class MyEnginePlugin(Plugin, EngineMixin):
        def register(self, app):
            ...

        async def synthesize(self, text, voice_id, options):
            ...

        async def list_voices(self):
            ...
"""

from __future__ import annotations

from abc import abstractmethod
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProcessorMixin(Protocol):
    """
    Mixin for audio processor plugins.

    Processors transform audio data (e.g., effects, normalization, compression).
    """

    @abstractmethod
    async def process(
        self,
        audio_data: bytes,
        sample_rate: int,
        options: dict[str, Any],
    ) -> bytes:
        """
        Process audio data.

        Args:
            audio_data: Raw audio bytes to process.
            sample_rate: Sample rate of the audio in Hz.
            options: Processing options specific to this processor.

        Returns:
            Processed audio bytes.
        """
        ...


@runtime_checkable
class EngineMixin(Protocol):
    """
    Mixin for TTS/synthesis engine plugins.

    Engines generate audio from text using various synthesis methods.
    """

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice_id: str,
        options: dict[str, Any],
    ) -> bytes:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize.
            voice_id: Voice identifier to use.
            options: Synthesis options specific to this engine.

        Returns:
            Synthesized audio bytes.
        """
        ...

    @abstractmethod
    async def list_voices(self) -> list[dict[str, Any]]:
        """
        List available voices.

        Returns:
            List of voice dictionaries with at least 'id' and 'name' keys.
        """
        ...

    @property
    @abstractmethod
    def sample_rate(self) -> int:
        """Return the engine's native output sample rate in Hz."""
        ...


@runtime_checkable
class ExporterMixin(Protocol):
    """
    Mixin for audio exporter plugins.

    Exporters convert audio to specific file formats.
    """

    @abstractmethod
    async def export(
        self,
        audio_data: bytes,
        output_path: Path,
        options: dict[str, Any],
    ) -> bool:
        """
        Export audio to a file.

        Args:
            audio_data: Raw audio bytes to export.
            output_path: Destination file path.
            options: Export options specific to this exporter.

        Returns:
            True if export succeeded, False otherwise.
        """
        ...

    @property
    @abstractmethod
    def supported_formats(self) -> list[str]:
        """Return list of supported export format extensions (e.g., ['flac', 'wav'])."""
        ...

    @property
    @abstractmethod
    def target_format(self) -> str:
        """Return the primary target format for this exporter."""
        ...


@runtime_checkable
class ImporterMixin(Protocol):
    """
    Mixin for audio importer plugins.

    Importers read audio from specific file formats.
    """

    @abstractmethod
    async def import_audio(
        self,
        input_path: Path,
        options: dict[str, Any],
    ) -> tuple[bytes, int]:
        """
        Import audio from a file.

        Args:
            input_path: Source file path.
            options: Import options specific to this importer.

        Returns:
            Tuple of (audio_data bytes, sample_rate int).
        """
        ...

    @property
    @abstractmethod
    def supported_formats(self) -> list[str]:
        """Return list of supported import format extensions."""
        ...


@runtime_checkable
class UIPanelMixin(Protocol):
    """
    Mixin for UI panel plugins.

    UI panels provide custom frontend components.
    """

    @property
    @abstractmethod
    def panel_id(self) -> str:
        """Unique identifier for this panel."""
        ...

    @property
    @abstractmethod
    def panel_title(self) -> str:
        """Display title for this panel."""
        ...

    @property
    @abstractmethod
    def panel_icon(self) -> str | None:
        """Optional icon name or path for this panel."""
        ...

    @abstractmethod
    def get_panel_state(self) -> dict[str, Any]:
        """Return current panel state for frontend rendering."""
        ...
