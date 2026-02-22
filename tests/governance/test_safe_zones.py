"""
Tests for safe zone protection.
"""

import os


class TestSafeZones:
    """Test safe zone protection."""

    def test_default_safe_zones_loaded(self, safe_zone_manager):
        """Test that default safe zones are loaded."""
        zones = safe_zone_manager.get_zones()
        assert len(zones) > 0

    def test_program_files_protected(self, safe_zone_manager):
        """Test that Program Files is protected."""
        violation = safe_zone_manager.check_path(
            agent_id="test_agent",
            path="C:\\Program Files\\SomeApp\\file.exe",
            tool_name="WriteFile",
        )

        assert violation is not None
        assert "Program Files" in violation.zone.description

    def test_windows_directory_protected(self, safe_zone_manager):
        """Test that Windows directory is protected."""
        violation = safe_zone_manager.check_path(
            agent_id="test_agent",
            path="C:\\Windows\\System32\\config\\SAM",
            tool_name="WriteFile",
        )

        assert violation is not None

    def test_startup_folder_protected(self, safe_zone_manager):
        """Test that startup folder is protected."""
        appdata = os.environ.get("APPDATA", "C:\\Users\\User\\AppData\\Roaming")
        startup_path = f"{appdata}\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\malware.exe"

        violation = safe_zone_manager.check_path(
            agent_id="test_agent",
            path=startup_path,
            tool_name="WriteFile",
        )

        assert violation is not None
        assert "startup" in violation.zone.description.lower()

    def test_registry_startup_key_protected(self, safe_zone_manager):
        """Test that registry startup keys are protected."""
        violation = safe_zone_manager.check_registry(
            agent_id="test_agent",
            key="HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            tool_name="RegistryWrite",
        )

        assert violation is not None

    def test_allowed_path_not_blocked(self, safe_zone_manager, temp_dir):
        """Test that non-protected paths are allowed."""
        violation = safe_zone_manager.check_path(
            agent_id="test_agent",
            path=str(temp_dir / "safe_file.txt"),
            tool_name="WriteFile",
        )

        assert violation is None

    def test_violation_records_details(self, safe_zone_manager):
        """Test that violations record proper details."""
        violation = safe_zone_manager.check_path(
            agent_id="agent_123",
            path="C:\\Windows\\System32\\test.dll",
            tool_name="WriteFile",
        )

        assert violation is not None
        assert violation.agent_id == "agent_123"
        assert violation.tool_name == "WriteFile"
        assert "C:\\Windows\\System32\\test.dll" in violation.attempted_resource


class TestSafeZoneManagement:
    """Test safe zone management operations."""

    def test_add_custom_zone(self, safe_zone_manager):
        """Test adding a custom safe zone."""
        from agent.safe_zones import SafeZone, SafeZoneType, ViolationAction

        custom_zone = SafeZone(
            zone_type=SafeZoneType.FILESYSTEM,
            pattern="D:\\Critical\\**",
            description="Critical data directory",
            action=ViolationAction.QUARANTINE_AND_ALERT,
        )

        safe_zone_manager.add_zone(custom_zone)

        violation = safe_zone_manager.check_path(
            agent_id="test_agent",
            path="D:\\Critical\\data\\file.db",
            tool_name="WriteFile",
        )

        assert violation is not None

    def test_disable_zone(self, safe_zone_manager):
        """Test disabling a safe zone."""
        zones = safe_zone_manager.get_zones()
        if zones:
            pattern = zones[0].pattern
            safe_zone_manager.disable_zone(pattern)

            disabled_zones = [
                z for z in safe_zone_manager.get_zones(enabled_only=False) if z.pattern == pattern
            ]
            assert len(disabled_zones) == 1
            assert not disabled_zones[0].enabled

    def test_get_violations(self, safe_zone_manager):
        """Test getting recorded violations."""
        # Generate some violations
        safe_zone_manager.check_path(
            agent_id="agent_1",
            path="C:\\Windows\\test.dll",
            tool_name="WriteFile",
        )
        safe_zone_manager.check_path(
            agent_id="agent_2",
            path="C:\\Program Files\\test.exe",
            tool_name="WriteFile",
        )

        violations = safe_zone_manager.get_violations()
        assert len(violations) >= 2

    def test_get_violations_by_agent(self, safe_zone_manager):
        """Test filtering violations by agent."""
        safe_zone_manager.check_path(
            agent_id="target_agent",
            path="C:\\Windows\\test.dll",
            tool_name="WriteFile",
        )
        safe_zone_manager.check_path(
            agent_id="other_agent",
            path="C:\\Windows\\other.dll",
            tool_name="WriteFile",
        )

        violations = safe_zone_manager.get_violations(agent_id="target_agent")
        assert all(v.agent_id == "target_agent" for v in violations)
