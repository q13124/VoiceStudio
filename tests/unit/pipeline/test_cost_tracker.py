"""
Unit tests for CostTracker and TokenCeilingManager (Phase 10.3).

Tests the cost tracking functionality for pipeline operations.
"""

import tempfile
import time

import pytest


class TestCostTracker:
    """Tests for CostTracker."""

    def test_import(self):
        """Test that CostTracker can be imported."""
        from app.core.pipeline.cost_tracker import CostTracker
        assert CostTracker is not None

    def test_create_tracker(self):
        """Test creating a cost tracker."""
        from app.core.pipeline.cost_tracker import CostTracker
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(data_dir=tmpdir)
            assert tracker is not None

    def test_record_session(self):
        """Test recording a session cost entry."""
        from app.core.pipeline.cost_tracker import CostTracker, SessionCostEntry
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(data_dir=tmpdir)

            entry = SessionCostEntry(
                session_id="test-session-001",
                provider="openai",
                total_tokens=150,
                turn_count=3,
                duration_seconds=60.0,
                estimated_cost_usd=0.0015,
                ceiling_triggered=False,
                timestamp=time.time(),
            )
            tracker.record_session(entry)

            summary = tracker.get_summary()
            assert summary["total_sessions"] == 1
            assert summary["total_cost_usd"] >= 0.0015

    def test_multiple_sessions(self):
        """Test tracking multiple sessions."""
        from app.core.pipeline.cost_tracker import CostTracker, SessionCostEntry
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(data_dir=tmpdir)

            for i in range(3):
                entry = SessionCostEntry(
                    session_id=f"session-{i}",
                    provider="openai",
                    total_tokens=100,
                    turn_count=2,
                    duration_seconds=30.0,
                    estimated_cost_usd=0.001,
                    ceiling_triggered=False,
                    timestamp=time.time(),
                )
                tracker.record_session(entry)

            summary = tracker.get_summary()
            assert summary["total_sessions"] == 3

    def test_cost_summary(self):
        """Test cost summary calculation."""
        from app.core.pipeline.cost_tracker import CostTracker, SessionCostEntry
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(data_dir=tmpdir)

            entry = SessionCostEntry(
                session_id="test-session",
                provider="openai",
                total_tokens=1000,
                turn_count=5,
                duration_seconds=120.0,
                estimated_cost_usd=0.01,
                ceiling_triggered=False,
                timestamp=time.time(),
            )
            tracker.record_session(entry)

            summary = tracker.get_summary()
            assert "total_sessions" in summary
            assert "total_cost_usd" in summary
            assert "avg_cost_per_session" in summary

    def test_empty_summary(self):
        """Test summary when no sessions recorded."""
        from app.core.pipeline.cost_tracker import CostTracker
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(data_dir=tmpdir)

            summary = tracker.get_summary()
            assert summary["total_sessions"] == 0
            assert summary["total_cost_usd"] == 0.0


class TestTokenCeilingManager:
    """Tests for TokenCeilingManager."""

    def test_import(self):
        """Test that TokenCeilingManager can be imported."""
        from app.core.pipeline.token_ceiling import TokenCeilingManager
        assert TokenCeilingManager is not None

    def test_create_manager(self):
        """Test creating a token ceiling manager."""
        from app.core.pipeline.token_ceiling import TokenCeilingManager
        manager = TokenCeilingManager()
        assert manager is not None

    def test_start_session(self):
        """Test starting a session."""
        from app.core.pipeline.token_ceiling import TokenCeilingManager
        manager = TokenCeilingManager()

        session_id = "test-session"
        manager.start_session(session_id, provider="openai")

        status = manager.get_session_status(session_id)
        assert status is not None
        assert status["session_id"] == session_id

    def test_record_usage(self):
        """Test recording token usage."""
        from app.core.pipeline.token_ceiling import TokenCeilingManager
        manager = TokenCeilingManager()

        session_id = "test-session"
        manager.start_session(session_id, provider="openai")

        result = manager.record_usage(session_id, input_tokens=100, output_tokens=50)
        assert result is not None
        assert result["total_tokens"] == 150

    def test_ceiling_check(self):
        """Test checking if ceiling is reached."""
        from app.core.pipeline.token_ceiling import CeilingConfig, TokenCeilingManager
        config = CeilingConfig(hard_ceiling_tokens=100, soft_ceiling_tokens=50)
        manager = TokenCeilingManager(config=config)

        session_id = "test-session"
        manager.start_session(session_id, provider="openai")

        # Add usage below ceiling
        result = manager.record_usage(session_id, input_tokens=30, output_tokens=20)
        assert not result.get("should_switch", True)

        # Add usage to exceed ceiling
        result = manager.record_usage(session_id, input_tokens=60, output_tokens=40)
        assert result.get("should_switch", False)

    def test_no_ceiling_with_large_limit(self):
        """Test behavior with very high ceiling."""
        from app.core.pipeline.token_ceiling import CeilingConfig, TokenCeilingManager
        config = CeilingConfig(hard_ceiling_tokens=1000000000)  # Very high limit
        manager = TokenCeilingManager(config=config)

        session_id = "unlimited"
        manager.start_session(session_id, provider="local")
        manager.record_usage(session_id, input_tokens=100000, output_tokens=100000)

        status = manager.get_session_status(session_id)
        assert not status.get("ceiling_reached", True)

    def test_end_session(self):
        """Test ending a session."""
        from app.core.pipeline.token_ceiling import TokenCeilingManager
        manager = TokenCeilingManager()

        session_id = "test-session"
        manager.start_session(session_id, provider="openai")
        manager.record_usage(session_id, input_tokens=100, output_tokens=50)

        final_status = manager.end_session(session_id)
        assert final_status is not None
        assert final_status["total_tokens"] == 150

        # Session should no longer exist
        assert manager.get_session_status(session_id) is None
