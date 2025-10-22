"""
VoiceStudio Unified Configuration System
Implements the configuration topology from the Unified Implementation Map
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class RouterConfig:
    host: str = "127.0.0.1"
    port: int = 5090
    models_dir: str = "C:\\ProgramData\\VoiceStudio\\models"
    cache_dir: str = "C:\\ProgramData\\VoiceStudio\\cache"
    debug: bool = False
    log_level: str = "info"
    quality_preference: Dict[str, int] = field(
        default_factory=lambda: {"quality": 3, "balanced": 2, "fast": 1}
    )
    fallback_order: List[str] = field(
        default_factory=lambda: ["xtts", "openvoice", "coqui", "tortoise"]
    )


@dataclass
class GatewayConfig:
    host: str = "127.0.0.1"
    port: int = 59120
    python_exe: str = "C:\\ProgramData\\VoiceStudio\\pyenv\\Scripts\\python.exe"
    gateway_script: str = (
        "C:\\ProgramData\\VoiceStudio\\workers\\ops\\engine_gateway.py"
    )
    restart_delay_ms: int = 1500


@dataclass
class WebUIConfig:
    host: str = "127.0.0.1"
    port: int = 5173
    dev_server: bool = True
    websocket_port: int = 5174
    hot_reload: bool = True
    debug_mode: bool = False


@dataclass
class TelemetryConfig:
    enabled: bool = True
    db_path: str = "C:\\ProgramData\\VoiceStudio\\telemetry.db"
    retention_days: int = 30
    metrics_export: Dict[str, Any] = field(
        default_factory=lambda: {
            "prometheus": {"enabled": False, "port": 9090},
            "grafana": {"enabled": False, "dashboard_url": "http://localhost:3000"},
        }
    )


@dataclass
class SecurityConfig:
    rate_limits: Dict[str, int] = field(
        default_factory=lambda: {
            "api_requests_per_minute": 100,
            "clones_per_day_per_user": 50,
            "max_file_size_mb": 100,
        }
    )
    input_validation: Dict[str, Any] = field(
        default_factory=lambda: {
            "max_text_length": 5000,
            "allowed_formats": ["wav", "mp3", "flac"],
            "malware_scan": False,
        }
    )
    encryption: Dict[str, bool] = field(
        default_factory=lambda: {"voice_profiles_at_rest": False, "audit_logging": True}
    )


@dataclass
class PluginConfig:
    enabled: bool = True
    hot_reload: bool = True
    registry_path: str = "C:\\ProgramData\\VoiceStudio\\plugins\\registry"
    plugin_directories: List[str] = field(
        default_factory=lambda: [
            "C:\\ProgramData\\VoiceStudio\\plugins\\engines",
            "C:\\ProgramData\\VoiceStudio\\plugins\\effects",
            "C:\\ProgramData\\VoiceStudio\\plugins\\analyzers",
        ]
    )
    debug_mode: bool = False


@dataclass
class TestingConfig:
    unit_test_coverage_threshold: int = 70
    integration_test_timeout: int = 30
    e2e_test_timeout: int = 120
    mock_engines: bool = False


@dataclass
class VoiceStudioConfig:
    router: RouterConfig = field(default_factory=RouterConfig)
    gateway: GatewayConfig = field(default_factory=GatewayConfig)
    web_ui: WebUIConfig = field(default_factory=WebUIConfig)
    telemetry: TelemetryConfig = field(default_factory=TelemetryConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)
    testing: TestingConfig = field(default_factory=TestingConfig)
    environment: Environment = Environment.DEVELOPMENT


class ConfigLoader:
    """Unified configuration loader following the Unified Implementation Map"""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.base_config_path = self.config_dir / "voicestudio.yaml"
        self.engines_config_path = self.config_dir / "engines.yaml"
        self.environments_dir = self.config_dir / "environments"

    def load_config(
        self, environment: Optional[Environment] = None
    ) -> VoiceStudioConfig:
        """Load configuration with environment-specific overrides"""

        # Determine environment
        if environment is None:
            env_str = os.getenv("VOICESTUDIO_ENV", "development").lower()
            try:
                environment = Environment(env_str)
            except ValueError:
                environment = Environment.DEVELOPMENT

        # Load base configuration
        base_config = self._load_yaml_file(self.base_config_path)

        # Load environment-specific overrides
        env_config_path = self.environments_dir / f"{environment.value}.yaml"
        env_config = self._load_yaml_file(env_config_path)

        # Merge configurations (environment overrides base)
        merged_config = self._deep_merge(base_config, env_config)

        # Create configuration objects
        config = VoiceStudioConfig(
            router=RouterConfig(**merged_config.get("router", {})),
            gateway=GatewayConfig(**merged_config.get("gateway", {})),
            web_ui=WebUIConfig(**merged_config.get("web_ui", {})),
            telemetry=TelemetryConfig(**merged_config.get("telemetry", {})),
            security=SecurityConfig(**merged_config.get("security", {})),
            plugins=PluginConfig(**merged_config.get("plugins", {})),
            testing=TestingConfig(**merged_config.get("testing", {})),
            environment=environment,
        )

        return config

    def load_engines_config(self) -> Dict[str, Any]:
        """Load engine-specific configuration"""
        return self._load_yaml_file(self.engines_config_path)

    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file safely"""
        if not file_path.exists():
            return {}

        try:
            with file_path.open("r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load {file_path}: {e}")
            return {}

    def _deep_merge(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def save_config(
        self, config: VoiceStudioConfig, environment: Optional[Environment] = None
    ):
        """Save configuration to YAML files"""
        env = environment or config.environment

        # Convert config to dictionary
        config_dict = {
            "router": {
                "host": config.router.host,
                "port": config.router.port,
                "models_dir": config.router.models_dir,
                "cache_dir": config.router.cache_dir,
                "debug": config.router.debug,
                "log_level": config.router.log_level,
                "quality_preference": config.router.quality_preference,
                "fallback_order": config.router.fallback_order,
            },
            "gateway": {
                "host": config.gateway.host,
                "port": config.gateway.port,
                "python_exe": config.gateway.python_exe,
                "gateway_script": config.gateway.gateway_script,
                "restart_delay_ms": config.gateway.restart_delay_ms,
            },
            "web_ui": {
                "host": config.web_ui.host,
                "port": config.web_ui.port,
                "dev_server": config.web_ui.dev_server,
                "websocket_port": config.web_ui.websocket_port,
                "hot_reload": config.web_ui.hot_reload,
                "debug_mode": config.web_ui.debug_mode,
            },
            "telemetry": {
                "enabled": config.telemetry.enabled,
                "db_path": config.telemetry.db_path,
                "retention_days": config.telemetry.retention_days,
                "metrics_export": config.telemetry.metrics_export,
            },
            "security": {
                "rate_limits": config.security.rate_limits,
                "input_validation": config.security.input_validation,
                "encryption": config.security.encryption,
            },
            "plugins": {
                "enabled": config.plugins.enabled,
                "hot_reload": config.plugins.hot_reload,
                "registry_path": config.plugins.registry_path,
                "plugin_directories": config.plugins.plugin_directories,
                "debug_mode": config.plugins.debug_mode,
            },
            "testing": {
                "unit_test_coverage_threshold": config.testing.unit_test_coverage_threshold,
                "integration_test_timeout": config.testing.integration_test_timeout,
                "e2e_test_timeout": config.testing.e2e_test_timeout,
                "mock_engines": config.testing.mock_engines,
            },
        }

        # Save base config
        with self.base_config_path.open("w", encoding="utf-8") as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

        # Save environment-specific config
        env_config_path = self.environments_dir / f"{env.value}.yaml"
        env_config_dict = {
            "router": {
                "debug": config.router.debug,
                "log_level": config.router.log_level,
            },
            "web_ui": {
                "dev_server": config.web_ui.dev_server,
                "hot_reload": config.web_ui.hot_reload,
                "debug_mode": config.web_ui.debug_mode,
            },
            "security": {
                "rate_limits": config.security.rate_limits,
                "encryption": config.security.encryption,
            },
            "testing": {"mock_engines": config.testing.mock_engines},
            "telemetry": {"metrics_export": config.telemetry.metrics_export},
            "plugins": {
                "hot_reload": config.plugins.hot_reload,
                "debug_mode": config.plugins.debug_mode,
            },
        }

        with env_config_path.open("w", encoding="utf-8") as f:
            yaml.dump(env_config_dict, f, default_flow_style=False, sort_keys=False)


# Global configuration instance
_config_loader = ConfigLoader()
_config_cache: Optional[VoiceStudioConfig] = None


def get_config(
    environment: Optional[Environment] = None, reload: bool = False
) -> VoiceStudioConfig:
    """Get VoiceStudio configuration with caching"""
    global _config_cache

    if _config_cache is None or reload:
        _config_cache = _config_loader.load_config(environment)

    return _config_cache


def get_engines_config() -> Dict[str, Any]:
    """Get engines configuration"""
    return _config_loader.load_engines_config()


def save_config(config: VoiceStudioConfig, environment: Optional[Environment] = None):
    """Save configuration to files"""
    _config_loader.save_config(config, environment)


# Convenience functions for common config access
def get_router_config() -> RouterConfig:
    return get_config().router


def get_gateway_config() -> GatewayConfig:
    return get_config().gateway


def get_web_ui_config() -> WebUIConfig:
    return get_config().web_ui


def get_security_config() -> SecurityConfig:
    return get_config().security


def get_plugin_config() -> PluginConfig:
    return get_config().plugins


def get_telemetry_config() -> TelemetryConfig:
    return get_config().telemetry


def get_testing_config() -> TestingConfig:
    return get_config().testing


if __name__ == "__main__":
    # Test configuration loading
    config = get_config(Environment.DEVELOPMENT)
    print(f"Loaded config for environment: {config.environment.value}")
    print(f"Router port: {config.router.port}")
    print(f"Gateway port: {config.gateway.port}")
    print(f"Web UI port: {config.web_ui.port}")
    print(
        f"Security rate limit: {config.security.rate_limits['api_requests_per_minute']}"
    )

    engines_config = get_engines_config()
    print(f"Available engines: {list(engines_config.keys())}")
