"""
Anomaly Detector

Detects suspicious patterns in agent behavior.
Triggers alerts and quarantine for potential security issues.
"""

from __future__ import annotations

import threading
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class AnomalyType(str, Enum):
    """Types of anomalies that can be detected."""

    RAPID_FIRE = "RapidFire"                   # Too many actions too fast
    REPEATED_DENIAL = "RepeatedDenial"         # Same action denied repeatedly
    SAFE_ZONE_PROBE = "SafeZoneProbe"          # Multiple attempts at protected areas
    UNUSUAL_PATTERN = "UnusualPattern"         # Deviation from normal behavior
    ESCALATION_ATTEMPT = "EscalationAttempt"   # Trying to access higher-risk tools
    PARAMETER_FUZZING = "ParameterFuzzing"     # Varying parameters systematically


class AnomalySeverity(str, Enum):
    """Severity levels for anomalies."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


@dataclass
class AnomalyEvent:
    """
    A detected anomaly event.

    Attributes:
        timestamp: When the anomaly was detected
        agent_id: ID of the agent exhibiting the behavior
        anomaly_type: Type of anomaly
        severity: Severity level
        description: Human-readable description
        evidence: Supporting evidence for the detection
        recommended_action: Suggested response
    """

    timestamp: datetime
    agent_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    description: str
    evidence: list[dict] = field(default_factory=list)
    recommended_action: str = "review"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "anomaly_type": self.anomaly_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "evidence": self.evidence,
            "recommended_action": self.recommended_action,
        }


@dataclass
class DetectorConfig:
    """
    Configuration for anomaly detection.

    Attributes:
        rapid_fire_threshold: Actions per minute to trigger rapid fire
        repeated_denial_threshold: Same denial count to trigger alert
        safe_zone_probe_threshold: Safe zone attempts to trigger alert
        tracking_window_minutes: How long to track behavior
        baseline_window_hours: How long to build behavior baseline
    """

    rapid_fire_threshold: int = 60
    repeated_denial_threshold: int = 3
    safe_zone_probe_threshold: int = 2
    tracking_window_minutes: int = 10
    baseline_window_hours: int = 24


@dataclass
class ActionRecord:
    """Record of an agent action for analysis."""

    timestamp: datetime
    tool_name: str
    parameters_hash: str
    result: str  # success/failure/denied
    risk_tier: str
    violation_type: str | None = None


class AnomalyDetector:
    """
    Detects anomalous agent behavior patterns.

    Analyzes action history to identify potential security issues
    or misbehaving agents.
    """

    def __init__(
        self,
        config: DetectorConfig | None = None,
        on_anomaly: Callable[[AnomalyEvent], None] | None = None,
    ):
        """
        Initialize the detector.

        Args:
            config: Detection configuration
            on_anomaly: Callback when anomaly is detected
        """
        self._config = config or DetectorConfig()
        self._on_anomaly = on_anomaly

        # Per-agent action history
        self._history: dict[str, deque[ActionRecord]] = {}

        # Per-agent baselines
        self._baselines: dict[str, dict] = {}

        # Recent anomalies
        self._recent_anomalies: deque[AnomalyEvent] = deque(maxlen=1000)

        self._lock = threading.Lock()

    def record_action(
        self,
        agent_id: str,
        tool_name: str,
        parameters_hash: str,
        result: str,
        risk_tier: str,
        violation_type: str | None = None,
    ) -> list[AnomalyEvent]:
        """
        Record an action and check for anomalies.

        Args:
            agent_id: ID of the agent
            tool_name: Name of the tool
            parameters_hash: Hash of parameters
            result: Result of the action
            risk_tier: Risk tier of the action
            violation_type: Type of violation if denied

        Returns:
            List of any anomalies detected
        """
        record = ActionRecord(
            timestamp=datetime.now(),
            tool_name=tool_name,
            parameters_hash=parameters_hash,
            result=result,
            risk_tier=risk_tier,
            violation_type=violation_type,
        )

        with self._lock:
            # Initialize history if needed
            if agent_id not in self._history:
                self._history[agent_id] = deque()

            self._history[agent_id].append(record)
            self._cleanup_old_records(agent_id)

            # Run detections
            anomalies = []
            anomalies.extend(self._check_rapid_fire(agent_id))
            anomalies.extend(self._check_repeated_denial(agent_id))
            anomalies.extend(self._check_safe_zone_probing(agent_id))
            anomalies.extend(self._check_escalation(agent_id))
            anomalies.extend(self._check_parameter_fuzzing(agent_id))

            # Record and notify
            for anomaly in anomalies:
                self._recent_anomalies.append(anomaly)
                if self._on_anomaly:
                    self._on_anomaly(anomaly)

            return anomalies

    def _cleanup_old_records(self, agent_id: str) -> None:
        """Remove records outside tracking window."""
        cutoff = datetime.now() - timedelta(
            minutes=self._config.tracking_window_minutes
        )

        history = self._history.get(agent_id)
        if history:
            while history and history[0].timestamp < cutoff:
                history.popleft()

    def _check_rapid_fire(self, agent_id: str) -> list[AnomalyEvent]:
        """Check for rapid-fire action pattern."""
        anomalies = []
        history = self._history.get(agent_id, [])

        # Count actions in the last minute
        one_min_ago = datetime.now() - timedelta(minutes=1)
        recent_count = sum(1 for r in history if r.timestamp >= one_min_ago)

        if recent_count >= self._config.rapid_fire_threshold:
            anomalies.append(AnomalyEvent(
                timestamp=datetime.now(),
                agent_id=agent_id,
                anomaly_type=AnomalyType.RAPID_FIRE,
                severity=AnomalySeverity.MEDIUM,
                description=f"Agent performing {recent_count} actions per minute",
                evidence=[{"actions_per_minute": recent_count}],
                recommended_action="throttle",
            ))

        return anomalies

    def _check_repeated_denial(self, agent_id: str) -> list[AnomalyEvent]:
        """Check for repeated denial of same action."""
        anomalies = []
        history = self._history.get(agent_id, [])

        # Group denials by tool+params
        denial_counts: dict[str, int] = {}
        for record in history:
            if record.result == "denied":
                key = f"{record.tool_name}:{record.parameters_hash}"
                denial_counts[key] = denial_counts.get(key, 0) + 1

        for key, count in denial_counts.items():
            if count >= self._config.repeated_denial_threshold:
                tool_name = key.split(":")[0]
                anomalies.append(AnomalyEvent(
                    timestamp=datetime.now(),
                    agent_id=agent_id,
                    anomaly_type=AnomalyType.REPEATED_DENIAL,
                    severity=AnomalySeverity.HIGH,
                    description=f"Repeated attempts at denied action: {tool_name}",
                    evidence=[{"tool": tool_name, "attempts": count}],
                    recommended_action="quarantine",
                ))

        return anomalies

    def _check_safe_zone_probing(self, agent_id: str) -> list[AnomalyEvent]:
        """Check for attempts to access safe zones."""
        anomalies = []
        history = self._history.get(agent_id, [])

        # Count safe zone violations
        safe_zone_attempts = sum(
            1 for r in history
            if r.result == "denied" and r.violation_type == "safe_zone"
        )

        if safe_zone_attempts >= self._config.safe_zone_probe_threshold:
            anomalies.append(AnomalyEvent(
                timestamp=datetime.now(),
                agent_id=agent_id,
                anomaly_type=AnomalyType.SAFE_ZONE_PROBE,
                severity=AnomalySeverity.CRITICAL,
                description="Multiple attempts to access protected areas",
                evidence=[{"safe_zone_attempts": safe_zone_attempts}],
                recommended_action="quarantine_immediately",
            ))

        return anomalies

    def _check_escalation(self, agent_id: str) -> list[AnomalyEvent]:
        """Check for privilege escalation attempts."""
        anomalies = []
        history = self._history.get(agent_id, [])

        # Look for pattern of increasing risk tiers
        risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}

        recent_high_risk = [
            r for r in history
            if risk_order.get(r.risk_tier, 0) >= 2
        ]

        if len(recent_high_risk) >= 3:
            # Check if there's an increasing pattern
            denied_high_risk = [r for r in recent_high_risk if r.result == "denied"]
            if len(denied_high_risk) >= 2:
                anomalies.append(AnomalyEvent(
                    timestamp=datetime.now(),
                    agent_id=agent_id,
                    anomaly_type=AnomalyType.ESCALATION_ATTEMPT,
                    severity=AnomalySeverity.HIGH,
                    description="Pattern of high-risk action attempts detected",
                    evidence=[{"high_risk_attempts": len(recent_high_risk)}],
                    recommended_action="review_and_possibly_quarantine",
                ))

        return anomalies

    def _check_parameter_fuzzing(self, agent_id: str) -> list[AnomalyEvent]:
        """Check for systematic parameter variation (potential fuzzing)."""
        anomalies = []
        history = self._history.get(agent_id, [])

        # Group by tool and count unique parameter hashes
        tool_params: dict[str, set[str]] = {}
        for record in history:
            if record.tool_name not in tool_params:
                tool_params[record.tool_name] = set()
            tool_params[record.tool_name].add(record.parameters_hash)

        # Flag if same tool called with many different parameter combinations
        for tool_name, params in tool_params.items():
            if len(params) >= 10:  # 10+ unique parameter combinations
                anomalies.append(AnomalyEvent(
                    timestamp=datetime.now(),
                    agent_id=agent_id,
                    anomaly_type=AnomalyType.PARAMETER_FUZZING,
                    severity=AnomalySeverity.MEDIUM,
                    description=f"Systematic parameter variation detected for {tool_name}",
                    evidence=[{"tool": tool_name, "unique_params": len(params)}],
                    recommended_action="review",
                ))

        return anomalies

    def get_agent_anomalies(
        self,
        agent_id: str,
        since: datetime | None = None,
    ) -> list[AnomalyEvent]:
        """Get anomalies for a specific agent."""
        with self._lock:
            anomalies = [
                a for a in self._recent_anomalies
                if a.agent_id == agent_id
            ]

            if since:
                anomalies = [a for a in anomalies if a.timestamp >= since]

            return anomalies

    def get_recent_anomalies(
        self,
        severity: AnomalySeverity | None = None,
        limit: int = 100,
    ) -> list[AnomalyEvent]:
        """Get recent anomalies across all agents."""
        with self._lock:
            anomalies = list(self._recent_anomalies)

            if severity:
                anomalies = [a for a in anomalies if a.severity == severity]

            return anomalies[-limit:]

    def get_high_risk_agents(self) -> list[str]:
        """Get list of agents with recent critical/high anomalies."""
        with self._lock:
            # Look at last hour
            one_hour_ago = datetime.now() - timedelta(hours=1)

            high_risk = set()
            for anomaly in self._recent_anomalies:
                if anomaly.timestamp >= one_hour_ago:
                    if anomaly.severity in (AnomalySeverity.HIGH, AnomalySeverity.CRITICAL):
                        high_risk.add(anomaly.agent_id)

            return list(high_risk)

    def get_stats(self) -> dict:
        """Get detector statistics."""
        with self._lock:
            one_hour_ago = datetime.now() - timedelta(hours=1)

            recent = [
                a for a in self._recent_anomalies
                if a.timestamp >= one_hour_ago
            ]

            by_type = {}
            by_severity = {}

            for anomaly in recent:
                by_type[anomaly.anomaly_type.value] = (
                    by_type.get(anomaly.anomaly_type.value, 0) + 1
                )
                by_severity[anomaly.severity.value] = (
                    by_severity.get(anomaly.severity.value, 0) + 1
                )

            return {
                "agents_tracked": len(self._history),
                "recent_anomalies_1h": len(recent),
                "by_type": by_type,
                "by_severity": by_severity,
                "high_risk_agents": self.get_high_risk_agents(),
            }
