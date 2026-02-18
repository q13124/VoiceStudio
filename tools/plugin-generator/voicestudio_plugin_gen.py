#!/usr/bin/env python3
"""
VoiceStudio Plugin Generator CLI

Interactive tool for scaffolding, validating, packaging, and managing plugins.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    import questionary
    HAS_QUESTIONARY = True
except ImportError:
    HAS_QUESTIONARY = False

try:
    from backend.services.plugin_schema_validator import PluginSchemaValidator
    HAS_SCHEMA_VALIDATOR = True
except ImportError:
    HAS_SCHEMA_VALIDATOR = False


class PluginGenerator:
    """Generate and manage VoiceStudio plugins."""
    
    TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates" / "plugins"
    PLUGINS_DIR = Path(__file__).parent.parent.parent / "plugins"
    SCHEMA_PATH = Path(__file__).parent.parent.parent / "shared" / "schemas" / "plugin-manifest.schema.json"
    
    TEMPLATE_TYPES = {
        "backend": "minimal-backend",
        "frontend": "minimal-frontend",
        "full-stack": "full-stack",
        "audio": "audio-effect",
        "audio-processor": "audio-effect-processor",
        "engine-adapter": "engine-adapter",
        "format-exporter": "format-exporter",
    }
    
    NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
    
    @staticmethod
    def validate_name(name: str) -> bool:
        """Validate plugin name format."""
        return bool(PluginGenerator.NAME_PATTERN.match(name))
    
    @staticmethod
    def interactive_prompt() -> Dict[str, str]:
        """Prompt user for plugin info interactively."""
        if not HAS_QUESTIONARY:
            return PluginGenerator.basic_prompt()
        
        answers = {
            'name': questionary.text(
                "Plugin name (lowercase, underscores):",
                validate=lambda x: PluginGenerator.validate_name(x) or "Invalid format"
            ).ask(),
            'display_name': questionary.text("Display name (human readable):").ask(),
            'author': questionary.text("Author name:").ask(),
            'description': questionary.text("Plugin description:").ask(),
            'version': questionary.text("Version (semantic):", default="1.0.0").ask(),
            'type': questionary.select(
                "Plugin type:",
                choices=['backend', 'frontend', 'full-stack', 'audio', 'audio-processor', 'engine-adapter', 'format-exporter']
            ).ask()
        }
        return answers
    
    @staticmethod
    def basic_prompt() -> Dict[str, str]:
        """Fallback prompt without questionary."""
        print("\nVoiceStudio Plugin Generator")
        print("=" * 40)
        
        while True:
            name = input("Plugin name (lowercase_with_underscores): ").strip()
            if PluginGenerator.validate_name(name):
                break
            print("Invalid format. Use lowercase letters, numbers, underscores only.")
        
        display_name = input("Display name: ").strip()
        author = input("Author name: ").strip()
        description = input("Description: ").strip()
        version = input("Version [1.0.0]: ").strip() or "1.0.0"
        
        print("\nPlugin types:")
        print("  1. backend    - Python backend plugin")
        print("  2. frontend   - C# WinUI frontend plugin")
        print("  3. full-stack - Python + C# plugin")
        print("  4. audio      - Audio processing plugin")
        print("  5. audio-processor - ProcessorPlugin-oriented audio template")
        print("  6. engine-adapter - Adapter template for existing engines")
        print("  7. format-exporter - Export plugin template using FFmpeg conversion")
        
        type_map = {
            "1": "backend",
            "2": "frontend",
            "3": "full-stack",
            "4": "audio",
            "5": "audio-processor",
            "6": "engine-adapter",
            "7": "format-exporter",
        }
        while True:
            choice = input("Choose type [1-7]: ").strip()
            if choice in type_map:
                ptype = type_map[choice]
                break
            print("Invalid choice. Enter 1-7.")
        
        return {
            'name': name,
            'display_name': display_name,
            'author': author,
            'description': description,
            'version': version,
            'type': ptype
        }
    
    @staticmethod
    def _replace_tokens(text: str, replacements: Dict[str, str]) -> str:
        """Replace template tokens in text."""
        for token, value in replacements.items():
            text = text.replace(token, value)
        return text

    @staticmethod
    def _rename_paths_with_tokens(output_dir: Path, replacements: Dict[str, str]) -> None:
        """
        Rename directories/files that still contain template tokens.

        Reverse sort ensures nested children are renamed before parents.
        """
        for path in sorted(output_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            new_name = PluginGenerator._replace_tokens(path.name, replacements)
            if new_name != path.name:
                path.rename(path.parent / new_name)

    @staticmethod
    def _rename_template_seed_paths(
        output_dir: Path,
        template_type: str,
        replacements: Dict[str, str],
    ) -> None:
        """Rename known seed paths that do not contain tokens in their names."""
        class_name = replacements.get("{{CLASS_NAME}}", "Plugin")
        desired_project_dir = f"{class_name}Plugin"
        desired_tests_dir = f"{class_name}Plugin.Tests"

        if template_type in {"frontend", "full-stack"}:
            sample_project = output_dir / "SamplePlugin"
            if sample_project.exists():
                sample_project.rename(output_dir / desired_project_dir)

        if template_type == "frontend":
            sample_tests = output_dir / "SamplePlugin.Tests"
            if sample_tests.exists():
                sample_tests.rename(output_dir / desired_tests_dir)

    @staticmethod
    def generate(output_dir: Path, template_type: str, replacements: Dict[str, str]) -> bool:
        """Generate plugin from template."""
        template_name = PluginGenerator.TEMPLATE_TYPES.get(template_type)
        if not template_name:
            print(f"ERROR: Unknown template type: {template_type}")
            return False
        
        template_path = PluginGenerator.TEMPLATES_DIR / template_name
        if not template_path.exists():
            print(f"ERROR: Template not found: {template_path}")
            return False
        
        if output_dir.exists():
            print(f"ERROR: Output directory already exists: {output_dir}")
            return False
        
        try:
            # Copy template
            shutil.copytree(template_path, output_dir)
            
            # Replace tokens in files
            for file_path in output_dir.rglob("*"):
                if file_path.is_file():
                    try:
                        content = file_path.read_text()
                        content = PluginGenerator._replace_tokens(content, replacements)
                        file_path.write_text(content)
                    except (UnicodeDecodeError, PermissionError):
                        pass  # Skip binary files

            # Replace tokens in directory and file names.
            PluginGenerator._rename_paths_with_tokens(output_dir, replacements)
            PluginGenerator._rename_template_seed_paths(output_dir, template_type, replacements)
            
            print(f"✓ Plugin generated at: {output_dir}")
            return True
        
        except Exception as e:
            print(f"ERROR: Failed to generate plugin: {e}")
            return False
    
    @staticmethod
    def validate(manifest_path: Path) -> bool:
        """Validate plugin manifest."""
        if not manifest_path.exists():
            print(f"ERROR: Manifest not found: {manifest_path}")
            return False
        
        try:
            if HAS_SCHEMA_VALIDATOR:
                validator = PluginSchemaValidator(schema_path=PluginGenerator.SCHEMA_PATH)
                is_valid, errors, manifest = validator.validate_file(manifest_path)
                if not is_valid:
                    for error in errors:
                        print(f"ERROR: {error}")
                    return False

                print(f"✓ Manifest valid: {manifest.get('name')} v{manifest.get('version')}")
                return True

            # Fallback validation when schema validator cannot be imported.
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)

            required = ["name", "version", "author", "plugin_type"]
            missing = [field for field in required if field not in manifest]
            if missing:
                for field in missing:
                    print(f"ERROR: Missing required field: {field}")
                return False

            print(
                "WARNING: Full schema validator unavailable; only basic checks were applied."
            )
            print(f"✓ Manifest valid (basic): {manifest['name']} v{manifest['version']}")
            return True
        
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in manifest: {e}")
            return False
        except Exception as e:
            print(f"ERROR: Validation failed: {e}")
            return False
    
    @staticmethod
    def test(plugin_path: Path) -> bool:
        """Run plugin tests."""
        tests_dir = plugin_path / "tests"
        if not tests_dir.exists():
            print("No tests directory found")
            return True
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(tests_dir), "-v"],
                cwd=plugin_path
            )
            return result.returncode == 0
        except Exception as e:
            print(f"ERROR: Failed to run tests: {e}")
            return False
    
    @staticmethod
    def package(plugin_path: Path, output_path: Optional[Path] = None) -> bool:
        """Package plugin as zip."""
        if not (plugin_path / "manifest.json").exists():
            print("ERROR: Plugin does not have manifest.json")
            return False
        
        if output_path is None:
            output_path = plugin_path.parent / f"{plugin_path.name}.zip"
        
        try:
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in plugin_path.rglob("*"):
                    if file_path.is_file() and not any(
                        part in file_path.parts for part in ['__pycache__', '.git', '.pytest_cache']
                    ):
                        arcname = file_path.relative_to(plugin_path.parent)
                        zf.write(file_path, arcname)
            
            print(f"✓ Plugin packaged: {output_path}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to package: {e}")
            return False
    
    @staticmethod
    def list_templates() -> None:
        """List available templates."""
        print("\nAvailable Templates:")
        print("=" * 40)
        for type_name, template_dir in PluginGenerator.TEMPLATE_TYPES.items():
            path = PluginGenerator.TEMPLATES_DIR / template_dir
            if path.exists():
                print(f"  {type_name:12} - {template_dir}")
    
    @staticmethod
    def info(plugin_path: Path) -> None:
        """Display plugin information."""
        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            print(f"ERROR: No manifest found at {manifest_path}")
            return
        
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)
            
            print(f"\nPlugin: {manifest.get('display_name', 'Unknown')}")
            print(f"  Name:     {manifest.get('name')}")
            print(f"  Version:  {manifest.get('version')}")
            print(f"  Author:   {manifest.get('author')}")
            print(f"  Type:     {manifest.get('plugin_type')}")
            print(f"  Desc:     {manifest.get('description')}")
        except Exception as e:
            print(f"ERROR: Failed to read manifest: {e}")


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="VoiceStudio Plugin Generator"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="VoiceStudio Plugin Generator 1.0.0",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate new plugin")
    gen_parser.add_argument("--name", help="Plugin name")
    gen_parser.add_argument(
        "--type",
        choices=["backend", "frontend", "full-stack", "audio", "audio-processor", "engine-adapter", "format-exporter"],
        help="Plugin type",
    )
    gen_parser.add_argument("--author", help="Author name")
    gen_parser.add_argument("--output", type=Path, help="Output directory")
    
    # Validate command
    val_parser = subparsers.add_parser("validate", help="Validate manifest")
    val_parser.add_argument("path", type=Path, help="Manifest path or plugin directory")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run plugin tests")
    test_parser.add_argument("path", type=Path, help="Plugin directory")
    
    # Package command
    pkg_parser = subparsers.add_parser("package", help="Package plugin")
    pkg_parser.add_argument("path", type=Path, help="Plugin directory")
    pkg_parser.add_argument("--output", type=Path, help="Output file")
    
    # List command
    subparsers.add_parser("list-templates", help="List templates")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show plugin info")
    info_parser.add_argument("path", type=Path, help="Plugin directory")
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == "generate":
        if args.name and args.type and args.author:
            # Non-interactive mode
            replacements = {
                "{{PLUGIN_NAME}}": args.name,
                "{{CLASS_NAME}}": args.name.replace("_", " ").title().replace(" ", ""),
                "{{DISPLAY_NAME}}": args.name.replace("_", " ").title(),
                "{{AUTHOR}}": args.author,
                "{{VERSION}}": "1.0.0",
                "{{DESCRIPTION}}": ""
            }
            output = args.output or PluginGenerator.PLUGINS_DIR / args.name
            return 0 if PluginGenerator.generate(output, args.type, replacements) else 1
        else:
            # Interactive mode
            info = PluginGenerator.interactive_prompt()
            replacements = {
                "{{PLUGIN_NAME}}": info['name'],
                "{{CLASS_NAME}}": info['name'].replace("_", " ").title().replace(" ", ""),
                "{{DISPLAY_NAME}}": info['display_name'],
                "{{AUTHOR}}": info['author'],
                "{{VERSION}}": info['version'],
                "{{DESCRIPTION}}": info['description']
            }
            output = PluginGenerator.PLUGINS_DIR / info['name']
            return 0 if PluginGenerator.generate(output, info['type'], replacements) else 1
    
    elif args.command == "validate":
        path = args.path / "manifest.json" if args.path.is_dir() else args.path
        return 0 if PluginGenerator.validate(path) else 1
    
    elif args.command == "test":
        return 0 if PluginGenerator.test(args.path) else 1
    
    elif args.command == "package":
        return 0 if PluginGenerator.package(args.path, args.output) else 1
    
    elif args.command == "list-templates":
        PluginGenerator.list_templates()
        return 0
    
    elif args.command == "info":
        PluginGenerator.info(args.path)
        return 0
    
    else:
        # Default: interactive generate
        info = PluginGenerator.interactive_prompt()
        replacements = {
            "{{PLUGIN_NAME}}": info['name'],
            "{{CLASS_NAME}}": info['name'].replace("_", " ").title().replace(" ", ""),
            "{{DISPLAY_NAME}}": info['display_name'],
            "{{AUTHOR}}": info['author'],
            "{{VERSION}}": info['version'],
            "{{DESCRIPTION}}": info['description']
        }
        output = PluginGenerator.PLUGINS_DIR / info['name']
        return 0 if PluginGenerator.generate(output, info['type'], replacements) else 1


if __name__ == "__main__":
    sys.exit(main())
