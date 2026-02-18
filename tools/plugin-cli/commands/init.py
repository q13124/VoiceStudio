"""
Plugin Init Command.

Initializes a new plugin project from a template.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import click

# Available templates
TEMPLATES = {
    "basic": "Basic plugin with minimal structure",
    "synthesis": "Text-to-speech synthesis plugin",
    "transcription": "Speech-to-text transcription plugin",
    "processing": "Audio processing plugin",
    "enhancement": "Voice enhancement plugin",
    "embedding": "Voice embedding extraction plugin",
    "diarization": "Speaker diarization plugin",
    "multilingual": "Multi-language support plugin",
}


# Map template names to functional categories
TEMPLATE_TO_CATEGORY = {
    "basic": "utilities",
    "synthesis": "voice_synthesis",
    "transcription": "speech_recognition",
    "processing": "audio_effects",
    "enhancement": "audio_effects",
    "embedding": "audio_analysis",
    "diarization": "speech_recognition",
    "multilingual": "utilities",
}


def get_template_manifest(name: str, template: str) -> Dict[str, Any]:
    """Generate a manifest for a new plugin (schema v4)."""
    category = TEMPLATE_TO_CATEGORY.get(template, "utilities")
    
    return {
        "$schema": "../shared/schemas/plugin-manifest.schema.json",
        "schema_version": "4.0",
        "id": f"com.voicestudio.{name.lower().replace('-', '_')}",
        "name": name,
        "version": "0.1.0",
        "description": f"A VoiceStudio {template} plugin",
        "author": {
            "name": "Your Name",
            "email": "your.email@example.com",
            "url": "",
        },
        "license": "MIT",
        "repository": "",
        "homepage": "",
        "engine": ">=0.15.0",
        "python": ">=3.9",
        "plugin_type": "backend_only",  # Architecture type
        "category": category,            # Functional category
        "capabilities": [],
        "dependencies": {
            "runtime": [],
            "optional": [],
            "python": [],
        },
        "distribution": {
            "published": False,
            "marketplace_url": "",
            "download_url": "",
            "changelog_url": "",
        },
        "catalog": {
            "tags": [],
            "featured": False,
            "verified": False,
        },
        "trust": {
            "signed": False,
            "signature_url": "",
            "checksum_algorithm": "sha256",
        },
        "security": {
            "sandboxed": True,
            "permissions": {
                "filesystem": {
                    "level": "read_only",
                    "paths": [],
                },
                "network": {
                    "level": "denied",
                    "allowed_hosts": [],
                },
                "subprocess": {
                    "level": "denied",
                },
                "audio": {
                    "level": "full",
                },
            },
        },
        "ui": {
            "has_settings": False,
            "settings_schema": None,
            "icon": "icon.png",
        },
    }


def get_template_main(name: str, template: str) -> str:
    """Generate main.py content for a new plugin."""
    class_name = "".join(word.capitalize() for word in name.replace("-", "_").split("_"))
    
    return f'''"""
{name} - A VoiceStudio {template} plugin.
"""

import logging
from typing import Any, Dict, Optional

from voicestudio_plugin_sdk import Plugin, PluginMetadata, capability

logger = logging.getLogger(__name__)


class {class_name}Plugin(Plugin):
    """
    {name} plugin implementation.
    
    This plugin provides {template} functionality for VoiceStudio.
    """
    
    def __init__(self, metadata: Optional[PluginMetadata] = None):
        """Initialize the plugin."""
        super().__init__(metadata)
        self._config: Dict[str, Any] = {{}}
    
    async def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the plugin with configuration.
        
        Args:
            config: Optional configuration dictionary.
        """
        await super().initialize(config)
        self._config = config or {{}}
        logger.info(f"{{self.name}} initialized with config: {{self._config}}")
    
    async def cleanup(self) -> None:
        """Clean up plugin resources."""
        logger.info(f"{{self.name}} cleaning up...")
        await super().cleanup()
    
    @capability("{template}")
    async def process(self, input_data: Any, **kwargs: Any) -> Any:
        """
        Process input data.
        
        Args:
            input_data: The input data to process.
            **kwargs: Additional keyword arguments.
        
        Returns:
            Processed output data.
        """
        logger.info(f"Processing with {{self.name}}")
        # TODO: Implement your {template} logic here
        return input_data


# Plugin entry point
def create_plugin() -> {class_name}Plugin:
    """Create and return the plugin instance."""
    return {class_name}Plugin()
'''


def get_template_readme(name: str, template: str) -> str:
    """Generate README.md content for a new plugin."""
    return f'''# {name}

A VoiceStudio {template} plugin.

## Installation

```bash
voicestudio-plugin pack .
voicestudio-plugin install {name.lower()}.vspkg
```

## Usage

After installation, the plugin will be available in VoiceStudio.

## Configuration

Configure the plugin through the VoiceStudio settings panel.

## Development

### Prerequisites

- Python 3.9+
- VoiceStudio Plugin SDK

### Setup

```bash
pip install -e .
```

### Testing

```bash
voicestudio-plugin test .
```

### Building

```bash
voicestudio-plugin pack .
```

## License

MIT License
'''


def get_template_test(name: str) -> str:
    """Generate test file content."""
    class_name = "".join(word.capitalize() for word in name.replace("-", "_").split("_"))
    module_name = name.lower().replace("-", "_")
    
    return f'''"""
Tests for {name} plugin.
"""

import pytest
from {module_name}.main import {class_name}Plugin, create_plugin


class Test{class_name}Plugin:
    """Test suite for {class_name}Plugin."""
    
    @pytest.fixture
    def plugin(self):
        """Create a plugin instance for testing."""
        return create_plugin()
    
    @pytest.mark.asyncio
    async def test_initialize(self, plugin):
        """Test plugin initialization."""
        await plugin.initialize({{}})
        assert plugin.initialized
    
    @pytest.mark.asyncio
    async def test_cleanup(self, plugin):
        """Test plugin cleanup."""
        await plugin.initialize()
        await plugin.cleanup()
        assert not plugin.initialized
    
    @pytest.mark.asyncio
    async def test_process(self, plugin):
        """Test plugin processing."""
        await plugin.initialize()
        result = await plugin.process("test input")
        assert result is not None
        await plugin.cleanup()
'''


def get_template_setup_py(name: str) -> str:
    """Generate setup.py content."""
    module_name = name.lower().replace("-", "_")
    
    return f'''"""
Setup configuration for {name} plugin.
"""

from setuptools import setup, find_packages

setup(
    name="{name}",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "voicestudio-plugin-sdk>=1.0.0",
    ],
    extras_require={{
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    }},
    python_requires=">=3.9",
    entry_points={{
        "voicestudio.plugins": [
            "{module_name}={module_name}.main:create_plugin",
        ],
    }},
)
'''


def get_template_pyproject(name: str) -> str:
    """Generate pyproject.toml content."""
    module_name = name.lower().replace("-", "_")
    
    return f'''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{name}"
version = "0.1.0"
description = "A VoiceStudio plugin"
readme = "README.md"
requires-python = ">=3.9"
license = {{text = "MIT"}}
authors = [
    {{name = "Your Name", email = "your.email@example.com"}}
]
dependencies = [
    "voicestudio-plugin-sdk>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.0.0",
]

[project.entry-points."voicestudio.plugins"]
{module_name} = "{module_name}.main:create_plugin"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
'''


@click.command("init")
@click.argument("name")
@click.option(
    "-t", "--template",
    type=click.Choice(list(TEMPLATES.keys())),
    default="basic",
    help="Plugin template to use.",
)
@click.option(
    "-o", "--output",
    type=click.Path(),
    default=None,
    help="Output directory (defaults to current directory).",
)
@click.option(
    "--no-git",
    is_flag=True,
    help="Skip git repository initialization.",
)
@click.pass_context
def init_command(
    ctx: click.Context,
    name: str,
    template: str,
    output: Optional[str],
    no_git: bool,
) -> None:
    """
    Initialize a new plugin project.
    
    Creates a new plugin project with the specified NAME using
    the chosen template. The project includes a manifest, main
    module, tests, and configuration files.
    
    Examples:
    
        voicestudio-plugin init my-plugin
        
        voicestudio-plugin init my-tts-plugin --template=synthesis
        
        voicestudio-plugin init my-plugin --output=/path/to/plugins
    """
    verbose = ctx.obj.get("verbose", False)
    quiet = ctx.obj.get("quiet", False)
    
    # Determine output directory
    base_dir = Path(output) if output else Path.cwd()
    plugin_dir = base_dir / name.lower().replace(" ", "-")
    module_name = name.lower().replace("-", "_").replace(" ", "_")
    
    if plugin_dir.exists():
        raise click.ClickException(f"Directory already exists: {plugin_dir}")
    
    if not quiet:
        click.echo(f"Creating plugin '{name}' with template '{template}'...")
    
    try:
        # Create directory structure
        plugin_dir.mkdir(parents=True)
        (plugin_dir / module_name).mkdir()
        (plugin_dir / "tests").mkdir()
        
        # Create manifest
        manifest = get_template_manifest(name, template)
        manifest_path = plugin_dir / "plugin.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        if verbose:
            click.echo(f"  Created: {manifest_path}")
        
        # Create main module
        init_path = plugin_dir / module_name / "__init__.py"
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(f'"""\\n{name} plugin.\\n"""\\n\\nfrom .main import create_plugin\\n\\n__all__ = ["create_plugin"]\\n')
        if verbose:
            click.echo(f"  Created: {init_path}")
        
        main_path = plugin_dir / module_name / "main.py"
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(get_template_main(name, template))
        if verbose:
            click.echo(f"  Created: {main_path}")
        
        # Create README
        readme_path = plugin_dir / "README.md"
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(get_template_readme(name, template))
        if verbose:
            click.echo(f"  Created: {readme_path}")
        
        # Create tests
        test_init_path = plugin_dir / "tests" / "__init__.py"
        with open(test_init_path, "w", encoding="utf-8") as f:
            f.write("")
        
        test_path = plugin_dir / "tests" / f"test_{module_name}.py"
        with open(test_path, "w", encoding="utf-8") as f:
            f.write(get_template_test(name))
        if verbose:
            click.echo(f"  Created: {test_path}")
        
        # Create setup.py
        setup_path = plugin_dir / "setup.py"
        with open(setup_path, "w", encoding="utf-8") as f:
            f.write(get_template_setup_py(name))
        if verbose:
            click.echo(f"  Created: {setup_path}")
        
        # Create pyproject.toml
        pyproject_path = plugin_dir / "pyproject.toml"
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(get_template_pyproject(name))
        if verbose:
            click.echo(f"  Created: {pyproject_path}")
        
        # Create icon placeholder
        icon_path = plugin_dir / "icon.png"
        # Create a minimal placeholder (empty file, user should replace)
        icon_path.touch()
        if verbose:
            click.echo(f"  Created: {icon_path} (placeholder)")
        
        # Create .gitignore
        gitignore_path = plugin_dir / ".gitignore"
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("""# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# VoiceStudio plugin artifacts
*.vspkg
*.sig
.plugin-cache/
""")
        if verbose:
            click.echo(f"  Created: {gitignore_path}")
        
        # Initialize git repository
        if not no_git:
            try:
                import subprocess
                subprocess.run(
                    ["git", "init"],
                    cwd=plugin_dir,
                    capture_output=True,
                    check=True,
                )
                if verbose:
                    click.echo("  Initialized git repository")
            except (subprocess.CalledProcessError, FileNotFoundError):
                if verbose:
                    click.echo("  Warning: Could not initialize git repository")
        
        if not quiet:
            click.echo(click.style(f"\nSuccess! Created plugin at: {plugin_dir}", fg="green"))
            click.echo("\nNext steps:")
            click.echo(f"  cd {plugin_dir}")
            click.echo("  pip install -e .[dev]")
            click.echo("  voicestudio-plugin validate .")
            click.echo("  voicestudio-plugin test .")
        
    except Exception as e:
        # Clean up on failure
        if plugin_dir.exists():
            import shutil
            shutil.rmtree(plugin_dir)
        raise click.ClickException(f"Failed to create plugin: {e}")
