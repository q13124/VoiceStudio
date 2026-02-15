"""
Overseer Recommendation Engine.

Generates recommendations with pattern matching and risk assessment.
Supports feedback tracking (outcome recording) and confidence calibration
from historical success rates. Strategies include retry, apply_fix,
rollback, restart, defer, escalate, and investigate.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from tools.overseer.issues.aggregator import _get_store
from tools.overseer.issues.config import (
    BLAST_RADIUS_WEIGHT,
    FREQUENCY_WEIGHT,
    PATTERN_SIMILARITY_THRESHOLD,
    SEVERITY_WEIGHT,
)
from tools.overseer.issues.models import (
    Issue,
    IssueSeverity,
    Recommendation,
)
from tools.overseer.issues.pattern_matcher import (
    FailurePattern,
    match_patterns,
)
from tools.overseer.issues.store import append_feedback_line, iter_feedback_lines


def assess_risk(issue: Issue) -> dict[str, Any]:
    """
    Assess risk for an issue (frequency, blast radius, severity).

    Returns dict with score, frequency_24h, blast_radius, trend, related_systems.
    """
    store = _get_store()
    frequency = store.count_by_pattern_hash(issue.pattern_hash, hours=24)
    correlated = store.get_by_correlation(issue.correlation_id)
    blast_radius = len({i.instance_id for i in correlated})
    severity_weight = {
        IssueSeverity.LOW: 1,
        IssueSeverity.MEDIUM: 2,
        IssueSeverity.HIGH: 3,
        IssueSeverity.CRITICAL: 4,
    }.get(issue.severity, 2)
    risk_score = (
        min(frequency, 10) * FREQUENCY_WEIGHT
        + min(blast_radius, 10) * BLAST_RADIUS_WEIGHT
        + severity_weight * SEVERITY_WEIGHT
    )
    return {
        "score": round(risk_score, 2),
        "frequency_24h": frequency,
        "blast_radius": blast_radius,
        "trend": "increasing" if frequency > 1 else "single",
        "related_systems": list({i.instance_type.value for i in correlated}),
    }


def _action_type_for_rate(action: str) -> str:
    """Normalize action to a type key for success-rate lookup (e.g. apply_fix:xyz -> apply_fix)."""
    if action.startswith("apply_fix:"):
        return "apply_fix"
    return action


def get_action_success_rate(action: str, days: int = 90) -> float | None:
    """
    Return empirical success rate for an action from feedback (success / (success + failure)).
    Returns None if no feedback for that action in the window.
    """
    action_type = _action_type_for_rate(action)
    success = 0
    failure = 0
    for data in iter_feedback_lines(days=days):
        if _action_type_for_rate(data.get("action", "")) != action_type:
            continue
        outcome = (data.get("outcome") or "").lower()
        if outcome == "success":
            success += 1
        elif outcome == "failure":
            failure += 1
    total = success + failure
    if total == 0:
        return None
    return round(success / total, 3)


def record_recommendation_outcome(
    issue_id: str,
    action: str,
    outcome: str,
    note: str | None = None,
) -> bool:
    """
    Record that a recommendation was applied and its outcome (success, failure, deferred).
    Used for action validation and confidence calibration.
    """
    outcome = (outcome or "").lower()
    if outcome not in ("success", "failure", "deferred"):
        return False
    record = {
        "issue_id": issue_id,
        "action": action,
        "outcome": outcome,
        "applied_at": datetime.now(timezone.utc).isoformat(),
        "note": note,
    }
    try:
        append_feedback_line(json.dumps(record, separators=(",", ":")))
        return True
    except Exception:
        return False


def suggest_actions(
    issue: Issue,
    matched_patterns: list[tuple[FailurePattern, float]],
) -> list[Recommendation]:
    """
    Suggest recommended actions for an issue given matched patterns.

    Returns list of Recommendation: retry_with_params, apply_fix, rollback,
    restart, defer, escalate_to_human, investigate. Confidence is calibrated
    from historical feedback when available.
    """
    recommendations: list[Recommendation] = []
    risk = assess_risk(issue)
    seen_actions: set = set()

    def _add(action: str, default_confidence: float, rationale: str, similar: list[str]) -> None:
        if action in seen_actions:
            return
        seen_actions.add(action)
        calibrated = get_action_success_rate(action)
        confidence = default_confidence if calibrated is None else calibrated
        recommendations.append(
            Recommendation(
                action=action,
                confidence=confidence,
                rationale=rationale,
                similar_issues=list(similar) if similar else [],
                risk_assessment=risk,
            )
        )

    # Parameter adjustment -> retry_with_params
    if any(
        getattr(p, "resolution_strategy", "") == "parameter_adjustment"
        for p, _ in matched_patterns
    ):
        _add(
            "retry_with_params",
            0.8,
            "Similar issue resolved by adjusting parameters",
            [p.issue_id for p, _ in matched_patterns[:3] if p.issue_id],
        )

    # Resolution confirmed -> apply_fix
    for pattern, _ in matched_patterns:
        if getattr(pattern, "resolution_confirmed", False):
            fix_id = getattr(pattern, "fix_id", None) or "unknown"
            action = f"apply_fix:{fix_id}"
            if action not in seen_actions:
                seen_actions.add(action)
                conf = get_action_success_rate(action)
                if conf is None:
                    conf = 0.9
                recommendations.append(
                    Recommendation(
                        action=action,
                        confidence=conf,
                        rationale=f"Proven fix for {pattern.pattern}",
                        similar_issues=[pattern.issue_id] if pattern.issue_id else [],
                        risk_assessment=risk,
                    )
                )

    # Pattern suggests rollback or restart
    for pattern, _ in matched_patterns:
        strategy = getattr(pattern, "resolution_strategy", "") or ""
        if strategy == "rollback":
            _add("rollback", 0.75, "Similar issue resolved by rolling back change", [])
            break
        if strategy == "restart":
            _add("restart", 0.75, "Similar issue resolved by restarting process/service", [])
            break

    # Low severity and no strong match -> defer
    if issue.severity == IssueSeverity.LOW and not recommendations:
        _add(
            "defer",
            0.6,
            "Low severity; can be deferred if not blocking",
            [],
        )

    # Critical with no automated path -> escalate
    if issue.severity == IssueSeverity.CRITICAL and not any(
        r.action == "escalate_to_human" for r in recommendations
    ):
        _add(
            "escalate_to_human",
            1.0,
            "Critical issue with no known automated resolution",
            [],
        )

    # Fallback: investigate
    if not recommendations:
        _add(
            "investigate",
            0.5,
            "No matching pattern; manual investigation recommended",
            [],
        )

    return recommendations


def generate_recommendations(issue: Issue) -> list[Recommendation]:
    """
    Main entry: generate recommendations for an issue.

    Uses pattern matching and risk assessment.
    """
    matched = match_patterns(issue, threshold=PATTERN_SIMILARITY_THRESHOLD)
    return suggest_actions(issue, matched)


def learn_from_resolution(
    issue_id: str,
    resolution_note: str,
    fix_id: str | None = None,
) -> bool:
    """
    Update learned patterns when an issue is resolved.

    Optional: call from CLI resolve command to record resolution.
    """
    try:
        import os
        from pathlib import Path

        from tools.overseer.learning.failure_analyzer import (
            DEFAULT_PATTERNS_PATH,
        )
        root = Path(__file__).resolve().parents[3]
        path = root / DEFAULT_PATTERNS_PATH.replace("/", os.sep)
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "issue_id": issue_id,
            "resolution_note": resolution_note,
            "fix_id": fix_id,
            "resolution_confirmed": True,
        }
        with path.open("a", encoding="utf-8") as f:
            import json
            f.write(json.dumps({"pattern": resolution_note, "context": entry}) + "\n")
        return True
    except Exception:
        return False
