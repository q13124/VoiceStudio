"""
Integration tests for unified configuration loader.
Tests YAML, TOML, JSON support and validation.
"""

import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.config.config_loader import ConfigLoader, load_config, save_config


class TestConfigLoader:
    """Tests for unified configuration loader."""

    def test_json_loading(self):
        """Test loading JSON configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"test": "value", "number": 42}')
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = ConfigLoader(temp_path)
            config = loader.load(validate=False)
            assert config["test"] == "value"
            assert config["number"] == 42
        finally:
            temp_path.unlink()

    def test_yaml_loading(self):
        """Test loading YAML configuration."""
        pytest.importorskip("yaml")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("test: value\nnumber: 42")
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = ConfigLoader(temp_path)
            config = loader.load(validate=False)
            assert config["test"] == "value"
            assert config["number"] == 42
        finally:
            temp_path.unlink()

    def test_toml_loading(self):
        """Test loading TOML configuration."""
        pytest.importorskip("toml")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write('test = "value"\nnumber = 42')
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = ConfigLoader(temp_path)
            config = loader.load(validate=False)
            assert config["test"] == "value"
            assert config["number"] == 42
        finally:
            temp_path.unlink()

    def test_format_detection(self):
        """Test format detection from file extension."""
        loader_json = ConfigLoader("test.json")
        assert loader_json.detect_format() == "json"

        loader_yaml = ConfigLoader("test.yaml")
        assert loader_yaml.detect_format() == "yaml"

        loader_yml = ConfigLoader("test.yml")
        assert loader_yml.detect_format() == "yaml"

        loader_toml = ConfigLoader("test.toml")
        assert loader_toml.detect_format() == "toml"

    def test_get_set_dot_notation(self):
        """Test get/set with dot notation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"app": {"name": "VoiceStudio", "version": "1.0"}}')
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = ConfigLoader(temp_path)
            config = loader.load(validate=False)
            loader.config = config

            # Test get with dot notation
            assert loader.get("app.name") == "VoiceStudio"
            assert loader.get("app.version") == "1.0"
            assert loader.get("app.nonexistent", "default") == "default"

            # Test set with dot notation
            loader.set("app.new_key", "new_value")
            assert loader.get("app.new_key") == "new_value"
        finally:
            temp_path.unlink()

    def test_cerberus_validation(self):
        """Test Cerberus schema validation."""
        pytest.importorskip("cerberus")

        schema = {
            "name": {"type": "string", "required": True},
            "version": {"type": "string", "required": True},
            "enabled": {"type": "boolean", "default": True},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"name": "test", "version": "1.0", "enabled": true}')
            f.flush()
            temp_path = Path(f.name)

        try:
            loader = ConfigLoader(temp_path)
            config = loader.load(validate=True, schema=schema)
            assert config["name"] == "test"
        finally:
            temp_path.unlink()

    def test_save_json(self):
        """Test saving JSON configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = Path(f.name)

        try:
            config = {"test": "value", "number": 42}
            save_config(config, temp_path, format="json")

            loader = ConfigLoader(temp_path)
            loaded = loader.load(validate=False)
            assert loaded == config
        finally:
            temp_path.unlink()

    def test_save_yaml(self):
        """Test saving YAML configuration."""
        pytest.importorskip("yaml")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = Path(f.name)

        try:
            config = {"test": "value", "number": 42}
            save_config(config, temp_path, format="yaml")

            loader = ConfigLoader(temp_path)
            loaded = loader.load(validate=False)
            assert loaded == config
        finally:
            temp_path.unlink()

    def test_save_toml(self):
        """Test saving TOML configuration."""
        pytest.importorskip("toml")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            temp_path = Path(f.name)

        try:
            config = {"test": "value", "number": 42}
            save_config(config, temp_path, format="toml")

            loader = ConfigLoader(temp_path)
            loaded = loader.load(validate=False)
            assert loaded == config
        finally:
            temp_path.unlink()
