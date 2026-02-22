"""
Policy Loader for Plugin Governance.

Phase 4 Enhancement: Loads policy configuration from files
and environment. Supports JSON and YAML formats.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .models import PolicyConfig

logger = logging.getLogger(__name__)


class PolicyLoader:
    """
    Loads and merges policy configurations from multiple sources.

    Policy sources (in order of precedence, highest last):
        1. Built-in defaults
        2. System policy file
        3. User policy file
        4. Environment overrides
    """

    # Default paths
    DEFAULT_SYSTEM_POLICY = "config/plugin-policy.json"
    DEFAULT_USER_POLICY = "user-plugin-policy.json"

    def __init__(
        self,
        system_path: Optional[Union[str, Path]] = None,
        user_path: Optional[Union[str, Path]] = None,
        base_dir: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize the policy loader.

        Args:
            system_path: Path to system policy file (optional)
            user_path: Path to user policy file (optional)
            base_dir: Base directory for relative paths
        """
        self._base_dir = Path(base_dir) if base_dir else Path.cwd()
        self._system_path = self._resolve_path(system_path, self.DEFAULT_SYSTEM_POLICY)
        self._user_path = self._resolve_path(user_path, self.DEFAULT_USER_POLICY)

    def _resolve_path(self, path: Optional[Union[str, Path]], default: str) -> Path:
        """Resolve a path relative to base directory."""
        if path is None:
            path = default
        p = Path(path)
        if not p.is_absolute():
            p = self._base_dir / p
        return p

    def load(self) -> PolicyConfig:
        """
        Load the complete policy configuration.

        Merges policies from all sources with proper precedence.

        Returns:
            Merged PolicyConfig
        """
        # Start with defaults
        config = PolicyConfig()

        # Load system policy
        if self._system_path.exists():
            try:
                system_config = self._load_file(self._system_path)
                config = self._merge_configs(config, system_config)
                logger.info(f"Loaded system policy: {self._system_path}")
            except Exception as e:
                logger.error(f"Failed to load system policy: {e}")

        # Load user policy (overrides system)
        if self._user_path.exists():
            try:
                user_config = self._load_file(self._user_path)
                config = self._merge_configs(config, user_config)
                logger.info(f"Loaded user policy: {self._user_path}")
            except Exception as e:
                logger.error(f"Failed to load user policy: {e}")

        # Apply environment overrides
        config = self._apply_env_overrides(config)

        return config

    def _load_file(self, path: Path) -> PolicyConfig:
        """Load a policy config from a file."""
        content = path.read_text(encoding="utf-8")

        if path.suffix in (".yaml", ".yml"):
            # Try YAML if available
            try:
                import yaml

                data = yaml.safe_load(content)
            except ImportError:
                raise ImportError(
                    f"PyYAML required to load {path}. " "Install with: pip install pyyaml"
                )
        else:
            # Default to JSON
            data = json.loads(content)

        return PolicyConfig.from_dict(data)

    def _merge_configs(self, base: PolicyConfig, override: PolicyConfig) -> PolicyConfig:
        """
        Merge two policy configs.

        Override takes precedence for scalar values.
        Lists and sets are combined.
        """
        # Create new config based on override
        merged = PolicyConfig(
            version=override.version or base.version,
            name=override.name or base.name,
            description=override.description or base.description,
            default_action=override.default_action,
            default_trust_level=override.default_trust_level,
            require_signature=override.require_signature or base.require_signature,
            require_manifest_id=override.require_manifest_id,
            whitelist_mode=override.whitelist_mode or base.whitelist_mode,
        )

        # Merge sets
        merged.whitelist = base.whitelist | override.whitelist
        merged.blacklist = base.blacklist | override.blacklist
        merged.trusted_publishers = base.trusted_publishers | override.trusted_publishers
        merged.trusted_sources = base.trusted_sources | override.trusted_sources

        # Merge lists (avoid duplicates)
        merged.global_permission_caps = list(base.global_permission_caps)
        for cap in override.global_permission_caps:
            if cap not in merged.global_permission_caps:
                merged.global_permission_caps.append(cap)

        merged.global_denied_permissions = list(
            set(base.global_denied_permissions) | set(override.global_denied_permissions)
        )

        # Merge rules (override rules take precedence by ID)
        rule_map = {r.rule_id: r for r in base.rules}
        for rule in override.rules:
            rule_map[rule.rule_id] = rule
        merged.rules = list(rule_map.values())
        merged.rules.sort(key=lambda r: r.priority, reverse=True)

        # Merge plugin policies (override takes precedence)
        merged.plugin_policies = dict(base.plugin_policies)
        merged.plugin_policies.update(override.plugin_policies)

        return merged

    def _apply_env_overrides(self, config: PolicyConfig) -> PolicyConfig:
        """Apply environment variable overrides."""
        # VOICESTUDIO_PLUGIN_WHITELIST_MODE
        whitelist_mode = os.environ.get("VOICESTUDIO_PLUGIN_WHITELIST_MODE")
        if whitelist_mode is not None:
            config.whitelist_mode = whitelist_mode.lower() in ("1", "true", "yes")
            logger.info(f"Env override: whitelist_mode={config.whitelist_mode}")

        # VOICESTUDIO_PLUGIN_REQUIRE_SIGNATURE
        require_sig = os.environ.get("VOICESTUDIO_PLUGIN_REQUIRE_SIGNATURE")
        if require_sig is not None:
            config.require_signature = require_sig.lower() in ("1", "true", "yes")
            logger.info(f"Env override: require_signature={config.require_signature}")

        # VOICESTUDIO_PLUGIN_BLACKLIST (comma-separated)
        blacklist = os.environ.get("VOICESTUDIO_PLUGIN_BLACKLIST")
        if blacklist:
            for plugin_id in blacklist.split(","):
                plugin_id = plugin_id.strip()
                if plugin_id:
                    config.blacklist.add(plugin_id)
                    logger.info(f"Env override: blacklisted {plugin_id}")

        # VOICESTUDIO_PLUGIN_WHITELIST (comma-separated)
        whitelist = os.environ.get("VOICESTUDIO_PLUGIN_WHITELIST")
        if whitelist:
            for plugin_id in whitelist.split(","):
                plugin_id = plugin_id.strip()
                if plugin_id:
                    config.whitelist.add(plugin_id)
                    logger.info(f"Env override: whitelisted {plugin_id}")

        # VOICESTUDIO_PLUGIN_DENY_PERMISSIONS (comma-separated)
        deny_perms = os.environ.get("VOICESTUDIO_PLUGIN_DENY_PERMISSIONS")
        if deny_perms:
            for perm in deny_perms.split(","):
                perm = perm.strip()
                if perm:
                    config.global_denied_permissions.append(perm)
                    logger.info(f"Env override: denied permission {perm}")

        return config

    def save_user_policy(self, config: PolicyConfig) -> None:
        """
        Save the policy configuration to the user policy file.

        Args:
            config: The configuration to save
        """
        # Ensure parent directory exists
        self._user_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict and save
        data = config.to_dict()
        content = json.dumps(data, indent=2)
        self._user_path.write_text(content, encoding="utf-8")
        logger.info(f"Saved user policy to {self._user_path}")

    def create_default_policy_file(self, path: Optional[Path] = None) -> Path:
        """
        Create a default policy file template.

        Args:
            path: Where to create the file (default: system policy path)

        Returns:
            Path to the created file
        """
        if path is None:
            path = self._system_path

        default_config = PolicyConfig(
            version="1.0",
            name="default",
            description="Default VoiceStudio plugin policy",
        )

        # Add some example rules
        from .models import PermissionCap, PolicyRule

        default_config.rules = [
            PolicyRule(
                rule_id="example-deny-network",
                description="Example: Deny network for untrusted plugins",
                priority=10,
                min_trust_level=None,
                max_trust_level=None,
                denied_permissions=["network.*"],
            ),
        ]

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        # Save
        data = default_config.to_dict()
        content = json.dumps(data, indent=2)
        path.write_text(content, encoding="utf-8")
        logger.info(f"Created default policy file at {path}")

        return path

    @staticmethod
    def validate_policy_file(path: Union[str, Path]) -> tuple:
        """
        Validate a policy file without loading it.

        Args:
            path: Path to the policy file

        Returns:
            Tuple of (valid: bool, errors: List[str])
        """
        path = Path(path)
        errors: List[str] = []

        if not path.exists():
            return False, [f"File not found: {path}"]

        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            return False, [f"Failed to read file: {e}"]

        try:
            if path.suffix in (".yaml", ".yml"):
                try:
                    import yaml

                    data = yaml.safe_load(content)
                except ImportError:
                    return False, ["PyYAML required to validate YAML files"]
            else:
                data = json.loads(content)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except Exception as e:
            return False, [f"Failed to parse file: {e}"]

        # Validate required fields
        if not isinstance(data, dict):
            return False, ["Policy must be a JSON object"]

        # Validate version
        version = data.get("version")
        if version and not isinstance(version, str):
            errors.append("'version' must be a string")

        # Validate action values
        valid_actions = {"allow", "deny", "warn", "review"}
        default_action = data.get("default_action")
        if default_action and default_action not in valid_actions:
            errors.append(f"Invalid default_action: {default_action}")

        # Validate rules
        rules = data.get("rules", [])
        if not isinstance(rules, list):
            errors.append("'rules' must be an array")
        else:
            for i, rule in enumerate(rules):
                if not isinstance(rule, dict):
                    errors.append(f"Rule {i} must be an object")
                    continue
                if "rule_id" not in rule:
                    errors.append(f"Rule {i} missing 'rule_id'")
                rule_action = rule.get("action")
                if rule_action and rule_action not in valid_actions:
                    errors.append(f"Rule {i} has invalid action: {rule_action}")

        return len(errors) == 0, errors
