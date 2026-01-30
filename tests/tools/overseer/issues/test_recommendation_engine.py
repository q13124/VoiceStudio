"""Unit tests for Overseer recommendation engine (assess_risk, suggest_actions, generate_recommendations, feedback)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from tools.overseer.issues.models import (
    InstanceType,
    Issue,
    IssueSeverity,
    IssueStatus,
)
from tools.overseer.issues.recommendation_engine import (
    assess_risk,
    generate_recommendations,
    get_action_success_rate,
    record_recommendation_outcome,
    suggest_actions,
)
from tools.overseer.issues.store import IssueStore, get_feedback_file_path
from tools.overseer.issues.pattern_matcher import FailurePattern


def _issue(
    pattern_hash: str = "ph1",
    correlation_id: str = "corr-1",
    severity: IssueSeverity = IssueSeverity.MEDIUM,
    message: str = "Error message",
) -> Issue:
    return Issue(
        id="issue-1",
        timestamp=datetime.now(timezone.utc),
        instance_type=InstanceType.ENGINE,
        instance_id="engine-1",
        correlation_id=correlation_id,
        severity=severity,
        category="Test",
        error_type="ValueError",
        message=message,
        context={},
        pattern_hash=pattern_hash,
        status=IssueStatus.NEW,
        recommendations=[],
        resolved_at=None,
        resolved_by=None,
    )


def _failure_pattern(
    resolution_strategy: str = "",
    resolution_confirmed: bool = False,
    fix_id: str | None = None,
    issue_id: str | None = "past-1",
) -> FailurePattern:
    return FailurePattern(
        pattern="known_pattern",
        normalized_message="error message",
        message_snippet="Error message",
        context={},
        timestamp="2026-01-28T12:00:00",
        issue_id=issue_id,
        resolution_confirmed=resolution_confirmed,
        fix_id=fix_id,
        resolution_strategy=resolution_strategy,
    )


@pytest.fixture
def feedback_dir(tmp_path: Path) -> Path:
    """Use a temp dir for recommendation feedback file in tests."""
    return tmp_path


@pytest.fixture
def temp_store(tmp_path: Path) -> IssueStore:
    return IssueStore(
        storage_dir=tmp_path,
        max_file_size_mb=1,
        retention_days=90,
    )


class TestAssessRisk:
    def test_assess_risk_returns_dict_with_expected_keys(self, temp_store: IssueStore) -> None:
        issue = _issue()
        temp_store.append(issue)
        with patch("tools.overseer.issues.recommendation_engine._get_store", return_value=temp_store):
            risk = assess_risk(issue)
        assert "score" in risk
        assert "frequency_24h" in risk
        assert "blast_radius" in risk
        assert "trend" in risk
        assert "related_systems" in risk
        assert risk["frequency_24h"] >= 1
        assert risk["blast_radius"] >= 1

    def test_assess_risk_higher_severity_higher_score(self, temp_store: IssueStore) -> None:
        low_issue = _issue(severity=IssueSeverity.LOW)
        critical_issue = _issue(severity=IssueSeverity.CRITICAL)
        temp_store.append(low_issue)
        temp_store.append(critical_issue)
        with patch("tools.overseer.issues.recommendation_engine._get_store", return_value=temp_store):
            risk_low = assess_risk(low_issue)
            risk_critical = assess_risk(critical_issue)
        assert risk_critical["score"] >= risk_low["score"]


class TestSuggestActions:
    def test_no_matches_yields_investigate(self, temp_store: IssueStore) -> None:
        issue = _issue()
        temp_store.append(issue)
        with patch("tools.overseer.issues.recommendation_engine._get_store", return_value=temp_store):
            recs = suggest_actions(issue, [])
        assert len(recs) >= 1
        assert recs[0].action == "investigate"
        assert recs[0].confidence == 0.5

    def test_parameter_adjustment_pattern_yields_retry_with_params(self, temp_store: IssueStore) -> None:
        issue = _issue()
        temp_store.append(issue)
        pattern = _failure_pattern(resolution_strategy="parameter_adjustment")
        with patch("tools.overseer.issues.recommendation_engine._get_store", return_value=temp_store):
            recs = suggest_actions(issue, [(pattern, 0.9)])
        assert any(r.action == "retry_with_params" for r in recs)

    def test_resolution_confirmed_yields_apply_fix(self, temp_store: IssueStore) -> None:
        issue = _issue()
        temp_store.append(issue)
        pattern = _failure_pattern(resolution_confirmed=True, fix_id="fix-123")
        with patch("tools.overseer.issues.recommendation_engine._get_store", return_value=temp_store):
            recs = suggest_actions(issue, [(pattern, 0.9)])
        assert any(r.action == "apply_fix:fix-123" for r in recs)

    def test_critical_no_matches_yields_escalate_to_human(self, temp_store: IssueStore) -> None:
        issue = _issue(severity=IssueSeverity.CRITICAL)
        temp_store.append(issue)
        with patch("tools.overseer.issues.recommendation_engine._get_store", return_value=temp_store):
            recs = suggest_actions(issue, [])
        assert any(r.action == "escalate_to_human" for r in recs)
        assert any(r.confidence == 1.0 for r in recs)


class TestGenerateRecommendations:
    def test_generate_recommendations_returns_list(self, temp_store: IssueStore) -> None:
        issue = _issue()
        temp_store.append(issue)
        with patch("tools.overseer.issues.recommendation_engine._get_store", return_value=temp_store):
            recs = generate_recommendations(issue)
        assert isinstance(recs, list)
        assert len(recs) >= 1
        assert all(hasattr(r, "action") and hasattr(r, "confidence") for r in recs)
        assert all(hasattr(r, "risk_assessment") for r in recs)


class TestRecordRecommendationOutcome:
    def test_record_accepts_success_failure_deferred(self, feedback_dir: Path) -> None:
        with patch("tools.overseer.issues.store.get_feedback_file_path", return_value=feedback_dir / "feedback.jsonl"):
            assert record_recommendation_outcome("i1", "retry_with_params", "success") is True
            assert record_recommendation_outcome("i2", "apply_fix:fix-1", "failure", note="n") is True
            assert record_recommendation_outcome("i3", "restart", "deferred") is True

    def test_record_rejects_invalid_outcome(self, feedback_dir: Path) -> None:
        with patch("tools.overseer.issues.store.get_feedback_file_path", return_value=feedback_dir / "feedback.jsonl"):
            assert record_recommendation_outcome("i1", "retry_with_params", "invalid") is False
            assert record_recommendation_outcome("i1", "retry_with_params", "") is False


class TestGetActionSuccessRate:
    def test_empty_feedback_returns_none(self, feedback_dir: Path) -> None:
        with patch("tools.overseer.issues.store.get_feedback_file_path", return_value=feedback_dir / "feedback.jsonl"):
            assert get_action_success_rate("retry_with_params") is None

    def test_success_rate_calibrated_from_feedback(self, feedback_dir: Path) -> None:
        path = feedback_dir / "feedback.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        with open(path, "w", encoding="utf-8") as f:
            f.write('{"issue_id":"a","action":"retry_with_params","outcome":"success","applied_at":"' + now + '"}\n')
            f.write('{"issue_id":"b","action":"retry_with_params","outcome":"failure","applied_at":"' + now + '"}\n')
            f.write('{"issue_id":"c","action":"retry_with_params","outcome":"success","applied_at":"' + now + '"}\n')
        with patch("tools.overseer.issues.store.get_feedback_file_path", return_value=path):
            rate = get_action_success_rate("retry_with_params", days=90)
        assert rate is not None
        assert rate == pytest.approx(2 / 3, abs=0.01)


class TestSuggestActionsRollbackRestartDefer:
    def test_rollback_strategy_suggested(self, temp_store: IssueStore) -> None:
        issue = _issue()
        temp_store.append(issue)
        pattern = _failure_pattern(resolution_strategy="rollback")
        with patch("tools.overseer.issues.recommendation_engine._get_store", return_value=temp_store):
            recs = suggest_actions(issue, [(pattern, 0.85)])
        assert any(r.action == "rollback" for r in recs)

    def test_restart_strategy_suggested(self, temp_store: IssueStore) -> None:
        issue = _issue()
        temp_store.append(issue)
        pattern = _failure_pattern(resolution_strategy="restart")
        with patch("tools.overseer.issues.recommendation_engine._get_store", return_value=temp_store):
            recs = suggest_actions(issue, [(pattern, 0.85)])
        assert any(r.action == "restart" for r in recs)

    def test_low_severity_no_match_yields_defer(self, temp_store: IssueStore) -> None:
        issue = _issue(severity=IssueSeverity.LOW)
        temp_store.append(issue)
        with patch("tools.overseer.issues.recommendation_engine._get_store", return_value=temp_store):
            recs = suggest_actions(issue, [])
        assert any(r.action == "defer" for r in recs)
