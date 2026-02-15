#!/usr/bin/env python3
"""
VoiceStudio Panel Scaffold Generator

Generates a new UI panel with View, ViewModel, code-behind, and test files
following VoiceStudio's MVVM patterns.

Usage:
    python tools/scaffolds/generate_panel.py --name QualityMonitor
    python tools/scaffolds/generate_panel.py --name QualityMonitor --region Center
    python tools/scaffolds/generate_panel.py --name QualityMonitor --description "Quality monitoring dashboard"

Generated files:
    - src/VoiceStudio.App/Views/Panels/{Name}View.xaml
    - src/VoiceStudio.App/Views/Panels/{Name}View.xaml.cs
    - src/VoiceStudio.App/ViewModels/{Name}ViewModel.cs
    - tests/ui/test_{name}.py

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


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def to_display_name(name: str) -> str:
    """Convert PascalCase to display name with spaces."""
    return re.sub(r'([A-Z])', r' \1', name).strip()


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


def generate_panel(
    name: str,
    region: str = "Center",
    description: str | None = None,
    project_root: Path | None = None,
    dry_run: bool = False
) -> ScaffoldResult:
    """
    Generate a new panel with all required files.

    Args:
        name: PascalCase name for the panel (e.g., "QualityMonitor")
        region: Panel region (Center, Left, Right, Bottom)
        description: Optional description for help text
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
    if not name[0].isupper():
        errors.append(f"Panel name must be PascalCase: {name}")
        return ScaffoldResult(False, files_created, errors, manual_steps)

    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', name):
        errors.append(f"Invalid panel name (use PascalCase, alphanumeric only): {name}")
        return ScaffoldResult(False, files_created, errors, manual_steps)

    # Validate region
    valid_regions = ["Center", "Left", "Right", "Bottom"]
    if region not in valid_regions:
        errors.append(f"Invalid region '{region}'. Must be one of: {', '.join(valid_regions)}")
        return ScaffoldResult(False, files_created, errors, manual_steps)

    # Prepare replacements
    snake_name = to_snake_case(name)
    display_name = to_display_name(name)
    panel_id = snake_name.replace("_", "-")

    if description is None:
        description = f"The {display_name} panel."

    replacements = {
        "NAME": name,
        "DISPLAY_NAME": display_name,
        "PANEL_ID": panel_id,
        "REGION": region,
        "DESCRIPTION": description,
        "DATE": datetime.now().strftime("%Y-%m-%d"),
    }

    # Define output paths
    views_dir = project_root / "src" / "VoiceStudio.App" / "Views" / "Panels"
    viewmodels_dir = project_root / "src" / "VoiceStudio.App" / "ViewModels"
    tests_dir = project_root / "tests" / "ui"

    output_files = [
        (views_dir / f"{name}View.xaml", "panel_view.xaml.template"),
        (views_dir / f"{name}View.xaml.cs", "panel_view.xaml.cs.template"),
        (viewmodels_dir / f"{name}ViewModel.cs", "panel_viewmodel.cs.template"),
        (tests_dir / f"test_{snake_name}.py", "panel_test.py.template"),
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
        "1. Register panel in PanelRegistry.cs or AdvancedPanelRegistrationService.cs:"
    )
    manual_steps.append(
        f"   _panels.Add(new PanelDescriptor(\"{panel_id}\", \"{display_name}\", typeof({name}View)));"
    )
    manual_steps.append("2. Build: dotnet build VoiceStudio.sln -c Debug -p:Platform=x64")
    manual_steps.append(f"3. Test: python -m pytest tests/ui/test_{snake_name}.py -v")
    manual_steps.append(f"4. Add resource string Panel.{name}.DisplayName to Resources.resw")

    success = len(errors) == 0
    return ScaffoldResult(success, files_created, errors, manual_steps)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a new VoiceStudio panel scaffold"
    )
    parser.add_argument(
        "--name", required=True,
        help="PascalCase name for the panel (e.g., QualityMonitor)"
    )
    parser.add_argument(
        "--region", default="Center",
        choices=["Center", "Left", "Right", "Bottom"],
        help="Panel region (default: Center)"
    )
    parser.add_argument(
        "--description",
        help="Description for help text"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be created without creating files"
    )

    args = parser.parse_args()

    result = generate_panel(
        name=args.name,
        region=args.region,
        description=args.description,
        dry_run=args.dry_run
    )

    print("\n" + "=" * 60)
    print("VOICESTUDIO PANEL SCAFFOLD")
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
        print(f"[OK] Panel scaffold for '{args.name}' generated successfully!")
    else:
        print("[ERROR] Panel scaffold generation failed.")

    print("=" * 60 + "\n")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
