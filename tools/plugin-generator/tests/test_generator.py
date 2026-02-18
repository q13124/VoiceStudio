"""Tests for Plugin Generator"""
import json
import tempfile
from pathlib import Path

import pytest
from voicestudio_plugin_gen import PluginGenerator


def test_validate_name_valid():
    assert PluginGenerator.validate_name("my_plugin")
    assert PluginGenerator.validate_name("plugin123")
    assert PluginGenerator.validate_name("a")

def test_validate_name_invalid():
    assert not PluginGenerator.validate_name("My-Plugin")
    assert not PluginGenerator.validate_name("123_plugin")
    assert not PluginGenerator.validate_name("plugin ")

def test_generate_backend_plugin():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "test_plugin"
        replacements = {
            "{{PLUGIN_NAME}}": "test_plugin",
            "{{CLASS_NAME}}": "TestPlugin",
            "{{DISPLAY_NAME}}": "Test Plugin",
            "{{AUTHOR}}": "Test Author",
            "{{VERSION}}": "1.0.0",
            "{{DESCRIPTION}}": "Test plugin"
        }
        
        result = PluginGenerator.generate(output_dir, "backend", replacements)
        
        assert result
        assert (output_dir / "manifest.json").exists()
        assert (output_dir / "plugin.py").exists()
        assert (output_dir / "tests").exists()


def test_generate_frontend_renames_tokenized_paths():
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "ui_plugin"
        replacements = {
            "{{PLUGIN_NAME}}": "ui_plugin",
            "{{CLASS_NAME}}": "UiPlugin",
            "{{DISPLAY_NAME}}": "UI Plugin",
            "{{AUTHOR}}": "Test Author",
            "{{VERSION}}": "1.0.0",
            "{{DESCRIPTION}}": "Frontend test plugin",
        }

        result = PluginGenerator.generate(output_dir, "frontend", replacements)

        assert result
        assert (output_dir / "UiPluginPlugin").exists()
        assert (output_dir / "UiPluginPlugin.Tests").exists()
        assert (output_dir / "UiPluginPlugin" / "UiPluginPlugin.csproj").exists()

def test_validate_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest_path = Path(tmpdir) / "manifest.json"
        manifest = {
            "name": "test",
            "version": "1.0.0",
            "author": "Test",
            "plugin_type": "backend_only",
            "entry_points": {"backend": "plugin.register"}
        }
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f)
        
        result = PluginGenerator.validate(manifest_path)
        assert result

def test_validate_invalid_manifest():
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest_path = Path(tmpdir) / "manifest.json"
        manifest_path.write_text("{invalid json")
        
        result = PluginGenerator.validate(manifest_path)
        assert not result
