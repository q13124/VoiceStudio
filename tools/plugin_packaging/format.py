"""
VoiceStudio Plugin Package Format (.vspkg).

Phase 4 Enhancement: Defines the .vspkg archive format.

Format Specification:
=====================
.vspkg is a ZIP archive with the following structure:

plugin.vspkg
├── MANIFEST.json       # Package metadata (required)
├── SIGNATURE.json      # Cryptographic signature (optional)
├── CHECKSUMS.sha256    # File checksums (required)
├── manifest.json       # Plugin manifest (required)
├── plugin.py           # Plugin entry point (required for backend plugins)
├── assets/             # Plugin assets (optional)
│   ├── icon.png
│   └── preview.png
├── ui/                 # Frontend components (optional)
│   └── *.xaml
└── ... other plugin files

MANIFEST.json Schema:
{
    "format_version": "1.0.0",
    "package_id": "unique-plugin-id",
    "package_version": "1.0.0",
    "plugin_manifest": "manifest.json",
    "created_at": "2026-02-17T00:00:00Z",
    "created_by": "author-name",
    "min_voicestudio_version": "1.3.0",
    "files": ["list", "of", "included", "files"],
    "total_size": 12345
}
"""

from __future__ import annotations

import json
import logging
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

FORMAT_VERSION = "1.0.0"
PACKAGE_EXTENSION = ".vspkg"
REQUIRED_FILES = ["MANIFEST.json", "CHECKSUMS.sha256", "manifest.json"]
OPTIONAL_FILES = ["SIGNATURE.json"]


@dataclass
class VSPKGManifest:
    """Package manifest metadata."""
    format_version: str
    package_id: str
    package_version: str
    plugin_manifest: str
    created_at: str
    created_by: str
    min_voicestudio_version: str
    files: list[str] = field(default_factory=list)
    total_size: int = 0
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VSPKGManifest:
        """Create from dictionary."""
        return cls(
            format_version=data.get("format_version", FORMAT_VERSION),
            package_id=data.get("package_id", ""),
            package_version=data.get("package_version", ""),
            plugin_manifest=data.get("plugin_manifest", "manifest.json"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            created_by=data.get("created_by", ""),
            min_voicestudio_version=data.get("min_voicestudio_version", "1.0.0"),
            files=data.get("files", []),
            total_size=data.get("total_size", 0),
        )
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "format_version": self.format_version,
            "package_id": self.package_id,
            "package_version": self.package_version,
            "plugin_manifest": self.plugin_manifest,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "min_voicestudio_version": self.min_voicestudio_version,
            "files": self.files,
            "total_size": self.total_size,
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)


class VSPKGFormat:
    """
    VoiceStudio Plugin Package format handler.
    
    Provides utilities for reading and validating .vspkg archives.
    """
    
    @staticmethod
    def is_valid_package(path: Path) -> bool:
        """
        Check if a file is a valid .vspkg package.
        
        Args:
            path: Path to the package file
            
        Returns:
            True if valid package structure
        """
        if not path.exists() or path.suffix != PACKAGE_EXTENSION:
            return False
        
        try:
            with zipfile.ZipFile(path, "r") as zf:
                names = set(zf.namelist())
                # Check required files
                return all(required in names for required in REQUIRED_FILES)
        except (zipfile.BadZipFile, Exception):
            return False
    
    @staticmethod
    def read_manifest(path: Path) -> VSPKGManifest | None:
        """
        Read the package manifest from a .vspkg file.
        
        Args:
            path: Path to the package file
            
        Returns:
            Package manifest or None if invalid
        """
        try:
            with zipfile.ZipFile(path, "r") as zf:
                manifest_data = zf.read("MANIFEST.json")
                data = json.loads(manifest_data.decode("utf-8"))
                return VSPKGManifest.from_dict(data)
        except Exception as e:
            # GAP-PY-001: Invalid package, return None
            logger.debug(f"Failed to read manifest from {path}: {e}")
            return None
    
    @staticmethod
    def read_plugin_manifest(path: Path) -> dict[str, Any] | None:
        """
        Read the plugin manifest.json from a .vspkg file.
        
        Args:
            path: Path to the package file
            
        Returns:
            Plugin manifest dict or None if invalid
        """
        try:
            with zipfile.ZipFile(path, "r") as zf:
                pkg_manifest = VSPKGFormat.read_manifest(path)
                if not pkg_manifest:
                    return None
                
                plugin_manifest_path = pkg_manifest.plugin_manifest
                manifest_data = zf.read(plugin_manifest_path)
                return json.loads(manifest_data.decode("utf-8"))
        except Exception as e:
            # GAP-PY-001: Invalid package or missing manifest
            logger.debug(f"Failed to read plugin manifest from {path}: {e}")
            return None
    
    @staticmethod
    def read_checksums(path: Path) -> dict[str, str]:
        """
        Read the checksums file from a .vspkg file.
        
        Args:
            path: Path to the package file
            
        Returns:
            Dict mapping filename to SHA256 hash
        """
        checksums = {}
        try:
            with zipfile.ZipFile(path, "r") as zf:
                checksum_data = zf.read("CHECKSUMS.sha256").decode("utf-8")
                for line in checksum_data.strip().split("\n"):
                    if not line or line.startswith("#"):
                        continue
                    parts = line.split("  ", 1)  # SHA256 format: hash  filename
                    if len(parts) == 2:
                        checksums[parts[1].strip()] = parts[0].strip()
        except Exception as e:
            # GAP-PY-001: Checksums are optional (older packages may not have them)
            logger.debug(f"Failed to read checksums from {path}: {e}")
        return checksums
    
    @staticmethod
    def has_signature(path: Path) -> bool:
        """
        Check if a package has a signature.
        
        Args:
            path: Path to the package file
            
        Returns:
            True if signature present
        """
        try:
            with zipfile.ZipFile(path, "r") as zf:
                return "SIGNATURE.json" in zf.namelist()
        except Exception as e:
            # GAP-PY-001: Invalid package
            logger.debug(f"Failed to check signature in {path}: {e}")
            return False
    
    @staticmethod
    def list_files(path: Path) -> list[str]:
        """
        List all files in a package.
        
        Args:
            path: Path to the package file
            
        Returns:
            List of file paths in the archive
        """
        try:
            with zipfile.ZipFile(path, "r") as zf:
                return zf.namelist()
        except Exception as e:
            # GAP-PY-001: Invalid package
            logger.debug(f"Failed to list files in {path}: {e}")
            return []
    
    @staticmethod
    def extract(path: Path, destination: Path) -> bool:
        """
        Extract a package to a directory.
        
        Args:
            path: Path to the package file
            destination: Extraction destination
            
        Returns:
            True if successful
        """
        try:
            destination.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path, "r") as zf:
                zf.extractall(destination)
            return True
        except Exception as e:
            # GAP-PY-001: Extraction failed
            logger.debug(f"Failed to extract {path} to {destination}: {e}")
            return False
    
    @staticmethod
    def get_format_version() -> str:
        """Get the current format version."""
        return FORMAT_VERSION
    
    @staticmethod
    def extract_file(path: Path, filename: str, destination: Path) -> bool:
        """
        Extract a single file from a package.
        
        Args:
            path: Path to the package file
            filename: Name of the file to extract
            destination: Destination directory
            
        Returns:
            True if successful
        """
        try:
            destination.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path, "r") as zf:
                if filename in zf.namelist():
                    zf.extract(filename, destination)
                    return True
                return False
        except Exception as e:
            # GAP-PY-001: Extraction failed
            logger.debug(f"Failed to extract {filename} from {path}: {e}")
            return False
    
    @staticmethod
    def extract_all(path: Path, destination: Path) -> bool:
        """
        Extract all files from a package.
        
        Alias for extract() for backwards compatibility.
        
        Args:
            path: Path to the package file
            destination: Destination directory
            
        Returns:
            True if successful
        """
        return VSPKGFormat.extract(path, destination)
