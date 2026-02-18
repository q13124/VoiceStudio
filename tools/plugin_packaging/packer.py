"""
VoiceStudio Plugin Packer.

Phase 4 Enhancement: Creates .vspkg packages from plugin directories.
"""

from __future__ import annotations

import hashlib
import json
import logging
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .format import FORMAT_VERSION, PACKAGE_EXTENSION, VSPKGManifest

logger = logging.getLogger(__name__)


# Files to exclude from packaging
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".git",
    ".gitignore",
    ".DS_Store",
    "Thumbs.db",
    "*.egg-info",
    ".pytest_cache",
    ".mypy_cache",
    "*.log",
    ".env",
    ".venv",
    "venv",
    "node_modules",
]


@dataclass
class PackResult:
    """Result of packing operation."""
    success: bool
    package_path: Path | None = None
    manifest: VSPKGManifest | None = None
    files_included: int = 0
    total_size: int = 0
    error: str | None = None
    warnings: list[str] = field(default_factory=list)


class PluginPacker:
    """
    Creates .vspkg packages from plugin source directories.
    
    Features:
    - Validates plugin structure before packing
    - Generates SHA256 checksums for all files
    - Creates package manifest
    - Supports custom exclusion patterns
    """
    
    def __init__(
        self,
        exclude_patterns: list[str] | None = None,
        author: str = "",
        min_voicestudio_version: str = "1.0.0",
    ):
        """
        Initialize packer.
        
        Args:
            exclude_patterns: Additional patterns to exclude
            author: Default author name
            min_voicestudio_version: Minimum VoiceStudio version required
        """
        self._exclude_patterns = EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            self._exclude_patterns.extend(exclude_patterns)
        self._author = author
        self._min_version = min_voicestudio_version
    
    def pack(
        self,
        plugin_dir: Path,
        output_dir: Path | None = None,
        output_name: str | None = None,
    ) -> PackResult:
        """
        Pack a plugin directory into a .vspkg file.
        
        Args:
            plugin_dir: Path to the plugin directory
            output_dir: Output directory (default: same as plugin_dir)
            output_name: Output filename without extension (default: plugin id)
            
        Returns:
            Pack result with status and details
        """
        warnings = []
        
        # Validate plugin directory
        if not plugin_dir.exists() or not plugin_dir.is_dir():
            return PackResult(
                success=False,
                error=f"Plugin directory not found: {plugin_dir}",
            )
        
        # Check for required files
        manifest_path = plugin_dir / "manifest.json"
        if not manifest_path.exists():
            return PackResult(
                success=False,
                error="manifest.json not found in plugin directory",
            )
        
        # Read plugin manifest
        try:
            plugin_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as e:
            return PackResult(
                success=False,
                error=f"Failed to read manifest.json: {e}",
            )
        
        # Extract plugin info (prefer 'id' over 'name' for package_id)
        plugin_id = plugin_manifest.get("id") or plugin_manifest.get("name", plugin_dir.name)
        plugin_version = plugin_manifest.get("version", "0.0.0")
        
        # Determine output path
        if output_dir is None:
            output_dir = plugin_dir.parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if output_name is None:
            output_name = f"{plugin_id}-{plugin_version}"
        
        package_path = output_dir / f"{output_name}{PACKAGE_EXTENSION}"
        
        # Collect files to include
        files_to_pack: list[tuple[Path, str]] = []  # (absolute_path, archive_path)
        total_size = 0
        
        for file_path in plugin_dir.rglob("*"):
            if file_path.is_dir():
                continue
            
            # Check exclusions
            relative_path = file_path.relative_to(plugin_dir)
            if self._should_exclude(relative_path):
                continue
            
            files_to_pack.append((file_path, str(relative_path)))
            total_size += file_path.stat().st_size
        
        if not files_to_pack:
            return PackResult(
                success=False,
                error="No files to pack after applying exclusions",
            )
        
        # Check for plugin.py (required for backend plugins)
        has_plugin_py = any(path == "plugin.py" for _, path in files_to_pack)
        if not has_plugin_py and plugin_manifest.get("entry_points", {}).get("backend"):
            warnings.append("Backend entry point specified but plugin.py not found")
        
        # Generate checksums
        checksums = self._generate_checksums(files_to_pack)
        
        # Create package manifest
        pkg_manifest = VSPKGManifest(
            format_version=FORMAT_VERSION,
            package_id=plugin_id,
            package_version=plugin_version,
            plugin_manifest="manifest.json",
            created_at=datetime.now().isoformat(),
            created_by=self._author or plugin_manifest.get("author", "unknown"),
            min_voicestudio_version=self._min_version,
            files=[path for _, path in files_to_pack],
            total_size=total_size,
        )
        
        # Create the package
        try:
            with zipfile.ZipFile(
                package_path, "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=9,
            ) as zf:
                # Add package manifest
                zf.writestr("MANIFEST.json", pkg_manifest.to_json())
                
                # Add checksums
                checksum_content = self._format_checksums(checksums)
                zf.writestr("CHECKSUMS.sha256", checksum_content)
                
                # Add plugin files
                for file_path, archive_path in files_to_pack:
                    zf.write(file_path, archive_path)
            
            logger.info(f"Created package: {package_path}")
            
            return PackResult(
                success=True,
                package_path=package_path,
                manifest=pkg_manifest,
                files_included=len(files_to_pack),
                total_size=total_size,
                warnings=warnings,
            )
            
        except Exception as e:
            logger.error(f"Failed to create package: {e}")
            # Clean up partial file
            if package_path.exists():
                package_path.unlink()
            return PackResult(
                success=False,
                error=f"Failed to create package: {e}",
                warnings=warnings,
            )
    
    def _should_exclude(self, path: Path) -> bool:
        """Check if a path should be excluded."""
        path_str = str(path)
        path_name = path.name
        
        for pattern in self._exclude_patterns:
            if pattern.startswith("*"):
                # Wildcard pattern
                if path_name.endswith(pattern[1:]):
                    return True
            elif pattern in path_str or pattern == path_name:
                return True
        
        return False
    
    def _generate_checksums(
        self, files: list[tuple[Path, str]]
    ) -> dict[str, str]:
        """Generate SHA256 checksums for files."""
        checksums = {}
        
        for file_path, archive_path in files:
            sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            checksums[archive_path] = sha256.hexdigest()
        
        return checksums
    
    def _format_checksums(self, checksums: dict[str, str]) -> str:
        """Format checksums in SHA256SUM format."""
        lines = [
            "# VoiceStudio Plugin Package Checksums",
            f"# Generated: {datetime.now().isoformat()}",
            "#",
        ]
        
        for filename, hash_value in sorted(checksums.items()):
            lines.append(f"{hash_value}  {filename}")
        
        return "\n".join(lines) + "\n"


def pack_plugin(
    plugin_dir: str | Path,
    output_dir: str | Path | None = None,
    author: str = "",
) -> PackResult:
    """
    Convenience function to pack a plugin.
    
    Args:
        plugin_dir: Path to plugin directory
        output_dir: Output directory
        author: Author name
        
    Returns:
        Pack result
    """
    packer = PluginPacker(author=author)
    return packer.pack(
        Path(plugin_dir),
        Path(output_dir) if output_dir else None,
    )
