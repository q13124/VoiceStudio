"""
SDK CLI utilities.

Provides commands for generating TypedDicts, validating manifests,
and other SDK development tasks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def generate_types(output: str | None = None) -> None:
    """Generate TypedDict definitions from protocol spec."""
    try:
        from backend.plugins.sdk import SDKGenerator, get_protocol_spec

        spec = get_protocol_spec()
        gen = SDKGenerator(spec)
        result = gen.generate_typed_dicts()

        if output:
            Path(output).write_text(result, encoding="utf-8")
            print(f"Generated types to {output}")
        else:
            print(result)

    except ImportError:
        print("Error: Cannot import protocol spec. Ensure you're running from VoiceStudio root.")
        sys.exit(1)


def generate_client(output: str | None = None) -> None:
    """Generate client stubs from protocol spec."""
    try:
        from backend.plugins.sdk import SDKGenerator, get_protocol_spec

        spec = get_protocol_spec()
        gen = SDKGenerator(spec)
        result = gen.generate_client_stubs()

        if output:
            Path(output).write_text(result, encoding="utf-8")
            print(f"Generated client to {output}")
        else:
            print(result)

    except ImportError:
        print("Error: Cannot import protocol spec. Ensure you're running from VoiceStudio root.")
        sys.exit(1)


def validate_manifest(path: str) -> bool:
    """Validate a plugin manifest file."""
    from .manifest import PluginManifest

    try:
        manifest = PluginManifest.from_file(path)
        print(f"Valid manifest: {manifest.name} v{manifest.version}")
        print(f"  ID: {manifest.id}")
        print(f"  Capabilities: {len(manifest.capabilities)}")
        print(f"  Permissions: {len(manifest.permissions)}")
        return True

    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False

    except KeyError as e:
        print(f"Missing required field: {e}")
        return False

    except Exception as e:
        print(f"Validation error: {e}")
        return False


def init_plugin(name: str, output_dir: str = ".") -> None:
    """Initialize a new plugin project."""
    from .manifest import Capability, PluginManifest

    output_path = Path(output_dir) / name
    output_path.mkdir(parents=True, exist_ok=True)

    # Create manifest
    manifest = PluginManifest(
        id=name,
        name=name.replace("-", " ").title(),
        version="0.1.0",
        description="A VoiceStudio plugin",
        author="Your Name",
        capabilities=[
            Capability(
                name="example",
                description="An example capability",
            )
        ],
    )

    manifest_path = output_path / "plugin.json"
    manifest.save(str(manifest_path))
    print(f"Created {manifest_path}")

    # Create main.py
    main_content = '''"""
{name} plugin for VoiceStudio.
"""

from voicestudio_plugin_sdk import Plugin, PluginManifest, Capability


class {class_name}(Plugin):
    """Plugin implementation."""

    manifest = PluginManifest.from_file("plugin.json")

    async def on_initialize(self, config: dict) -> None:
        """Initialize the plugin."""
        self.log.info("Plugin initializing...")

    async def on_invoke(self, capability: str, params: dict) -> dict:
        """Handle capability invocations."""
        if capability == "example":
            return {{"message": "Hello from {name}!"}}

        raise ValueError(f"Unknown capability: {{capability}}")


if __name__ == "__main__":
    plugin = {class_name}()
    plugin.run()
'''.format(
        name=name,
        class_name=name.replace("-", "").title().replace(" ", "") + "Plugin",
    )

    main_path = output_path / "main.py"
    main_path.write_text(main_content, encoding="utf-8")
    print(f"Created {main_path}")

    # Create README
    readme_content = f"""# {name}

A VoiceStudio plugin.

## Installation

```bash
voicestudio-plugin install .
```

## Development

```bash
# Run directly for testing
python main.py
```
"""

    readme_path = output_path / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")
    print(f"Created {readme_path}")

    print(f"\nPlugin initialized at {output_path}")
    print("Next steps:")
    print(f"  1. cd {output_path}")
    print("  2. Edit plugin.json to customize your plugin")
    print("  3. Implement capabilities in main.py")


def main() -> None:
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="VoiceStudio Plugin SDK utilities"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a new plugin")
    init_parser.add_argument("name", help="Plugin name")
    init_parser.add_argument(
        "-o", "--output", default=".", help="Output directory"
    )

    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a plugin manifest"
    )
    validate_parser.add_argument("path", help="Path to plugin.json")

    # generate-types command
    gen_types_parser = subparsers.add_parser(
        "generate-types", help="Generate TypedDict definitions"
    )
    gen_types_parser.add_argument(
        "-o", "--output", help="Output file path"
    )

    # generate-client command
    gen_client_parser = subparsers.add_parser(
        "generate-client", help="Generate client stubs"
    )
    gen_client_parser.add_argument(
        "-o", "--output", help="Output file path"
    )

    # Parse args
    args = parser.parse_args()

    if args.command == "init":
        init_plugin(args.name, args.output)
    elif args.command == "validate":
        success = validate_manifest(args.path)
        sys.exit(0 if success else 1)
    elif args.command == "generate-types":
        generate_types(args.output)
    elif args.command == "generate-client":
        generate_client(args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
