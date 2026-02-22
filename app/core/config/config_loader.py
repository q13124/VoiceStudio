"""
Unified Configuration Loader
Supports JSON, YAML, and TOML configuration files with validation.
Part of FREE_LIBRARIES_INTEGRATION - Worker 3.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Try importing optional parsers
try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    logger.warning("pyyaml not installed, YAML support unavailable")

try:
    import toml

    HAS_TOML = True
except ImportError:
    HAS_TOML = False
    logger.warning("toml not installed, TOML support unavailable")

try:
    from pydantic import BaseModel, ValidationError

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    logger.warning("pydantic not installed, validation support limited")

try:
    from cerberus import Validator

    HAS_CERBERUS = True
except ImportError:
    HAS_CERBERUS = False
    logger.warning("cerberus not installed, schema validation unavailable")


class ConfigLoader:
    """
    Unified configuration loader supporting JSON, YAML, and TOML formats.
    """

    def __init__(self, config_path: str | Path):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config: dict[str, Any] = {}
        self.format: str | None = None

    def detect_format(self) -> str:
        """
        Detect configuration file format from extension.

        Returns:
            Format string: 'json', 'yaml', 'toml', or 'unknown'
        """
        suffix = self.config_path.suffix.lower()
        if suffix == ".json":
            return "json"
        elif suffix in (".yaml", ".yml"):
            return "yaml"
        elif suffix == ".toml":
            return "toml"
        else:
            return "unknown"

    def load(self, validate: bool = True, schema: dict | None = None) -> dict[str, Any]:
        """
        Load configuration from file.

        Args:
            validate: Whether to validate configuration
            schema: Optional Cerberus schema for validation

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid or format unsupported
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        self.format = self.detect_format()

        # Load based on format
        if self.format == "json":
            self.config = self._load_json()
        elif self.format == "yaml":
            if not HAS_YAML:
                raise ValueError("YAML support requires pyyaml. Install with: pip install pyyaml")
            self.config = self._load_yaml()
        elif self.format == "toml":
            if not HAS_TOML:
                raise ValueError("TOML support requires toml. Install with: pip install toml")
            self.config = self._load_toml()
        else:
            raise ValueError(f"Unsupported configuration format: {self.format}")

        # Validate if requested
        if validate:
            if schema and HAS_CERBERUS:
                self._validate_cerberus(schema)
            elif HAS_PYDANTIC:
                # Basic validation with pydantic
                self._validate_pydantic()

        logger.info(f"Loaded configuration from {self.config_path} (format: {self.format})")
        return self.config

    def _load_json(self) -> dict[str, Any]:
        """Load JSON configuration."""
        with open(self.config_path, encoding="utf-8") as f:
            return json.load(f)

    def _load_yaml(self) -> dict[str, Any]:
        """Load YAML configuration."""
        with open(self.config_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _load_toml(self) -> dict[str, Any]:
        """Load TOML configuration."""
        with open(self.config_path, encoding="utf-8") as f:
            return toml.load(f)

    def _validate_cerberus(self, schema: dict) -> None:
        """Validate configuration using Cerberus schema."""
        if not HAS_CERBERUS:
            return

        validator = Validator(schema)
        if not validator.validate(self.config):
            errors = validator.errors
            raise ValueError(f"Configuration validation failed: {errors}")

    def _validate_pydantic(self) -> None:
        """Basic validation using Pydantic (if available)."""
        if not HAS_PYDANTIC:
            return

        # Basic type checking
        if not isinstance(self.config, dict):
            raise ValueError("Configuration must be a dictionary")

    def save(self, format: str | None = None) -> None:
        """
        Save configuration to file.

        Args:
            format: Output format ('json', 'yaml', 'toml'). If None, uses detected format.
        """
        save_format = format or self.format or "json"

        if save_format == "json":
            self._save_json()
        elif save_format == "yaml":
            if not HAS_YAML:
                raise ValueError("YAML support requires pyyaml")
            self._save_yaml()
        elif save_format == "toml":
            if not HAS_TOML:
                raise ValueError("TOML support requires toml")
            self._save_toml()
        else:
            raise ValueError(f"Unsupported format: {save_format}")

        logger.info(f"Saved configuration to {self.config_path} (format: {save_format})")

    def _save_json(self) -> None:
        """Save as JSON atomically (tmp + replace)."""
        tmp_path = self.config_path.with_suffix(self.config_path.suffix + ".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.config_path)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise

    def _save_yaml(self) -> None:
        """Save as YAML atomically (tmp + replace)."""
        tmp_path = self.config_path.with_suffix(self.config_path.suffix + ".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            os.replace(tmp_path, self.config_path)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise

    def _save_toml(self) -> None:
        """Save as TOML atomically (tmp + replace)."""
        tmp_path = self.config_path.with_suffix(self.config_path.suffix + ".tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                toml.dump(self.config, f)
            os.replace(tmp_path, self.config_path)
        except Exception:
            if tmp_path.exists():
                tmp_path.unlink()
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports dot notation)."""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def update(self, updates: dict[str, Any]) -> None:
        """Update configuration with new values."""
        self.config.update(updates)


class PydanticConfigModel(BaseModel):
    """
    Base Pydantic model for configuration validation.
    Extend this class for specific configuration schemas.
    """

    ...


def load_config(
    config_path: str | Path,
    format: str | None = None,
    validate: bool = True,
    schema: dict | None = None,
) -> dict[str, Any]:
    """
    Convenience function to load configuration.

    Args:
        config_path: Path to configuration file
        format: Force format ('json', 'yaml', 'toml'). If None, auto-detect.
        validate: Whether to validate configuration
        schema: Optional Cerberus schema for validation

    Returns:
        Configuration dictionary
    """
    loader = ConfigLoader(config_path)
    if format:
        loader.format = format
    return loader.load(validate=validate, schema=schema)


def save_config(config: dict[str, Any], config_path: str | Path, format: str = "json") -> None:
    """
    Convenience function to save configuration.

    Args:
        config: Configuration dictionary
        config_path: Path to save configuration file
        format: Output format ('json', 'yaml', 'toml')
    """
    loader = ConfigLoader(config_path)
    loader.config = config
    loader.format = format
    loader.save(format=format)
