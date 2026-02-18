"""
Plugin Validate Command.

Validates plugin manifests and structure against the schema.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click

# Required manifest fields (schema v4)
REQUIRED_FIELDS = [
    "schema_version",
    "id",
    "name",
    "version",
    "description",
    "author",
    "license",
    "plugin_type",  # Architecture type: backend_only, frontend_only, full_stack
    "category",     # Functional category: voice_synthesis, speech_recognition, etc.
]

# Valid plugin architecture types (manifest 'plugin_type' field)
VALID_PLUGIN_TYPES = [
    "backend_only",
    "frontend_only",
    "full_stack",
]

# Valid plugin functional categories (manifest 'category' field)
VALID_CATEGORIES = [
    "voice_synthesis",
    "speech_recognition",
    "audio_effects",
    "audio_analysis",
    "voice_conversion",
    "video_processing",
    "integrations",
    "utilities",
    "developer_tools",
]

# Valid permission levels
VALID_PERMISSION_LEVELS = ["denied", "read_only", "write", "full"]


def find_manifest(path: Path) -> Optional[Path]:
    """Find the plugin manifest file."""
    # Check for plugin.json first
    manifest_path = path / "plugin.json"
    if manifest_path.exists():
        return manifest_path
    
    # Check for manifest.json
    manifest_path = path / "manifest.json"
    if manifest_path.exists():
        return manifest_path
    
    # Check if path is a file itself
    if path.is_file() and path.suffix == ".json":
        return path
    
    return None


def load_manifest(path: Path) -> Dict[str, Any]:
    """Load and parse the manifest file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_required_fields(manifest: Dict[str, Any]) -> List[str]:
    """Validate that all required fields are present."""
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")
        elif not manifest[field]:
            errors.append(f"Empty required field: {field}")
    return errors


def validate_version_format(version: str) -> List[str]:
    """Validate version string format (semver)."""
    errors = []
    parts = version.split(".")
    if len(parts) != 3:
        errors.append(f"Invalid version format: {version} (expected: X.Y.Z)")
        return errors
    
    for i, part in enumerate(parts):
        # Handle pre-release suffixes
        base_part = part.split("-")[0]
        try:
            int(base_part)
        except ValueError:
            errors.append(f"Invalid version component: {part}")
    
    return errors


def validate_plugin_id(plugin_id: str) -> List[str]:
    """Validate plugin ID format."""
    errors = []
    
    if not plugin_id:
        errors.append("Plugin ID cannot be empty")
        return errors
    
    # Check format: should be reverse domain notation
    parts = plugin_id.split(".")
    if len(parts) < 2:
        errors.append(
            f"Invalid plugin ID format: {plugin_id} "
            "(expected: reverse domain notation, e.g., com.example.myplugin)"
        )
    
    # Check for invalid characters
    import re
    if not re.match(r"^[a-z0-9._-]+$", plugin_id):
        errors.append(
            f"Invalid plugin ID: {plugin_id} "
            "(only lowercase letters, numbers, dots, hyphens, and underscores allowed)"
        )
    
    return errors


def validate_author(author: Any) -> List[str]:
    """Validate author field structure."""
    errors = []
    
    if isinstance(author, str):
        if not author:
            errors.append("Author name cannot be empty")
        return errors
    
    if isinstance(author, dict):
        if "name" not in author or not author["name"]:
            errors.append("Author object must have a 'name' field")
        
        if author.get("email"):
            import re
            email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
            if not re.match(email_pattern, author["email"]):
                errors.append(f"Invalid email format: {author['email']}")
        
        return errors
    
    errors.append("Author must be a string or object with 'name' field")
    return errors


def validate_plugin_type(plugin_type: str) -> List[str]:
    """Validate plugin architecture type (plugin_type field)."""
    errors = []
    if plugin_type not in VALID_PLUGIN_TYPES:
        errors.append(
            f"Invalid plugin_type: {plugin_type} "
            f"(valid types: {', '.join(VALID_PLUGIN_TYPES)})"
        )
    return errors


def validate_category(category: str) -> List[str]:
    """Validate plugin functional category."""
    errors = []
    if category not in VALID_CATEGORIES:
        errors.append(
            f"Invalid category: {category} "
            f"(valid categories: {', '.join(VALID_CATEGORIES)})"
        )
    return errors


def validate_dependencies(dependencies: Any) -> List[str]:
    """Validate dependencies structure."""
    errors = []
    
    if not isinstance(dependencies, dict):
        errors.append("Dependencies must be an object")
        return errors
    
    valid_keys = ["runtime", "optional", "python"]
    for key in dependencies:
        if key not in valid_keys:
            errors.append(f"Unknown dependency category: {key}")
        elif not isinstance(dependencies[key], list):
            errors.append(f"Dependency category '{key}' must be an array")
    
    return errors


def validate_security(security: Any) -> List[str]:
    """Validate security configuration."""
    errors = []
    
    if not isinstance(security, dict):
        errors.append("Security must be an object")
        return errors
    
    # Validate permissions
    permissions = security.get("permissions", {})
    if isinstance(permissions, dict):
        for category, config in permissions.items():
            if isinstance(config, dict):
                level = config.get("level")
                if level and level not in VALID_PERMISSION_LEVELS:
                    errors.append(
                        f"Invalid permission level for {category}: {level} "
                        f"(valid: {', '.join(VALID_PERMISSION_LEVELS)})"
                    )
    
    return errors


def validate_ui(ui: Any) -> List[str]:
    """Validate UI configuration."""
    errors = []
    
    if not isinstance(ui, dict):
        errors.append("UI must be an object")
        return errors
    
    # Check icon exists if specified
    if ui.get("icon"):
        # Just validate it's a string for now
        if not isinstance(ui["icon"], str):
            errors.append("UI icon must be a string path")
    
    return errors


def validate_manifest(
    manifest: Dict[str, Any],
    plugin_dir: Optional[Path] = None,
) -> Tuple[List[str], List[str]]:
    """
    Validate a plugin manifest.
    
    Returns:
        Tuple of (errors, warnings)
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    # Required fields
    errors.extend(validate_required_fields(manifest))
    
    # Version format
    if "version" in manifest:
        errors.extend(validate_version_format(manifest["version"]))
    
    # Plugin ID
    if "id" in manifest:
        errors.extend(validate_plugin_id(manifest["id"]))
    
    # Author
    if "author" in manifest:
        errors.extend(validate_author(manifest["author"]))
    
    # Plugin architecture type
    if "plugin_type" in manifest:
        errors.extend(validate_plugin_type(manifest["plugin_type"]))
    
    # Plugin functional category
    if "category" in manifest:
        errors.extend(validate_category(manifest["category"]))
    
    # Dependencies
    if "dependencies" in manifest:
        errors.extend(validate_dependencies(manifest["dependencies"]))
    
    # Security
    if "security" in manifest:
        errors.extend(validate_security(manifest["security"]))
    
    # UI
    if "ui" in manifest:
        errors.extend(validate_ui(manifest["ui"]))
    
    # Warnings for optional but recommended fields
    if "description" in manifest and len(manifest["description"]) < 10:
        warnings.append("Description is very short, consider adding more detail")
    
    if "repository" not in manifest or not manifest.get("repository"):
        warnings.append("No repository URL specified")
    
    if "homepage" not in manifest or not manifest.get("homepage"):
        warnings.append("No homepage URL specified")
    
    if "capabilities" not in manifest or not manifest.get("capabilities"):
        warnings.append("No capabilities declared")
    
    # File existence checks
    if plugin_dir:
        # Check for main module
        module_name = manifest.get("id", "").split(".")[-1].replace("-", "_")
        main_module = plugin_dir / module_name
        if not main_module.exists():
            main_py = plugin_dir / "main.py"
            if not main_py.exists():
                errors.append(
                    f"Main module not found: expected '{module_name}/' or 'main.py'"
                )
        
        # Check for icon
        icon = manifest.get("ui", {}).get("icon")
        if icon:
            icon_path = plugin_dir / icon
            if not icon_path.exists():
                warnings.append(f"Icon file not found: {icon}")
        
        # Check for README
        readme = plugin_dir / "README.md"
        if not readme.exists():
            warnings.append("No README.md found")
    
    return errors, warnings


def validate_plugin_structure(plugin_dir: Path) -> Tuple[List[str], List[str]]:
    """
    Validate the overall plugin directory structure.
    
    Returns:
        Tuple of (errors, warnings)
    """
    errors: List[str] = []
    warnings: List[str] = []
    
    # Check for manifest
    manifest_path = find_manifest(plugin_dir)
    if not manifest_path:
        errors.append("No plugin.json or manifest.json found")
        return errors, warnings
    
    # Load and validate manifest
    try:
        manifest = load_manifest(manifest_path)
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in manifest: {e}")
        return errors, warnings
    except Exception as e:
        errors.append(f"Failed to read manifest: {e}")
        return errors, warnings
    
    manifest_errors, manifest_warnings = validate_manifest(manifest, plugin_dir)
    errors.extend(manifest_errors)
    warnings.extend(manifest_warnings)
    
    # Check for tests
    tests_dir = plugin_dir / "tests"
    if not tests_dir.exists():
        warnings.append("No tests directory found")
    elif not list(tests_dir.glob("test_*.py")):
        warnings.append("No test files found in tests/")
    
    return errors, warnings


@click.command("validate")
@click.argument(
    "path",
    type=click.Path(exists=True),
    default=".",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Treat warnings as errors.",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results as JSON.",
)
@click.pass_context
def validate_command(
    ctx: click.Context,
    path: str,
    strict: bool,
    output_json: bool,
) -> None:
    """
    Validate a plugin manifest and structure.
    
    Validates the plugin at PATH (defaults to current directory).
    Checks for required fields, correct formats, and recommended
    best practices.
    
    Examples:
    
        voicestudio-plugin validate
        
        voicestudio-plugin validate ./my-plugin
        
        voicestudio-plugin validate --strict
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)
    
    plugin_path = Path(path).resolve()
    
    if plugin_path.is_file():
        # Validate just the manifest file
        try:
            manifest = load_manifest(plugin_path)
            errors, warnings = validate_manifest(manifest)
        except Exception as e:
            if output_json:
                click.echo(json.dumps({
                    "valid": False,
                    "errors": [str(e)],
                    "warnings": [],
                }))
            else:
                raise click.ClickException(f"Failed to validate: {e}")
            return
    else:
        # Validate the plugin directory
        errors, warnings = validate_plugin_structure(plugin_path)
    
    # Handle strict mode
    if strict:
        errors.extend(warnings)
        warnings = []
    
    # Determine validity
    is_valid = len(errors) == 0
    
    # Output results
    if output_json:
        result = {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
        }
        click.echo(json.dumps(result, indent=2))
    else:
        if not quiet:
            if errors:
                click.echo(click.style("Validation Errors:", fg="red", bold=True))
                for error in errors:
                    click.echo(click.style(f"  [X] {error}", fg="red"))
            
            if warnings:
                click.echo(click.style("\nWarnings:", fg="yellow", bold=True))
                for warning in warnings:
                    click.echo(click.style(f"  [!] {warning}", fg="yellow"))
            
            if is_valid:
                if not errors and not warnings:
                    click.echo(click.style("[OK] Plugin is valid", fg="green"))
                else:
                    click.echo(click.style("\n[OK] Plugin is valid (with warnings)", fg="green"))
    
    # Exit with error code if invalid
    if not is_valid:
        sys.exit(1)
