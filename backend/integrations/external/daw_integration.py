"""
Phase 6: External App Integration
Task 6.1: DAW (Digital Audio Workstation) integration support.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import logging

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


class DAWIntegration(ABC):
    """Abstract base class for DAW integration."""
    
    @property
    @abstractmethod
    def daw_type(self) -> DAWType:
        """Get the DAW type."""
        pass
    
    @abstractmethod
    async def detect_installation(self) -> Optional[Path]:
        """Detect if the DAW is installed."""
        pass
    
    @abstractmethod
    async def open_project(self, project_path: Path) -> DAWProject:
        """Open a DAW project."""
        pass
    
    @abstractmethod
    async def export_to_daw(
        self,
        audio_path: Path,
        project: DAWProject,
        settings: DAWExportSettings
    ) -> Path:
        """Export audio to DAW project."""
        pass
    
    @abstractmethod
    async def import_from_daw(
        self,
        project: DAWProject,
        track_index: int
    ) -> Path:
        """Import audio from DAW project."""
        pass


class ReaperIntegration(DAWIntegration):
    """Integration with REAPER DAW."""
    
    @property
    def daw_type(self) -> DAWType:
        return DAWType.REAPER
    
    async def detect_installation(self) -> Optional[Path]:
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
        """Open a REAPER project (.rpp file)."""
        if not project_path.exists():
            raise FileNotFoundError(f"Project not found: {project_path}")
        
        # Parse REAPER project file
        project = DAWProject(
            path=project_path,
            name=project_path.stem,
            daw_type=DAWType.REAPER,
        )
        
        # Basic RPP parsing
        with open(project_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Extract sample rate
            if "SAMPLERATE" in content:
                try:
                    line = [l for l in content.split('\n') if 'SAMPLERATE' in l][0]
                    project.sample_rate = int(line.split()[1])
                except (IndexError, ValueError):
                    pass
            
            # Extract tempo
            if "TEMPO" in content:
                try:
                    line = [l for l in content.split('\n') if 'TEMPO' in l][0]
                    project.tempo = float(line.split()[1])
                except (IndexError, ValueError):
                    pass
        
        return project
    
    async def export_to_daw(
        self,
        audio_path: Path,
        project: DAWProject,
        settings: DAWExportSettings
    ) -> Path:
        """Export audio to REAPER project."""
        # Create a REAPER-compatible import path
        import_dir = project.path.parent / "imports"
        import_dir.mkdir(exist_ok=True)
        
        output_path = import_dir / audio_path.name
        
        # Copy/convert audio file
        import shutil
        shutil.copy2(audio_path, output_path)
        
        logger.info(f"Exported audio to REAPER project: {output_path}")
        
        return output_path
    
    async def import_from_daw(
        self,
        project: DAWProject,
        track_index: int
    ) -> Path:
        """Import audio from REAPER project.
        
        Note: REAPER project parsing requires RPP format support which is complex.
        For now, users should export audio from REAPER manually, then import the WAV file.
        """
        raise NotImplementedError(
            "REAPER project import requires RPP file parsing which is not yet implemented. "
            "Please export audio from REAPER to WAV format and import directly."
        )


class AudacityIntegration(DAWIntegration):
    """Integration with Audacity."""
    
    @property
    def daw_type(self) -> DAWType:
        return DAWType.AUDACITY
    
    async def detect_installation(self) -> Optional[Path]:
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
        """Open an Audacity project."""
        project = DAWProject(
            path=project_path,
            name=project_path.stem,
            daw_type=DAWType.AUDACITY,
        )
        
        return project
    
    async def export_to_daw(
        self,
        audio_path: Path,
        project: DAWProject,
        settings: DAWExportSettings
    ) -> Path:
        """Export audio for Audacity."""
        # Audacity can open WAV files directly
        return audio_path
    
    async def import_from_daw(
        self,
        project: DAWProject,
        track_index: int
    ) -> Path:
        """Import audio from Audacity project.
        
        Note: Audacity project parsing requires AUP3/AUP format support which is complex.
        For now, users should export audio from Audacity manually, then import the WAV file.
        """
        raise NotImplementedError(
            "Audacity project import requires AUP3/AUP file parsing which is not yet implemented. "
            "Please export audio from Audacity to WAV format and import directly."
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
    
    def get_integration(self, daw_type: DAWType) -> Optional[DAWIntegration]:
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
        settings: Optional[DAWExportSettings] = None
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
