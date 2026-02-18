"""
Configuration utilities for VoiceStudio plugins.

Provides typed configuration management with validation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Generic, Optional, TypeVar, Union

T = TypeVar("T")


class ConfigType(str, Enum):
    """Configuration field types."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"
    FILE = "file"
    FILE_PATH = "file_path"  # Alias for FILE
    DIRECTORY = "directory"
    DIRECTORY_PATH = "directory_path"  # Alias for DIRECTORY
    COLOR = "color"
    SLIDER = "slider"
    PASSWORD = "password"


@dataclass
class ConfigField(Generic[T]):
    """
    A typed configuration field definition.

    Example:
        volume = ConfigField(
            name="volume",
            label="Output Volume",
            type=ConfigType.SLIDER,
            default=1.0,
            min_value=0.0,
            max_value=2.0,
            description="Adjust the output volume level"
        )
    """

    name: str
    label: str
    type: ConfigType
    default: T
    description: str = ""
    required: bool = False

    # For numeric types
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    step: Optional[Union[int, float]] = None

    # For select types - can be list of strings or list of dicts
    options: list[Any] = field(default_factory=list)

    # For file/directory paths
    file_types: list[str] = field(default_factory=list)

    # Validation
    validator: Optional[Callable[[Any], bool]] = None

    def validate(self, value: Any) -> bool:
        """
        Validate a value against this field's constraints.

        Args:
            value: The value to validate.

        Returns:
            True if valid, False otherwise.
        """
        if value is None:
            return not self.required

        # Type checking
        if self.type == ConfigType.STRING:
            if not isinstance(value, str):
                return False
        elif self.type == ConfigType.INTEGER:
            if not isinstance(value, int) or isinstance(value, bool):
                return False
        elif self.type == ConfigType.FLOAT:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False
        elif self.type == ConfigType.BOOLEAN:
            if not isinstance(value, bool):
                return False
        elif self.type in (ConfigType.SELECT, ConfigType.MULTISELECT):
            # Handle both string options and dict options
            valid_values = []
            for opt in self.options:
                if isinstance(opt, dict):
                    valid_values.append(opt.get("value"))
                else:
                    valid_values.append(opt)

            if self.type == ConfigType.SELECT:
                if value not in valid_values:
                    return False
            else:
                if not isinstance(value, list):
                    return False
                if not all(v in valid_values for v in value):
                    return False

        # Range checking
        if self.type in (ConfigType.INTEGER, ConfigType.FLOAT, ConfigType.SLIDER):
            if self.min_value is not None and value < self.min_value:
                return False
            if self.max_value is not None and value > self.max_value:
                return False

        # Custom validation
        return not (self.validator is not None and not self.validator(value))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for manifest serialization."""
        result = {
            "name": self.name,
            "label": self.label,
            "type": self.type.value,
            "default": self.default,
            "required": self.required,
        }

        if self.description:
            result["description"] = self.description

        if self.min_value is not None:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value
        if self.step is not None:
            result["step"] = self.step

        if self.options:
            result["options"] = self.options

        if self.file_types:
            result["fileTypes"] = self.file_types

        return result


class PluginConfig:
    """
    Plugin configuration manager.

    Provides typed access to plugin configuration values with validation.

    Can be used in two ways:

    1. Declarative (class-based):
        class MyPluginConfig(PluginConfig):
            volume = ConfigField(
                name="volume",
                label="Volume",
                type=ConfigType.SLIDER,
                default=1.0,
                min_value=0.0,
                max_value=2.0
            )

        config = MyPluginConfig({"volume": 0.8})
        print(config.volume)  # 0.8

    2. Imperative (instance-based):
        config = PluginConfig()
        config.add_field(ConfigField(
            name="volume",
            label="Volume",
            type=ConfigType.FLOAT,
            default=1.0,
        ))
    """

    def __init__(self, values: Optional[dict[str, Any]] = None) -> None:
        """
        Initialize configuration with values.

        Args:
            values: Configuration values dictionary.
        """
        self._values = values or {}
        self._instance_fields: list[ConfigField] = []
        self._fields_map: dict[str, ConfigField] = {}

        # Collect class-level fields
        self._collect_class_fields()
        self._apply_defaults()

    def _collect_class_fields(self) -> None:
        """Collect all ConfigField definitions from the class."""
        for name in dir(self.__class__):
            if name.startswith("_"):
                continue
            value = getattr(self.__class__, name, None)
            if isinstance(value, ConfigField):
                self._fields_map[value.name] = value

    @property
    def fields(self) -> list[ConfigField]:
        """Get all configuration fields."""
        # Combine class-level and instance-level fields
        all_fields = list(self._fields_map.values())
        return all_fields

    def add_field(self, field: ConfigField) -> None:
        """
        Add a configuration field.

        Args:
            field: The field to add.
        """
        self._instance_fields.append(field)
        self._fields_map[field.name] = field
        # Apply default if not set
        if field.name not in self._values:
            self._values[field.name] = field.default

    def get_field(self, name: str) -> Optional[ConfigField]:
        """
        Get a field by name.

        Args:
            name: Field name.

        Returns:
            The field or None if not found.
        """
        return self._fields_map.get(name)

    def _apply_defaults(self) -> None:
        """Apply default values for missing configuration."""
        for name, field in self._fields_map.items():
            if name not in self._values:
                self._values[name] = field.default

    def get_defaults(self) -> dict[str, Any]:
        """
        Get default values for all fields.

        Returns:
            Dictionary of field names to default values.
        """
        return {field.name: field.default for field in self.fields}

    def merge_with_defaults(self, user_config: dict[str, Any]) -> dict[str, Any]:
        """
        Merge user configuration with defaults.

        Args:
            user_config: User-provided configuration.

        Returns:
            Complete configuration with defaults applied.
        """
        result = self.get_defaults()
        result.update(user_config)
        return result

    def __getattr__(self, name: str) -> Any:
        """Get configuration value by field name."""
        if name.startswith("_"):
            raise AttributeError(name)

        # Look up in fields map
        if name in self._fields_map:
            return self._values.get(name, self._fields_map[name].default)

        raise AttributeError(f"No configuration field '{name}'")

    def get(self, name: str, default: T = None) -> T:
        """Get a configuration value with optional default."""
        return self._values.get(name, default)

    def set(self, name: str, value: Any) -> None:
        """Set a configuration value."""
        if name in self._fields_map:
            field = self._fields_map[name]
            if not field.validate(value):
                raise ValueError(f"Invalid value for field '{name}': {value}")
        self._values[name] = value

    def validate(self, user_config: Optional[dict[str, Any]] = None) -> bool:
        """
        Validate configuration values.

        Args:
            user_config: Optional user config to validate. If not provided,
                        validates the internal values.

        Returns:
            True if all values are valid, False otherwise.
        """
        config_to_check = user_config if user_config is not None else self._values

        for field in self.fields:
            value = config_to_check.get(field.name)

            if field.required and value is None:
                return False

            if value is not None and not field.validate(value):
                return False

        return True

    def validate_with_errors(self) -> list[str]:
        """
        Validate all configuration values and return errors.

        Returns:
            List of validation error messages.
        """
        errors = []

        for field in self.fields:
            value = self._values.get(field.name)

            if field.required and value is None:
                errors.append(f"Required field '{field.label}' is missing")
                continue

            if value is not None and not field.validate(value):
                errors.append(f"Invalid value for '{field.label}': {value}")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Get all configuration values as a dictionary."""
        return self._values.copy()

    def to_schema(self) -> dict[str, Any]:
        """
        Get the configuration schema for UI generation.

        Returns:
            Schema dictionary with fields list.
        """
        return {
            "fields": [field.to_dict() for field in self.fields]
        }

    @classmethod
    def get_schema(cls) -> list[dict[str, Any]]:
        """
        Get the configuration schema for UI generation (class method).

        Returns:
            List of field schema dictionaries.
        """
        fields = {}
        for name in dir(cls):
            if name.startswith("_"):
                continue
            value = getattr(cls, name, None)
            if isinstance(value, ConfigField):
                fields[value.name] = value
        return [field.to_dict() for field in fields.values()]
