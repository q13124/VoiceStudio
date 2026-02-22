"""
SLO enforcer with performance budget definitions and policy integration.

This module implements Service Level Objectives (SLOs) for plugins,
allowing definition of performance budgets and automated enforcement
of quality standards.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)


class BudgetType(str, Enum):
    """Types of performance budgets."""

    # Latency budgets
    STARTUP_LATENCY_MS = "startup_latency_ms"
    IPC_LATENCY_MS = "ipc_latency_ms"
    CAPABILITY_LATENCY_MS = "capability_latency_ms"

    # Resource budgets
    MEMORY_MB = "memory_mb"
    CPU_PERCENT = "cpu_percent"
    DISK_MB = "disk_mb"

    # Reliability budgets
    ERROR_RATE_PERCENT = "error_rate_percent"
    CRASH_RATE_PERCENT = "crash_rate_percent"
    TIMEOUT_RATE_PERCENT = "timeout_rate_percent"

    # Throughput budgets
    REQUESTS_PER_SECOND = "requests_per_second"
    OPERATIONS_PER_SECOND = "operations_per_second"


class ThresholdOperator(str, Enum):
    """Operators for threshold comparisons."""

    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "lte"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "gte"
    EQUAL = "eq"
    NOT_EQUAL = "ne"


@dataclass
class Threshold:
    """A threshold for SLO evaluation."""

    value: float
    operator: ThresholdOperator = ThresholdOperator.LESS_THAN_OR_EQUAL

    def evaluate(self, actual: float) -> bool:
        """Check if actual value meets the threshold."""
        if self.operator == ThresholdOperator.LESS_THAN:
            return actual < self.value
        elif self.operator == ThresholdOperator.LESS_THAN_OR_EQUAL:
            return actual <= self.value
        elif self.operator == ThresholdOperator.GREATER_THAN:
            return actual > self.value
        elif self.operator == ThresholdOperator.GREATER_THAN_OR_EQUAL:
            return actual >= self.value
        elif self.operator == ThresholdOperator.EQUAL:
            return actual == self.value
        elif self.operator == ThresholdOperator.NOT_EQUAL:
            return actual != self.value
        return False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "value": self.value,
            "operator": self.operator.value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Threshold:
        """Create from dictionary."""
        return cls(
            value=data["value"],
            operator=ThresholdOperator(data.get("operator", "lte")),
        )


@dataclass
class Budget:
    """A performance budget definition."""

    budget_type: BudgetType
    warning_threshold: Threshold
    error_threshold: Threshold
    critical_threshold: Threshold | None = None
    description: str = ""
    enabled: bool = True

    def evaluate(self, actual: float) -> tuple[str, bool]:
        """
        Evaluate actual value against budget thresholds.

        Returns:
            Tuple of (severity level, is_passing).
            Severity: "ok", "warning", "error", "critical"
        """
        if not self.enabled:
            return "ok", True

        # Check from most severe to least
        if self.critical_threshold and not self.critical_threshold.evaluate(actual):
            return "critical", False
        if not self.error_threshold.evaluate(actual):
            return "error", False
        if not self.warning_threshold.evaluate(actual):
            return "warning", True  # Warning is still passing
        return "ok", True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "budget_type": self.budget_type.value,
            "warning_threshold": self.warning_threshold.to_dict(),
            "error_threshold": self.error_threshold.to_dict(),
            "description": self.description,
            "enabled": self.enabled,
        }
        if self.critical_threshold:
            result["critical_threshold"] = self.critical_threshold.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Budget:
        """Create from dictionary."""
        critical = None
        if "critical_threshold" in data:
            critical = Threshold.from_dict(data["critical_threshold"])

        return cls(
            budget_type=BudgetType(data["budget_type"]),
            warning_threshold=Threshold.from_dict(data["warning_threshold"]),
            error_threshold=Threshold.from_dict(data["error_threshold"]),
            critical_threshold=critical,
            description=data.get("description", ""),
            enabled=data.get("enabled", True),
        )


class PolicyAction(str, Enum):
    """Actions to take when SLO violations occur."""

    LOG = "log"  # Log the violation
    ALERT = "alert"  # Send alert notification
    THROTTLE = "throttle"  # Reduce plugin resources/rate
    SUSPEND = "suspend"  # Temporarily suspend plugin
    TERMINATE = "terminate"  # Stop and disable plugin
    QUARANTINE = "quarantine"  # Isolate plugin for investigation


@dataclass
class SLOPolicy:
    """Policy defining actions for SLO violations."""

    name: str
    actions: dict[str, list[PolicyAction]]  # severity -> actions
    cooldown_seconds: int = 300  # Time between enforcement actions
    consecutive_violations_before_escalate: int = 3
    auto_recovery: bool = True  # Auto-clear violations after recovery

    def get_actions(self, severity: str) -> list[PolicyAction]:
        """Get actions for a severity level."""
        return self.actions.get(severity, [PolicyAction.LOG])

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "actions": {k: [a.value for a in v] for k, v in self.actions.items()},
            "cooldown_seconds": self.cooldown_seconds,
            "consecutive_violations_before_escalate": (self.consecutive_violations_before_escalate),
            "auto_recovery": self.auto_recovery,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SLOPolicy:
        """Create from dictionary."""
        actions = {k: [PolicyAction(a) for a in v] for k, v in data.get("actions", {}).items()}
        return cls(
            name=data["name"],
            actions=actions,
            cooldown_seconds=data.get("cooldown_seconds", 300),
            consecutive_violations_before_escalate=data.get(
                "consecutive_violations_before_escalate", 3
            ),
            auto_recovery=data.get("auto_recovery", True),
        )


# Default policies
DEFAULT_POLICY = SLOPolicy(
    name="default",
    actions={
        "warning": [PolicyAction.LOG],
        "error": [PolicyAction.LOG, PolicyAction.ALERT],
        "critical": [PolicyAction.LOG, PolicyAction.ALERT, PolicyAction.THROTTLE],
    },
)

STRICT_POLICY = SLOPolicy(
    name="strict",
    actions={
        "warning": [PolicyAction.LOG, PolicyAction.ALERT],
        "error": [PolicyAction.LOG, PolicyAction.ALERT, PolicyAction.SUSPEND],
        "critical": [PolicyAction.LOG, PolicyAction.ALERT, PolicyAction.TERMINATE],
    },
    consecutive_violations_before_escalate=1,
)

LENIENT_POLICY = SLOPolicy(
    name="lenient",
    actions={
        "warning": [PolicyAction.LOG],
        "error": [PolicyAction.LOG],
        "critical": [PolicyAction.LOG, PolicyAction.ALERT],
    },
    consecutive_violations_before_escalate=5,
)


@dataclass
class SLOConfig:
    """Complete SLO configuration for a plugin or system."""

    name: str
    budgets: list[Budget]
    policy: SLOPolicy = field(default_factory=lambda: DEFAULT_POLICY)
    evaluation_window_seconds: int = 60
    minimum_samples: int = 10  # Minimum samples before enforcing

    def get_budget(self, budget_type: BudgetType) -> Budget | None:
        """Get budget by type."""
        for budget in self.budgets:
            if budget.budget_type == budget_type:
                return budget
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "budgets": [b.to_dict() for b in self.budgets],
            "policy": self.policy.to_dict(),
            "evaluation_window_seconds": self.evaluation_window_seconds,
            "minimum_samples": self.minimum_samples,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SLOConfig:
        """Create from dictionary."""
        return cls(
            name=data["name"],
            budgets=[Budget.from_dict(b) for b in data.get("budgets", [])],
            policy=SLOPolicy.from_dict(data["policy"]) if "policy" in data else DEFAULT_POLICY,
            evaluation_window_seconds=data.get("evaluation_window_seconds", 60),
            minimum_samples=data.get("minimum_samples", 10),
        )

    @classmethod
    def from_json_file(cls, path: Path) -> SLOConfig:
        """Load configuration from JSON file."""
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def to_json_file(self, path: Path) -> None:
        """Save configuration to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)


# Default SLO configurations for different plugin tiers
def create_standard_slo() -> SLOConfig:
    """Create standard SLO configuration for typical plugins."""
    return SLOConfig(
        name="standard",
        budgets=[
            Budget(
                budget_type=BudgetType.STARTUP_LATENCY_MS,
                warning_threshold=Threshold(1000),
                error_threshold=Threshold(3000),
                critical_threshold=Threshold(10000),
                description="Plugin startup time",
            ),
            Budget(
                budget_type=BudgetType.IPC_LATENCY_MS,
                warning_threshold=Threshold(50),
                error_threshold=Threshold(100),
                critical_threshold=Threshold(500),
                description="IPC message round-trip time",
            ),
            Budget(
                budget_type=BudgetType.MEMORY_MB,
                warning_threshold=Threshold(256),
                error_threshold=Threshold(512),
                critical_threshold=Threshold(1024),
                description="Plugin memory usage",
            ),
            Budget(
                budget_type=BudgetType.CPU_PERCENT,
                warning_threshold=Threshold(50),
                error_threshold=Threshold(80),
                critical_threshold=Threshold(95),
                description="Plugin CPU usage",
            ),
            Budget(
                budget_type=BudgetType.ERROR_RATE_PERCENT,
                warning_threshold=Threshold(1),
                error_threshold=Threshold(5),
                critical_threshold=Threshold(10),
                description="Request error rate",
            ),
        ],
    )


def create_realtime_slo() -> SLOConfig:
    """Create SLO for real-time audio processing plugins."""
    return SLOConfig(
        name="realtime",
        budgets=[
            Budget(
                budget_type=BudgetType.STARTUP_LATENCY_MS,
                warning_threshold=Threshold(500),
                error_threshold=Threshold(1000),
                critical_threshold=Threshold(2000),
                description="Plugin startup time (strict for real-time)",
            ),
            Budget(
                budget_type=BudgetType.IPC_LATENCY_MS,
                warning_threshold=Threshold(10),
                error_threshold=Threshold(25),
                critical_threshold=Threshold(50),
                description="IPC latency (tight for real-time audio)",
            ),
            Budget(
                budget_type=BudgetType.CAPABILITY_LATENCY_MS,
                warning_threshold=Threshold(20),
                error_threshold=Threshold(50),
                critical_threshold=Threshold(100),
                description="Capability execution time",
            ),
            Budget(
                budget_type=BudgetType.MEMORY_MB,
                warning_threshold=Threshold(128),
                error_threshold=Threshold(256),
                critical_threshold=Threshold(512),
                description="Memory (smaller for real-time)",
            ),
            Budget(
                budget_type=BudgetType.ERROR_RATE_PERCENT,
                warning_threshold=Threshold(0.1),
                error_threshold=Threshold(0.5),
                critical_threshold=Threshold(1),
                description="Error rate (near-zero for real-time)",
            ),
        ],
        policy=STRICT_POLICY,
        evaluation_window_seconds=10,
    )


class SLOStatus(str, Enum):
    """Overall SLO status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


@dataclass
class SLOViolation:
    """Record of an SLO violation."""

    budget_type: BudgetType
    severity: str
    actual_value: float
    threshold_value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    plugin_id: str | None = None
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "budget_type": self.budget_type.value,
            "severity": self.severity,
            "actual_value": self.actual_value,
            "threshold_value": self.threshold_value,
            "timestamp": self.timestamp.isoformat(),
            "plugin_id": self.plugin_id,
            "message": self.message,
        }


@dataclass
class SLOResult:
    """Result of SLO evaluation."""

    status: SLOStatus
    violations: list[SLOViolation]
    warnings: list[SLOViolation]
    passing: dict[BudgetType, float]  # Budget type -> actual value
    timestamp: datetime = field(default_factory=datetime.utcnow)
    plugin_id: str | None = None
    evaluation_window_seconds: int = 60
    sample_count: int = 0

    @property
    def is_healthy(self) -> bool:
        """Check if all SLOs are healthy."""
        return self.status == SLOStatus.HEALTHY

    @property
    def violation_count(self) -> int:
        """Get total violation count."""
        return len(self.violations)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "violations": [v.to_dict() for v in self.violations],
            "warnings": [w.to_dict() for w in self.warnings],
            "passing": {k.value: v for k, v in self.passing.items()},
            "timestamp": self.timestamp.isoformat(),
            "plugin_id": self.plugin_id,
            "evaluation_window_seconds": self.evaluation_window_seconds,
            "sample_count": self.sample_count,
        }


@dataclass
class MetricSample:
    """A single metric sample."""

    budget_type: BudgetType
    value: float
    timestamp: float = field(default_factory=time.time)


class SLOEnforcer:
    """
    SLO enforcer that monitors metrics and enforces policies.

    Collects metrics, evaluates them against SLO budgets, and
    executes policy actions when violations occur.
    """

    def __init__(
        self,
        config: SLOConfig,
        plugin_id: str | None = None,
        action_handlers: dict[PolicyAction, Callable[[SLOViolation], None]] | None = None,
    ):
        """
        Initialize SLO enforcer.

        Args:
            config: SLO configuration with budgets and policies.
            plugin_id: Optional plugin identifier.
            action_handlers: Custom handlers for policy actions.
        """
        self.config = config
        self.plugin_id = plugin_id
        self.action_handlers = action_handlers or {}

        # Metric samples storage (ring buffer per budget type)
        self._samples: dict[BudgetType, list[MetricSample]] = {
            b.budget_type: [] for b in config.budgets
        }
        self._max_samples = 1000

        # Violation tracking
        self._violations: list[SLOViolation] = []
        self._consecutive_violations: dict[BudgetType, int] = {}
        self._last_action_time: dict[BudgetType, float] = {}

        # Status history
        self._status_history: list[tuple[datetime, SLOStatus]] = []

        logger.info(
            f"SLO enforcer initialized for {plugin_id or 'system'} "
            f"with {len(config.budgets)} budgets"
        )

    def record(self, budget_type: BudgetType, value: float) -> None:
        """
        Record a metric sample.

        Args:
            budget_type: Type of the metric.
            value: Metric value.
        """
        if budget_type not in self._samples:
            self._samples[budget_type] = []

        sample = MetricSample(budget_type=budget_type, value=value)
        samples = self._samples[budget_type]
        samples.append(sample)

        # Trim to max samples
        if len(samples) > self._max_samples:
            self._samples[budget_type] = samples[-self._max_samples :]

    def record_batch(self, metrics: dict[BudgetType, float]) -> None:
        """
        Record multiple metric samples at once.

        Args:
            metrics: Dictionary of budget type to value.
        """
        for budget_type, value in metrics.items():
            self.record(budget_type, value)

    def evaluate(self, current_values: dict[BudgetType, float] | None = None) -> SLOResult:
        """
        Evaluate current SLO status.

        Args:
            current_values: Optional current metric values.
                           If not provided, uses aggregated samples.

        Returns:
            SLOResult with status, violations, and warnings.
        """
        now = datetime.utcnow()
        violations: list[SLOViolation] = []
        warnings: list[SLOViolation] = []
        passing: dict[BudgetType, float] = {}
        sample_count = 0

        # Get values for evaluation
        values_to_check = current_values or {}

        # If not provided, aggregate from samples
        if not values_to_check:
            window_start = time.time() - self.config.evaluation_window_seconds
            for budget in self.config.budgets:
                samples = self._samples.get(budget.budget_type, [])
                window_samples = [s for s in samples if s.timestamp >= window_start]
                sample_count += len(window_samples)

                if window_samples:
                    # Use appropriate aggregation based on budget type
                    if budget.budget_type in (
                        BudgetType.ERROR_RATE_PERCENT,
                        BudgetType.CRASH_RATE_PERCENT,
                        BudgetType.TIMEOUT_RATE_PERCENT,
                    ):
                        # Rates use mean
                        values_to_check[budget.budget_type] = sum(
                            s.value for s in window_samples
                        ) / len(window_samples)
                    elif budget.budget_type in (
                        BudgetType.MEMORY_MB,
                        BudgetType.CPU_PERCENT,
                    ):
                        # Resource metrics use max
                        values_to_check[budget.budget_type] = max(s.value for s in window_samples)
                    else:
                        # Latency metrics use P95
                        sorted_values = sorted(s.value for s in window_samples)
                        p95_index = int(len(sorted_values) * 0.95)
                        values_to_check[budget.budget_type] = sorted_values[
                            min(p95_index, len(sorted_values) - 1)
                        ]

        # Check if we have enough samples
        if sample_count < self.config.minimum_samples and not current_values:
            return SLOResult(
                status=SLOStatus.HEALTHY,
                violations=[],
                warnings=[],
                passing={},
                plugin_id=self.plugin_id,
                evaluation_window_seconds=self.config.evaluation_window_seconds,
                sample_count=sample_count,
            )

        # Evaluate each budget
        for budget in self.config.budgets:
            if budget.budget_type not in values_to_check:
                continue

            value = values_to_check[budget.budget_type]
            severity, is_passing = budget.evaluate(value)

            if severity == "ok":
                passing[budget.budget_type] = value
                # Clear consecutive violations on recovery
                if self.config.policy.auto_recovery:
                    self._consecutive_violations[budget.budget_type] = 0
            else:
                # Get appropriate threshold value for reporting
                if severity == "critical" and budget.critical_threshold:
                    threshold_value = budget.critical_threshold.value
                elif severity == "error":
                    threshold_value = budget.error_threshold.value
                else:
                    threshold_value = budget.warning_threshold.value

                violation = SLOViolation(
                    budget_type=budget.budget_type,
                    severity=severity,
                    actual_value=value,
                    threshold_value=threshold_value,
                    plugin_id=self.plugin_id,
                    message=f"{budget.description}: {value:.2f} exceeded {severity} threshold {threshold_value}",
                )

                if is_passing:
                    warnings.append(violation)
                else:
                    violations.append(violation)
                    self._violations.append(violation)

                    # Track consecutive violations
                    self._consecutive_violations[budget.budget_type] = (
                        self._consecutive_violations.get(budget.budget_type, 0) + 1
                    )

        # Determine overall status
        if any(v.severity == "critical" for v in violations):
            status = SLOStatus.CRITICAL
        elif violations:
            status = SLOStatus.UNHEALTHY
        elif warnings:
            status = SLOStatus.DEGRADED
        else:
            status = SLOStatus.HEALTHY

        # Record status history
        self._status_history.append((now, status))
        if len(self._status_history) > 100:
            self._status_history = self._status_history[-100:]

        result = SLOResult(
            status=status,
            violations=violations,
            warnings=warnings,
            passing=passing,
            plugin_id=self.plugin_id,
            evaluation_window_seconds=self.config.evaluation_window_seconds,
            sample_count=sample_count,
        )

        return result

    def enforce(self, result: SLOResult | None = None) -> list[PolicyAction]:
        """
        Enforce SLO policies based on evaluation result.

        Args:
            result: Optional evaluation result. If not provided, runs evaluate().

        Returns:
            List of actions that were executed.
        """
        if result is None:
            result = self.evaluate()

        executed_actions: list[PolicyAction] = []
        now = time.time()

        for violation in result.violations:
            # Check cooldown
            last_action = self._last_action_time.get(violation.budget_type, 0)
            if now - last_action < self.config.policy.cooldown_seconds:
                logger.debug(f"Skipping action for {violation.budget_type} (cooldown)")
                continue

            # Check escalation threshold
            consecutive = self._consecutive_violations.get(violation.budget_type, 1)
            if consecutive < self.config.policy.consecutive_violations_before_escalate:
                # Use lower severity actions
                actions = self.config.policy.get_actions("warning")
            else:
                actions = self.config.policy.get_actions(violation.severity)

            # Execute actions
            for action in actions:
                try:
                    self._execute_action(action, violation)
                    executed_actions.append(action)
                except Exception as e:
                    logger.error(f"Failed to execute action {action}: {e}")

            self._last_action_time[violation.budget_type] = now

        return executed_actions

    def _execute_action(self, action: PolicyAction, violation: SLOViolation) -> None:
        """Execute a policy action."""
        # Check for custom handler
        if action in self.action_handlers:
            self.action_handlers[action](violation)
            return

        # Default implementations
        if action == PolicyAction.LOG:
            logger.warning(
                f"SLO violation: {violation.budget_type.value} "
                f"({violation.severity}): {violation.message}"
            )
        elif action == PolicyAction.ALERT:
            logger.error(
                f"SLO ALERT: {violation.budget_type.value} "
                f"({violation.severity}): {violation.message}"
            )
        elif action == PolicyAction.THROTTLE:
            logger.warning(f"SLO throttle triggered for {violation.plugin_id or 'system'}")
        elif action == PolicyAction.SUSPEND:
            logger.warning(f"SLO suspend triggered for {violation.plugin_id or 'system'}")
        elif action == PolicyAction.TERMINATE:
            logger.error(f"SLO terminate triggered for {violation.plugin_id or 'system'}")
        elif action == PolicyAction.QUARANTINE:
            logger.error(f"SLO quarantine triggered for {violation.plugin_id or 'system'}")

    def get_violation_history(
        self, since: datetime | None = None, limit: int = 100
    ) -> list[SLOViolation]:
        """Get violation history."""
        violations = self._violations
        if since:
            violations = [v for v in violations if v.timestamp >= since]
        return violations[-limit:]

    def get_status_history(
        self, since: datetime | None = None, limit: int = 100
    ) -> list[tuple[datetime, SLOStatus]]:
        """Get status history."""
        history = self._status_history
        if since:
            history = [(t, s) for t, s in history if t >= since]
        return history[-limit:]

    def get_uptime_percentage(self, window: timedelta = timedelta(hours=24)) -> float:
        """Calculate uptime percentage over a time window."""
        if not self._status_history:
            return 100.0

        cutoff = datetime.utcnow() - window
        relevant = [(t, s) for t, s in self._status_history if t >= cutoff]

        if not relevant:
            return 100.0

        # Count healthy/degraded vs unhealthy/critical
        healthy = sum(1 for _, s in relevant if s in (SLOStatus.HEALTHY, SLOStatus.DEGRADED))
        return (healthy / len(relevant)) * 100

    def clear_violations(self) -> None:
        """Clear violation history and counters."""
        self._violations.clear()
        self._consecutive_violations.clear()
        self._last_action_time.clear()

    def reset_samples(self) -> None:
        """Clear all metric samples."""
        for budget_type in self._samples:
            self._samples[budget_type].clear()

    def get_sample_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics about collected samples."""
        stats = {}
        for budget_type, samples in self._samples.items():
            if samples:
                values = [s.value for s in samples]
                stats[budget_type.value] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "mean": sum(values) / len(values),
                    "oldest": datetime.fromtimestamp(samples[0].timestamp).isoformat(),
                    "newest": datetime.fromtimestamp(samples[-1].timestamp).isoformat(),
                }
            else:
                stats[budget_type.value] = {"count": 0}
        return stats

    def to_dict(self) -> dict[str, Any]:
        """Get full enforcer state as dictionary."""
        result = self.evaluate()
        return {
            "plugin_id": self.plugin_id,
            "config": self.config.to_dict(),
            "current_result": result.to_dict(),
            "violation_count": len(self._violations),
            "sample_stats": self.get_sample_stats(),
            "uptime_24h": self.get_uptime_percentage(),
        }
