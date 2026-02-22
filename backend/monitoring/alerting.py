"""
Phase 8: Alerting System
Task 8.6: Alerting for critical events.
"""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status."""

    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class AlertCondition:
    """Condition that triggers an alert."""

    name: str
    description: str
    metric_name: str
    operator: str  # "gt", "lt", "eq", "gte", "lte"
    threshold: float
    duration_seconds: int = 0  # How long condition must be true
    severity: AlertSeverity = AlertSeverity.WARNING
    tags: list[str] = field(default_factory=list)


@dataclass
class Alert:
    """An alert instance."""

    alert_id: str
    condition_name: str
    severity: AlertSeverity
    status: AlertStatus
    title: str
    message: str
    metric_value: float
    threshold: float
    triggered_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    acknowledged_by: str | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class AlertChannel:
    """Base class for alert notification channels."""

    async def send(self, alert: Alert) -> bool:
        """Send an alert notification."""
        raise NotImplementedError


class LogAlertChannel(AlertChannel):
    """Alert channel that logs alerts."""

    async def send(self, alert: Alert) -> bool:
        """Log the alert."""
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL,
        }.get(alert.severity, logging.WARNING)

        logger.log(
            log_level, f"ALERT [{alert.severity.value.upper()}] {alert.title}: {alert.message}"
        )

        return True


class FileAlertChannel(AlertChannel):
    """Alert channel that writes to a file."""

    def __init__(self, file_path: str):
        from pathlib import Path

        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    async def send(self, alert: Alert) -> bool:
        """Write alert to file."""
        try:
            entry = {
                "alert_id": alert.alert_id,
                "severity": alert.severity.value,
                "title": alert.title,
                "message": alert.message,
                "triggered_at": alert.triggered_at.isoformat(),
                "metric_value": alert.metric_value,
                "threshold": alert.threshold,
            }

            with open(self.file_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

            return True
        except Exception as e:
            logger.error(f"Failed to write alert to file: {e}")
            return False


class CallbackAlertChannel(AlertChannel):
    """Alert channel that calls a callback function."""

    def __init__(self, callback: Callable[[Alert], None]):
        self.callback = callback

    async def send(self, alert: Alert) -> bool:
        """Call the callback."""
        try:
            if asyncio.iscoroutinefunction(self.callback):
                await self.callback(alert)
            else:
                self.callback(alert)
            return True
        except Exception as e:
            logger.error(f"Alert callback failed: {e}")
            return False


class AlertManager:
    """Manager for handling alerts."""

    def __init__(self):
        self._conditions: dict[str, AlertCondition] = {}
        self._alerts: dict[str, Alert] = {}
        self._channels: list[AlertChannel] = []
        self._suppression_rules: list[dict[str, Any]] = []
        self._metric_values: dict[str, list[tuple[datetime, float]]] = {}

        # Add default log channel
        self._channels.append(LogAlertChannel())

    def add_condition(self, condition: AlertCondition) -> None:
        """Add an alert condition."""
        self._conditions[condition.name] = condition

    def remove_condition(self, name: str) -> bool:
        """Remove an alert condition."""
        if name in self._conditions:
            del self._conditions[name]
            return True
        return False

    def add_channel(self, channel: AlertChannel) -> None:
        """Add a notification channel."""
        self._channels.append(channel)

    def add_suppression_rule(
        self,
        condition_name: str | None = None,
        severity: AlertSeverity | None = None,
        tags: list[str] | None = None,
        duration_minutes: int = 60,
    ) -> None:
        """Add a suppression rule."""
        self._suppression_rules.append(
            {
                "condition_name": condition_name,
                "severity": severity,
                "tags": tags,
                "expires_at": datetime.now() + timedelta(minutes=duration_minutes),
            }
        )

    async def check_metric(self, metric_name: str, value: float) -> list[Alert]:
        """Check a metric value against conditions."""
        # Store metric value
        if metric_name not in self._metric_values:
            self._metric_values[metric_name] = []

        self._metric_values[metric_name].append((datetime.now(), value))

        # Trim old values
        cutoff = datetime.now() - timedelta(minutes=10)
        self._metric_values[metric_name] = [
            (t, v) for t, v in self._metric_values[metric_name] if t >= cutoff
        ]

        # Check conditions
        triggered_alerts = []

        for condition in self._conditions.values():
            if condition.metric_name != metric_name:
                continue

            if self._evaluate_condition(condition, value):
                alert = await self._trigger_alert(condition, value)
                if alert:
                    triggered_alerts.append(alert)

        return triggered_alerts

    def _evaluate_condition(self, condition: AlertCondition, value: float) -> bool:
        """Evaluate if a condition is met."""
        operators = {
            "gt": lambda v, t: v > t,
            "lt": lambda v, t: v < t,
            "eq": lambda v, t: v == t,
            "gte": lambda v, t: v >= t,
            "lte": lambda v, t: v <= t,
        }

        op = operators.get(condition.operator)
        if not op:
            return False

        if not op(value, condition.threshold):
            return False

        # Check duration requirement
        if condition.duration_seconds > 0:
            values = self._metric_values.get(condition.metric_name, [])
            cutoff = datetime.now() - timedelta(seconds=condition.duration_seconds)
            recent = [(t, v) for t, v in values if t >= cutoff]

            # All recent values must meet condition
            if not all(op(v, condition.threshold) for _, v in recent):
                return False

        return True

    async def _trigger_alert(self, condition: AlertCondition, value: float) -> Alert | None:
        """Trigger an alert."""
        import uuid

        # Check if alert already exists for this condition
        existing = next(
            (
                a
                for a in self._alerts.values()
                if a.condition_name == condition.name and a.status == AlertStatus.ACTIVE
            ),
            None,
        )

        if existing:
            return None  # Don't re-trigger

        # Check suppression
        if self._is_suppressed(condition):
            return None

        alert = Alert(
            alert_id=str(uuid.uuid4()),
            condition_name=condition.name,
            severity=condition.severity,
            status=AlertStatus.ACTIVE,
            title=f"Alert: {condition.name}",
            message=f"{condition.description} (value: {value}, threshold: {condition.threshold})",
            metric_value=value,
            threshold=condition.threshold,
            triggered_at=datetime.now(),
            tags=condition.tags,
        )

        self._alerts[alert.alert_id] = alert

        # Send to channels
        for channel in self._channels:
            try:
                await channel.send(alert)
            except Exception as e:
                logger.error(f"Failed to send alert to channel: {e}")

        return alert

    def _is_suppressed(self, condition: AlertCondition) -> bool:
        """Check if alert should be suppressed."""
        now = datetime.now()

        for rule in self._suppression_rules:
            if rule["expires_at"] < now:
                continue

            if rule["condition_name"] and rule["condition_name"] != condition.name:
                continue

            if rule["severity"] and rule["severity"] != condition.severity:
                continue

            if rule["tags"] and not any(t in condition.tags for t in rule["tags"]):
                continue

            return True

        return False

    def acknowledge(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert."""
        alert = self._alerts.get(alert_id)
        if alert and alert.status == AlertStatus.ACTIVE:
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.now()
            alert.acknowledged_by = user
            return True
        return False

    def resolve(self, alert_id: str) -> bool:
        """Resolve an alert."""
        alert = self._alerts.get(alert_id)
        if alert and alert.status in (AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED):
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now()
            return True
        return False

    def get_active_alerts(self) -> list[Alert]:
        """Get all active alerts."""
        return [a for a in self._alerts.values() if a.status == AlertStatus.ACTIVE]

    def get_all_alerts(
        self,
        status: AlertStatus | None = None,
        severity: AlertSeverity | None = None,
        limit: int = 100,
    ) -> list[Alert]:
        """Get filtered alerts."""
        alerts = list(self._alerts.values())

        if status:
            alerts = [a for a in alerts if a.status == status]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        alerts.sort(key=lambda a: a.triggered_at, reverse=True)

        return alerts[:limit]


# Default conditions
def create_default_conditions() -> list[AlertCondition]:
    """Create default alert conditions."""
    return [
        AlertCondition(
            name="high_cpu_usage",
            description="CPU usage is above 90%",
            metric_name="cpu_usage_percent",
            operator="gt",
            threshold=90,
            duration_seconds=60,
            severity=AlertSeverity.WARNING,
        ),
        AlertCondition(
            name="high_memory_usage",
            description="Memory usage is above 90%",
            metric_name="memory_usage_percent",
            operator="gt",
            threshold=90,
            duration_seconds=60,
            severity=AlertSeverity.WARNING,
        ),
        AlertCondition(
            name="high_error_rate",
            description="Error rate is above 10 per minute",
            metric_name="error_rate_per_minute",
            operator="gt",
            threshold=10,
            duration_seconds=30,
            severity=AlertSeverity.ERROR,
        ),
        AlertCondition(
            name="low_disk_space",
            description="Free disk space is below 1 GB",
            metric_name="disk_free_gb",
            operator="lt",
            threshold=1,
            severity=AlertSeverity.ERROR,
        ),
        AlertCondition(
            name="synthesis_slow",
            description="Synthesis is taking longer than 30 seconds",
            metric_name="synthesis_duration_seconds",
            operator="gt",
            threshold=30,
            severity=AlertSeverity.WARNING,
        ),
    ]
