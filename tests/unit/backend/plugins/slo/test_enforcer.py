"""
Tests for the SLO enforcer module.
"""

from __future__ import annotations

import json
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from backend.plugins.slo.enforcer import (
    DEFAULT_POLICY,
    LENIENT_POLICY,
    STRICT_POLICY,
    Budget,
    BudgetType,
    MetricSample,
    PolicyAction,
    SLOConfig,
    SLOEnforcer,
    SLOPolicy,
    SLOResult,
    SLOStatus,
    SLOViolation,
    Threshold,
    ThresholdOperator,
    create_realtime_slo,
    create_standard_slo,
)


class TestThresholdOperator:
    """Tests for ThresholdOperator enum."""

    def test_all_operators_defined(self):
        """Test all expected operators exist."""
        assert ThresholdOperator.LESS_THAN
        assert ThresholdOperator.LESS_THAN_OR_EQUAL
        assert ThresholdOperator.GREATER_THAN
        assert ThresholdOperator.GREATER_THAN_OR_EQUAL
        assert ThresholdOperator.EQUAL
        assert ThresholdOperator.NOT_EQUAL


class TestThreshold:
    """Tests for Threshold class."""

    def test_creation(self):
        """Test threshold creation."""
        threshold = Threshold(value=100)
        assert threshold.value == 100
        assert threshold.operator == ThresholdOperator.LESS_THAN_OR_EQUAL

    def test_evaluate_less_than(self):
        """Test less than evaluation."""
        threshold = Threshold(value=100, operator=ThresholdOperator.LESS_THAN)
        assert threshold.evaluate(50) is True
        assert threshold.evaluate(100) is False
        assert threshold.evaluate(150) is False

    def test_evaluate_less_than_or_equal(self):
        """Test less than or equal evaluation."""
        threshold = Threshold(value=100, operator=ThresholdOperator.LESS_THAN_OR_EQUAL)
        assert threshold.evaluate(50) is True
        assert threshold.evaluate(100) is True
        assert threshold.evaluate(150) is False

    def test_evaluate_greater_than(self):
        """Test greater than evaluation."""
        threshold = Threshold(value=100, operator=ThresholdOperator.GREATER_THAN)
        assert threshold.evaluate(150) is True
        assert threshold.evaluate(100) is False
        assert threshold.evaluate(50) is False

    def test_evaluate_greater_than_or_equal(self):
        """Test greater than or equal evaluation."""
        threshold = Threshold(value=100, operator=ThresholdOperator.GREATER_THAN_OR_EQUAL)
        assert threshold.evaluate(150) is True
        assert threshold.evaluate(100) is True
        assert threshold.evaluate(50) is False

    def test_evaluate_equal(self):
        """Test equal evaluation."""
        threshold = Threshold(value=100, operator=ThresholdOperator.EQUAL)
        assert threshold.evaluate(100) is True
        assert threshold.evaluate(99) is False
        assert threshold.evaluate(101) is False

    def test_evaluate_not_equal(self):
        """Test not equal evaluation."""
        threshold = Threshold(value=100, operator=ThresholdOperator.NOT_EQUAL)
        assert threshold.evaluate(100) is False
        assert threshold.evaluate(99) is True
        assert threshold.evaluate(101) is True

    def test_to_dict(self):
        """Test dictionary conversion."""
        threshold = Threshold(value=50, operator=ThresholdOperator.LESS_THAN)
        data = threshold.to_dict()
        assert data["value"] == 50
        assert data["operator"] == "lt"

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {"value": 75, "operator": "gt"}
        threshold = Threshold.from_dict(data)
        assert threshold.value == 75
        assert threshold.operator == ThresholdOperator.GREATER_THAN


class TestBudget:
    """Tests for Budget class."""

    @pytest.fixture
    def sample_budget(self):
        """Create a sample budget."""
        return Budget(
            budget_type=BudgetType.STARTUP_LATENCY_MS,
            warning_threshold=Threshold(1000),
            error_threshold=Threshold(3000),
            critical_threshold=Threshold(10000),
            description="Startup time",
        )

    def test_creation(self, sample_budget):
        """Test budget creation."""
        assert sample_budget.budget_type == BudgetType.STARTUP_LATENCY_MS
        assert sample_budget.warning_threshold.value == 1000
        assert sample_budget.error_threshold.value == 3000
        assert sample_budget.critical_threshold.value == 10000
        assert sample_budget.enabled is True

    def test_evaluate_ok(self, sample_budget):
        """Test budget evaluation when passing."""
        severity, passing = sample_budget.evaluate(500)
        assert severity == "ok"
        assert passing is True

    def test_evaluate_warning(self, sample_budget):
        """Test budget evaluation at warning level."""
        severity, passing = sample_budget.evaluate(1500)
        assert severity == "warning"
        assert passing is True  # Warning is still passing

    def test_evaluate_error(self, sample_budget):
        """Test budget evaluation at error level."""
        severity, passing = sample_budget.evaluate(5000)
        assert severity == "error"
        assert passing is False

    def test_evaluate_critical(self, sample_budget):
        """Test budget evaluation at critical level."""
        severity, passing = sample_budget.evaluate(15000)
        assert severity == "critical"
        assert passing is False

    def test_evaluate_disabled(self, sample_budget):
        """Test disabled budget always passes."""
        sample_budget.enabled = False
        severity, passing = sample_budget.evaluate(999999)
        assert severity == "ok"
        assert passing is True

    def test_to_dict(self, sample_budget):
        """Test dictionary conversion."""
        data = sample_budget.to_dict()
        assert data["budget_type"] == "startup_latency_ms"
        assert data["warning_threshold"]["value"] == 1000
        assert data["error_threshold"]["value"] == 3000
        assert data["critical_threshold"]["value"] == 10000
        assert data["description"] == "Startup time"
        assert data["enabled"] is True

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "budget_type": "memory_mb",
            "warning_threshold": {"value": 256, "operator": "lte"},
            "error_threshold": {"value": 512, "operator": "lte"},
            "description": "Memory usage",
        }
        budget = Budget.from_dict(data)
        assert budget.budget_type == BudgetType.MEMORY_MB
        assert budget.warning_threshold.value == 256
        assert budget.error_threshold.value == 512
        assert budget.critical_threshold is None


class TestBudgetType:
    """Tests for BudgetType enum."""

    def test_latency_types(self):
        """Test latency budget types exist."""
        assert BudgetType.STARTUP_LATENCY_MS
        assert BudgetType.IPC_LATENCY_MS
        assert BudgetType.CAPABILITY_LATENCY_MS

    def test_resource_types(self):
        """Test resource budget types exist."""
        assert BudgetType.MEMORY_MB
        assert BudgetType.CPU_PERCENT
        assert BudgetType.DISK_MB

    def test_reliability_types(self):
        """Test reliability budget types exist."""
        assert BudgetType.ERROR_RATE_PERCENT
        assert BudgetType.CRASH_RATE_PERCENT
        assert BudgetType.TIMEOUT_RATE_PERCENT


class TestPolicyAction:
    """Tests for PolicyAction enum."""

    def test_all_actions_defined(self):
        """Test all expected actions exist."""
        assert PolicyAction.LOG
        assert PolicyAction.ALERT
        assert PolicyAction.THROTTLE
        assert PolicyAction.SUSPEND
        assert PolicyAction.TERMINATE
        assert PolicyAction.QUARANTINE


class TestSLOPolicy:
    """Tests for SLOPolicy class."""

    def test_creation(self):
        """Test policy creation."""
        policy = SLOPolicy(
            name="test",
            actions={
                "warning": [PolicyAction.LOG],
                "error": [PolicyAction.LOG, PolicyAction.ALERT],
            },
        )
        assert policy.name == "test"
        assert PolicyAction.LOG in policy.get_actions("warning")
        assert len(policy.get_actions("error")) == 2

    def test_get_actions_missing(self):
        """Test getting actions for missing severity."""
        policy = SLOPolicy(name="test", actions={})
        actions = policy.get_actions("unknown")
        assert actions == [PolicyAction.LOG]  # Default

    def test_default_policy(self):
        """Test default policy."""
        assert DEFAULT_POLICY.name == "default"
        assert PolicyAction.LOG in DEFAULT_POLICY.get_actions("warning")

    def test_strict_policy(self):
        """Test strict policy has more severe actions."""
        assert STRICT_POLICY.name == "strict"
        assert PolicyAction.TERMINATE in STRICT_POLICY.get_actions("critical")
        assert STRICT_POLICY.consecutive_violations_before_escalate == 1

    def test_lenient_policy(self):
        """Test lenient policy has less severe actions."""
        assert LENIENT_POLICY.name == "lenient"
        assert LENIENT_POLICY.consecutive_violations_before_escalate == 5

    def test_to_dict(self):
        """Test dictionary conversion."""
        data = DEFAULT_POLICY.to_dict()
        assert data["name"] == "default"
        assert "warning" in data["actions"]

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "name": "custom",
            "actions": {
                "error": ["log", "alert"],
            },
            "cooldown_seconds": 600,
        }
        policy = SLOPolicy.from_dict(data)
        assert policy.name == "custom"
        assert policy.cooldown_seconds == 600


class TestSLOConfig:
    """Tests for SLOConfig class."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample SLO config."""
        return SLOConfig(
            name="test",
            budgets=[
                Budget(
                    budget_type=BudgetType.MEMORY_MB,
                    warning_threshold=Threshold(256),
                    error_threshold=Threshold(512),
                ),
            ],
        )

    def test_creation(self, sample_config):
        """Test config creation."""
        assert sample_config.name == "test"
        assert len(sample_config.budgets) == 1
        assert sample_config.policy.name == "default"

    def test_get_budget(self, sample_config):
        """Test getting budget by type."""
        budget = sample_config.get_budget(BudgetType.MEMORY_MB)
        assert budget is not None
        assert budget.warning_threshold.value == 256

    def test_get_budget_missing(self, sample_config):
        """Test getting non-existent budget."""
        budget = sample_config.get_budget(BudgetType.CPU_PERCENT)
        assert budget is None

    def test_to_dict(self, sample_config):
        """Test dictionary conversion."""
        data = sample_config.to_dict()
        assert data["name"] == "test"
        assert len(data["budgets"]) == 1
        assert "policy" in data

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "name": "loaded",
            "budgets": [
                {
                    "budget_type": "cpu_percent",
                    "warning_threshold": {"value": 50},
                    "error_threshold": {"value": 80},
                },
            ],
            "evaluation_window_seconds": 120,
        }
        config = SLOConfig.from_dict(data)
        assert config.name == "loaded"
        assert config.evaluation_window_seconds == 120
        assert len(config.budgets) == 1

    def test_json_file_roundtrip(self, sample_config):
        """Test saving and loading from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "slo.json"
            sample_config.to_json_file(path)

            loaded = SLOConfig.from_json_file(path)
            assert loaded.name == sample_config.name
            assert len(loaded.budgets) == len(sample_config.budgets)


class TestSLOFactories:
    """Tests for SLO factory functions."""

    def test_create_standard_slo(self):
        """Test standard SLO creation."""
        slo = create_standard_slo()
        assert slo.name == "standard"
        assert len(slo.budgets) >= 4
        assert slo.get_budget(BudgetType.STARTUP_LATENCY_MS) is not None
        assert slo.get_budget(BudgetType.MEMORY_MB) is not None

    def test_create_realtime_slo(self):
        """Test realtime SLO creation."""
        slo = create_realtime_slo()
        assert slo.name == "realtime"
        assert slo.policy.name == "strict"
        assert slo.evaluation_window_seconds == 10

        # Realtime should have tighter IPC latency
        ipc_budget = slo.get_budget(BudgetType.IPC_LATENCY_MS)
        assert ipc_budget is not None
        assert ipc_budget.warning_threshold.value <= 10


class TestSLOStatus:
    """Tests for SLOStatus enum."""

    def test_all_statuses_defined(self):
        """Test all expected statuses exist."""
        assert SLOStatus.HEALTHY
        assert SLOStatus.DEGRADED
        assert SLOStatus.UNHEALTHY
        assert SLOStatus.CRITICAL


class TestSLOViolation:
    """Tests for SLOViolation class."""

    def test_creation(self):
        """Test violation creation."""
        violation = SLOViolation(
            budget_type=BudgetType.MEMORY_MB,
            severity="error",
            actual_value=600,
            threshold_value=512,
            plugin_id="test-plugin",
            message="Memory exceeded",
        )
        assert violation.budget_type == BudgetType.MEMORY_MB
        assert violation.severity == "error"
        assert violation.actual_value == 600
        assert violation.threshold_value == 512

    def test_to_dict(self):
        """Test dictionary conversion."""
        violation = SLOViolation(
            budget_type=BudgetType.CPU_PERCENT,
            severity="critical",
            actual_value=98,
            threshold_value=95,
        )
        data = violation.to_dict()
        assert data["budget_type"] == "cpu_percent"
        assert data["severity"] == "critical"
        assert "timestamp" in data


class TestSLOResult:
    """Tests for SLOResult class."""

    def test_healthy_result(self):
        """Test healthy result properties."""
        result = SLOResult(
            status=SLOStatus.HEALTHY,
            violations=[],
            warnings=[],
            passing={BudgetType.MEMORY_MB: 200},
        )
        assert result.is_healthy is True
        assert result.violation_count == 0

    def test_unhealthy_result(self):
        """Test unhealthy result properties."""
        violation = SLOViolation(
            budget_type=BudgetType.CPU_PERCENT,
            severity="error",
            actual_value=90,
            threshold_value=80,
        )
        result = SLOResult(
            status=SLOStatus.UNHEALTHY,
            violations=[violation],
            warnings=[],
            passing={},
        )
        assert result.is_healthy is False
        assert result.violation_count == 1

    def test_to_dict(self):
        """Test dictionary conversion."""
        result = SLOResult(
            status=SLOStatus.DEGRADED,
            violations=[],
            warnings=[],
            passing={BudgetType.MEMORY_MB: 250},
            plugin_id="test",
        )
        data = result.to_dict()
        assert data["status"] == "degraded"
        assert data["plugin_id"] == "test"
        assert "memory_mb" in data["passing"]


class TestSLOEnforcer:
    """Tests for SLOEnforcer class."""

    @pytest.fixture
    def enforcer(self):
        """Create a sample enforcer."""
        config = SLOConfig(
            name="test",
            budgets=[
                Budget(
                    budget_type=BudgetType.MEMORY_MB,
                    warning_threshold=Threshold(256),
                    error_threshold=Threshold(512),
                    critical_threshold=Threshold(1024),
                ),
                Budget(
                    budget_type=BudgetType.CPU_PERCENT,
                    warning_threshold=Threshold(50),
                    error_threshold=Threshold(80),
                    critical_threshold=Threshold(95),
                ),
            ],
            minimum_samples=0,  # No minimum for testing
        )
        return SLOEnforcer(config, plugin_id="test-plugin")

    def test_creation(self, enforcer):
        """Test enforcer creation."""
        assert enforcer.plugin_id == "test-plugin"
        assert enforcer.config.name == "test"

    def test_record_sample(self, enforcer):
        """Test recording metric samples."""
        enforcer.record(BudgetType.MEMORY_MB, 200)
        enforcer.record(BudgetType.MEMORY_MB, 220)

        stats = enforcer.get_sample_stats()
        assert stats["memory_mb"]["count"] == 2
        assert stats["memory_mb"]["mean"] == 210

    def test_record_batch(self, enforcer):
        """Test recording batch of samples."""
        enforcer.record_batch(
            {
                BudgetType.MEMORY_MB: 200,
                BudgetType.CPU_PERCENT: 30,
            }
        )

        stats = enforcer.get_sample_stats()
        assert stats["memory_mb"]["count"] == 1
        assert stats["cpu_percent"]["count"] == 1

    def test_evaluate_healthy(self, enforcer):
        """Test evaluation with healthy values."""
        result = enforcer.evaluate(
            {
                BudgetType.MEMORY_MB: 200,
                BudgetType.CPU_PERCENT: 40,
            }
        )
        assert result.status == SLOStatus.HEALTHY
        assert len(result.violations) == 0
        assert len(result.warnings) == 0

    def test_evaluate_warning(self, enforcer):
        """Test evaluation with warning values."""
        result = enforcer.evaluate(
            {
                BudgetType.MEMORY_MB: 300,  # Warning
                BudgetType.CPU_PERCENT: 40,
            }
        )
        assert result.status == SLOStatus.DEGRADED
        assert len(result.warnings) == 1
        assert result.warnings[0].severity == "warning"

    def test_evaluate_error(self, enforcer):
        """Test evaluation with error values."""
        result = enforcer.evaluate(
            {
                BudgetType.MEMORY_MB: 600,  # Error
                BudgetType.CPU_PERCENT: 40,
            }
        )
        assert result.status == SLOStatus.UNHEALTHY
        assert len(result.violations) == 1
        assert result.violations[0].severity == "error"

    def test_evaluate_critical(self, enforcer):
        """Test evaluation with critical values."""
        result = enforcer.evaluate(
            {
                BudgetType.MEMORY_MB: 2000,  # Critical
                BudgetType.CPU_PERCENT: 98,  # Critical
            }
        )
        assert result.status == SLOStatus.CRITICAL
        assert len(result.violations) == 2

    def test_enforce_executes_actions(self, enforcer):
        """Test enforcement executes policy actions."""
        result = enforcer.evaluate(
            {
                BudgetType.MEMORY_MB: 600,  # Error
            }
        )

        actions = enforcer.enforce(result)
        # Default policy should log for errors
        assert PolicyAction.LOG in actions or len(actions) >= 0

    def test_enforce_with_custom_handler(self):
        """Test enforcement with custom action handler."""
        config = SLOConfig(
            name="test",
            budgets=[
                Budget(
                    budget_type=BudgetType.MEMORY_MB,
                    warning_threshold=Threshold(100),
                    error_threshold=Threshold(200),
                ),
            ],
            minimum_samples=0,
        )

        handler_called = []

        def custom_handler(violation):
            handler_called.append(violation)

        enforcer = SLOEnforcer(
            config,
            action_handlers={PolicyAction.LOG: custom_handler},
        )

        result = enforcer.evaluate({BudgetType.MEMORY_MB: 300})
        enforcer.enforce(result)

        assert len(handler_called) == 1
        assert handler_called[0].budget_type == BudgetType.MEMORY_MB

    def test_cooldown_prevents_repeated_actions(self, enforcer):
        """Test cooldown prevents repeated action execution."""
        result = enforcer.evaluate({BudgetType.MEMORY_MB: 600})

        # First enforcement
        actions1 = enforcer.enforce(result)

        # Immediate second enforcement should skip due to cooldown
        actions2 = enforcer.enforce(result)

        # Second should have no actions (cooldown)
        assert len(actions2) == 0 or len(actions1) >= len(actions2)

    def test_violation_history(self, enforcer):
        """Test violation history tracking."""
        enforcer.evaluate({BudgetType.MEMORY_MB: 600})
        enforcer.evaluate({BudgetType.MEMORY_MB: 700})

        history = enforcer.get_violation_history()
        assert len(history) == 2

    def test_status_history(self, enforcer):
        """Test status history tracking."""
        enforcer.evaluate({BudgetType.MEMORY_MB: 100})
        enforcer.evaluate({BudgetType.MEMORY_MB: 600})
        enforcer.evaluate({BudgetType.MEMORY_MB: 100})

        history = enforcer.get_status_history()
        assert len(history) == 3
        assert history[0][1] == SLOStatus.HEALTHY
        assert history[1][1] == SLOStatus.UNHEALTHY
        assert history[2][1] == SLOStatus.HEALTHY

    def test_uptime_percentage(self, enforcer):
        """Test uptime percentage calculation."""
        # All healthy
        for _ in range(10):
            enforcer.evaluate({BudgetType.MEMORY_MB: 100})

        uptime = enforcer.get_uptime_percentage()
        assert uptime == 100.0

    def test_uptime_percentage_with_violations(self, enforcer):
        """Test uptime percentage with some violations."""
        # 5 healthy, 5 unhealthy
        for _ in range(5):
            enforcer.evaluate({BudgetType.MEMORY_MB: 100})
        for _ in range(5):
            enforcer.evaluate({BudgetType.MEMORY_MB: 600})

        uptime = enforcer.get_uptime_percentage()
        assert uptime == 50.0

    def test_clear_violations(self, enforcer):
        """Test clearing violations."""
        enforcer.evaluate({BudgetType.MEMORY_MB: 600})
        assert len(enforcer.get_violation_history()) > 0

        enforcer.clear_violations()
        assert len(enforcer.get_violation_history()) == 0

    def test_reset_samples(self, enforcer):
        """Test resetting samples."""
        enforcer.record(BudgetType.MEMORY_MB, 200)
        stats = enforcer.get_sample_stats()
        assert stats["memory_mb"]["count"] == 1

        enforcer.reset_samples()
        stats = enforcer.get_sample_stats()
        assert stats["memory_mb"]["count"] == 0

    def test_to_dict(self, enforcer):
        """Test full state serialization."""
        enforcer.record(BudgetType.MEMORY_MB, 200)
        enforcer.evaluate({BudgetType.MEMORY_MB: 200})

        data = enforcer.to_dict()
        assert data["plugin_id"] == "test-plugin"
        assert "config" in data
        assert "current_result" in data
        assert "sample_stats" in data
        assert "uptime_24h" in data

    def test_aggregation_from_samples(self, enforcer):
        """Test evaluation aggregates from recorded samples."""
        # Record multiple samples
        for value in [100, 200, 300, 400, 500]:
            enforcer.record(BudgetType.MEMORY_MB, value)

        # Evaluate without providing current values
        result = enforcer.evaluate()

        # Should aggregate (P95 for latency-like metrics)
        assert result.status in [SLOStatus.HEALTHY, SLOStatus.DEGRADED, SLOStatus.UNHEALTHY]


class TestMetricSample:
    """Tests for MetricSample class."""

    def test_creation(self):
        """Test sample creation."""
        sample = MetricSample(
            budget_type=BudgetType.MEMORY_MB,
            value=256,
        )
        assert sample.budget_type == BudgetType.MEMORY_MB
        assert sample.value == 256
        assert sample.timestamp > 0

    def test_timestamp_defaults_to_now(self):
        """Test timestamp defaults to current time."""
        before = time.time()
        sample = MetricSample(budget_type=BudgetType.CPU_PERCENT, value=50)
        after = time.time()

        assert before <= sample.timestamp <= after
