"""
Plugin Pack Command.

Packages plugins into .vspkg format.
"""

import hashlib
import json
import os
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import click

# Files to exclude from packages
DEFAULT_EXCLUDES = {
    # Python cache
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    
    # Virtual environments
    "venv",
    ".venv",
    "env",
    ".env",
    "ENV",
    
    # Build artifacts
    "build",
    "dist",
    "*.egg-info",
    "*.egg",
    "htmlcov",
    ".coverage",
    ".pytest_cache",
    ".tox",
    
    # IDE files
    ".idea",
    ".vscode",
    "*.swp",
    "*.swo",
    
    # Git
    ".git",
    ".gitignore",
    ".gitattributes",
    
    # Plugin artifacts
    "*.vspkg",
    "*.sig",
    ".plugin-cache",
    
    # Documentation build
    "_build",
    "site",
    
    # OS files
    ".DS_Store",
    "Thumbs.db",
}


def should_exclude(path: Path, excludes: Set[str]) -> bool:
    """Check if a path should be excluded from the package."""
    name = path.name
    
    for pattern in excludes:
        if pattern.startswith("*"):
            # Suffix match
            if name.endswith(pattern[1:]):
                return True
        elif pattern.endswith("*"):
            # Prefix match
            if name.startswith(pattern[:-1]):
                return True
        else:
            # Exact match
            if name == pattern:
                return True
    
    return False


def collect_files(
    plugin_dir: Path,
    excludes: Set[str],
) -> List[Path]:
    """Collect all files to include in the package."""
    files = []
    
    for item in plugin_dir.rglob("*"):
        # Skip directories themselves
        if item.is_dir():
            continue
        
        # Check exclusions
        rel_path = item.relative_to(plugin_dir)
        skip = False
        
        for part in rel_path.parts:
            if should_exclude(Path(part), excludes):
                skip = True
                break
        
        if not skip:
            files.append(item)
    
    return sorted(files)


def calculate_checksum(file_path: Path, algorithm: str = "sha256") -> str:
    """Calculate checksum of a file."""
    hasher = hashlib.new(algorithm)
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def calculate_package_checksum(files: List[Path], plugin_dir: Path) -> Dict[str, str]:
    """Calculate checksums for all files in the package."""
    checksums = {}
    
    for file_path in files:
        rel_path = str(file_path.relative_to(plugin_dir))
        checksums[rel_path] = calculate_checksum(file_path)
    
    return checksums


def load_manifest(plugin_dir: Path) -> Dict[str, Any]:
    """Load the plugin manifest."""
    manifest_path = plugin_dir / "plugin.json"
    if not manifest_path.exists():
        manifest_path = plugin_dir / "manifest.json"
    
    if not manifest_path.exists():
        raise click.ClickException("No plugin.json or manifest.json found")
    
    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def create_package_manifest(
    manifest: Dict[str, Any],
    checksums: Dict[str, str],
    files: List[str],
) -> Dict[str, Any]:
    """Create the .vspkg package manifest."""
    return {
        "format_version": "1.0",
        "created_at": datetime.utcnow().isoformat() + "Z",
        "plugin": {
            "id": manifest.get("id", ""),
            "name": manifest.get("name", ""),
            "version": manifest.get("version", ""),
            "author": manifest.get("author", {}),
        },
        "files": files,
        "checksums": checksums,
        "checksum_algorithm": "sha256",
    }


def create_vspkg(
    plugin_dir: Path,
    output_path: Path,
    excludes: Set[str],
    verbose: bool = False,
    quiet: bool = False,
) -> Dict[str, Any]:
    """
    Create a .vspkg package.
    
    Returns:
        Package metadata including checksums
    """
    # Load manifest
    manifest = load_manifest(plugin_dir)
    
    # Collect files
    files = collect_files(plugin_dir, excludes)
    
    if not files:
        raise click.ClickException("No files to package")
    
    if verbose and not quiet:
        click.echo(f"Collecting {len(files)} files...")
    
    # Calculate checksums
    checksums = calculate_package_checksum(files, plugin_dir)
    
    # Create file list (relative paths)
    file_list = [str(f.relative_to(plugin_dir)) for f in files]
    
    # Create package manifest
    pkg_manifest = create_package_manifest(manifest, checksums, file_list)
    
    # Create the package
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add all plugin files
        for file_path in files:
            rel_path = file_path.relative_to(plugin_dir)
            if verbose and not quiet:
                click.echo(f"  Adding: {rel_path}")
            zf.write(file_path, rel_path)
        
        # Add package manifest
        pkg_manifest_json = json.dumps(pkg_manifest, indent=2)
        zf.writestr("VSPKG-MANIFEST.json", pkg_manifest_json)
    
    # Calculate package checksum
    pkg_manifest["package_checksum"] = calculate_checksum(output_path)
    
    return pkg_manifest


@click.command("pack")
@click.argument(
    "path",
    type=click.Path(exists=True),
    default=".",
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file path (default: <name>-<version>.vspkg).",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Additional patterns to exclude from package.",
)
@click.option(
    "--include-tests",
    is_flag=True,
    help="Include test files in package.",
)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Validate plugin before packing.",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output package info as JSON.",
)
@click.pass_context
def pack_command(
    ctx: click.Context,
    path: str,
    output: Optional[str],
    exclude: tuple,
    include_tests: bool,
    validate: bool,
    output_json: bool,
) -> None:
    """
    Package a plugin into .vspkg format.
    
    Creates a distributable .vspkg package from the plugin at PATH
    (defaults to current directory). The package includes all plugin
    files and a manifest with checksums.
    
    Examples:
    
        voicestudio-plugin pack
        
        voicestudio-plugin pack ./my-plugin --output dist/my-plugin.vspkg
        
        voicestudio-plugin pack --exclude "*.md" --exclude "docs/*"
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)
    
    plugin_path = Path(path).resolve()
    
    # Validate first
    if validate:
        from .validate import validate_plugin_structure
        
        errors, warnings = validate_plugin_structure(plugin_path)
        
        if errors:
            if not output_json:
                click.echo(click.style("Validation errors:", fg="red"))
                for error in errors:
                    click.echo(click.style(f"  [X] {error}", fg="red"))
            raise click.ClickException(
                "Plugin validation failed. Fix errors or use --no-validate."
            )
        
        if warnings and verbose and not quiet:
            click.echo(click.style("Validation warnings:", fg="yellow"))
            for warning in warnings:
                click.echo(click.style(f"  [!] {warning}", fg="yellow"))
    
    # Load manifest to get name and version
    manifest = load_manifest(plugin_path)
    plugin_name = manifest.get("name", "plugin").lower().replace(" ", "-")
    plugin_version = manifest.get("version", "0.0.0")
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = plugin_path / f"{plugin_name}-{plugin_version}.vspkg"
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build exclusion set
    excludes = DEFAULT_EXCLUDES.copy()
    excludes.update(exclude)
    
    # Optionally exclude tests
    if not include_tests:
        excludes.add("tests")
        excludes.add("test")
        excludes.add("test_*.py")
        excludes.add("*_test.py")
    
    if not quiet and not output_json:
        click.echo(f"Packaging plugin: {plugin_name} v{plugin_version}")
    
    # Create the package
    pkg_info = create_vspkg(
        plugin_path,
        output_path,
        excludes,
        verbose=verbose,
        quiet=quiet,
    )
    
    # Output results
    if output_json:
        result = {
            "success": True,
            "package": str(output_path),
            "plugin_id": pkg_info["plugin"]["id"],
            "plugin_version": pkg_info["plugin"]["version"],
            "file_count": len(pkg_info["files"]),
            "checksum": pkg_info.get("package_checksum", ""),
        }
        click.echo(json.dumps(result, indent=2))
    else:
        if not quiet:
            file_count = len(pkg_info["files"])
            pkg_size = output_path.stat().st_size
            
            # Format size
            if pkg_size > 1024 * 1024:
                size_str = f"{pkg_size / (1024 * 1024):.2f} MB"
            elif pkg_size > 1024:
                size_str = f"{pkg_size / 1024:.2f} KB"
            else:
                size_str = f"{pkg_size} bytes"
            
            click.echo()
            click.echo(click.style("[OK] Package created successfully", fg="green"))
            click.echo(f"  Output: {output_path}")
            click.echo(f"  Files: {file_count}")
            click.echo(f"  Size: {size_str}")
            click.echo(f"  Checksum: {pkg_info.get('package_checksum', 'N/A')[:16]}...")
            click.echo()
            click.echo("Next steps:")
            click.echo(f"  voicestudio-plugin sign {output_path}")
