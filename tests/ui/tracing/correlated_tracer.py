"""
CorrelatedTracer - Links UI actions to backend API calls with assertion support.

Provides a unified interface for tracing the relationship between user
interactions in the UI and the resulting backend API calls, enabling:
- Correlation of UI actions to specific API endpoints
- Assertion helpers for validating expected API behavior
- Timeline visualization of UI -> API flow
- Performance metrics across the full stack
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from .api_monitor import APIMonitor
from .workflow_tracer import WorkflowTracer


class CorrelationState(Enum):
    """State of a UI-API correlation."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class UIAction:
    """Represents a UI action that may trigger API calls."""
    name: str
    element_id: str | None
    action_type: str  # click, type, navigate, etc.
    timestamp: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CorrelatedCall:
    """Represents an API call correlated to a UI action."""
    ui_action: UIAction
    method: str
    endpoint: str
    request_time: float
    response_time: float | None = None
    status_code: int | None = None
    response_data: Any = None
    error: str | None = None

    @property
    def latency_ms(self) -> float | None:
        if self.response_time is None:
            return None
        return (self.response_time - self.request_time) * 1000

    @property
    def total_ms(self) -> float:
        """Time from UI action to API response."""
        if self.response_time is None:
            return (time.perf_counter() - self.ui_action.timestamp) * 1000
        return (self.response_time - self.ui_action.timestamp) * 1000


@dataclass
class Correlation:
    """A complete UI action to API response correlation."""
    id: str
    ui_action: UIAction
    expected_endpoints: list[str]
    api_calls: list[CorrelatedCall] = field(default_factory=list)
    state: CorrelationState = CorrelationState.PENDING
    assertions: list[dict] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float | None = None

    @property
    def duration_ms(self) -> float:
        if self.end_time is None:
            return (time.perf_counter() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000


class CorrelatedTracer:
    """
    Unified tracer linking UI actions to backend API calls.

    Usage:
        tracer = CorrelatedTracer(workflow_tracer, api_monitor)

        # Start tracking a UI action
        with tracer.track_action("click_import", "ImportButton", "click") as ctx:
            driver.find_element("accessibility id", "ImportButton").click()
            # API calls made during this block are automatically correlated
            ctx.expect_endpoint("/api/library/assets/upload")
            ctx.assert_status(201)
    """

    def __init__(
        self,
        workflow_tracer: WorkflowTracer,
        api_monitor: APIMonitor,
        correlation_timeout: float = 10.0,
    ):
        self.tracer = workflow_tracer
        self.monitor = api_monitor
        self.correlation_timeout = correlation_timeout
        self.correlations: list[Correlation] = []
        self._active_correlation: Correlation | None = None
        self._correlation_counter = 0
        self._original_monitor_hook: Callable | None = None

    def track_action(
        self,
        name: str,
        element_id: str | None = None,
        action_type: str = "click",
        expected_endpoints: list[str] | None = None,
        **metadata,
    ) -> CorrelationContext:
        """
        Start tracking a UI action and its correlated API calls.

        Args:
            name: Descriptive name for the action.
            element_id: Automation ID of the UI element.
            action_type: Type of action (click, type, navigate, etc.).
            expected_endpoints: List of API endpoints expected to be called.
            **metadata: Additional metadata to attach.

        Returns:
            CorrelationContext for use in a `with` block.
        """
        self._correlation_counter += 1
        correlation_id = f"corr_{self._correlation_counter:04d}"

        ui_action = UIAction(
            name=name,
            element_id=element_id,
            action_type=action_type,
            timestamp=time.perf_counter(),
            metadata=metadata,
        )

        correlation = Correlation(
            id=correlation_id,
            ui_action=ui_action,
            expected_endpoints=expected_endpoints or [],
            start_time=time.perf_counter(),
        )

        self.correlations.append(correlation)
        return CorrelationContext(self, correlation)

    def _start_correlation(self, correlation: Correlation):
        """Activate correlation tracking."""
        self._active_correlation = correlation
        correlation.state = CorrelationState.IN_PROGRESS

        # Log to workflow tracer
        self.tracer.step(
            f"[CORR] {correlation.ui_action.name} "
            f"({correlation.ui_action.action_type})"
        )

    def _end_correlation(self, correlation: Correlation):
        """Complete correlation tracking."""
        correlation.end_time = time.perf_counter()

        # Determine final state
        if correlation.assertions:
            all_passed = all(a.get("passed", False) for a in correlation.assertions)
            correlation.state = (
                CorrelationState.COMPLETED if all_passed
                else CorrelationState.FAILED
            )
        elif correlation.api_calls:
            correlation.state = CorrelationState.COMPLETED
        else:
            correlation.state = CorrelationState.TIMEOUT

        # Log summary
        call_count = len(correlation.api_calls)
        duration = correlation.duration_ms
        self.tracer.step(
            f"[CORR] Completed: {correlation.ui_action.name} "
            f"({call_count} API calls, {duration:.1f}ms)"
        )

        if self._active_correlation == correlation:
            self._active_correlation = None

    def record_api_call(
        self,
        method: str,
        endpoint: str,
        status_code: int | None = None,
        response_data: Any = None,
        error: str | None = None,
        request_time: float | None = None,
        response_time: float | None = None,
    ):
        """
        Record an API call and correlate to active UI action.

        This is called automatically when using APIMonitor with correlation.
        """
        if not self._active_correlation:
            return

        call = CorrelatedCall(
            ui_action=self._active_correlation.ui_action,
            method=method,
            endpoint=endpoint,
            request_time=request_time or time.perf_counter(),
            response_time=response_time,
            status_code=status_code,
            response_data=response_data,
            error=error,
        )
        self._active_correlation.api_calls.append(call)

    def assert_endpoint_called(
        self,
        endpoint: str,
        method: str | None = None,
        correlation: Correlation | None = None,
    ) -> bool:
        """Assert that an endpoint was called during the correlation."""
        corr = correlation or self._active_correlation
        if not corr:
            return False

        for call in corr.api_calls:
            if endpoint in call.endpoint:
                if method is None or call.method.upper() == method.upper():
                    return True
        return False

    def assert_status(
        self,
        expected_status: int,
        endpoint: str | None = None,
        correlation: Correlation | None = None,
    ) -> bool:
        """Assert API call returned expected status code."""
        corr = correlation or self._active_correlation
        if not corr:
            return False

        for call in corr.api_calls:
            if endpoint is None or endpoint in call.endpoint:
                if call.status_code == expected_status:
                    return True
        return False

    def get_correlation_summary(self) -> dict:
        """Get summary of all correlations."""
        return {
            "total": len(self.correlations),
            "completed": sum(
                1 for c in self.correlations
                if c.state == CorrelationState.COMPLETED
            ),
            "failed": sum(
                1 for c in self.correlations
                if c.state == CorrelationState.FAILED
            ),
            "total_api_calls": sum(
                len(c.api_calls) for c in self.correlations
            ),
            "correlations": [
                {
                    "id": c.id,
                    "action": c.ui_action.name,
                    "state": c.state.value,
                    "duration_ms": c.duration_ms,
                    "api_calls": len(c.api_calls),
                }
                for c in self.correlations
            ],
        }

    def export_timeline(self, output_path: Path) -> Path:
        """Export correlation timeline to JSON."""
        import json

        timeline = []
        for corr in self.correlations:
            entry = {
                "id": corr.id,
                "ui_action": {
                    "name": corr.ui_action.name,
                    "element": corr.ui_action.element_id,
                    "type": corr.ui_action.action_type,
                    "timestamp": corr.ui_action.timestamp,
                },
                "state": corr.state.value,
                "duration_ms": corr.duration_ms,
                "api_calls": [
                    {
                        "method": call.method,
                        "endpoint": call.endpoint,
                        "status": call.status_code,
                        "latency_ms": call.latency_ms,
                    }
                    for call in corr.api_calls
                ],
                "assertions": corr.assertions,
            }
            timeline.append(entry)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(timeline, f, indent=2, default=str)

        return output_path


class CorrelationContext:
    """Context manager for correlation tracking with assertion helpers."""

    def __init__(self, tracer: CorrelatedTracer, correlation: Correlation):
        self._tracer = tracer
        self._correlation = correlation

    def __enter__(self) -> CorrelationContext:
        self._tracer._start_correlation(self._correlation)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._correlation.state = CorrelationState.FAILED
            self._correlation.assertions.append({
                "type": "exception",
                "passed": False,
                "error": str(exc_val),
            })
        self._tracer._end_correlation(self._correlation)
        return False

    def expect_endpoint(
        self,
        endpoint: str,
        method: str | None = None,  # Reserved for future method filtering
        timeout: float | None = None,  # Reserved for future timeout handling
    ) -> CorrelationContext:
        """Declare expected endpoint to be called."""
        _ = method, timeout  # Reserved for future use
        if endpoint not in self._correlation.expected_endpoints:
            self._correlation.expected_endpoints.append(endpoint)
        return self

    def assert_status(
        self,
        expected_status: int,
        endpoint: str | None = None,
    ) -> CorrelationContext:
        """Assert expected status code from API call."""
        passed = self._tracer.assert_status(
            expected_status, endpoint, self._correlation
        )
        self._correlation.assertions.append({
            "type": "status",
            "expected": expected_status,
            "endpoint": endpoint,
            "passed": passed,
        })
        return self

    def assert_endpoint_called(
        self,
        endpoint: str,
        method: str | None = None,
    ) -> CorrelationContext:
        """Assert endpoint was called."""
        passed = self._tracer.assert_endpoint_called(
            endpoint, method, self._correlation
        )
        self._correlation.assertions.append({
            "type": "endpoint_called",
            "endpoint": endpoint,
            "method": method,
            "passed": passed,
        })
        return self

    def assert_response_contains(
        self,
        key: str,
        value: Any = None,
        endpoint: str | None = None,
    ) -> CorrelationContext:
        """Assert response data contains expected key/value."""
        passed = False
        for call in self._correlation.api_calls:
            if endpoint and endpoint not in call.endpoint:
                continue
            if isinstance(call.response_data, dict):
                if key in call.response_data:
                    if value is None or call.response_data[key] == value:
                        passed = True
                        break

        self._correlation.assertions.append({
            "type": "response_contains",
            "key": key,
            "value": value,
            "endpoint": endpoint,
            "passed": passed,
        })
        return self

    @property
    def api_calls(self) -> list[CorrelatedCall]:
        """Access correlated API calls."""
        return self._correlation.api_calls

    @property
    def correlation(self) -> Correlation:
        """Access the underlying correlation object."""
        return self._correlation
