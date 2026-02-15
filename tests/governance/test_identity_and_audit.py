"""
Tests for agent identity and audit logging.
"""

from datetime import datetime


class TestAgentIdentity:
    """Test agent identity functionality."""

    def test_create_identity(self):
        """Test creating an agent identity."""
        from agent.identity import AgentIdentity, AgentRole

        identity = AgentIdentity.create(
            role=AgentRole.CODER,
            user_id="test_user",
            config={"model": "gpt-4"},
        )

        assert identity.agent_id is not None
        assert identity.role == AgentRole.CODER
        assert identity.user_id == "test_user"
        assert identity.config_hash != ""
        assert identity.correlation_id != ""

    def test_identity_state_transitions(self):
        """Test valid state transitions."""
        from agent.identity import AgentIdentity, AgentRole, AgentState

        identity = AgentIdentity.create(
            role=AgentRole.TESTER,
            user_id="user",
        )

        # Created -> Running is valid
        assert identity.state == AgentState.CREATED
        assert identity.transition_to(AgentState.RUNNING)
        assert identity.state == AgentState.RUNNING

        # Running -> Completed is valid
        assert identity.transition_to(AgentState.COMPLETED)
        assert identity.state == AgentState.COMPLETED

    def test_invalid_state_transition(self):
        """Test invalid state transitions are rejected."""
        from agent.identity import AgentIdentity, AgentRole, AgentState

        identity = AgentIdentity.create(
            role=AgentRole.CODER,
            user_id="user",
        )

        # Created -> Completed is NOT valid (must go through Running)
        assert not identity.transition_to(AgentState.COMPLETED)
        assert identity.state == AgentState.CREATED

    def test_identity_serialization(self):
        """Test identity serialization round-trip."""
        from agent.identity import AgentIdentity, AgentRole

        identity = AgentIdentity.create(
            role=AgentRole.SUPPORT,
            user_id="user",
        )

        data = identity.to_dict()
        restored = AgentIdentity.from_dict(data)

        assert restored.agent_id == identity.agent_id
        assert restored.role == identity.role
        assert restored.user_id == identity.user_id


class TestAgentRegistry:
    """Test agent registry functionality."""

    def test_register_agent(self, agent_registry, agent_identity):
        """Test registering an agent."""
        agent_registry.register(agent_identity)

        retrieved = agent_registry.get(agent_identity.agent_id)
        assert retrieved is not None
        assert retrieved.agent_id == agent_identity.agent_id

    def test_unregister_agent(self, agent_registry, agent_identity):
        """Test unregistering an agent."""
        agent_registry.register(agent_identity)

        result = agent_registry.unregister(agent_identity.agent_id)
        assert result

        retrieved = agent_registry.get(agent_identity.agent_id)
        assert retrieved is None

    def test_update_state(self, agent_registry, agent_identity):
        """Test updating agent state."""
        from agent.identity import AgentState

        agent_registry.register(agent_identity)

        result = agent_registry.update_state(
            agent_identity.agent_id,
            AgentState.RUNNING,
        )
        assert result

        retrieved = agent_registry.get(agent_identity.agent_id)
        assert retrieved.state == AgentState.RUNNING

    def test_quarantine_agent(self, agent_registry, agent_identity):
        """Test quarantining an agent."""
        from agent.identity import AgentState

        agent_identity.transition_to(AgentState.RUNNING)
        agent_registry.register(agent_identity)

        result = agent_registry.quarantine(agent_identity.agent_id)
        assert result

        retrieved = agent_registry.get(agent_identity.agent_id)
        assert retrieved.state == AgentState.QUARANTINED

    def test_get_active_agents(self, agent_registry):
        """Test getting active agents."""
        from agent.identity import AgentIdentity, AgentRole, AgentState

        # Create active agents
        for _i in range(3):
            identity = AgentIdentity.create(
                role=AgentRole.CODER,
                user_id="user",
            )
            identity.transition_to(AgentState.RUNNING)
            agent_registry.register(identity)

        # Create completed agent
        completed = AgentIdentity.create(
            role=AgentRole.CODER,
            user_id="user",
        )
        completed.transition_to(AgentState.RUNNING)
        completed.transition_to(AgentState.COMPLETED)
        agent_registry.register(completed)

        active = agent_registry.get_active()
        assert len(active) == 3


class TestAuditLogging:
    """Test audit logging functionality."""

    def test_log_success(self, audit_logger, agent_identity):
        """Test logging a successful action."""
        entry = audit_logger.log_success(
            agent=agent_identity,
            tool_name="ReadFile",
            parameters={"path": "/test/file.txt"},
            output_data="file contents",
        )

        assert entry.result == "success"
        assert entry.tool_name == "ReadFile"
        assert entry.agent_id == agent_identity.agent_id

    def test_log_failure(self, audit_logger, agent_identity):
        """Test logging a failed action."""
        try:
            raise ValueError("Test error")
        except Exception as e:
            entry = audit_logger.log_failure(
                agent=agent_identity,
                tool_name="WriteFile",
                parameters={"path": "/test/file.txt"},
                error=e,
            )

        assert entry.result == "failure"
        assert "Test error" in entry.error_stack

    def test_log_denied(self, audit_logger, agent_identity):
        """Test logging a denied action."""
        entry = audit_logger.log_denied(
            agent=agent_identity,
            tool_name="RunProcess",
            parameters={"exe": "powershell"},
            reason="Executable not in allowlist",
        )

        assert entry.result == "denied"
        assert "not in allowlist" in entry.error_stack

    def test_audit_store_query(self, audit_store, agent_identity):
        """Test querying the audit store."""
        from agent.audit_store import AuditEntry

        # Add some entries
        for i in range(5):
            entry = AuditEntry(
                timestamp=datetime.now(),
                agent_id=agent_identity.agent_id,
                user_id=agent_identity.user_id,
                correlation_id=agent_identity.correlation_id,
                tool_name=f"Tool{i}",
                result="success",
            )
            audit_store.append(entry)

        # Query
        results = audit_store.query(agent_id=agent_identity.agent_id)
        assert len(results) == 5

    def test_secret_redaction(self, audit_store):
        """Test that secrets are redacted from logs."""
        from agent.audit_store import AuditEntry

        entry = AuditEntry(
            timestamp=datetime.now(),
            agent_id="agent",
            user_id="user",
            correlation_id="corr",
            tool_name="HttpRequest",
            parameters={
                "url": "http://api.example.com",
                "api_key": "sk-secret-key-12345",
                "password": "supersecret",
            },
        )

        # Redaction happens on append
        audit_store.append(entry)

        # Query back
        results = audit_store.query(tool_name="HttpRequest")
        assert len(results) == 1

        params = results[0].parameters
        assert params["api_key"] == "[REDACTED]"
        assert params["password"] == "[REDACTED]"
        assert params["url"] == "http://api.example.com"  # URL not redacted
