"""
Tests for Plugin Policy Engine.

Phase 4 Enhancement: Tests for policy evaluation including
whitelist/blacklist, permission caps, and trust levels.
"""

import json
import tempfile
from pathlib import Path

import pytest

from backend.plugins.policy.engine import (
    PolicyDecision,
    PolicyEngine,
    get_policy_engine,
    set_policy_engine,
)
from backend.plugins.policy.loader import PolicyLoader
from backend.plugins.policy.models import (
    PermissionCap,
    PluginPolicy,
    PolicyAction,
    PolicyConfig,
    PolicyRule,
    TrustLevel,
)


class TestTrustLevel:
    """Tests for TrustLevel enum."""

    def test_trust_ordering(self):
        """Test trust levels are properly ordered."""
        assert TrustLevel.UNTRUSTED < TrustLevel.COMMUNITY
        assert TrustLevel.COMMUNITY < TrustLevel.VERIFIED
        assert TrustLevel.VERIFIED < TrustLevel.OFFICIAL
        assert TrustLevel.OFFICIAL < TrustLevel.SYSTEM


class TestPolicyAction:
    """Tests for PolicyAction enum."""

    def test_action_values(self):
        """Test action values."""
        assert PolicyAction.ALLOW.value == "allow"
        assert PolicyAction.DENY.value == "deny"
        assert PolicyAction.WARN.value == "warn"
        assert PolicyAction.REVIEW.value == "review"


class TestPermissionCap:
    """Tests for PermissionCap."""

    def test_permission_pattern_with_action(self):
        """Test permission pattern with specific action."""
        cap = PermissionCap(category="audio", action="record", max_level="denied")
        assert cap.permission_pattern == "audio.record"

    def test_permission_pattern_wildcard(self):
        """Test permission pattern without action (wildcard)."""
        cap = PermissionCap(category="network", max_level="read_only")
        assert cap.permission_pattern == "network.*"


class TestPolicyRule:
    """Tests for PolicyRule."""

    def test_matches_exact_id(self):
        """Test exact ID matching."""
        rule = PolicyRule(rule_id="test", plugin_id="com.example.plugin")
        assert rule.matches_id("com.example.plugin") is True
        assert rule.matches_id("com.example.other") is False

    def test_matches_glob_pattern(self):
        """Test glob pattern matching."""
        rule = PolicyRule(rule_id="test", plugin_id="com.example.*")
        assert rule.matches_id("com.example.plugin") is True
        assert rule.matches_id("com.example.another") is True
        assert rule.matches_id("com.other.plugin") is False

    def test_matches_regex_pattern(self):
        """Test regex pattern matching."""
        rule = PolicyRule(rule_id="test", plugin_id_pattern=r"com\.example\..*")
        assert rule.matches_id("com.example.plugin") is True
        assert rule.matches_id("com.other.plugin") is False

    def test_matches_no_criteria(self):
        """Test rule with no ID criteria matches all."""
        rule = PolicyRule(rule_id="test")
        assert rule.matches_id("any.plugin.id") is True

    def test_matches_trust_level(self):
        """Test trust level matching."""
        rule = PolicyRule(
            rule_id="test",
            min_trust_level=TrustLevel.COMMUNITY,
            max_trust_level=TrustLevel.VERIFIED,
        )
        assert rule.matches_trust(TrustLevel.UNTRUSTED) is False
        assert rule.matches_trust(TrustLevel.COMMUNITY) is True
        assert rule.matches_trust(TrustLevel.VERIFIED) is True
        assert rule.matches_trust(TrustLevel.OFFICIAL) is False


class TestPolicyConfig:
    """Tests for PolicyConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = PolicyConfig()
        assert config.default_action == PolicyAction.ALLOW
        assert config.whitelist_mode is False
        assert len(config.whitelist) == 0
        assert len(config.blacklist) == 0

    def test_whitelist_operations(self):
        """Test whitelist add/remove."""
        config = PolicyConfig()
        config.add_to_whitelist("plugin-a")
        assert config.is_whitelisted("plugin-a") is True
        assert config.is_blacklisted("plugin-a") is False

        config.remove_from_whitelist("plugin-a")
        assert config.is_whitelisted("plugin-a") is False

    def test_blacklist_operations(self):
        """Test blacklist add/remove."""
        config = PolicyConfig()
        config.add_to_blacklist("plugin-b")
        assert config.is_blacklisted("plugin-b") is True
        assert config.is_whitelisted("plugin-b") is False

    def test_whitelist_removes_from_blacklist(self):
        """Test adding to whitelist removes from blacklist."""
        config = PolicyConfig()
        config.add_to_blacklist("plugin-c")
        assert config.is_blacklisted("plugin-c") is True

        config.add_to_whitelist("plugin-c")
        assert config.is_whitelisted("plugin-c") is True
        assert config.is_blacklisted("plugin-c") is False

    def test_to_dict_and_from_dict(self):
        """Test serialization round-trip."""
        config = PolicyConfig(
            name="test",
            whitelist_mode=True,
            require_signature=True,
        )
        config.add_to_whitelist("plugin-x")
        config.add_to_blacklist("plugin-y")

        data = config.to_dict()
        restored = PolicyConfig.from_dict(data)

        assert restored.name == "test"
        assert restored.whitelist_mode is True
        assert restored.require_signature is True
        assert restored.is_whitelisted("plugin-x") is True
        assert restored.is_blacklisted("plugin-y") is True

    def test_rules_sorted_by_priority(self):
        """Test rules are sorted by priority."""
        config = PolicyConfig()
        config.rules = [
            PolicyRule(rule_id="low", priority=1),
            PolicyRule(rule_id="high", priority=10),
            PolicyRule(rule_id="medium", priority=5),
        ]
        config.__post_init__()

        assert config.rules[0].rule_id == "high"
        assert config.rules[1].rule_id == "medium"
        assert config.rules[2].rule_id == "low"


class TestPolicyDecision:
    """Tests for PolicyDecision."""

    def test_is_permission_denied_exact(self):
        """Test exact permission denial check."""
        decision = PolicyDecision(
            plugin_id="test",
            allowed=True,
            action=PolicyAction.ALLOW,
            trust_level=TrustLevel.COMMUNITY,
            denied_permissions={"network.http"},
        )
        assert decision.is_permission_denied("network.http") is True
        assert decision.is_permission_denied("network.websocket") is False

    def test_is_permission_denied_wildcard(self):
        """Test wildcard permission denial check."""
        decision = PolicyDecision(
            plugin_id="test",
            allowed=True,
            action=PolicyAction.ALLOW,
            trust_level=TrustLevel.COMMUNITY,
            denied_permissions={"network.*"},
        )
        assert decision.is_permission_denied("network.http") is True
        assert decision.is_permission_denied("network.websocket") is True
        assert decision.is_permission_denied("audio.playback") is False

    def test_get_permission_cap(self):
        """Test getting permission cap."""
        decision = PolicyDecision(
            plugin_id="test",
            allowed=True,
            action=PolicyAction.ALLOW,
            trust_level=TrustLevel.COMMUNITY,
            permission_caps={"filesystem.*": "read_only"},
        )
        assert decision.get_permission_cap("filesystem.write") == "read_only"
        assert decision.get_permission_cap("network.http") is None

    def test_apply_cap(self):
        """Test applying permission cap."""
        decision = PolicyDecision(
            plugin_id="test",
            allowed=True,
            action=PolicyAction.ALLOW,
            trust_level=TrustLevel.COMMUNITY,
            permission_caps={"filesystem.*": "read_only"},
        )

        # Requesting more than cap allows
        assert decision.apply_cap("filesystem.write", "full") == "read_only"
        # Requesting equal to cap
        assert decision.apply_cap("filesystem.read", "read_only") == "read_only"
        # No cap
        assert decision.apply_cap("audio.playback", "full") == "full"


class TestPolicyEngine:
    """Tests for PolicyEngine."""

    def test_default_allows_all(self):
        """Test default config allows all plugins with valid manifest."""
        engine = PolicyEngine()
        decision = engine.evaluate("any.plugin.id", manifest={"id": "any.plugin.id"})
        assert decision.allowed is True
        assert decision.action == PolicyAction.ALLOW

    def test_blacklist_denies(self):
        """Test blacklisted plugins are denied."""
        config = PolicyConfig()
        config.add_to_blacklist("bad.plugin")
        engine = PolicyEngine(config)

        decision = engine.evaluate("bad.plugin")
        assert decision.allowed is False
        assert decision.action == PolicyAction.DENY
        assert "blacklist" in decision.applied_rules

    def test_whitelist_mode_requires_whitelist(self):
        """Test whitelist mode requires plugins to be whitelisted."""
        config = PolicyConfig(whitelist_mode=True)
        config.add_to_whitelist("good.plugin")
        engine = PolicyEngine(config)

        # Whitelisted plugin allowed
        decision = engine.evaluate("good.plugin", manifest={"id": "good.plugin"})
        assert decision.allowed is True

        # Non-whitelisted plugin denied
        decision = engine.evaluate("other.plugin", manifest={"id": "other.plugin"})
        assert decision.allowed is False

    def test_require_signature(self):
        """Test signature requirement."""
        config = PolicyConfig(require_signature=True)
        engine = PolicyEngine(config)

        # Without valid signature
        decision = engine.evaluate(
            "test.plugin",
            manifest={"id": "test.plugin"},
            signature_valid=False,
        )
        assert decision.allowed is False
        assert "require_signature" in decision.applied_rules

        # With valid signature
        decision = engine.evaluate(
            "test.plugin",
            manifest={"id": "test.plugin"},
            signature_valid=True,
        )
        assert decision.allowed is True

    def test_require_manifest_id(self):
        """Test manifest ID requirement."""
        config = PolicyConfig(require_manifest_id=True)
        engine = PolicyEngine(config)

        # Without manifest ID
        decision = engine.evaluate("test.plugin", manifest={})
        assert decision.allowed is False
        assert "require_manifest_id" in decision.applied_rules

        # With manifest ID
        decision = engine.evaluate("test.plugin", manifest={"id": "test.plugin"})
        assert decision.allowed is True

    def test_global_denied_permissions(self):
        """Test global permission denial."""
        config = PolicyConfig(global_denied_permissions=["process.spawn"])
        engine = PolicyEngine(config)

        decision = engine.evaluate("test.plugin", manifest={"id": "test"})
        assert decision.is_permission_denied("process.spawn") is True

    def test_global_permission_caps(self):
        """Test global permission caps."""
        config = PolicyConfig()
        config.global_permission_caps = [
            PermissionCap(category="filesystem", max_level="read_only")
        ]
        engine = PolicyEngine(config)

        decision = engine.evaluate("test.plugin", manifest={"id": "test"})
        assert decision.permission_caps.get("filesystem.*") == "read_only"

    def test_trust_level_system_plugin(self):
        """Test system plugin gets system trust level."""
        engine = PolicyEngine()
        decision = engine.evaluate("com.voicestudio.core", manifest={"id": "com.voicestudio.core"})
        assert decision.trust_level == TrustLevel.SYSTEM

    def test_trust_level_trusted_publisher(self):
        """Test trusted publisher gets verified trust level."""
        config = PolicyConfig(trusted_publishers={"TrustedDev"})
        engine = PolicyEngine(config)

        decision = engine.evaluate(
            "other.plugin",
            manifest={"id": "other.plugin"},
            publisher="TrustedDev",
        )
        assert decision.trust_level == TrustLevel.VERIFIED

    def test_rule_application(self):
        """Test policy rules are applied."""
        config = PolicyConfig()
        config.rules = [
            PolicyRule(
                rule_id="deny-network-untrusted",
                plugin_id="*",
                max_trust_level=TrustLevel.COMMUNITY,
                denied_permissions=["network.*"],
            )
        ]
        engine = PolicyEngine(config)

        decision = engine.evaluate(
            "untrusted.plugin",
            manifest={"id": "untrusted.plugin"},
            signature_valid=False,
        )
        assert decision.is_permission_denied("network.http") is True
        assert "rule:deny-network-untrusted" in decision.applied_rules

    def test_plugin_specific_policy(self):
        """Test plugin-specific policy overrides."""
        config = PolicyConfig()
        config.plugin_policies["specific.plugin"] = PluginPolicy(
            plugin_id="specific.plugin",
            action=PolicyAction.WARN,
            allow_network=False,
            allow_subprocess=False,
        )
        engine = PolicyEngine(config)

        decision = engine.evaluate(
            "specific.plugin",
            manifest={"id": "specific.plugin"},
        )
        assert decision.action == PolicyAction.WARN
        assert decision.allow_network is False
        assert "plugin_policy:specific.plugin" in decision.applied_rules

    def test_action_warn_allows_with_warning(self):
        """Test WARN action allows but adds warning."""
        config = PolicyConfig()
        config.plugin_policies["warn.plugin"] = PluginPolicy(
            plugin_id="warn.plugin",
            action=PolicyAction.WARN,
        )
        engine = PolicyEngine(config)

        decision = engine.evaluate("warn.plugin", manifest={"id": "warn.plugin"})
        assert decision.allowed is True
        assert len(decision.warnings) > 0

    def test_action_review_blocks_with_review(self):
        """Test REVIEW action blocks pending review."""
        config = PolicyConfig()
        config.plugin_policies["review.plugin"] = PluginPolicy(
            plugin_id="review.plugin",
            action=PolicyAction.REVIEW,
        )
        engine = PolicyEngine(config)

        decision = engine.evaluate("review.plugin", manifest={"id": "review.plugin"})
        assert decision.allowed is False
        assert decision.requires_review is True

    def test_check_permission(self):
        """Test permission checking with cached decision."""
        engine = PolicyEngine()
        decision = engine.evaluate("test.plugin", manifest={"id": "test"})
        engine.cache_decision("test.plugin", decision)

        allowed, level, reason = engine.check_permission("test.plugin", "audio.playback")
        assert allowed is True

    def test_update_config_clears_cache(self):
        """Test updating config clears decision cache."""
        engine = PolicyEngine()
        decision = engine.evaluate("test.plugin", manifest={"id": "test"})
        engine.cache_decision("test.plugin", decision)

        # Verify cached
        assert engine.get_cached_decision("test.plugin") is not None

        # Update config
        new_config = PolicyConfig(name="new")
        engine.update_config(new_config)

        # Cache should be cleared
        assert engine.get_cached_decision("test.plugin") is None


class TestPolicyLoader:
    """Tests for PolicyLoader."""

    def test_load_defaults_when_no_files(self):
        """Test loading defaults when no policy files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = PolicyLoader(
                base_dir=tmpdir,
                system_path="nonexistent.json",
                user_path="nonexistent.json",
            )
            config = loader.load()
            assert config.name == "default"
            assert config.default_action == PolicyAction.ALLOW

    def test_load_from_file(self):
        """Test loading policy from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a policy file
            policy_data = {
                "version": "1.0",
                "name": "test-policy",
                "whitelist_mode": True,
                "whitelist": ["allowed.plugin"],
            }
            policy_path = Path(tmpdir) / "policy.json"
            policy_path.write_text(json.dumps(policy_data))

            loader = PolicyLoader(
                base_dir=tmpdir,
                system_path="policy.json",
            )
            config = loader.load()

            assert config.name == "test-policy"
            assert config.whitelist_mode is True
            assert config.is_whitelisted("allowed.plugin") is True

    def test_user_policy_overrides_system(self):
        """Test user policy overrides system policy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create system policy
            system_data = {
                "name": "system",
                "whitelist": ["system.plugin"],
            }
            system_path = Path(tmpdir) / "system.json"
            system_path.write_text(json.dumps(system_data))

            # Create user policy
            user_data = {
                "name": "user",
                "whitelist": ["user.plugin"],
            }
            user_path = Path(tmpdir) / "user.json"
            user_path.write_text(json.dumps(user_data))

            loader = PolicyLoader(
                base_dir=tmpdir,
                system_path="system.json",
                user_path="user.json",
            )
            config = loader.load()

            # Name should be from user policy
            assert config.name == "user"
            # Whitelists should be merged
            assert config.is_whitelisted("system.plugin") is True
            assert config.is_whitelisted("user.plugin") is True

    def test_save_user_policy(self):
        """Test saving user policy."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = PolicyLoader(base_dir=tmpdir, user_path="saved.json")

            config = PolicyConfig(name="saved-policy")
            config.add_to_whitelist("new.plugin")
            loader.save_user_policy(config)

            # Verify file was created
            saved_path = Path(tmpdir) / "saved.json"
            assert saved_path.exists()

            # Verify content
            data = json.loads(saved_path.read_text())
            assert data["name"] == "saved-policy"
            assert "new.plugin" in data["whitelist"]

    def test_validate_policy_file_valid(self):
        """Test validating a valid policy file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_data = {
                "version": "1.0",
                "default_action": "allow",
                "rules": [{"rule_id": "test-rule", "action": "warn"}],
            }
            policy_path = Path(tmpdir) / "valid.json"
            policy_path.write_text(json.dumps(policy_data))

            valid, errors = PolicyLoader.validate_policy_file(policy_path)
            assert valid is True
            assert len(errors) == 0

    def test_validate_policy_file_invalid_action(self):
        """Test validating policy with invalid action."""
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_data = {
                "default_action": "invalid_action",
            }
            policy_path = Path(tmpdir) / "invalid.json"
            policy_path.write_text(json.dumps(policy_data))

            valid, errors = PolicyLoader.validate_policy_file(policy_path)
            assert valid is False
            assert any("invalid" in e.lower() for e in errors)

    def test_validate_policy_file_missing_rule_id(self):
        """Test validating policy with missing rule_id."""
        with tempfile.TemporaryDirectory() as tmpdir:
            policy_data = {
                "rules": [{"action": "allow"}],  # Missing rule_id
            }
            policy_path = Path(tmpdir) / "invalid.json"
            policy_path.write_text(json.dumps(policy_data))

            valid, errors = PolicyLoader.validate_policy_file(policy_path)
            assert valid is False
            assert any("rule_id" in e for e in errors)

    def test_create_default_policy_file(self):
        """Test creating default policy template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            loader = PolicyLoader(base_dir=tmpdir)
            path = loader.create_default_policy_file(Path(tmpdir) / "default.json")

            assert path.exists()

            # Verify it's valid JSON
            data = json.loads(path.read_text())
            assert "version" in data
            assert "rules" in data


class TestGlobalPolicyEngine:
    """Tests for global policy engine instance."""

    def test_get_policy_engine(self):
        """Test getting global engine."""
        engine = get_policy_engine()
        assert isinstance(engine, PolicyEngine)

    def test_set_policy_engine(self):
        """Test setting global engine."""
        custom_config = PolicyConfig(name="custom")
        custom_engine = PolicyEngine(custom_config)
        set_policy_engine(custom_engine)

        engine = get_policy_engine()
        assert engine.config.name == "custom"
