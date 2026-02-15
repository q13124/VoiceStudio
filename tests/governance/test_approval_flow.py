"""
Tests for approval flow.
"""

from datetime import datetime, timedelta


class TestApprovalManager:
    """Test the approval manager functionality."""

    def test_create_request(self, approval_manager, agent_identity):
        """Test creating an approval request."""
        request = approval_manager.create_request(
            agent_id=agent_identity.agent_id,
            user_id=agent_identity.user_id,
            correlation_id=agent_identity.correlation_id,
            tool_name="RunProcess",
            parameters={"exe": "python", "args": ["script.py"]},
            risk_tier="high",
            reason="Running external process",
        )

        assert request.request_id is not None
        assert request.status.value == "Pending"
        assert request.is_pending
        assert request.tool_name == "RunProcess"

    def test_approve_request(self, approval_manager, agent_identity):
        """Test approving a request."""
        request = approval_manager.create_request(
            agent_id=agent_identity.agent_id,
            user_id=agent_identity.user_id,
            correlation_id=agent_identity.correlation_id,
            tool_name="RunProcess",
            parameters={},
            risk_tier="high",
            reason="Test",
        )

        result = approval_manager.approve(
            request_id=request.request_id,
            decided_by="test_approver",
            reason="Approved for testing",
        )

        assert result

        # Check request was updated
        updated = approval_manager.get_request(request.request_id)
        assert updated.status.value == "Approved"
        assert updated.decided_by == "test_approver"

    def test_deny_request(self, approval_manager, agent_identity):
        """Test denying a request."""
        request = approval_manager.create_request(
            agent_id=agent_identity.agent_id,
            user_id=agent_identity.user_id,
            correlation_id=agent_identity.correlation_id,
            tool_name="HttpRequest",
            parameters={"url": "http://external.com"},
            risk_tier="high",
            reason="External network access",
        )

        result = approval_manager.deny(
            request_id=request.request_id,
            decided_by="test_approver",
            reason="Not allowed",
        )

        assert result

        updated = approval_manager.get_request(request.request_id)
        assert updated.status.value == "Denied"

    def test_get_pending_requests(self, approval_manager, agent_identity):
        """Test getting pending requests."""
        # Create multiple requests
        for i in range(3):
            approval_manager.create_request(
                agent_id=agent_identity.agent_id,
                user_id=agent_identity.user_id,
                correlation_id=agent_identity.correlation_id,
                tool_name=f"Tool{i}",
                parameters={},
                risk_tier="high",
                reason=f"Request {i}",
            )

        pending = approval_manager.get_pending_requests()
        assert len(pending) == 3

    def test_request_expiration(self, approval_manager, agent_identity):
        """Test that requests expire."""
        request = approval_manager.create_request(
            agent_id=agent_identity.agent_id,
            user_id=agent_identity.user_id,
            correlation_id=agent_identity.correlation_id,
            tool_name="Test",
            parameters={},
            risk_tier="high",
            reason="Test",
            timeout_minutes=0,  # Immediate expiration
        )

        # Force expiration by setting expires_at to past
        request.expires_at = datetime.now() - timedelta(minutes=1)

        assert request.is_expired
        assert not request.is_pending

    def test_cancel_request(self, approval_manager, agent_identity):
        """Test canceling a request."""
        request = approval_manager.create_request(
            agent_id=agent_identity.agent_id,
            user_id=agent_identity.user_id,
            correlation_id=agent_identity.correlation_id,
            tool_name="Test",
            parameters={},
            risk_tier="high",
            reason="Test",
        )

        result = approval_manager.cancel(request.request_id)
        assert result

        updated = approval_manager.get_request(request.request_id)
        assert updated.status.value == "Cancelled"


class TestApprovalHistory:
    """Test approval history functionality."""

    def test_get_history(self, approval_manager, agent_identity):
        """Test getting approval history."""
        # Create and decide on some requests
        for i in range(5):
            request = approval_manager.create_request(
                agent_id=agent_identity.agent_id,
                user_id=agent_identity.user_id,
                correlation_id=agent_identity.correlation_id,
                tool_name=f"Tool{i}",
                parameters={},
                risk_tier="high",
                reason=f"Request {i}",
            )

            if i % 2 == 0:
                approval_manager.approve(request.request_id, "approver", "OK")
            else:
                approval_manager.deny(request.request_id, "approver", "Not OK")

        history = approval_manager.get_history()
        assert len(history) == 5
