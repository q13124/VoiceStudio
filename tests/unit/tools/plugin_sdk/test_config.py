"""
Unit tests for the config module.
"""

import os
import sys

import pytest

# Add SDK to path for testing
sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "tools", "plugin-sdk")
)

from voicestudio_sdk.config import ConfigField, ConfigType, PluginConfig


class TestConfigType:
    """Tests for ConfigType enum."""

    def test_config_types_exist(self):
        """Test that all expected config types exist."""
        assert ConfigType.STRING
        assert ConfigType.INTEGER
        assert ConfigType.FLOAT
        assert ConfigType.BOOLEAN
        assert ConfigType.SELECT
        assert ConfigType.MULTISELECT
        assert ConfigType.FILE
        assert ConfigType.DIRECTORY
        assert ConfigType.COLOR
        assert ConfigType.PASSWORD


class TestConfigField:
    """Tests for ConfigField class."""

    def test_create_string_field(self):
        """Test creating a string config field."""
        field = ConfigField(
            name="api_key",
            label="API Key",
            type=ConfigType.STRING,
            default="",
        )

        assert field.name == "api_key"
        assert field.label == "API Key"
        assert field.type == ConfigType.STRING
        assert field.default == ""

    def test_create_integer_field_with_range(self):
        """Test creating an integer field with min/max."""
        field = ConfigField(
            name="count",
            label="Count",
            type=ConfigType.INTEGER,
            default=10,
            min_value=1,
            max_value=100,
        )

        assert field.min_value == 1
        assert field.max_value == 100
        assert field.default == 10

    def test_create_float_field(self):
        """Test creating a float field."""
        field = ConfigField(
            name="speed",
            label="Speech Speed",
            type=ConfigType.FLOAT,
            default=1.0,
            min_value=0.5,
            max_value=2.0,
        )

        assert field.type == ConfigType.FLOAT
        assert field.default == 1.0

    def test_create_boolean_field(self):
        """Test creating a boolean field."""
        field = ConfigField(
            name="enabled",
            label="Enable Feature",
            type=ConfigType.BOOLEAN,
            default=True,
        )

        assert field.type == ConfigType.BOOLEAN
        assert field.default is True

    def test_create_select_field(self):
        """Test creating a select field with options."""
        field = ConfigField(
            name="voice",
            label="Voice",
            type=ConfigType.SELECT,
            default="default",
            options=["default", "female", "male"],
        )

        assert field.type == ConfigType.SELECT
        assert field.options == ["default", "female", "male"]

    def test_create_file_field(self):
        """Test creating a file field."""
        field = ConfigField(
            name="model_path",
            label="Model File",
            type=ConfigType.FILE,
            default="",
            file_types=[".pt", ".pth", ".bin"],
        )

        assert field.type == ConfigType.FILE
        assert field.file_types == [".pt", ".pth", ".bin"]

    def test_validate_string_field(self):
        """Test validating string values."""
        field = ConfigField(
            name="text",
            label="Text",
            type=ConfigType.STRING,
            default="",
        )

        assert field.validate("hello") is True
        assert field.validate("") is True
        assert field.validate(123) is False  # Wrong type

    def test_validate_integer_range(self):
        """Test validating integer values in range."""
        field = ConfigField(
            name="count",
            label="Count",
            type=ConfigType.INTEGER,
            default=10,
            min_value=1,
            max_value=100,
        )

        assert field.validate(50) is True
        assert field.validate(1) is True
        assert field.validate(100) is True
        assert field.validate(0) is False  # Below min
        assert field.validate(101) is False  # Above max

    def test_validate_float_range(self):
        """Test validating float values in range."""
        field = ConfigField(
            name="speed",
            label="Speed",
            type=ConfigType.FLOAT,
            default=1.0,
            min_value=0.5,
            max_value=2.0,
        )

        assert field.validate(1.5) is True
        assert field.validate(0.5) is True
        assert field.validate(2.0) is True
        assert field.validate(0.4) is False  # Below min
        assert field.validate(2.1) is False  # Above max

    def test_validate_select_options(self):
        """Test validating select values against options."""
        field = ConfigField(
            name="voice",
            label="Voice",
            type=ConfigType.SELECT,
            default="default",
            options=["default", "female", "male"],
        )

        assert field.validate("default") is True
        assert field.validate("female") is True
        assert field.validate("invalid") is False  # Not in options

    def test_validate_boolean(self):
        """Test validating boolean values."""
        field = ConfigField(
            name="enabled",
            label="Enabled",
            type=ConfigType.BOOLEAN,
            default=True,
        )

        assert field.validate(True) is True
        assert field.validate(False) is True
        assert field.validate("true") is False  # String, not boolean

    def test_validate_with_custom_validator(self):
        """Test validating with custom validator function."""

        def validate_email(value):
            return isinstance(value, str) and "@" in value

        field = ConfigField(
            name="email",
            label="Email",
            type=ConfigType.STRING,
            default="",
            validator=validate_email,
        )

        assert field.validate("test@example.com") is True
        assert field.validate("invalid") is False

    def test_to_dict(self):
        """Test converting field to dictionary."""
        field = ConfigField(
            name="speed",
            label="Speed",
            type=ConfigType.FLOAT,
            default=1.0,
            min_value=0.5,
            max_value=2.0,
            description="Speech speed multiplier",
        )

        data = field.to_dict()

        assert data["name"] == "speed"
        assert data["label"] == "Speed"
        assert data["type"] == "float"
        assert data["default"] == 1.0
        assert data["min_value"] == 0.5
        assert data["max_value"] == 2.0
        assert data["description"] == "Speech speed multiplier"


class TestPluginConfig:
    """Tests for PluginConfig class."""

    def test_create_empty_config(self):
        """Test creating empty config."""
        config = PluginConfig()
        assert config.fields == []

    def test_add_field(self):
        """Test adding a field to config."""
        config = PluginConfig()

        field = ConfigField(
            name="test",
            label="Test",
            type=ConfigType.STRING,
            default="",
        )

        config.add_field(field)

        assert len(config.fields) == 1
        assert config.fields[0].name == "test"

    def test_add_multiple_fields(self):
        """Test adding multiple fields."""
        config = PluginConfig()

        config.add_field(
            ConfigField(
                name="field1",
                label="Field 1",
                type=ConfigType.STRING,
                default="",
            )
        )
        config.add_field(
            ConfigField(
                name="field2",
                label="Field 2",
                type=ConfigType.INTEGER,
                default=0,
            )
        )

        assert len(config.fields) == 2

    def test_get_field(self):
        """Test getting a field by name."""
        config = PluginConfig()

        config.add_field(
            ConfigField(
                name="test",
                label="Test",
                type=ConfigType.STRING,
                default="",
            )
        )

        field = config.get_field("test")
        assert field is not None
        assert field.name == "test"

        assert config.get_field("nonexistent") is None

    def test_apply_defaults(self):
        """Test applying default values."""
        config = PluginConfig()

        config.add_field(
            ConfigField(
                name="name",
                label="Name",
                type=ConfigType.STRING,
                default="default_name",
            )
        )
        config.add_field(
            ConfigField(
                name="count",
                label="Count",
                type=ConfigType.INTEGER,
                default=10,
            )
        )

        defaults = config.get_defaults()

        assert defaults["name"] == "default_name"
        assert defaults["count"] == 10

    def test_validate_config(self):
        """Test validating user configuration."""
        config = PluginConfig()

        config.add_field(
            ConfigField(
                name="speed",
                label="Speed",
                type=ConfigType.FLOAT,
                default=1.0,
                min_value=0.5,
                max_value=2.0,
            )
        )
        config.add_field(
            ConfigField(
                name="voice",
                label="Voice",
                type=ConfigType.SELECT,
                default="default",
                options=["default", "female", "male"],
            )
        )

        # Valid config
        assert config.validate({"speed": 1.5, "voice": "female"}) is True

        # Invalid speed
        assert config.validate({"speed": 3.0, "voice": "female"}) is False

        # Invalid voice
        assert config.validate({"speed": 1.0, "voice": "invalid"}) is False

    def test_validate_partial_config(self):
        """Test validating config with missing fields."""
        config = PluginConfig()

        config.add_field(
            ConfigField(
                name="required_field",
                label="Required",
                type=ConfigType.STRING,
                default="",
                required=True,
            )
        )

        # Missing required field should fail if value is empty
        # Note: actual validation logic depends on implementation
        pass  # Placeholder for required field validation

    def test_to_schema(self):
        """Test generating UI schema."""
        config = PluginConfig()

        config.add_field(
            ConfigField(
                name="speed",
                label="Speed",
                type=ConfigType.FLOAT,
                default=1.0,
                min_value=0.5,
                max_value=2.0,
            )
        )

        schema = config.to_schema()

        assert "fields" in schema
        assert len(schema["fields"]) == 1
        assert schema["fields"][0]["name"] == "speed"

    def test_merge_with_defaults(self):
        """Test merging user config with defaults."""
        config = PluginConfig()

        config.add_field(
            ConfigField(
                name="field1",
                label="Field 1",
                type=ConfigType.STRING,
                default="default1",
            )
        )
        config.add_field(
            ConfigField(
                name="field2",
                label="Field 2",
                type=ConfigType.INTEGER,
                default=10,
            )
        )

        user_config = {"field1": "custom"}

        merged = config.merge_with_defaults(user_config)

        assert merged["field1"] == "custom"
        assert merged["field2"] == 10  # Default value
