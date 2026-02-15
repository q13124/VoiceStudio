"""
Tests for kill switch functionality.
"""



class TestKillSwitch:
    """Test kill switch behavior."""

    def test_kill_agent(self, kill_switch):
        """Test killing a specific agent."""
        activation = kill_switch.kill_agent(
            agent_id="agent_123",
            activated_by="admin",
            reason="Misbehaving agent",
        )

        assert activation.level.value == "Agent"
        assert activation.target_id == "agent_123"
        assert activation.is_active

    def test_kill_session(self, kill_switch):
        """Test killing a session."""
        activation = kill_switch.kill_session(
            session_id="session_456",
            activated_by="admin",
            reason="Session compromised",
        )

        assert activation.level.value == "Session"
        assert activation.is_active

    def test_kill_machine(self, kill_switch):
        """Test machine-level kill switch."""
        activation = kill_switch.kill_machine(
            machine_id="machine_789",
            activated_by="admin",
            reason="Machine compromised",
        )

        assert activation.level.value == "Machine"
        assert activation.is_active

    def test_kill_all(self, kill_switch):
        """Test global kill switch."""
        activation = kill_switch.kill_all(
            activated_by="admin",
            reason="Emergency stop",
        )

        assert activation.level.value == "Global"
        assert activation.target_id == "*"
        assert kill_switch.is_global_kill_active()

    def test_is_blocked_by_agent_kill(self, kill_switch):
        """Test that agent is blocked by agent-level kill."""
        kill_switch.kill_agent("agent_123", "admin", "Test")

        blocking = kill_switch.is_blocked(agent_id="agent_123")

        assert blocking is not None
        assert blocking.target_id == "agent_123"

    def test_is_blocked_by_machine_kill(self, kill_switch):
        """Test that agent is blocked by machine-level kill."""
        kill_switch.kill_machine("machine_789", "admin", "Test")

        blocking = kill_switch.is_blocked(
            agent_id="any_agent",
            machine_id="machine_789",
        )

        assert blocking is not None
        assert blocking.level.value == "Machine"

    def test_is_blocked_by_global_kill(self, kill_switch):
        """Test that all agents are blocked by global kill."""
        kill_switch.kill_all("admin", "Emergency")

        # Any agent should be blocked
        blocking = kill_switch.is_blocked(agent_id="any_agent")

        assert blocking is not None
        assert blocking.level.value == "Global"

    def test_not_blocked_when_no_kill(self, kill_switch):
        """Test that agent is not blocked when no kill switch is active."""
        blocking = kill_switch.is_blocked(agent_id="agent_123")

        assert blocking is None

    def test_deactivate_kill_switch(self, kill_switch):
        """Test deactivating a kill switch."""
        activation = kill_switch.kill_agent("agent_123", "admin", "Test")

        result = kill_switch.deactivate(
            activation_id=activation.activation_id,
            deactivated_by="admin",
        )

        assert result
        assert not activation.is_active

        # Agent should no longer be blocked
        blocking = kill_switch.is_blocked(agent_id="agent_123")
        assert blocking is None

    def test_deactivate_all(self, kill_switch):
        """Test deactivating all kill switches."""
        # Create multiple kill switches
        kill_switch.kill_agent("agent_1", "admin", "Test")
        kill_switch.kill_agent("agent_2", "admin", "Test")
        kill_switch.kill_machine("machine_1", "admin", "Test")

        count = kill_switch.deactivate_all(deactivated_by="admin")

        assert count == 3
        assert len(kill_switch.get_active_activations()) == 0


class TestKillSwitchPersistence:
    """Test kill switch persistence."""

    def test_persistence(self, temp_dir):
        """Test that kill switch state persists."""
        from agent.kill_switch import KillSwitch

        storage_path = temp_dir / "kill_switches.json"

        # Create and activate
        ks1 = KillSwitch(storage_path=storage_path)
        ks1.kill_agent("agent_123", "admin", "Test")

        # Create new instance from same storage
        ks2 = KillSwitch(storage_path=storage_path)

        # Should still be active
        blocking = ks2.is_blocked(agent_id="agent_123")
        assert blocking is not None


class TestKillSwitchStats:
    """Test kill switch statistics."""

    def test_get_stats(self, kill_switch):
        """Test getting kill switch stats."""
        kill_switch.kill_agent("agent_1", "admin", "Test")
        kill_switch.kill_agent("agent_2", "admin", "Test")
        kill_switch.kill_machine("machine_1", "admin", "Test")

        stats = kill_switch.get_stats()

        assert stats["total_active"] == 3
        assert stats["active_by_level"]["Agent"] == 2
        assert stats["active_by_level"]["Machine"] == 1
