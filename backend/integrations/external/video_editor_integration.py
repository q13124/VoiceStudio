"""
Phase 6: External App Integration
Task 6.2: Video editor integration support.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class VideoEditorType(Enum):
    """Supported video editor types."""

    PREMIERE_PRO = "premiere_pro"
    DAVINCI_RESOLVE = "davinci_resolve"
    FINAL_CUT_PRO = "final_cut_pro"
    VEGAS_PRO = "vegas_pro"
    AFTER_EFFECTS = "after_effects"
    KDENLIVE = "kdenlive"
    OPENSHOT = "openshot"
    SHOTCUT = "shotcut"


@dataclass
class VideoProject:
    """Video project information."""

    path: Path
    name: str
    editor_type: VideoEditorType
    frame_rate: float = 30.0
    resolution: tuple[int, int] = (1920, 1080)
    duration: float = 0.0
    audio_tracks: list[dict[str, Any]] = field(default_factory=list)
    video_tracks: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SubtitleEntry:
    """A single subtitle entry."""

    start_time: float
    end_time: float
    text: str
    style: str | None = None


@dataclass
class VideoExportSettings:
    """Settings for exporting to video editor."""

    audio_format: str = "wav"
    sample_rate: int = 48000
    bit_depth: int = 24
    include_subtitles: bool = True
    subtitle_format: str = "srt"
    sync_to_timecode: bool = True


class VideoEditorIntegration(ABC):
    """Abstract base class for video editor integration."""

    @property
    @abstractmethod
    def editor_type(self) -> VideoEditorType:
        """Get the video editor type."""
        pass

    @abstractmethod
    async def detect_installation(self) -> Path | None:
        """Detect if the video editor is installed."""
        pass

    @abstractmethod
    async def export_audio_with_subtitles(
        self,
        audio_path: Path,
        subtitles: list[SubtitleEntry],
        settings: VideoExportSettings,
        output_dir: Path,
    ) -> dict[str, Path]:
        """Export audio and subtitles for video editor."""
        pass

    @abstractmethod
    async def generate_project_import(
        self, audio_path: Path, subtitles: list[SubtitleEntry], settings: VideoExportSettings
    ) -> str:
        """Generate import script/file for video editor."""
        pass


class DaVinciResolveIntegration(VideoEditorIntegration):
    """Integration with DaVinci Resolve."""

    @property
    def editor_type(self) -> VideoEditorType:
        return VideoEditorType.DAVINCI_RESOLVE

    async def detect_installation(self) -> Path | None:
        """Detect DaVinci Resolve installation."""
        import os

        paths = [
            Path(os.environ.get("PROGRAMFILES", "")) / "Blackmagic Design/DaVinci Resolve",
            Path("C:/Program Files/Blackmagic Design/DaVinci Resolve"),
        ]

        for path in paths:
            if path.exists():
                return path

        return None

    async def export_audio_with_subtitles(
        self,
        audio_path: Path,
        subtitles: list[SubtitleEntry],
        settings: VideoExportSettings,
        output_dir: Path,
    ) -> dict[str, Path]:
        """Export audio and subtitles for DaVinci Resolve."""
        output_dir.mkdir(parents=True, exist_ok=True)

        outputs: dict[str, Path] = {}

        # Copy audio file
        audio_output = output_dir / audio_path.name
        import shutil

        shutil.copy2(audio_path, audio_output)
        outputs["audio"] = audio_output

        # Generate SRT subtitles
        if subtitles and settings.include_subtitles:
            srt_path = output_dir / f"{audio_path.stem}.srt"
            srt_content = self._generate_srt(subtitles)
            srt_path.write_text(srt_content, encoding="utf-8")
            outputs["subtitles"] = srt_path

        return outputs

    async def generate_project_import(
        self, audio_path: Path, subtitles: list[SubtitleEntry], settings: VideoExportSettings
    ) -> str:
        """Generate DaVinci Resolve import instructions."""
        return f"""
DaVinci Resolve Import Instructions:
1. Open DaVinci Resolve
2. Create or open a project
3. Go to File > Import > Media
4. Select the audio file: {audio_path.name}
5. Drag the audio to the timeline
6. For subtitles, go to File > Import > Subtitle
7. Select the .srt file
"""

    def _generate_srt(self, subtitles: list[SubtitleEntry]) -> str:
        """Generate SRT format subtitles."""
        lines = []

        for i, entry in enumerate(subtitles, 1):
            start = self._format_srt_time(entry.start_time)
            end = self._format_srt_time(entry.end_time)
            lines.append(f"{i}")
            lines.append(f"{start} --> {end}")
            lines.append(entry.text)
            lines.append("")

        return "\n".join(lines)

    def _format_srt_time(self, seconds: float) -> str:
        """Format time for SRT format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class PremierProIntegration(VideoEditorIntegration):
    """Integration with Adobe Premiere Pro."""

    @property
    def editor_type(self) -> VideoEditorType:
        return VideoEditorType.PREMIERE_PRO

    async def detect_installation(self) -> Path | None:
        """Detect Premiere Pro installation."""
        import os

        paths = [
            Path(os.environ.get("PROGRAMFILES", "")) / "Adobe/Adobe Premiere Pro 2024",
            Path(os.environ.get("PROGRAMFILES", "")) / "Adobe/Adobe Premiere Pro 2023",
            Path(os.environ.get("PROGRAMFILES", "")) / "Adobe/Adobe Premiere Pro CC",
        ]

        for path in paths:
            if path.exists():
                return path

        return None

    async def export_audio_with_subtitles(
        self,
        audio_path: Path,
        subtitles: list[SubtitleEntry],
        settings: VideoExportSettings,
        output_dir: Path,
    ) -> dict[str, Path]:
        """Export audio and subtitles for Premiere Pro."""
        output_dir.mkdir(parents=True, exist_ok=True)

        outputs: dict[str, Path] = {}

        # Copy audio file
        audio_output = output_dir / audio_path.name
        import shutil

        shutil.copy2(audio_path, audio_output)
        outputs["audio"] = audio_output

        # Generate SRT subtitles (Premiere supports SRT)
        if subtitles and settings.include_subtitles:
            srt_path = output_dir / f"{audio_path.stem}.srt"
            srt_content = self._generate_srt(subtitles)
            srt_path.write_text(srt_content, encoding="utf-8")
            outputs["subtitles"] = srt_path

        return outputs

    async def generate_project_import(
        self, audio_path: Path, subtitles: list[SubtitleEntry], settings: VideoExportSettings
    ) -> str:
        """Generate Premiere Pro import instructions."""
        return f"""
Adobe Premiere Pro Import Instructions:
1. Open Adobe Premiere Pro
2. Create or open a project
3. Double-click in the Project panel to import
4. Select the audio file: {audio_path.name}
5. Drag the audio to the timeline
6. For captions, go to File > Import and select the .srt file
7. Or use the Captions workspace for manual entry
"""

    def _generate_srt(self, subtitles: list[SubtitleEntry]) -> str:
        """Generate SRT format subtitles."""
        lines = []

        for i, entry in enumerate(subtitles, 1):
            start = self._format_srt_time(entry.start_time)
            end = self._format_srt_time(entry.end_time)
            lines.append(f"{i}")
            lines.append(f"{start} --> {end}")
            lines.append(entry.text)
            lines.append("")

        return "\n".join(lines)

    def _format_srt_time(self, seconds: float) -> str:
        """Format time for SRT format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class VideoEditorManager:
    """Manager for video editor integrations."""

    def __init__(self):
        self._integrations: dict[VideoEditorType, VideoEditorIntegration] = {}
        self._detected_editors: dict[VideoEditorType, Path] = {}

        # Register default integrations
        self.register(DaVinciResolveIntegration())
        self.register(PremierProIntegration())

    def register(self, integration: VideoEditorIntegration) -> None:
        """Register a video editor integration."""
        self._integrations[integration.editor_type] = integration

    def get_integration(self, editor_type: VideoEditorType) -> VideoEditorIntegration | None:
        """Get a video editor integration by type."""
        return self._integrations.get(editor_type)

    async def detect_installed_editors(self) -> dict[VideoEditorType, Path]:
        """Detect all installed video editors."""
        self._detected_editors.clear()

        for editor_type, integration in self._integrations.items():
            path = await integration.detect_installation()
            if path:
                self._detected_editors[editor_type] = path
                logger.info(f"Detected {editor_type.value} at {path}")

        return self._detected_editors

    async def export_for_video(
        self,
        audio_path: Path,
        subtitles: list[SubtitleEntry],
        editor_type: VideoEditorType,
        output_dir: Path,
        settings: VideoExportSettings | None = None,
    ) -> dict[str, Path]:
        """Export audio and subtitles for a video editor."""
        integration = self.get_integration(editor_type)
        if not integration:
            raise ValueError(f"No integration for {editor_type.value}")

        settings = settings or VideoExportSettings()

        return await integration.export_audio_with_subtitles(
            audio_path, subtitles, settings, output_dir
        )
