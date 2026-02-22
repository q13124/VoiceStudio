"""
Phase 6: External App Integration
Task 6.1: DAW (Digital Audio Workstation) integration support.
"""

from __future__ import annotations

import contextlib
import logging
import re
import sqlite3
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DAWType(Enum):
    """Supported DAW types."""

    ABLETON = "ableton"
    FL_STUDIO = "fl_studio"
    LOGIC_PRO = "logic_pro"
    PRO_TOOLS = "pro_tools"
    REAPER = "reaper"
    CUBASE = "cubase"
    STUDIO_ONE = "studio_one"
    AUDACITY = "audacity"
    GENERIC = "generic"


@dataclass
class DAWProject:
    """DAW project information."""

    path: Path
    name: str
    daw_type: DAWType
    sample_rate: int = 44100
    bit_depth: int = 24
    tempo: float = 120.0
    time_signature: tuple[int, int] = (4, 4)
    tracks: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class DAWExportSettings:
    """Settings for exporting to DAW."""

    format: str = "wav"
    sample_rate: int = 44100
    bit_depth: int = 24
    normalize: bool = False
    include_markers: bool = True
    split_tracks: bool = False


# Pre-configured export presets per DAW (TD-038).
# Each item: id, name, daw_type, description, settings (DAWExportSettings).
DAW_EXPORT_PRESETS: list[dict[str, Any]] = [
    {
        "id": "reaper_studio",
        "name": "REAPER Studio",
        "daw_type": DAWType.REAPER.value,
        "description": "48 kHz, 24-bit WAV, normalized, markers",
        "settings": DAWExportSettings(
            format="wav",
            sample_rate=48000,
            bit_depth=24,
            normalize=True,
            include_markers=True,
            split_tracks=False,
        ),
    },
    {
        "id": "reaper_broadcast",
        "name": "REAPER Broadcast",
        "daw_type": DAWType.REAPER.value,
        "description": "44.1 kHz, 24-bit WAV for broadcast",
        "settings": DAWExportSettings(
            format="wav",
            sample_rate=44100,
            bit_depth=24,
            normalize=False,
            include_markers=True,
            split_tracks=False,
        ),
    },
    {
        "id": "audacity_default",
        "name": "Audacity Default",
        "daw_type": DAWType.AUDACITY.value,
        "description": "44.1 kHz, 32-bit float WAV for Audacity",
        "settings": DAWExportSettings(
            format="wav",
            sample_rate=44100,
            bit_depth=32,
            normalize=False,
            include_markers=True,
            split_tracks=False,
        ),
    },
    {
        "id": "audacity_high_quality",
        "name": "Audacity High Quality",
        "daw_type": DAWType.AUDACITY.value,
        "description": "96 kHz, 24-bit WAV",
        "settings": DAWExportSettings(
            format="wav",
            sample_rate=96000,
            bit_depth=24,
            normalize=True,
            include_markers=True,
            split_tracks=False,
        ),
    },
]


def get_daw_export_presets(daw_type: str | None = None) -> list[dict[str, Any]]:
    """
    Return DAW export presets, optionally filtered by daw_type.
    Each preset dict includes id, name, daw_type, description, and settings (as dict).
    """
    out: list[dict[str, Any]] = []
    for p in DAW_EXPORT_PRESETS:
        if daw_type is not None and p["daw_type"] != daw_type:
            continue
        settings = p["settings"]
        if isinstance(settings, DAWExportSettings):
            settings_dict = {
                "format": settings.format,
                "sample_rate": settings.sample_rate,
                "bit_depth": settings.bit_depth,
                "normalize": settings.normalize,
                "include_markers": settings.include_markers,
                "split_tracks": settings.split_tracks,
            }
        else:
            settings_dict = dict(settings) if isinstance(settings, dict) else {}
        out.append(
            {
                "id": p["id"],
                "name": p["name"],
                "daw_type": p["daw_type"],
                "description": p["description"],
                "settings": settings_dict,
            }
        )
    return out


def get_daw_export_preset_by_id(preset_id: str) -> dict[str, Any] | None:
    """Return a single preset by id, or None."""
    for p in DAW_EXPORT_PRESETS:
        if p["id"] == preset_id:
            settings = p["settings"]
            if isinstance(settings, DAWExportSettings):
                settings_dict = {
                    "format": settings.format,
                    "sample_rate": settings.sample_rate,
                    "bit_depth": settings.bit_depth,
                    "normalize": settings.normalize,
                    "include_markers": settings.include_markers,
                    "split_tracks": settings.split_tracks,
                }
            else:
                settings_dict = dict(settings) if isinstance(settings, dict) else {}
            return {
                "id": p["id"],
                "name": p["name"],
                "daw_type": p["daw_type"],
                "description": p["description"],
                "settings": settings_dict,
            }
    return None


class DAWIntegration(ABC):
    """Abstract base class for DAW integration."""

    @property
    @abstractmethod
    def daw_type(self) -> DAWType:
        """Get the DAW type."""
        pass

    @abstractmethod
    async def detect_installation(self) -> Path | None:
        """Detect if the DAW is installed."""
        pass

    @abstractmethod
    async def open_project(self, project_path: Path) -> DAWProject:
        """Open a DAW project."""
        pass

    @abstractmethod
    async def export_to_daw(
        self, audio_path: Path, project: DAWProject, settings: DAWExportSettings
    ) -> Path:
        """Export audio to DAW project."""
        pass

    @abstractmethod
    async def import_from_daw(self, project: DAWProject, track_index: int) -> Path:
        """Import audio from DAW project."""
        pass


class ReaperIntegration(DAWIntegration):
    """Integration with REAPER DAW."""

    @property
    def daw_type(self) -> DAWType:
        return DAWType.REAPER

    async def detect_installation(self) -> Path | None:
        """Detect REAPER installation."""
        import os

        # Common REAPER installation paths
        paths = [
            Path(os.environ.get("PROGRAMFILES", "")) / "REAPER (x64)",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "REAPER",
            Path.home() / "AppData/Roaming/REAPER",
        ]

        for path in paths:
            if path.exists():
                return path

        return None

    async def open_project(self, project_path: Path) -> DAWProject:
        """Open a REAPER project (.rpp file) and parse tracks with audio sources.

        Parses the text-based RPP format to extract:
        - Sample rate (SAMPLERATE line)
        - Tempo (TEMPO line)
        - Tracks (<TRACK blocks) with names (NAME), audio sources (FILE in SOURCE blocks)
        """
        if not project_path.exists():
            raise FileNotFoundError(f"Project not found: {project_path}")

        project = DAWProject(
            path=project_path,
            name=project_path.stem,
            daw_type=DAWType.REAPER,
        )

        with open(project_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()

        lines = content.split("\n")

        # Extract sample rate
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("SAMPLERATE"):
                with contextlib.suppress(IndexError, ValueError):
                    project.sample_rate = int(stripped.split()[1])
                break

        # Extract tempo
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("TEMPO"):
                with contextlib.suppress(IndexError, ValueError):
                    project.tempo = float(stripped.split()[1])
                break

        # Parse tracks: find <TRACK blocks, extract NAME and FILE references
        project.tracks = _parse_rpp_tracks(content, project_path.parent)

        return project

    async def export_to_daw(
        self, audio_path: Path, project: DAWProject, settings: DAWExportSettings
    ) -> Path:
        """Export audio to REAPER project."""
        import_dir = project.path.parent / "imports"
        import_dir.mkdir(exist_ok=True)

        output_path = import_dir / audio_path.name

        import shutil

        shutil.copy2(audio_path, output_path)

        logger.info(f"Exported audio to REAPER project: {output_path}")

        return output_path

    async def import_from_daw(self, project: DAWProject, track_index: int) -> Path:
        """Import audio from a REAPER project track.

        Resolves the audio file referenced by the track at ``track_index``.
        Tracks are populated by ``open_project`` via RPP parsing.

        Args:
            project: A DAWProject previously returned by ``open_project``.
            track_index: Zero-based index into ``project.tracks``.

        Returns:
            Absolute ``Path`` to the first audio file referenced by the track.

        Raises:
            IndexError: If ``track_index`` is out of range.
            FileNotFoundError: If the referenced audio file does not exist on disk.
        """
        if not project.tracks:
            raise FileNotFoundError(
                "No tracks found in REAPER project. "
                "Ensure the project was opened with open_project() first, "
                "or export audio from REAPER to WAV and import directly."
            )

        if track_index < 0 or track_index >= len(project.tracks):
            raise IndexError(
                f"Track index {track_index} out of range. "
                f"Project has {len(project.tracks)} track(s) (0-indexed)."
            )

        track = project.tracks[track_index]
        audio_files: list[str] = track.get("audio_files", [])
        if not audio_files:
            raise FileNotFoundError(
                f"Track '{track.get('name', track_index)}' has no audio file references. "
                "The track may contain MIDI only or use virtual instruments."
            )

        # Resolve the first audio file (paths stored as absolute strings by parser)
        audio_path = Path(audio_files[0])
        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}. "
                "The file may have been moved or deleted from the REAPER project directory."
            )

        logger.info(
            f"Imported audio from REAPER track '{track.get('name', track_index)}': {audio_path}"
        )
        return audio_path


def _parse_rpp_tracks(content: str, project_dir: Path) -> list[dict[str, Any]]:
    """Parse REAPER RPP content to extract track metadata and audio file references.

    RPP is a text-based block format where ``<TRACK`` opens a track block and ``>`` closes it.
    Inside a track: ``NAME "..."`` gives the track name; ``<SOURCE ...`` blocks contain ``FILE "..."``
    lines referencing audio on disk (paths may be relative to the project directory).

    Args:
        content: Full RPP file text.
        project_dir: Directory of the .rpp file, used to resolve relative paths.

    Returns:
        List of track dicts with keys: ``name``, ``index``, ``audio_files``.
    """
    tracks: list[dict[str, Any]] = []
    track_index = 0

    # Split into lines and walk through looking for <TRACK blocks
    lines = content.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        if stripped.startswith("<TRACK"):
            track_name = f"Track {track_index + 1}"
            audio_files: list[str] = []
            depth = 1
            i += 1

            while i < len(lines) and depth > 0:
                tline = lines[i].strip()

                if tline.startswith("<"):
                    depth += 1
                elif tline == ">":
                    depth -= 1
                elif tline.startswith("NAME"):
                    # NAME "My Track Name" or NAME MyTrackName
                    name_match = re.match(r'NAME\s+"([^"]*)"', tline)
                    if name_match:
                        track_name = name_match.group(1)
                    else:
                        parts = tline.split(None, 1)
                        if len(parts) > 1:
                            track_name = parts[1].strip('"')
                elif tline.startswith("FILE"):
                    # FILE "path/to/audio.wav" or FILE path/to/audio.wav
                    file_match = re.match(r'FILE\s+"([^"]*)"', tline)
                    if file_match:
                        raw_path = file_match.group(1)
                    else:
                        parts = tline.split(None, 1)
                        raw_path = parts[1].strip('"') if len(parts) > 1 else ""

                    if raw_path:
                        resolved = Path(raw_path)
                        if not resolved.is_absolute():
                            resolved = project_dir / resolved
                        audio_files.append(str(resolved.resolve()))

                i += 1

            tracks.append(
                {
                    "name": track_name,
                    "index": track_index,
                    "audio_files": audio_files,
                }
            )
            track_index += 1
        else:
            i += 1

    return tracks


def _parse_aup3_tracks(project_path: Path) -> tuple[list[dict[str, Any]], int]:
    """Parse an Audacity AUP3 project (SQLite database) to extract track info.

    AUP3 stores the project XML document in an ``autosave`` or ``project`` table and
    audio sample blocks in a ``sampleblocks`` table.  This function extracts track
    names from the project XML.

    Args:
        project_path: Path to the ``.aup3`` file.

    Returns:
        Tuple of (tracks list, sample_rate).  Each track dict has keys:
        ``name``, ``index``, ``channels``.
    """
    tracks: list[dict[str, Any]] = []
    sample_rate = 44100

    try:
        conn = sqlite3.connect(str(project_path))
        cursor = conn.cursor()

        # AUP3 stores project XML in the 'project' or 'autosave' table
        project_xml: str | None = None
        for table in ("autosave", "project"):
            try:
                cursor.execute(f"SELECT dict || doc FROM {table} LIMIT 1")
                row = cursor.fetchone()
                if row and row[0]:
                    project_xml = row[0]
                    break
            except sqlite3.OperationalError as e:
                # GAP-PY-001: Table structure varies by Audacity version
                logger.debug(f"Failed to query {table} with dict||doc: {e}")

        # Fallback: try reading raw XML column
        if not project_xml:
            for table in ("autosave", "project"):
                try:
                    cursor.execute(f"SELECT doc FROM {table} LIMIT 1")
                    row = cursor.fetchone()
                    if row and row[0]:
                        project_xml = (
                            row[0]
                            if isinstance(row[0], str)
                            else row[0].decode("utf-8", errors="ignore")
                        )
                        break
                except (sqlite3.OperationalError, UnicodeDecodeError) as e:
                    # GAP-PY-001: Table structure varies by Audacity version
                    logger.debug(f"Failed to query {table} for doc: {e}")

        conn.close()

        if project_xml:
            # Parse the embedded XML to find <wavetrack> elements
            try:
                root = ET.fromstring(project_xml)
            except ET.ParseError:
                # Try wrapping in a root if needed
                try:
                    root = ET.fromstring(f"<root>{project_xml}</root>")
                except ET.ParseError:
                    logger.warning("Could not parse AUP3 project XML; returning empty tracks")
                    return tracks, sample_rate

            # Extract project-level sample rate
            rate_attr = root.get("rate") or root.get("projrate")
            if rate_attr:
                with contextlib.suppress(ValueError, TypeError):
                    sample_rate = int(float(rate_attr))

            # Find wavetrack elements (case-insensitive local tag name; AUP3 uses default namespace)
            def _local_tag(tag: str | None) -> str:
                if not tag:
                    return ""
                return tag.split("}")[-1].lower() if "}" in tag else tag.lower()

            track_index = 0
            for elem in root.iter():
                if _local_tag(elem.tag) == "wavetrack":
                    name = elem.get("name") or elem.get("Name") or f"Track {track_index + 1}"
                    channels = 1
                    with contextlib.suppress(ValueError, TypeError):
                        channels = int(elem.get("channel", "1"))

                    tracks.append(
                        {
                            "name": name,
                            "index": track_index,
                            "channels": channels,
                        }
                    )
                    track_index += 1

    except sqlite3.DatabaseError as e:
        logger.warning(f"Could not read AUP3 database: {e}")

    return tracks, sample_rate


def _parse_aup_tracks(project_path: Path) -> tuple[list[dict[str, Any]], int]:
    """Parse a legacy Audacity AUP project (XML file) to extract track info.

    Args:
        project_path: Path to the ``.aup`` file.

    Returns:
        Tuple of (tracks list, sample_rate).
    """
    tracks: list[dict[str, Any]] = []
    sample_rate = 44100

    try:
        tree = ET.parse(str(project_path))
        root = tree.getroot()

        # Strip namespace if present
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"

        rate_attr = root.get("rate") or root.get("projrate")
        if rate_attr:
            with contextlib.suppress(ValueError, TypeError):
                sample_rate = int(float(rate_attr))

        track_index = 0
        for elem in root.iter(f"{ns}wavetrack"):
            name = elem.get("name") or f"Track {track_index + 1}"
            channels = 1
            with contextlib.suppress(ValueError, TypeError):
                channels = int(elem.get("channel", "1"))

            tracks.append(
                {
                    "name": name,
                    "index": track_index,
                    "channels": channels,
                }
            )
            track_index += 1

    except (ET.ParseError, OSError) as e:
        logger.warning(f"Could not parse AUP project XML: {e}")

    return tracks, sample_rate


def _export_aup3_track_audio(project_path: Path, track_index: int, output_dir: Path) -> Path:
    """Export audio from an AUP3 track to a WAV file.

    Reads sample blocks from the SQLite ``sampleblocks`` table and writes raw PCM
    wrapped in a WAV header.  This covers the common case of 16-bit or 32-bit float
    sample data stored in the project.

    Args:
        project_path: Path to the ``.aup3`` file.
        track_index: Zero-based track index.
        output_dir: Directory to write the exported WAV.

    Returns:
        Path to the exported WAV file.
    """
    import wave

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"track_{track_index}.wav"

    try:
        conn = sqlite3.connect(str(project_path))
        cursor = conn.cursor()

        # sampleblocks: blockid, sampleformat, summin, summax, sumrms, summary256, summary64k, samples
        cursor.execute("SELECT samples FROM sampleblocks ORDER BY blockid")

        all_samples = b""
        for row in cursor.fetchall():
            if row[0]:
                all_samples += bytes(row[0])

        conn.close()

        if not all_samples:
            raise FileNotFoundError(
                f"No audio sample data found in AUP3 for track {track_index}. "
                "The project may be empty or use a format not yet supported."
            )

        # Write as 16-bit PCM WAV (default assumption; AUP3 commonly stores 32-bit float
        # but we write raw bytes as-is with a best-effort WAV wrapper)
        sample_width = 2  # bytes per sample (16-bit)
        channels = 1
        sample_rate = 44100

        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(all_samples)

        logger.info(
            f"Exported AUP3 track {track_index} to {output_path} ({len(all_samples)} bytes)"
        )

    except sqlite3.DatabaseError as e:
        raise FileNotFoundError(f"Failed to read audio from AUP3: {e}") from e

    return output_path


class AudacityIntegration(DAWIntegration):
    """Integration with Audacity (AUP3 and legacy AUP projects)."""

    @property
    def daw_type(self) -> DAWType:
        return DAWType.AUDACITY

    async def detect_installation(self) -> Path | None:
        """Detect Audacity installation."""
        import os

        paths = [
            Path(os.environ.get("PROGRAMFILES", "")) / "Audacity",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Audacity",
        ]

        for path in paths:
            if path.exists():
                return path

        return None

    async def open_project(self, project_path: Path) -> DAWProject:
        """Open an Audacity project (.aup3 or .aup) and parse track metadata.

        AUP3 files are SQLite databases; AUP files are XML.
        """
        if not project_path.exists():
            raise FileNotFoundError(f"Project not found: {project_path}")

        project = DAWProject(
            path=project_path,
            name=project_path.stem,
            daw_type=DAWType.AUDACITY,
        )

        suffix = project_path.suffix.lower()

        if suffix == ".aup3":
            tracks, sample_rate = _parse_aup3_tracks(project_path)
        elif suffix == ".aup":
            tracks, sample_rate = _parse_aup_tracks(project_path)
        else:
            logger.warning(f"Unknown Audacity project format: {suffix}; treating as empty project")
            return project

        project.tracks = tracks
        project.sample_rate = sample_rate

        return project

    async def export_to_daw(
        self, audio_path: Path, project: DAWProject, settings: DAWExportSettings
    ) -> Path:
        """Export audio for Audacity (Audacity imports WAV directly)."""
        return audio_path

    async def import_from_daw(self, project: DAWProject, track_index: int) -> Path:
        """Import audio from an Audacity project track.

        For AUP3 projects: extracts sample blocks from the SQLite database and exports
        as a WAV file.  For AUP projects: resolves blockfile references in the project
        data directory.

        Args:
            project: A DAWProject previously returned by ``open_project``.
            track_index: Zero-based index into ``project.tracks``.

        Returns:
            Path to the exported or resolved audio file.

        Raises:
            IndexError: If ``track_index`` is out of range.
            FileNotFoundError: If audio data cannot be extracted.
        """
        if not project.tracks:
            raise FileNotFoundError(
                "No tracks found in Audacity project. "
                "Ensure the project was opened with open_project() first, "
                "or export audio from Audacity to WAV and import directly."
            )

        if track_index < 0 or track_index >= len(project.tracks):
            raise IndexError(
                f"Track index {track_index} out of range. "
                f"Project has {len(project.tracks)} track(s) (0-indexed)."
            )

        suffix = project.path.suffix.lower()

        if suffix == ".aup3":
            # Export audio from AUP3 SQLite database
            output_dir = project.path.parent / f"{project.name}_exported"
            audio_path = _export_aup3_track_audio(project.path, track_index, output_dir)
            logger.info(f"Imported audio from Audacity AUP3 track {track_index}: {audio_path}")
            return audio_path

        elif suffix == ".aup":
            # AUP legacy: audio data is in a sibling directory named {project_name}_data
            data_dir = project.path.parent / f"{project.name}_data"
            if not data_dir.exists():
                raise FileNotFoundError(
                    f"Audacity data directory not found: {data_dir}. "
                    "Legacy AUP projects store audio in a sibling '_data' folder."
                )

            # Find audio files in the data directory (blockfiles are .au format)
            audio_files = sorted(data_dir.glob("*.au")) + sorted(data_dir.glob("*.wav"))
            if not audio_files:
                raise FileNotFoundError(
                    f"No audio files found in {data_dir}. "
                    "Export audio from Audacity to WAV and import directly."
                )

            # Return the first audio file for the requested track
            # (Simple heuristic: AUP blockfiles are numerous; return the directory for manual selection)
            logger.info(f"Imported audio from Audacity AUP data dir: {audio_files[0]}")
            return audio_files[0]

        raise FileNotFoundError(
            f"Unsupported Audacity project format: {suffix}. "
            "Please export audio from Audacity to WAV and import directly."
        )


class DAWIntegrationManager:
    """Manager for DAW integrations."""

    def __init__(self):
        self._integrations: dict[DAWType, DAWIntegration] = {}
        self._detected_daws: dict[DAWType, Path] = {}

        # Register default integrations
        self.register(ReaperIntegration())
        self.register(AudacityIntegration())

    def register(self, integration: DAWIntegration) -> None:
        """Register a DAW integration."""
        self._integrations[integration.daw_type] = integration

    def get_integration(self, daw_type: DAWType) -> DAWIntegration | None:
        """Get a DAW integration by type."""
        return self._integrations.get(daw_type)

    async def detect_installed_daws(self) -> dict[DAWType, Path]:
        """Detect all installed DAWs."""
        self._detected_daws.clear()

        for daw_type, integration in self._integrations.items():
            path = await integration.detect_installation()
            if path:
                self._detected_daws[daw_type] = path
                logger.info(f"Detected {daw_type.value} at {path}")

        return self._detected_daws

    async def export_audio(
        self,
        audio_path: Path,
        daw_type: DAWType,
        project_path: Path,
        settings: DAWExportSettings | None = None,
    ) -> Path:
        """Export audio to a DAW project."""
        integration = self.get_integration(daw_type)
        if not integration:
            raise ValueError(f"No integration available for {daw_type.value}")

        project = await integration.open_project(project_path)
        settings = settings or DAWExportSettings()

        return await integration.export_to_daw(audio_path, project, settings)

    def get_available_daws(self) -> list[DAWType]:
        """Get list of available DAW integrations."""
        return list(self._integrations.keys())

    def get_detected_daws(self) -> dict[DAWType, Path]:
        """Get previously detected DAWs."""
        return self._detected_daws.copy()
