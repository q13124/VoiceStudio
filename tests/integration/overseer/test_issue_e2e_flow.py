"""
Integration tests for Overseer issue system end-to-end flow.

Verifies: record -> store -> query -> recommendations -> feedback -> calibration,
and metrics export. Uses temp directories for store and feedback.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Project root
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Skip entire module if tools.overseer is not available
try:
    from tools.overseer.issues.aggregator import record_issue
except ImportError:
    pytest.skip("tools.overseer module not available", allow_module_level=True)

from tools.overseer.issues.aggregator import record_issue
from tools.overseer.issues.metrics import get_affected_slos, get_prometheus_metrics
from tools.overseer.issues.models import InstanceType, IssueSeverity
from tools.overseer.issues.recommendation_engine import (
    generate_recommendations,
    get_action_success_rate,
    record_recommendation_outcome,
)
from tools.overseer.issues.store import IssueStore


@pytest.fixture
def temp_dirs(tmp_path: Path):
    """Temp dirs for issue store and feedback file."""
    store_dir = tmp_path / "issues"
    store_dir.mkdir()
    feedback_path = tmp_path / "recommendation_feedback.jsonl"
    return {"store_dir": store_dir, "feedback_path": feedback_path}


@pytest.fixture
def temp_store(temp_dirs):
    """IssueStore backed by temp dir."""
    return IssueStore(
        storage_dir=temp_dirs["store_dir"],
        max_file_size_mb=1,
        retention_days=90,
    )


def _patch_store(store: IssueStore):
    return patch("tools.overseer.issues.aggregator._get_store", return_value=store)


def _patch_feedback(path: Path):
    return patch("tools.overseer.issues.store.get_feedback_file_path", return_value=path)


class TestIssueE2EFlow:
    """Record -> query -> recommendations -> feedback -> calibration."""

    def test_record_query_recommendations(
        self,
        temp_store: IssueStore,
        temp_dirs,
    ) -> None:
        with _patch_store(temp_store):
            issue = record_issue(
                instance_type=InstanceType.ENGINE,
                instance_id="test-engine",
                correlation_id="e2e-correlation",
                error_type="ValueError",
                message="Test integration error",
                context={"step": "integration"},
                severity=IssueSeverity.MEDIUM,
                category="engine",
            )
        assert issue.id

        issues = temp_store.query(limit=10)
        assert len(issues) >= 1
        found = next((i for i in issues if i.id == issue.id), None)
        assert found is not None
        assert found.message == "Test integration error"

        with _patch_store(temp_store):
            recs = generate_recommendations(found)
        assert isinstance(recs, list)
        assert len(recs) >= 1
        assert all(hasattr(r, "action") and hasattr(r, "confidence") for r in recs)

    def test_feedback_and_calibration(
        self,
        temp_store: IssueStore,
        temp_dirs,
    ) -> None:
        feedback_path = temp_dirs["feedback_path"]
        feedback_path.parent.mkdir(parents=True, exist_ok=True)

        with _patch_feedback(feedback_path):
            assert (
                record_recommendation_outcome("issue-1", "retry_with_params", "success", note="e2e")
                is True
            )
            assert record_recommendation_outcome("issue-2", "retry_with_params", "failure") is True

        with _patch_feedback(feedback_path):
            rate = get_action_success_rate("retry_with_params", days=90)
        assert rate is not None
        assert rate == pytest.approx(0.5, abs=0.01)


class TestMetricsAndSLO:
    """Prometheus metrics and SLO linkage."""

    def test_prometheus_metrics_with_temp_store(
        self,
        temp_store: IssueStore,
        temp_dirs,
    ) -> None:
        with _patch_store(temp_store):
            record_issue(
                instance_type=InstanceType.ENGINE,
                instance_id="metrics-test",
                correlation_id="m1",
                error_type="TestError",
                message="For metrics",
                context={},
                severity=IssueSeverity.HIGH,
                category="engine",
            )
        with _patch_store(temp_store):
            text = get_prometheus_metrics(store=temp_store, time_window_hours=24)
        assert "overseer_issues_total" in text
        assert "high" in text or "total" in text

    def test_get_affected_slos(self) -> None:
        assert get_affected_slos("engine") == ["SLO-5"]
        assert get_affected_slos("synthesis") == ["SLO-1"]
        assert get_affected_slos("unknown") == ["SLO-3"]
