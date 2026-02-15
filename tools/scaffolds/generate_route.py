#!/usr/bin/env python3
"""
VoiceStudio Route Scaffold Generator

Generates a new FastAPI route with router, Pydantic models, and test files
following VoiceStudio's backend patterns.

Usage:
    python tools/scaffolds/generate_route.py --name quality_metrics
    python tools/scaffolds/generate_route.py --name quality_metrics --methods GET,POST,DELETE

Generated files:
    - backend/api/routes/{name}.py
    - backend/api/models/{name}_models.py
    - tests/unit/backend/api/routes/test_{name}.py

Part of the Claude Recommendations Integration (Phase 2).
"""

from __future__ import annotations

import argparse
import re
import sys
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


def generate_route(
    name: str,
    methods: list[str] | None = None,
    project_root: Path | None = None,
    dry_run: bool = False
) -> ScaffoldResult:
    """
    Generate a new API route with all required files.

    Args:
        name: snake_case name for the route (e.g., "quality_metrics")
        methods: HTTP methods to include (default: GET, POST)
        project_root: Project root directory
        dry_run: If True, don't create files, just report what would be created

    Returns:
        ScaffoldResult with created files and any errors
    """
    if project_root is None:
        project_root = find_project_root()

    if methods is None:
        methods = ["GET", "POST"]

    errors: list[str] = []
    files_created: list[str] = []
    manual_steps: list[str] = []

    # Validate name
    if not re.match(r'^[a-z][a-z0-9_]*$', name):
        errors.append(f"Invalid route name (use snake_case): {name}")
        return ScaffoldResult(False, files_created, errors, manual_steps)

    # Prepare replacements
    pascal_name = to_pascal_case(name)
    display_name = to_display_name(name)
    route_path = name.replace("_", "-")

    replacements = {
        "NAME": pascal_name,
        "SNAKE_NAME": name,
        "DISPLAY_NAME": display_name,
        "ROUTE_PATH": route_path,
    }

    # Define output paths
    routes_dir = project_root / "backend" / "api" / "routes"
    models_dir = project_root / "backend" / "api" / "models"
    tests_dir = project_root / "tests" / "unit" / "backend" / "api" / "routes"

    output_files = [
        (routes_dir / f"{name}.py", "route_router.py.template"),
        (models_dir / f"{name}_models.py", "route_models.py.template"),
        (tests_dir / f"test_{name}.py", "route_test.py.template"),
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
        "1. Register router in backend/api/main.py:"
    )
    manual_steps.append(
        f"   from backend.api.routes.{name} import router as {name}_router"
    )
    manual_steps.append(
        f"   app.include_router({name}_router)"
    )
    manual_steps.append(f"2. Test: python -m pytest tests/unit/backend/api/routes/test_{name}.py -v")
    manual_steps.append(f"3. Start backend and test endpoint: curl http://localhost:8001/api/{route_path}")

    success = len(errors) == 0
    return ScaffoldResult(success, files_created, errors, manual_steps)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a new VoiceStudio API route scaffold"
    )
    parser.add_argument(
        "--name", required=True,
        help="snake_case name for the route (e.g., quality_metrics)"
    )
    parser.add_argument(
        "--methods", default="GET,POST",
        help="Comma-separated HTTP methods (default: GET,POST)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be created without creating files"
    )

    args = parser.parse_args()

    methods = [m.strip().upper() for m in args.methods.split(",")]

    result = generate_route(
        name=args.name,
        methods=methods,
        dry_run=args.dry_run
    )

    print("\n" + "=" * 60)
    print("VOICESTUDIO ROUTE SCAFFOLD")
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
        print(f"[OK] Route scaffold for '{args.name}' generated successfully!")
    else:
        print("[ERROR] Route scaffold generation failed.")

    print("=" * 60 + "\n")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
