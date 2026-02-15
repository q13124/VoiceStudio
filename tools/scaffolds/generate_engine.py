#!/usr/bin/env python3
"""
VoiceStudio Engine Scaffold Generator

Generates a new engine adapter with manifest, Python implementation,
and test files following VoiceStudio's engine patterns.

Usage:
    python tools/scaffolds/generate_engine.py --name cosyvoice --type audio --subtype tts
    python tools/scaffolds/generate_engine.py --name my_engine --type video --subtype generation

Generated files:
    - engines/{type}/{engine_id}/engine.manifest.json
    - app/core/engines/{engine_id}_engine.py
    - tests/unit/engines/test_{engine_id}.py

Part of the Claude Recommendations Integration (Phase 2).
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import NamedTuple


class ScaffoldResult(NamedTuple):
    """Result of scaffold generation."""
    success: bool
    files_created: list[str]
    errors: list[str]
    manual_steps: list[str]


def find_project_root() -> Path:
    """Find the VoiceStudio project root directory."""
    current = Path(__file__).resolve().parent

    markers = ["VoiceStudio.sln", "global.json", ".cursor"]

    for _ in range(10):
        for marker in markers:
            if (current / marker).exists():
                return current
        current = current.parent

    return Path.cwd()


def to_pascal_case(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def to_display_name(name: str) -> str:
    """Convert snake_case to display name with spaces."""
    return " ".join(word.capitalize() for word in name.split("_"))


def load_template(template_name: str, project_root: Path) -> str:
    """Load a template file."""
    template_path = project_root / "tools" / "scaffolds" / "templates" / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text(encoding="utf-8")


def render_template(template: str, replacements: dict[str, str]) -> str:
    """Replace placeholders in template with actual values."""
    result = template
    for key, value in replacements.items():
        result = result.replace(f"{{{{{key}}}}}", value)
    return result


def generate_engine(
    name: str,
    engine_type: str,
    engine_subtype: str,
    description: str | None = None,
    project_root: Path | None = None,
    dry_run: bool = False
) -> ScaffoldResult:
    """
    Generate a new engine with all required files.

    Args:
        name: snake_case name for the engine (e.g., "cosyvoice")
        engine_type: Engine type (audio, image, video)
        engine_subtype: Engine subtype (tts, stt, cloning, generation, etc.)
        description: Optional description
        project_root: Project root directory
        dry_run: If True, don't create files, just report what would be created

    Returns:
        ScaffoldResult with created files and any errors
    """
    if project_root is None:
        project_root = find_project_root()

    errors: list[str] = []
    files_created: list[str] = []
    manual_steps: list[str] = []

    # Validate name
    if not re.match(r'^[a-z][a-z0-9_]*$', name):
        errors.append(f"Invalid engine name (use snake_case): {name}")
        return ScaffoldResult(False, files_created, errors, manual_steps)

    # Validate type
    valid_types = ["audio", "image", "video"]
    if engine_type not in valid_types:
        errors.append(f"Invalid engine type '{engine_type}'. Must be one of: {', '.join(valid_types)}")
        return ScaffoldResult(False, files_created, errors, manual_steps)

    # Prepare replacements
    pascal_name = to_pascal_case(name)
    display_name = to_display_name(name)

    if description is None:
        description = f"{display_name} engine for {engine_subtype}"

    replacements = {
        "NAME": pascal_name,
        "ENGINE_ID": name,
        "DISPLAY_NAME": display_name,
        "ENGINE_TYPE": engine_type,
        "ENGINE_SUBTYPE": engine_subtype,
        "DESCRIPTION": description,
        "DATE": datetime.now().strftime("%Y-%m-%d"),
    }

    # Define output paths
    manifest_dir = project_root / "engines" / engine_type / name
    engine_dir = project_root / "app" / "core" / "engines"
    tests_dir = project_root / "tests" / "unit" / "engines"

    output_files = [
        (manifest_dir / "engine.manifest.json", "engine_manifest.json.template"),
        (engine_dir / f"{name}_engine.py", "engine_adapter.py.template"),
        (tests_dir / f"test_{name}.py", "engine_test.py.template"),
    ]

    # Check for existing files
    for output_path, _ in output_files:
        if output_path.exists():
            errors.append(f"File already exists: {output_path}")

    if errors and not dry_run:
        return ScaffoldResult(False, files_created, errors, manual_steps)

    # Generate files
    for output_path, template_name in output_files:
        try:
            template = load_template(template_name, project_root)
            content = render_template(template, replacements)

            if dry_run:
                files_created.append(f"[DRY RUN] {output_path}")
            else:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(content, encoding="utf-8")
                files_created.append(str(output_path.relative_to(project_root)))
        except Exception as e:
            errors.append(f"Failed to create {output_path}: {e}")

    # Add manual steps
    manual_steps.append(
        "1. Add engine to config: backend/config/engine_config.json"
    )
    manual_steps.append(
        f"   Add entry for '{name}' with manifest path"
    )
    manual_steps.append(f"2. Implement engine methods in app/core/engines/{name}_engine.py")
    manual_steps.append(f"3. Add dependencies to engines/{engine_type}/{name}/engine.manifest.json")
    manual_steps.append(f"4. Test: python -m pytest tests/unit/engines/test_{name}.py -v")
    manual_steps.append("5. Run health check: verify engine appears in /api/engines")

    success = len(errors) == 0
    return ScaffoldResult(success, files_created, errors, manual_steps)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a new VoiceStudio engine scaffold"
    )
    parser.add_argument(
        "--name", required=True,
        help="snake_case name for the engine (e.g., cosyvoice)"
    )
    parser.add_argument(
        "--type", required=True, dest="engine_type",
        choices=["audio", "image", "video"],
        help="Engine type (audio, image, video)"
    )
    parser.add_argument(
        "--subtype", required=True,
        help="Engine subtype (e.g., tts, stt, cloning, generation)"
    )
    parser.add_argument(
        "--description",
        help="Description for the engine"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be created without creating files"
    )

    args = parser.parse_args()

    result = generate_engine(
        name=args.name,
        engine_type=args.engine_type,
        engine_subtype=args.subtype,
        description=args.description,
        dry_run=args.dry_run
    )

    print("\n" + "=" * 60)
    print("VOICESTUDIO ENGINE SCAFFOLD")
    print("=" * 60)

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  [ERROR] {error}")

    if result.files_created:
        print("\nFiles created:")
        for file in result.files_created:
            print(f"  [OK] {file}")

    if result.manual_steps:
        print("\nManual steps required:")
        for step in result.manual_steps:
            print(f"  {step}")

    print("\n" + "=" * 60)

    if result.success:
        print(f"[OK] Engine scaffold for '{args.name}' generated successfully!")
    else:
        print("[ERROR] Engine scaffold generation failed.")

    print("=" * 60 + "\n")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
