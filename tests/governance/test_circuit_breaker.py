"""
Tests for circuit breaker functionality.
"""


class TestCircuitBreaker:
    """Test circuit breaker behavior."""

    def test_circuit_starts_closed(self, circuit_breaker_manager):
        """Test that circuit starts in closed state."""
        breaker = circuit_breaker_manager.get_breaker("test_agent")
        assert breaker.is_closed
        assert not breaker.is_open

    def test_trip_on_denied_threshold(self, circuit_breaker_manager):
        """Test circuit trips after denied action threshold."""
        breaker = circuit_breaker_manager.get_breaker("test_agent")

        # Record denials up to threshold
        for i in range(3):
            tripped = breaker.record_denied(f"Tool{i}", "Denied by policy")

        # Should trip on third denial
        assert tripped
        assert breaker.is_open

    def test_trip_on_failure_threshold(self, circuit_breaker_manager):
        """Test circuit trips after failure threshold."""
        breaker = circuit_breaker_manager.get_breaker("test_agent")

        # Record failures up to threshold
        for i in range(5):
            tripped = breaker.record_failure(f"Tool{i}", "Failed")

        # Should trip on fifth failure
        assert tripped
        assert breaker.is_open

    def test_success_resets_half_open(self, circuit_breaker_manager):
        """Test that success in half-open state resets circuit."""
        breaker = circuit_breaker_manager.get_breaker("test_agent")

        # Trip the circuit
        for i in range(3):
            breaker.record_denied(f"Tool{i}", "Denied")

        assert breaker.is_open

        # Force to half-open by advancing time (simulated by force)
        breaker._state = breaker._state.__class__("HalfOpen")

        # Record success
        breaker.record_success()

        assert breaker.is_closed

    def test_force_trip(self, circuit_breaker_manager):
        """Test force tripping a circuit."""
        breaker = circuit_breaker_manager.get_breaker("test_agent")

        breaker.force_trip("Manual intervention")

        assert breaker.is_open
        assert breaker.trip_count == 1

    def test_force_reset(self, circuit_breaker_manager):
        """Test force resetting a circuit."""
        breaker = circuit_breaker_manager.get_breaker("test_agent")

        breaker.force_trip("Test")
        assert breaker.is_open

        breaker.force_reset()
        assert breaker.is_closed

    def test_get_tripped_agents(self, circuit_breaker_manager):
        """Test getting list of tripped agents."""
        # Trip some agents
        for i in range(3):
            breaker = circuit_breaker_manager.get_breaker(f"agent_{i}")
            breaker.force_trip("Test")

        tripped = circuit_breaker_manager.get_tripped_agents()
        assert len(tripped) == 3

    def test_trip_all(self, circuit_breaker_manager):
        """Test tripping all circuits."""
        # Create some breakers
        for i in range(5):
            circuit_breaker_manager.get_breaker(f"agent_{i}")

        count = circuit_breaker_manager.trip_all("Emergency stop")
        assert count == 5

    def test_reset_all(self, circuit_breaker_manager):
        """Test resetting all circuits."""
        # Create and trip some breakers
        for i in range(5):
            breaker = circuit_breaker_manager.get_breaker(f"agent_{i}")
            breaker.force_trip("Test")

        count = circuit_breaker_manager.reset_all()
        assert count == 5

        tripped = circuit_breaker_manager.get_tripped_agents()
        assert len(tripped) == 0


class TestCircuitBreakerStats:
    """Test circuit breaker statistics."""

    def test_get_stats(self, circuit_breaker_manager):
        """Test getting circuit breaker stats."""
        breaker = circuit_breaker_manager.get_breaker("test_agent")

        # Record some events
        breaker.record_denied("Tool1", "Denied")
        breaker.record_failure("Tool2", "Failed")

        stats = breaker.get_stats()

        assert stats["agent_id"] == "test_agent"
        assert stats["state"] == "Closed"
        assert stats["recent_denials"] == 1
        assert stats["recent_failures"] == 1
