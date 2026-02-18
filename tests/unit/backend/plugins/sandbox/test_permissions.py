"""
Tests for Plugin Permission Enforcement System.

Phase 4 Enhancement: Tests for hardened permission enforcement
including hierarchical checking, audit logging, and guards.
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from backend.plugins.sandbox.permissions import (
    PermissionAuditEntry,
    PermissionAuditor,
    PermissionCategory,
    PermissionCheck,
    PermissionEnforcer,
    PermissionLevel,
    PermissionRegistry,
    get_auditor,
    get_registry,
    permission_guard,
)


class TestPermissionLevel:
    """Tests for PermissionLevel enum."""

    def test_level_ordering(self):
        """Test permission levels are properly ordered."""
        assert PermissionLevel.DENIED.value < PermissionLevel.READ_ONLY.value
        assert PermissionLevel.READ_ONLY.value < PermissionLevel.WRITE.value
        assert PermissionLevel.WRITE.value < PermissionLevel.FULL.value

    def test_level_comparison(self):
        """Test level comparison for permission checks."""
        # Full grants include read-only
        assert PermissionLevel.FULL.value >= PermissionLevel.READ_ONLY.value
        # Read-only does not include write
        assert PermissionLevel.READ_ONLY.value < PermissionLevel.WRITE.value


class TestPermissionCategory:
    """Tests for PermissionCategory enum."""

    def test_standard_categories(self):
        """Test all standard categories exist."""
        assert PermissionCategory.AUDIO.value == "audio"
        assert PermissionCategory.FILESYSTEM.value == "filesystem"
        assert PermissionCategory.NETWORK.value == "network"
        assert PermissionCategory.UI.value == "ui"
        assert PermissionCategory.SETTINGS.value == "settings"
        assert PermissionCategory.HOST_API.value == "host_api"
        assert PermissionCategory.ENGINE.value == "engine"
        assert PermissionCategory.PROCESS.value == "process"


class TestPermissionCheck:
    """Tests for PermissionCheck dataclass."""

    def test_create_granted_check(self):
        """Test creating a granted permission check."""
        check = PermissionCheck(
            granted=True,
            permission="audio.playback",
            level=PermissionLevel.FULL,
            reason="Granted at level FULL",
        )
        assert check.granted is True
        assert check.permission == "audio.playback"
        assert check.level == PermissionLevel.FULL
        assert check.timestamp > 0

    def test_to_dict(self):
        """Test converting check to dictionary."""
        check = PermissionCheck(
            granted=False,
            permission="network.http",
            level=PermissionLevel.DENIED,
            reason="Permission not configured",
        )
        d = check.to_dict()
        assert d["granted"] is False
        assert d["permission"] == "network.http"
        assert d["level"] == "DENIED"
        assert "timestamp" in d


class TestPermissionAuditor:
    """Tests for PermissionAuditor."""

    def test_record_entry(self):
        """Test recording audit entries."""
        auditor = PermissionAuditor()
        entry = PermissionAuditEntry(
            plugin_id="test-plugin",
            permission="audio.playback",
            granted=True,
            reason="Test",
            timestamp=time.time(),
        )
        auditor.record(entry)

        entries = auditor.get_entries()
        assert len(entries) == 1
        assert entries[0].plugin_id == "test-plugin"

    def test_filter_by_plugin(self):
        """Test filtering entries by plugin ID."""
        auditor = PermissionAuditor()

        auditor.record(
            PermissionAuditEntry(
                plugin_id="plugin-a",
                permission="audio.playback",
                granted=True,
                reason="Test",
                timestamp=time.time(),
            )
        )
        auditor.record(
            PermissionAuditEntry(
                plugin_id="plugin-b",
                permission="network.http",
                granted=False,
                reason="Test",
                timestamp=time.time(),
            )
        )

        entries = auditor.get_entries(plugin_id="plugin-a")
        assert len(entries) == 1
        assert entries[0].plugin_id == "plugin-a"

    def test_filter_by_granted(self):
        """Test filtering entries by granted status."""
        auditor = PermissionAuditor()

        auditor.record(
            PermissionAuditEntry(
                plugin_id="test",
                permission="audio.playback",
                granted=True,
                reason="Allowed",
                timestamp=time.time(),
            )
        )
        auditor.record(
            PermissionAuditEntry(
                plugin_id="test",
                permission="network.http",
                granted=False,
                reason="Denied",
                timestamp=time.time(),
            )
        )

        denied = auditor.get_entries(granted=False)
        assert len(denied) == 1
        assert denied[0].permission == "network.http"

    def test_denial_counts(self):
        """Test tracking denial counts."""
        auditor = PermissionAuditor()

        # Record multiple denials
        for _ in range(3):
            auditor.record(
                PermissionAuditEntry(
                    plugin_id="test",
                    permission="network.http",
                    granted=False,
                    reason="Denied",
                    timestamp=time.time(),
                )
            )

        counts = auditor.get_denial_counts(plugin_id="test")
        assert counts.get("network.http") == 3

    def test_max_entries_limit(self):
        """Test that max entries limit is respected."""
        auditor = PermissionAuditor(max_entries=10)

        # Record more than max entries
        for i in range(15):
            auditor.record(
                PermissionAuditEntry(
                    plugin_id=f"plugin-{i}",
                    permission="test.perm",
                    granted=True,
                    reason="Test",
                    timestamp=time.time(),
                )
            )

        # Should have been trimmed
        entries = auditor.get_entries()
        assert len(entries) <= 10


class TestPermissionEnforcer:
    """Tests for PermissionEnforcer."""

    def test_boolean_permission_granted(self):
        """Test boolean permission grant."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={"audio": True},
            auditor=PermissionAuditor(),
        )

        check = enforcer.check("audio.playback")
        assert check.granted is True
        assert check.level == PermissionLevel.FULL

    def test_boolean_permission_denied(self):
        """Test boolean permission denial."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={"audio": False},
            auditor=PermissionAuditor(),
        )

        check = enforcer.check("audio.playback")
        assert check.granted is False
        assert check.level == PermissionLevel.DENIED

    def test_specific_action_permission(self):
        """Test specific action permission."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={
                "audio": {
                    "playback": True,
                    "record": False,
                }
            },
            auditor=PermissionAuditor(),
        )

        playback = enforcer.check("audio.playback")
        assert playback.granted is True

        record = enforcer.check("audio.record")
        assert record.granted is False

    def test_enabled_flag_fallback(self):
        """Test enabled flag fallback."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={
                "audio": {
                    "enabled": True,
                }
            },
            auditor=PermissionAuditor(),
        )

        # Should fall back to category wildcard
        check = enforcer.check("audio.playback")
        assert check.granted is True

    def test_permission_level_string(self):
        """Test permission level as string."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={
                "filesystem": {
                    "read": "full",
                    "write": "read_only",
                }
            },
            auditor=PermissionAuditor(),
        )

        # Full access check should pass with full level
        read_check = enforcer.check("filesystem.read")
        assert read_check.granted is True
        assert read_check.level == PermissionLevel.FULL

        # Full access check should fail with read_only level
        write_check = enforcer.check("filesystem.write", PermissionLevel.FULL)
        assert write_check.granted is False
        assert write_check.level == PermissionLevel.READ_ONLY

        # Read-only check should pass with read_only level
        write_read = enforcer.check("filesystem.write", PermissionLevel.READ_ONLY)
        assert write_read.granted is True

    def test_require_raises_on_denied(self):
        """Test require raises PermissionError."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={},
            auditor=PermissionAuditor(),
        )

        with pytest.raises(PermissionError) as exc_info:
            enforcer.require("network.http")

        assert "Permission denied" in str(exc_info.value)

    def test_require_passes_on_granted(self):
        """Test require passes when granted."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={"network": True},
            auditor=PermissionAuditor(),
        )

        # Should not raise
        enforcer.require("network.http")

    def test_has_method(self):
        """Test has() convenience method."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={"audio": True},
            auditor=PermissionAuditor(),
        )

        assert enforcer.has("audio.playback") is True
        assert enforcer.has("network.http") is False

    def test_get_level(self):
        """Test get_level method."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={"audio": "read_only"},
            auditor=PermissionAuditor(),
        )

        level = enforcer.get_level("audio.playback")
        assert level == PermissionLevel.READ_ONLY

    def test_list_granted(self):
        """Test listing granted permissions."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={
                "audio": True,
                "network": False,
                "ui": {"notify": True},
            },
            auditor=PermissionAuditor(),
        )

        granted = enforcer.list_granted()
        assert "audio.*" in granted
        assert "ui.notify" in granted
        assert "network.*" not in granted

    def test_temporary_grant(self):
        """Test temporary permission grant."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={},
            auditor=PermissionAuditor(),
        )

        # Initially denied
        assert enforcer.has("network.http") is False

        # Grant temporarily
        enforcer.grant_temporary("network.http")
        assert enforcer.has("network.http") is True

        # Revoke
        enforcer.revoke_temporary("network.http")
        assert enforcer.has("network.http") is False

    def test_revoke_all_temporary(self):
        """Test revoking all temporary permissions."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={},
            auditor=PermissionAuditor(),
        )

        enforcer.grant_temporary("network.http")
        enforcer.grant_temporary("process.spawn")

        enforcer.revoke_all_temporary()

        assert enforcer.has("network.http") is False
        assert enforcer.has("process.spawn") is False

    def test_invalid_permission_format(self):
        """Test invalid permission format is denied."""
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={"audio": True},
            auditor=PermissionAuditor(),
        )

        check = enforcer.check("invalid")  # No category.action format
        assert check.granted is False
        assert "Invalid permission format" in check.reason


class TestPermissionGuard:
    """Tests for permission_guard decorator."""

    @pytest.mark.asyncio
    async def test_guard_allows_with_permission(self):
        """Test guard allows when permission granted."""
        auditor = PermissionAuditor()
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={"audio": True},
            auditor=auditor,
        )

        class TestService:
            def __init__(self):
                self.enforcer = enforcer

            @permission_guard("audio.playback")
            async def play(self):
                return "played"

        service = TestService()
        result = await service.play()
        assert result == "played"

    @pytest.mark.asyncio
    async def test_guard_denies_without_permission(self):
        """Test guard denies when permission not granted."""
        auditor = PermissionAuditor()
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={},
            auditor=auditor,
        )

        class TestService:
            def __init__(self):
                self.enforcer = enforcer

            @permission_guard("audio.playback")
            async def play(self):
                return "played"

        service = TestService()

        with pytest.raises(PermissionError):
            await service.play()

    @pytest.mark.asyncio
    async def test_guard_with_required_level(self):
        """Test guard with specific required level."""
        auditor = PermissionAuditor()
        enforcer = PermissionEnforcer(
            plugin_id="test",
            permissions={"filesystem": {"write": "read_only"}},
            auditor=auditor,
        )

        class TestService:
            def __init__(self):
                self.enforcer = enforcer

            @permission_guard("filesystem.write", PermissionLevel.WRITE)
            async def write_file(self):
                return "written"

        service = TestService()

        # Should fail - has read_only but requires write
        with pytest.raises(PermissionError):
            await service.write_file()


class TestPermissionRegistry:
    """Tests for PermissionRegistry."""

    def test_register_permission(self):
        """Test registering a permission."""
        registry = PermissionRegistry()
        registry.register(
            "custom.action",
            "A custom permission",
            PermissionCategory.HOST_API,
            requires_trust=True,
        )

        info = registry.get("custom.action")
        assert info is not None
        assert info["description"] == "A custom permission"
        assert info["requires_trust"] is True

    def test_list_all(self):
        """Test listing all permissions."""
        registry = PermissionRegistry()
        registry.register("a.one", "Description A1")
        registry.register("b.two", "Description B2")

        all_perms = registry.list_all()
        assert "a.one" in all_perms
        assert "b.two" in all_perms

    def test_list_by_category(self):
        """Test listing permissions by category."""
        registry = PermissionRegistry()
        registry.register("audio.play", "Play audio", PermissionCategory.AUDIO)
        registry.register("network.http", "HTTP requests", PermissionCategory.NETWORK)

        audio = registry.list_by_category("audio")
        assert "audio.play" in audio
        assert "network.http" not in audio


class TestGlobalInstances:
    """Tests for global auditor and registry instances."""

    def test_global_auditor(self):
        """Test global auditor access."""
        auditor = get_auditor()
        assert isinstance(auditor, PermissionAuditor)

    def test_global_registry(self):
        """Test global registry has standard permissions."""
        registry = get_registry()

        # Should have standard audio permissions
        assert registry.get("audio.playback") is not None
        assert registry.get("filesystem.read") is not None
        assert registry.get("network.http") is not None
