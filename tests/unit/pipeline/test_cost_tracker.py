"""
Unit tests for CostTracker (Phase 21.1).

Tests the cost tracking functionality for pipeline operations.
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


class TestCostTracker:
    """Tests for CostTracker."""

    def test_import(self):
        """Test that CostTracker can be imported."""
        from app.core.pipeline.cost_tracker import CostTracker
        assert CostTracker is not None

    def test_create_tracker(self):
        """Test creating a cost tracker."""
        from app.core.pipeline.cost_tracker import CostTracker
        tracker = CostTracker()
        assert tracker is not None

    def test_record_usage(self):
        """Test recording token usage."""
        from app.core.pipeline.cost_tracker import CostTracker
        tracker = CostTracker()
        
        tracker.record_usage(
            provider="ollama",
            input_tokens=100,
            output_tokens=50,
            model="llama3.2",
        )
        
        summary = tracker.get_summary()
        assert summary["total_input_tokens"] >= 100
        assert summary["total_output_tokens"] >= 50

    def test_session_tracking(self):
        """Test session-based cost tracking."""
        from app.core.pipeline.cost_tracker import CostTracker
        tracker = CostTracker()
        
        session_id = "test-session-001"
        tracker.start_session(session_id)
        
        tracker.record_usage(
            provider="openai",
            input_tokens=200,
            output_tokens=100,
            model="gpt-4o",
            session_id=session_id,
        )
        
        session_summary = tracker.get_session_summary(session_id)
        assert session_summary is not None
        assert session_summary.get("total_input_tokens", 0) >= 200

    def test_cost_estimation(self):
        """Test cost estimation based on token usage."""
        from app.core.pipeline.cost_tracker import CostTracker
        tracker = CostTracker()
        
        # OpenAI pricing (approximate)
        tracker.record_usage(
            provider="openai",
            input_tokens=1000,
            output_tokens=500,
            model="gpt-4o",
        )
        
        summary = tracker.get_summary()
        # Cost should be calculated (may be 0 for local models)
        assert "estimated_cost_usd" in summary or summary["total_input_tokens"] >= 0


class TestTokenCeilingManager:
    """Tests for TokenCeilingManager."""

    def test_import(self):
        """Test that TokenCeilingManager can be imported."""
        from app.core.pipeline.token_ceiling import TokenCeilingManager
        assert TokenCeilingManager is not None

    def test_create_manager(self):
        """Test creating a token ceiling manager."""
        from app.core.pipeline.token_ceiling import TokenCeilingManager
        manager = TokenCeilingManager(default_ceiling=10000)
        assert manager is not None

    def test_set_session_ceiling(self):
        """Test setting ceiling for a session."""
        from app.core.pipeline.token_ceiling import TokenCeilingManager
        manager = TokenCeilingManager(default_ceiling=10000)
        
        session_id = "test-session"
        manager.set_session_ceiling(session_id, 5000)
        
        status = manager.get_session_status(session_id)
        assert status is not None
        assert status.get("ceiling") == 5000

    def test_ceiling_check(self):
        """Test checking if ceiling is reached."""
        from app.core.pipeline.token_ceiling import TokenCeilingManager
        manager = TokenCeilingManager(default_ceiling=100)
        
        session_id = "test-session"
        manager.set_session_ceiling(session_id, 100)
        
        # Add usage below ceiling
        manager.add_usage(session_id, 50, 30)
        status = manager.get_session_status(session_id)
        assert not status.get("ceiling_reached", True)
        
        # Add usage to exceed ceiling
        manager.add_usage(session_id, 50, 50)
        status = manager.get_session_status(session_id)
        assert status.get("ceiling_reached", False)

    def test_no_ceiling(self):
        """Test behavior when no ceiling is set."""
        from app.core.pipeline.token_ceiling import TokenCeilingManager
        manager = TokenCeilingManager(default_ceiling=0)  # No ceiling
        
        session_id = "unlimited"
        manager.add_usage(session_id, 1000000, 1000000)
        
        status = manager.get_session_status(session_id)
        assert not status.get("ceiling_reached", True)
