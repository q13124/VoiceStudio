"""
Phase 6: Import System
Task 6.7: Project and asset import capabilities.
"""

from __future__ import annotations

import json
import logging
import shutil
import zipfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ImportFormat(Enum):
    """Supported import formats."""

    VOICESTUDIO_PROJECT = "vsproj"
    VOICESTUDIO_ARCHIVE = "vsarc"
    AUDIO_FILE = "audio"
    TEXT_FILE = "text"
    SUBTITLE_FILE = "subtitle"
    VOICE_MODEL = "voice"
    WORKFLOW = "workflow"


@dataclass
class ImportResult:
    """Result of an import operation."""

    success: bool
    imported_items: list[str] = field(default_factory=list)
    skipped_items: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    project_path: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ImportOptions:
    """Options for importing."""

    overwrite_existing: bool = False
    import_voices: bool = True
    import_settings: bool = False
    import_workflows: bool = True
    target_directory: Path | None = None
    rename_prefix: str | None = None


class ProjectImporter:
    """Importer for VoiceStudio projects and assets."""

    SUPPORTED_AUDIO = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"}
    SUPPORTED_TEXT = {".txt", ".srt", ".vtt", ".ass", ".ssa"}

    def __init__(self, projects_dir: Path | None = None):
        self._projects_dir = projects_dir or Path.home() / "VoiceStudio/Projects"
        self._projects_dir.mkdir(parents=True, exist_ok=True)

    async def import_project_archive(
        self, archive_path: Path, options: ImportOptions | None = None
    ) -> ImportResult:
        """Import a VoiceStudio project archive."""
        options = options or ImportOptions()
        result = ImportResult(success=True)

        try:
            if not archive_path.exists():
                return ImportResult(success=False, errors=[f"Archive not found: {archive_path}"])

            # Extract archive
            with zipfile.ZipFile(archive_path, "r") as zf:
                # Read manifest
                try:
                    manifest_data = zf.read("manifest.json").decode("utf-8")
                    manifest = json.loads(manifest_data)
                except (KeyError, json.JSONDecodeError):
                    manifest = {}

                result.metadata = manifest

                # Determine project directory
                project_name = manifest.get("name", archive_path.stem)
                if options.rename_prefix:
                    project_name = f"{options.rename_prefix}_{project_name}"

                project_dir = (options.target_directory or self._projects_dir) / project_name

                if project_dir.exists() and not options.overwrite_existing:
                    # Generate unique name
                    counter = 1
                    while project_dir.exists():
                        project_dir = (
                            options.target_directory or self._projects_dir
                        ) / f"{project_name}_{counter}"
                        counter += 1

                # Extract files
                project_dir.mkdir(parents=True, exist_ok=True)

                for file_info in zf.infolist():
                    if file_info.is_dir():
                        continue

                    # Skip certain files based on options
                    if file_info.filename.startswith("voices/") and not options.import_voices:
                        result.skipped_items.append(file_info.filename)
                        continue

                    if file_info.filename.startswith("settings/") and not options.import_settings:
                        result.skipped_items.append(file_info.filename)
                        continue

                    if file_info.filename.startswith("workflows/") and not options.import_workflows:
                        result.skipped_items.append(file_info.filename)
                        continue

                    # Extract file
                    zf.extract(file_info, project_dir)
                    result.imported_items.append(file_info.filename)

                result.project_path = project_dir

        except Exception as e:
            result.success = False
            result.errors.append(str(e))
            logger.error(f"Import error: {e}")

        return result

    async def import_audio_files(
        self, file_paths: list[Path], project_path: Path, options: ImportOptions | None = None
    ) -> ImportResult:
        """Import audio files into a project."""
        options = options or ImportOptions()
        result = ImportResult(success=True)

        audio_dir = project_path / "audio"
        audio_dir.mkdir(parents=True, exist_ok=True)

        for file_path in file_paths:
            try:
                if not file_path.exists():
                    result.errors.append(f"File not found: {file_path}")
                    continue

                if file_path.suffix.lower() not in self.SUPPORTED_AUDIO:
                    result.skipped_items.append(str(file_path))
                    continue

                dest_path = audio_dir / file_path.name

                if dest_path.exists() and not options.overwrite_existing:
                    # Generate unique name
                    stem = file_path.stem
                    suffix = file_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = audio_dir / f"{stem}_{counter}{suffix}"
                        counter += 1

                shutil.copy2(file_path, dest_path)
                result.imported_items.append(str(dest_path))

            except Exception as e:
                result.errors.append(f"{file_path}: {e}")

        result.success = len(result.errors) == 0
        return result

    async def import_text_file(
        self, file_path: Path, options: ImportOptions | None = None
    ) -> ImportResult:
        """Import a text or subtitle file."""
        options = options or ImportOptions()
        result = ImportResult(success=True)

        try:
            if not file_path.exists():
                return ImportResult(success=False, errors=[f"File not found: {file_path}"])

            suffix = file_path.suffix.lower()

            if suffix == ".txt":
                content = file_path.read_text(encoding="utf-8")
                result.metadata = {
                    "type": "text",
                    "content": content,
                    "character_count": len(content),
                    "word_count": len(content.split()),
                }

            elif suffix == ".srt":
                content = file_path.read_text(encoding="utf-8")
                subtitles = self._parse_srt(content)
                result.metadata = {
                    "type": "subtitle",
                    "format": "srt",
                    "entries": subtitles,
                    "count": len(subtitles),
                }

            elif suffix == ".vtt":
                content = file_path.read_text(encoding="utf-8")
                subtitles = self._parse_vtt(content)
                result.metadata = {
                    "type": "subtitle",
                    "format": "vtt",
                    "entries": subtitles,
                    "count": len(subtitles),
                }

            result.imported_items.append(str(file_path))

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    async def import_voice_model(
        self, model_path: Path, voices_dir: Path, options: ImportOptions | None = None
    ) -> ImportResult:
        """Import a voice model."""
        options = options or ImportOptions()
        result = ImportResult(success=True)

        try:
            voices_dir.mkdir(parents=True, exist_ok=True)

            if model_path.is_dir():
                # Copy entire directory
                dest_path = voices_dir / model_path.name

                if dest_path.exists() and not options.overwrite_existing:
                    counter = 1
                    while dest_path.exists():
                        dest_path = voices_dir / f"{model_path.name}_{counter}"
                        counter += 1

                shutil.copytree(model_path, dest_path)
                result.imported_items.append(str(dest_path))

            else:
                # Copy single file
                dest_path = voices_dir / model_path.name

                if dest_path.exists() and not options.overwrite_existing:
                    stem = model_path.stem
                    suffix = model_path.suffix
                    counter = 1
                    while dest_path.exists():
                        dest_path = voices_dir / f"{stem}_{counter}{suffix}"
                        counter += 1

                shutil.copy2(model_path, dest_path)
                result.imported_items.append(str(dest_path))

        except Exception as e:
            result.success = False
            result.errors.append(str(e))

        return result

    def _parse_srt(self, content: str) -> list[dict[str, Any]]:
        """Parse SRT subtitle format."""
        entries = []
        blocks = content.strip().split("\n\n")

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                try:
                    # Parse index
                    index = int(lines[0])

                    # Parse timing
                    timing = lines[1].split(" --> ")
                    start_time = self._parse_srt_time(timing[0])
                    end_time = self._parse_srt_time(timing[1])

                    # Join remaining lines as text
                    text = "\n".join(lines[2:])

                    entries.append(
                        {
                            "index": index,
                            "start": start_time,
                            "end": end_time,
                            "text": text,
                        }
                    )
                except (ValueError, IndexError):
                    continue

        return entries

    def _parse_srt_time(self, time_str: str) -> float:
        """Parse SRT time format to seconds."""
        time_str = time_str.strip().replace(",", ".")
        parts = time_str.split(":")

        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = float(parts[2])

        return hours * 3600 + minutes * 60 + seconds

    def _parse_vtt(self, content: str) -> list[dict[str, Any]]:
        """Parse WebVTT subtitle format."""
        entries = []
        lines = content.strip().split("\n")

        # Skip WEBVTT header
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip() == "WEBVTT":
                start_idx = i + 1
                break

        current_entry: dict[str, Any] | None = None

        for line in lines[start_idx:]:
            line = line.strip()

            if "-->" in line:
                # Timing line
                parts = line.split("-->")
                start_time = self._parse_vtt_time(parts[0])
                end_time = self._parse_vtt_time(parts[1].split()[0])

                current_entry = {
                    "start": start_time,
                    "end": end_time,
                    "text": "",
                }

            elif line and current_entry is not None:
                if current_entry["text"]:
                    current_entry["text"] += "\n"
                current_entry["text"] += line

            elif not line and current_entry is not None:
                entries.append(current_entry)
                current_entry = None

        if current_entry is not None:
            entries.append(current_entry)

        return entries

    def _parse_vtt_time(self, time_str: str) -> float:
        """Parse WebVTT time format to seconds."""
        time_str = time_str.strip()

        # Handle both HH:MM:SS.mmm and MM:SS.mmm formats
        parts = time_str.split(":")

        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
        else:
            hours = 0
            minutes = int(parts[0])
            seconds = float(parts[1])

        return hours * 3600 + minutes * 60 + seconds
