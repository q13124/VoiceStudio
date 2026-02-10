"""
Phase 6: Export System
Task 6.10: Project export with packaging.
"""

import asyncio
import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional
import logging
import shutil

logger = logging.getLogger(__name__)


class ExportType(Enum):
    """Export types."""
    ARCHIVE = "archive"
    FOLDER = "folder"
    AUDIO_ONLY = "audio_only"
    STEMS = "stems"


@dataclass
class ProjectExportOptions:
    """Options for project export."""
    export_type: ExportType = ExportType.ARCHIVE
    include_sources: bool = True
    include_voices: bool = True
    include_workflows: bool = True
    include_settings: bool = False
    compress: bool = True
    compression_level: int = 6
    split_size_mb: Optional[int] = None
    password: Optional[str] = None
    output_path: Optional[Path] = None


@dataclass
class ExportManifest:
    """Manifest for exported project."""
    name: str
    version: str
    created_at: str
    voicestudio_version: str
    files: list[dict[str, Any]]
    metadata: dict[str, Any]


@dataclass
class ProjectExportResult:
    """Result of project export."""
    success: bool
    output_path: Optional[Path] = None
    output_files: list[Path] = field(default_factory=list)
    file_size: int = 0
    files_exported: int = 0
    errors: list[str] = field(default_factory=list)


class ProjectExporter:
    """Exporter for VoiceStudio projects."""
    
    def __init__(self, voicestudio_version: str = "1.0.0"):
        self._voicestudio_version = voicestudio_version
    
    async def export_project(
        self,
        project_path: Path,
        options: Optional[ProjectExportOptions] = None
    ) -> ProjectExportResult:
        """Export a project with specified options."""
        options = options or ProjectExportOptions()
        result = ProjectExportResult(success=True)
        
        try:
            if not project_path.exists():
                return ProjectExportResult(
                    success=False,
                    errors=[f"Project not found: {project_path}"]
                )
            
            # Determine output path
            output_path = options.output_path or project_path.parent / f"{project_path.name}_export"
            
            if options.export_type == ExportType.ARCHIVE:
                return await self._export_archive(project_path, output_path, options)
            elif options.export_type == ExportType.FOLDER:
                return await self._export_folder(project_path, output_path, options)
            elif options.export_type == ExportType.AUDIO_ONLY:
                return await self._export_audio_only(project_path, output_path, options)
            elif options.export_type == ExportType.STEMS:
                return await self._export_stems(project_path, output_path, options)
            else:
                return ProjectExportResult(
                    success=False,
                    errors=[f"Unknown export type: {options.export_type}"]
                )
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            return ProjectExportResult(success=False, errors=[str(e)])
    
    async def _export_archive(
        self,
        project_path: Path,
        output_path: Path,
        options: ProjectExportOptions
    ) -> ProjectExportResult:
        """Export project as ZIP archive."""
        result = ProjectExportResult(success=True)
        
        archive_path = output_path.with_suffix('.vsarc')
        
        # Create manifest
        manifest = self._create_manifest(project_path, options)
        
        with zipfile.ZipFile(
            archive_path,
            'w',
            compression=zipfile.ZIP_DEFLATED if options.compress else zipfile.ZIP_STORED,
            compresslevel=options.compression_level if options.compress else 0
        ) as zf:
            # Add manifest
            zf.writestr('manifest.json', json.dumps(manifest.__dict__, indent=2, default=str))
            
            # Add project files
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    relative = file_path.relative_to(project_path)
                    
                    # Filter based on options
                    if not self._should_include(relative, options):
                        continue
                    
                    zf.write(file_path, str(relative))
                    result.files_exported += 1
        
        result.output_path = archive_path
        result.output_files.append(archive_path)
        result.file_size = archive_path.stat().st_size
        
        return result
    
    async def _export_folder(
        self,
        project_path: Path,
        output_path: Path,
        options: ProjectExportOptions
    ) -> ProjectExportResult:
        """Export project as folder."""
        result = ProjectExportResult(success=True)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Create manifest
        manifest = self._create_manifest(project_path, options)
        manifest_path = output_path / 'manifest.json'
        manifest_path.write_text(json.dumps(manifest.__dict__, indent=2, default=str))
        
        # Copy files
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                relative = file_path.relative_to(project_path)
                
                if not self._should_include(relative, options):
                    continue
                
                dest = output_path / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, dest)
                result.files_exported += 1
                result.output_files.append(dest)
        
        result.output_path = output_path
        result.file_size = sum(f.stat().st_size for f in output_path.rglob('*') if f.is_file())
        
        return result
    
    async def _export_audio_only(
        self,
        project_path: Path,
        output_path: Path,
        options: ProjectExportOptions
    ) -> ProjectExportResult:
        """Export only audio files."""
        result = ProjectExportResult(success=True)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        audio_extensions = {'.wav', '.mp3', '.flac', '.ogg', '.m4a', '.aac'}
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                dest = output_path / file_path.name
                shutil.copy2(file_path, dest)
                result.files_exported += 1
                result.output_files.append(dest)
        
        result.output_path = output_path
        result.file_size = sum(f.stat().st_size for f in result.output_files)
        
        return result
    
    async def _export_stems(
        self,
        project_path: Path,
        output_path: Path,
        options: ProjectExportOptions
    ) -> ProjectExportResult:
        """Export audio stems by track."""
        result = ProjectExportResult(success=True)
        
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Read project file to get track info
        project_file = project_path / 'project.json'
        if project_file.exists():
            try:
                project_data = json.loads(project_file.read_text())
                tracks = project_data.get('tracks', [])
                
                for track in tracks:
                    track_name = track.get('name', 'Unknown')
                    track_dir = output_path / track_name
                    track_dir.mkdir(exist_ok=True)
                    
                    # Copy track audio files
                    track_files = project_path / 'audio' / track_name
                    if track_files.exists():
                        for audio_file in track_files.glob('*'):
                            if audio_file.is_file():
                                dest = track_dir / audio_file.name
                                shutil.copy2(audio_file, dest)
                                result.files_exported += 1
                                result.output_files.append(dest)
                                
            except Exception as e:
                result.errors.append(f"Error reading project: {e}")
        
        result.output_path = output_path
        result.file_size = sum(f.stat().st_size for f in result.output_files)
        
        return result
    
    def _create_manifest(
        self,
        project_path: Path,
        options: ProjectExportOptions
    ) -> ExportManifest:
        """Create export manifest."""
        files = []
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                relative = file_path.relative_to(project_path)
                
                if not self._should_include(relative, options):
                    continue
                
                files.append({
                    "path": str(relative),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                })
        
        # Read project metadata
        metadata: dict[str, Any] = {}
        project_file = project_path / 'project.json'
        if project_file.exists():
            try:
                metadata = json.loads(project_file.read_text())
            except Exception as e:
                logger.debug("Failed to parse project.json: %s", e)
        
        return ExportManifest(
            name=project_path.name,
            version="1.0",
            created_at=datetime.now().isoformat(),
            voicestudio_version=self._voicestudio_version,
            files=files,
            metadata=metadata,
        )
    
    def _should_include(self, relative_path: Path, options: ProjectExportOptions) -> bool:
        """Check if a file should be included in export."""
        path_str = str(relative_path)
        
        if path_str.startswith('voices') and not options.include_voices:
            return False
        
        if path_str.startswith('sources') and not options.include_sources:
            return False
        
        if path_str.startswith('workflows') and not options.include_workflows:
            return False
        
        if path_str.startswith('settings') and not options.include_settings:
            return False
        
        # Skip temp and cache files
        if any(part in path_str for part in ['__pycache__', '.cache', '.tmp']):
            return False
        
        return True
