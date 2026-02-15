"""
Workflow Tracer - Captures detailed execution traces for debugging.

Provides timestamped operation logging, screenshot capture at each step,
backend API call logging, error capture with full stack traces, panel
transition tracking, inter-panel event monitoring, and export to JSON/HTML reports.

Enhanced for comprehensive Allan Watts audio workflow testing with:
- Panel transition tracking with timing metrics
- Inter-panel event monitoring (EventAggregator events)
- Workflow phase tracking
- Performance profiling per operation type
- Detailed categorization of all traced events
"""

import json
import time
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class EventCategory(Enum):
    """Categories for traced events."""
    WORKFLOW = "workflow"
    PANEL = "panel"
    API = "api"
    UI = "ui"
    EVENT = "event"
    ERROR = "error"
    PERFORMANCE = "performance"


@dataclass
class PanelTransition:
    """Represents a panel transition with timing."""
    from_panel: str
    to_panel: str
    start_time: float
    end_time: float | None = None
    success: bool = False
    error: str | None = None

    @property
    def duration_ms(self) -> float:
        if self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time) * 1000


@dataclass
class TracedEvent:
    """Represents an inter-panel or application event."""
    event_name: str
    source_panel: str | None
    target_panel: str | None
    payload: dict[str, Any] | None
    timestamp: float
    category: str = "event"

# HTML report template
HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiceStudio Workflow Trace: {workflow_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; border-bottom: 2px solid #0078d4; padding-bottom: 10px; }}
        h2 {{ color: #0078d4; margin-top: 30px; }}
        .summary {{ background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .summary-item {{ display: inline-block; margin-right: 30px; }}
        .summary-label {{ font-weight: bold; color: #666; }}
        .summary-value {{ font-size: 1.2em; color: #333; }}
        .step {{ background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .step-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .step-name {{ font-weight: bold; color: #333; }}
        .step-time {{ color: #666; font-size: 0.9em; }}
        .step-elapsed {{ background: #e3f2fd; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }}
        .step.error {{ border-left: 4px solid #d32f2f; }}
        .step.success {{ border-left: 4px solid #4caf50; }}
        .api-call {{ background: #f9f9f9; padding: 10px; margin-top: 10px; border-radius: 4px; font-family: monospace; font-size: 0.9em; }}
        .api-method {{ font-weight: bold; }}
        .api-method.GET {{ color: #4caf50; }}
        .api-method.POST {{ color: #2196f3; }}
        .api-method.PUT {{ color: #ff9800; }}
        .api-method.DELETE {{ color: #f44336; }}
        .api-status {{ padding: 2px 6px; border-radius: 3px; }}
        .api-status.success {{ background: #c8e6c9; color: #2e7d32; }}
        .api-status.error {{ background: #ffcdd2; color: #c62828; }}
        .screenshot {{ max-width: 100%; margin-top: 10px; border: 1px solid #ddd; border-radius: 4px; }}
        .error-trace {{ background: #ffebee; padding: 10px; border-radius: 4px; margin-top: 10px; white-space: pre-wrap; font-family: monospace; font-size: 0.85em; color: #c62828; }}
        .collapsible {{ cursor: pointer; user-select: none; }}
        .collapsible::before {{ content: '▶ '; }}
        .collapsible.active::before {{ content: '▼ '; }}
        .content {{ display: none; padding-left: 20px; }}
        .content.show {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Workflow Trace: {workflow_name}</h1>

        <div class="summary">
            <div class="summary-item">
                <span class="summary-label">Started:</span>
                <span class="summary-value">{start_time}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Duration:</span>
                <span class="summary-value">{total_duration}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Steps:</span>
                <span class="summary-value">{step_count}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">API Calls:</span>
                <span class="summary-value">{api_call_count}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Status:</span>
                <span class="summary-value" style="color: {status_color}">{status}</span>
            </div>
        </div>

        <h2>Execution Steps</h2>
        {steps_html}

        <h2>API Calls</h2>
        {api_calls_html}
    </div>

    <script>
        document.querySelectorAll('.collapsible').forEach(el => {{
            el.addEventListener('click', function() {{
                this.classList.toggle('active');
                const content = this.nextElementSibling;
                content.classList.toggle('show');
            }});
        }});
    </script>
</body>
</html>
"""


class WorkflowTracer:
    """Captures detailed execution traces for debugging VoiceStudio workflows."""

    def __init__(self, workflow_name: str, output_dir: Path | None = None):
        """
        Initialize a workflow tracer.

        Args:
            workflow_name: Name of the workflow being traced.
            output_dir: Directory for output artifacts. Defaults to .buildlogs/validation/
        """
        self.workflow_name = workflow_name
        self.output_dir = output_dir or Path(".buildlogs/validation")
        self.trace_log: list[dict[str, Any]] = []
        self.screenshots: list[dict[str, Any]] = []
        self.api_calls: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []
        self._start_time: float | None = None
        self._step_start: float | None = None
        self._current_step: str | None = None

        # Panel transition tracking
        self.panel_transitions: list[PanelTransition] = []
        self._current_panel: str | None = None
        self._pending_transition: PanelTransition | None = None

        # Event tracking
        self.traced_events: list[TracedEvent] = []

        # Workflow phase tracking
        self._current_phase: str | None = None
        self.phases: list[dict[str, Any]] = []

        # Performance metrics by operation type
        self.performance_metrics: dict[str, list[float]] = {
            "panel_navigation": [],
            "api_call": [],
            "screenshot": [],
            "file_operation": [],
            "ui_interaction": [],
        }

        # Ensure output directories exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "screenshots").mkdir(exist_ok=True)
        (self.output_dir / "reports" / "workflow_traces").mkdir(parents=True, exist_ok=True)

    def start(self) -> "WorkflowTracer":
        """Start the workflow trace timer."""
        self._start_time = time.perf_counter()
        self.trace_log.append({
            "event": "workflow_start",
            "workflow": self.workflow_name,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": 0
        })
        return self

    def step(self, name: str, driver=None, capture_screenshot: bool = True) -> "WorkflowTracer":
        """
        Record a workflow step with optional screenshot.

        Args:
            name: Name/description of this step.
            driver: WinAppDriver session for screenshot capture.
            capture_screenshot: Whether to capture a screenshot.

        Returns:
            Self for method chaining.
        """
        timestamp = datetime.now()
        elapsed_ms = self._elapsed_ms()

        # Calculate step duration if there was a previous step
        step_duration_ms = None
        if self._step_start is not None:
            step_duration_ms = (time.perf_counter() - self._step_start) * 1000

        self._step_start = time.perf_counter()
        self._current_step = name

        step_entry = {
            "event": "step",
            "step": name,
            "step_number": len([s for s in self.trace_log if s.get("event") == "step"]) + 1,
            "timestamp": timestamp.isoformat(),
            "elapsed_ms": elapsed_ms,
            "step_duration_ms": step_duration_ms,
        }

        # Capture screenshot if driver provided
        if driver and capture_screenshot:
            screenshot_path = self._capture_screenshot(driver, name, len(self.screenshots) + 1)
            if screenshot_path:
                step_entry["screenshot"] = str(screenshot_path)

        self.trace_log.append(step_entry)
        return self

    def api_call(self, method: str, url: str, response, request_body: Any = None) -> "WorkflowTracer":
        """
        Log an API call with request/response details.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            response: Response object (requests.Response)
            request_body: Optional request body

        Returns:
            Self for method chaining.
        """
        elapsed_ms = self._elapsed_ms()

        response_body = None
        try:
            response_body = response.json()
        except Exception:
            response_body = response.text[:500] if hasattr(response, "text") else None

        call_entry = {
            "event": "api_call",
            "method": method,
            "url": url,
            "status": response.status_code if hasattr(response, "status_code") else None,
            "response_time_ms": response.elapsed.total_seconds() * 1000 if hasattr(response, "elapsed") else None,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": elapsed_ms,
            "current_step": self._current_step,
            "request_body": self._safe_serialize(request_body),
            "response_body": self._safe_serialize(response_body),
        }

        self.api_calls.append(call_entry)
        self.trace_log.append(call_entry)
        return self

    def error(self, exception: Exception, context: str = "") -> "WorkflowTracer":
        """
        Log an error with full stack trace.

        Args:
            exception: The exception that occurred.
            context: Additional context about the error.

        Returns:
            Self for method chaining.
        """
        elapsed_ms = self._elapsed_ms()

        error_entry = {
            "event": "error",
            "error_type": type(exception).__name__,
            "error_message": str(exception),
            "stack_trace": traceback.format_exc(),
            "context": context,
            "current_step": self._current_step,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": elapsed_ms,
        }

        self.errors.append(error_entry)
        self.trace_log.append(error_entry)
        return self

    def success(self, message: str = "") -> "WorkflowTracer":
        """Mark the workflow as successfully completed."""
        self.trace_log.append({
            "event": "workflow_complete",
            "status": "success",
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": self._elapsed_ms(),
        })
        return self

    def fail(self, message: str = "") -> "WorkflowTracer":
        """Mark the workflow as failed."""
        self.trace_log.append({
            "event": "workflow_complete",
            "status": "failed",
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": self._elapsed_ms(),
        })
        return self

    # =========================================================================
    # Panel Transition Tracking
    # =========================================================================

    def start_panel_transition(
        self,
        from_panel: str,
        to_panel: str,
        driver=None,
        capture_screenshot: bool = False
    ) -> "WorkflowTracer":
        """
        Start tracking a panel transition.

        Args:
            from_panel: Source panel name (can be empty for initial navigation).
            to_panel: Target panel name.
            driver: Optional WinAppDriver session for screenshot.
            capture_screenshot: Whether to capture a screenshot.

        Returns:
            Self for method chaining.
        """
        # Complete any pending transition first
        if self._pending_transition:
            self.end_panel_transition(success=False, error="Interrupted by new transition")

        self._pending_transition = PanelTransition(
            from_panel=from_panel or self._current_panel or "unknown",
            to_panel=to_panel,
            start_time=time.perf_counter(),
        )

        entry = {
            "event": "panel_transition_start",
            "category": EventCategory.PANEL.value,
            "from_panel": self._pending_transition.from_panel,
            "to_panel": to_panel,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": self._elapsed_ms(),
        }
        self.trace_log.append(entry)

        if driver and capture_screenshot:
            self._capture_screenshot(driver, f"transition_start_{to_panel}", len(self.screenshots) + 1)

        return self

    def end_panel_transition(
        self,
        success: bool = True,
        error: str | None = None,
        driver=None,
        capture_screenshot: bool = True
    ) -> "WorkflowTracer":
        """
        End tracking the current panel transition.

        Args:
            success: Whether the transition succeeded.
            error: Error message if transition failed.
            driver: Optional WinAppDriver session for screenshot.
            capture_screenshot: Whether to capture a screenshot.

        Returns:
            Self for method chaining.
        """
        if not self._pending_transition:
            return self

        self._pending_transition.end_time = time.perf_counter()
        self._pending_transition.success = success
        self._pending_transition.error = error

        duration_ms = self._pending_transition.duration_ms
        self.performance_metrics["panel_navigation"].append(duration_ms)

        entry = {
            "event": "panel_transition_end",
            "category": EventCategory.PANEL.value,
            "from_panel": self._pending_transition.from_panel,
            "to_panel": self._pending_transition.to_panel,
            "success": success,
            "duration_ms": duration_ms,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": self._elapsed_ms(),
        }
        self.trace_log.append(entry)

        if success:
            self._current_panel = self._pending_transition.to_panel

        self.panel_transitions.append(self._pending_transition)
        self._pending_transition = None

        if driver and capture_screenshot:
            panel_name = self._current_panel or "unknown"
            self._capture_screenshot(driver, f"panel_{panel_name}", len(self.screenshots) + 1)

        return self

    def panel_transition(
        self,
        from_panel: str,
        to_panel: str,
        success: bool,
        duration_ms: float,
        error: str | None = None
    ) -> "WorkflowTracer":
        """
        Record a complete panel transition (shorthand method).

        Args:
            from_panel: Source panel name.
            to_panel: Target panel name.
            success: Whether the transition succeeded.
            duration_ms: Duration in milliseconds.
            error: Optional error message.

        Returns:
            Self for method chaining.
        """
        transition = PanelTransition(
            from_panel=from_panel,
            to_panel=to_panel,
            start_time=time.perf_counter() - (duration_ms / 1000),
            end_time=time.perf_counter(),
            success=success,
            error=error,
        )
        self.panel_transitions.append(transition)
        self.performance_metrics["panel_navigation"].append(duration_ms)

        if success:
            self._current_panel = to_panel

        entry = {
            "event": "panel_transition",
            "category": EventCategory.PANEL.value,
            "from_panel": from_panel,
            "to_panel": to_panel,
            "success": success,
            "duration_ms": duration_ms,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": self._elapsed_ms(),
        }
        self.trace_log.append(entry)
        return self

    def get_current_panel(self) -> str | None:
        """Get the current panel name."""
        return self._current_panel

    # =========================================================================
    # Event Tracking
    # =========================================================================

    def trace_event(
        self,
        event_name: str,
        source_panel: str | None = None,
        target_panel: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> "WorkflowTracer":
        """
        Trace an inter-panel or application event.

        Args:
            event_name: Name of the event (e.g., "AssetAddedEvent").
            source_panel: Panel that published the event.
            target_panel: Panel that received/should receive the event.
            payload: Event payload data.

        Returns:
            Self for method chaining.
        """
        traced = TracedEvent(
            event_name=event_name,
            source_panel=source_panel or self._current_panel,
            target_panel=target_panel,
            payload=self._safe_serialize(payload),
            timestamp=time.perf_counter(),
        )
        self.traced_events.append(traced)

        entry = {
            "event": "traced_event",
            "category": EventCategory.EVENT.value,
            "event_name": event_name,
            "source_panel": traced.source_panel,
            "target_panel": target_panel,
            "payload": traced.payload,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": self._elapsed_ms(),
            "current_step": self._current_step,
        }
        self.trace_log.append(entry)
        return self

    def expect_event(
        self,
        event_name: str,
        within_ms: float = 5000,
        check_interval_ms: float = 100,
        validator: Callable[[TracedEvent], bool] | None = None,
    ) -> TracedEvent | None:
        """
        Wait for and expect an event to occur.

        Args:
            event_name: Name of the expected event.
            within_ms: Maximum time to wait in milliseconds.
            check_interval_ms: Interval between checks.
            validator: Optional function to validate the event.

        Returns:
            The traced event if found, None otherwise.
        """
        start = time.perf_counter()
        initial_count = len(self.traced_events)

        while (time.perf_counter() - start) * 1000 < within_ms:
            # Check for new events matching the name
            for evt in self.traced_events[initial_count:]:
                if evt.event_name == event_name:
                    if validator is None or validator(evt):
                        return evt
            time.sleep(check_interval_ms / 1000)

        return None

    # =========================================================================
    # Workflow Phase Tracking
    # =========================================================================

    def start_phase(self, phase_name: str, description: str = "") -> "WorkflowTracer":
        """
        Start a new workflow phase.

        Args:
            phase_name: Name of the phase.
            description: Description of what this phase does.

        Returns:
            Self for method chaining.
        """
        # End previous phase if any
        if self._current_phase and self.phases:
            self.phases[-1]["end_time"] = datetime.now().isoformat()
            self.phases[-1]["elapsed_ms"] = self._elapsed_ms()

        self._current_phase = phase_name
        phase_entry = {
            "phase_name": phase_name,
            "description": description,
            "start_time": datetime.now().isoformat(),
            "start_elapsed_ms": self._elapsed_ms(),
            "end_time": None,
            "elapsed_ms": None,
            "steps": [],
            "errors": [],
        }
        self.phases.append(phase_entry)

        entry = {
            "event": "phase_start",
            "category": EventCategory.WORKFLOW.value,
            "phase_name": phase_name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": self._elapsed_ms(),
        }
        self.trace_log.append(entry)
        return self

    def end_phase(self, success: bool = True, notes: str = "") -> "WorkflowTracer":
        """
        End the current workflow phase.

        Args:
            success: Whether the phase completed successfully.
            notes: Additional notes about the phase completion.

        Returns:
            Self for method chaining.
        """
        if not self._current_phase or not self.phases:
            return self

        current_phase = self.phases[-1]
        current_phase["end_time"] = datetime.now().isoformat()
        current_phase["elapsed_ms"] = self._elapsed_ms() - current_phase["start_elapsed_ms"]
        current_phase["success"] = success
        current_phase["notes"] = notes

        entry = {
            "event": "phase_end",
            "category": EventCategory.WORKFLOW.value,
            "phase_name": self._current_phase,
            "success": success,
            "notes": notes,
            "duration_ms": current_phase["elapsed_ms"],
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": self._elapsed_ms(),
        }
        self.trace_log.append(entry)
        self._current_phase = None
        return self

    # =========================================================================
    # UI Interaction Tracking
    # =========================================================================

    def ui_action(
        self,
        action_type: str,
        element_id: str,
        details: dict[str, Any] | None = None,
        driver=None,
        capture_screenshot: bool = False
    ) -> "WorkflowTracer":
        """
        Track a UI interaction.

        Args:
            action_type: Type of action (click, type, select, etc.).
            element_id: Automation ID or identifier of the element.
            details: Additional details (text typed, option selected, etc.).
            driver: Optional WinAppDriver session.
            capture_screenshot: Whether to capture a screenshot.

        Returns:
            Self for method chaining.
        """
        entry = {
            "event": "ui_action",
            "category": EventCategory.UI.value,
            "action_type": action_type,
            "element_id": element_id,
            "details": self._safe_serialize(details),
            "current_panel": self._current_panel,
            "current_step": self._current_step,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": self._elapsed_ms(),
        }
        self.trace_log.append(entry)

        if driver and capture_screenshot:
            self._capture_screenshot(driver, f"ui_{action_type}_{element_id}", len(self.screenshots) + 1)

        return self

    # =========================================================================
    # Performance Tracking
    # =========================================================================

    def record_timing(
        self,
        operation_type: str,
        duration_ms: float,
        details: str | None = None
    ) -> "WorkflowTracer":
        """
        Record a timing metric.

        Args:
            operation_type: Type of operation being timed.
            duration_ms: Duration in milliseconds.
            details: Optional details about the operation.

        Returns:
            Self for method chaining.
        """
        if operation_type not in self.performance_metrics:
            self.performance_metrics[operation_type] = []
        self.performance_metrics[operation_type].append(duration_ms)

        entry = {
            "event": "timing",
            "category": EventCategory.PERFORMANCE.value,
            "operation_type": operation_type,
            "duration_ms": duration_ms,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": self._elapsed_ms(),
        }
        self.trace_log.append(entry)
        return self

    def get_performance_summary(self) -> dict[str, dict[str, float]]:
        """
        Get a summary of performance metrics.

        Returns:
            Dictionary with min, max, avg, count for each operation type.
        """
        summary = {}
        for op_type, timings in self.performance_metrics.items():
            if timings:
                summary[op_type] = {
                    "count": len(timings),
                    "min_ms": min(timings),
                    "max_ms": max(timings),
                    "avg_ms": sum(timings) / len(timings),
                    "total_ms": sum(timings),
                }
        return summary

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    def _elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds since workflow start."""
        if self._start_time is None:
            return 0
        return (time.perf_counter() - self._start_time) * 1000

    def _capture_screenshot(self, driver, step_name: str, index: int) -> Path | None:
        """Capture and save a screenshot."""
        try:
            # Sanitize step name for filename
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in step_name)
            filename = f"step_{index:03d}_{safe_name}.png"
            filepath = self.output_dir / "screenshots" / filename

            driver.save_screenshot(str(filepath))

            self.screenshots.append({
                "step": step_name,
                "path": str(filepath),
                "timestamp": datetime.now().isoformat(),
            })

            return filepath
        except Exception as e:
            print(f"Warning: Failed to capture screenshot: {e}")
            return None

    def _safe_serialize(self, obj: Any) -> Any:
        """Safely serialize an object to JSON-compatible format."""
        if obj is None:
            return None
        try:
            # Test if it's JSON serializable
            json.dumps(obj)
            return obj
        except (TypeError, ValueError):
            return str(obj)[:1000]  # Truncate to prevent huge logs

    def export_json(self, output_path: Path | None = None) -> Path:
        """
        Export trace to JSON file.

        Args:
            output_path: Optional output path. Defaults to workflow_traces directory.

        Returns:
            Path to the exported JSON file.
        """
        if output_path is None:
            output_path = self.output_dir / "reports" / "workflow_traces" / f"{self.workflow_name}_trace.json"

        # Serialize panel transitions
        panel_transitions_data = [
            {
                "from_panel": t.from_panel,
                "to_panel": t.to_panel,
                "duration_ms": t.duration_ms,
                "success": t.success,
                "error": t.error,
            }
            for t in self.panel_transitions
        ]

        # Serialize traced events
        traced_events_data = [
            {
                "event_name": e.event_name,
                "source_panel": e.source_panel,
                "target_panel": e.target_panel,
                "payload": e.payload,
                "category": e.category,
            }
            for e in self.traced_events
        ]

        export_data = {
            "workflow_name": self.workflow_name,
            "export_time": datetime.now().isoformat(),
            "total_duration_ms": self._elapsed_ms(),
            "step_count": len([s for s in self.trace_log if s.get("event") == "step"]),
            "api_call_count": len(self.api_calls),
            "error_count": len(self.errors),
            "panel_transition_count": len(self.panel_transitions),
            "event_count": len(self.traced_events),
            "phase_count": len(self.phases),
            "trace_log": self.trace_log,
            "api_calls": self.api_calls,
            "screenshots": self.screenshots,
            "errors": self.errors,
            "panel_transitions": panel_transitions_data,
            "traced_events": traced_events_data,
            "phases": self.phases,
            "performance_summary": self.get_performance_summary(),
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, default=str)

        return output_path

    def export_html(self, output_path: Path | None = None) -> Path:
        """
        Export trace to HTML report.

        Args:
            output_path: Optional output path. Defaults to workflow_traces directory.

        Returns:
            Path to the exported HTML file.
        """
        if output_path is None:
            output_path = self.output_dir / "reports" / "workflow_traces" / f"{self.workflow_name}_trace.html"

        # Build steps HTML
        steps_html = ""
        for entry in self.trace_log:
            if entry.get("event") == "step":
                step_class = "step"
                if any(e.get("current_step") == entry["step"] for e in self.errors):
                    step_class += " error"
                else:
                    step_class += " success"

                screenshot_html = ""
                if "screenshot" in entry:
                    screenshot_html = f'<img class="screenshot" src="{entry["screenshot"]}" alt="Screenshot">'

                steps_html += f"""
                <div class="{step_class}">
                    <div class="step-header">
                        <span class="step-name">Step {entry.get('step_number', '?')}: {entry['step']}</span>
                        <span class="step-elapsed">{entry.get('elapsed_ms', 0):.1f}ms</span>
                    </div>
                    <div class="step-time">{entry['timestamp']}</div>
                    {screenshot_html}
                </div>
                """

        # Build API calls HTML
        api_calls_html = ""
        for call in self.api_calls:
            status_class = "success" if call.get("status", 500) < 400 else "error"
            api_calls_html += f"""
            <div class="api-call">
                <span class="api-method {call['method']}">{call['method']}</span>
                <span>{call['url']}</span>
                <span class="api-status {status_class}">{call.get('status', 'N/A')}</span>
                <span class="step-elapsed">{call.get('response_time_ms', 0):.1f}ms</span>
            </div>
            """

        # Build panel transitions HTML
        transitions_html = ""
        for t in self.panel_transitions:
            t_class = "success" if t.success else "error"
            transitions_html += f"""
            <div class="step {t_class}">
                <div class="step-header">
                    <span class="step-name">{t.from_panel} → {t.to_panel}</span>
                    <span class="step-elapsed">{t.duration_ms:.1f}ms</span>
                </div>
                {f'<div class="error-trace">{t.error}</div>' if t.error else ''}
            </div>
            """

        # Build performance summary HTML
        perf_summary = self.get_performance_summary()
        perf_html = ""
        for op_type, stats in perf_summary.items():
            perf_html += f"""
            <div class="api-call">
                <span class="api-method GET">{op_type}</span>
                <span>Count: {stats['count']}</span>
                <span>Avg: {stats['avg_ms']:.1f}ms</span>
                <span>Min: {stats['min_ms']:.1f}ms</span>
                <span>Max: {stats['max_ms']:.1f}ms</span>
            </div>
            """

        # Build phases HTML
        phases_html = ""
        for phase in self.phases:
            phase_class = "success" if phase.get("success", True) else "error"
            elapsed_ms = phase.get('elapsed_ms') or 0  # Handle None explicitly
            description = phase.get('description') or ''
            phase_name = phase.get('phase_name', 'Unknown Phase')
            phases_html += f"""
            <div class="step {phase_class}">
                <div class="step-header">
                    <span class="step-name">{phase_name}</span>
                    <span class="step-elapsed">{elapsed_ms:.1f}ms</span>
                </div>
                <div class="step-time">{description}</div>
            </div>
            """

        # Determine overall status
        completion = next((e for e in reversed(self.trace_log) if e.get("event") == "workflow_complete"), None)
        status = completion.get("status", "incomplete") if completion else "incomplete"
        status_color = "#4caf50" if status == "success" else "#d32f2f" if status == "failed" else "#ff9800"

        # Generate HTML using extended template
        html = self._build_extended_html_report(
            workflow_name=self.workflow_name,
            start_time=self.trace_log[0]["timestamp"] if self.trace_log else "N/A",
            total_duration=f"{self._elapsed_ms() / 1000:.2f}s",
            step_count=len([s for s in self.trace_log if s.get("event") == "step"]),
            api_call_count=len(self.api_calls),
            transition_count=len(self.panel_transitions),
            event_count=len(self.traced_events),
            status=status.upper(),
            status_color=status_color,
            steps_html=steps_html,
            api_calls_html=api_calls_html or "<p>No API calls recorded.</p>",
            transitions_html=transitions_html or "<p>No panel transitions recorded.</p>",
            perf_html=perf_html or "<p>No performance metrics recorded.</p>",
            phases_html=phases_html or "<p>No phases recorded.</p>",
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)

        return output_path

    def _build_extended_html_report(self, **kwargs) -> str:
        """Build an extended HTML report with all tracking sections."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiceStudio Workflow Trace: {kwargs['workflow_name']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; border-bottom: 2px solid #0078d4; padding-bottom: 10px; }}
        h2 {{ color: #0078d4; margin-top: 30px; }}
        .summary {{ background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 20px; }}
        .summary-item {{ display: inline-block; }}
        .summary-label {{ font-weight: bold; color: #666; display: block; font-size: 0.85em; }}
        .summary-value {{ font-size: 1.2em; color: #333; }}
        .step {{ background: #fff; padding: 15px; border-radius: 8px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .step-header {{ display: flex; justify-content: space-between; align-items: center; }}
        .step-name {{ font-weight: bold; color: #333; }}
        .step-time {{ color: #666; font-size: 0.9em; }}
        .step-elapsed {{ background: #e3f2fd; padding: 2px 8px; border-radius: 4px; font-size: 0.85em; }}
        .step.error {{ border-left: 4px solid #d32f2f; }}
        .step.success {{ border-left: 4px solid #4caf50; }}
        .api-call {{ background: #f9f9f9; padding: 10px; margin-bottom: 5px; border-radius: 4px; font-family: monospace; font-size: 0.9em; display: flex; gap: 15px; align-items: center; }}
        .api-method {{ font-weight: bold; min-width: 80px; }}
        .api-method.GET {{ color: #4caf50; }}
        .api-method.POST {{ color: #2196f3; }}
        .api-method.PUT {{ color: #ff9800; }}
        .api-method.DELETE {{ color: #f44336; }}
        .api-status {{ padding: 2px 6px; border-radius: 3px; }}
        .api-status.success {{ background: #c8e6c9; color: #2e7d32; }}
        .api-status.error {{ background: #ffcdd2; color: #c62828; }}
        .screenshot {{ max-width: 100%; margin-top: 10px; border: 1px solid #ddd; border-radius: 4px; }}
        .error-trace {{ background: #ffebee; padding: 10px; border-radius: 4px; margin-top: 10px; white-space: pre-wrap; font-family: monospace; font-size: 0.85em; color: #c62828; }}
        .tabs {{ display: flex; gap: 5px; margin-bottom: 20px; flex-wrap: wrap; }}
        .tab {{ padding: 10px 20px; background: #e0e0e0; border: none; cursor: pointer; border-radius: 4px 4px 0 0; }}
        .tab.active {{ background: #fff; font-weight: bold; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Workflow Trace: {kwargs['workflow_name']}</h1>

        <div class="summary">
            <div class="summary-item">
                <span class="summary-label">Started</span>
                <span class="summary-value">{kwargs['start_time']}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Duration</span>
                <span class="summary-value">{kwargs['total_duration']}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Steps</span>
                <span class="summary-value">{kwargs['step_count']}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">API Calls</span>
                <span class="summary-value">{kwargs['api_call_count']}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Transitions</span>
                <span class="summary-value">{kwargs['transition_count']}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Events</span>
                <span class="summary-value">{kwargs['event_count']}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Status</span>
                <span class="summary-value" style="color: {kwargs['status_color']}">{kwargs['status']}</span>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('steps')">Steps</button>
            <button class="tab" onclick="showTab('api')">API Calls</button>
            <button class="tab" onclick="showTab('transitions')">Panel Transitions</button>
            <button class="tab" onclick="showTab('phases')">Phases</button>
            <button class="tab" onclick="showTab('performance')">Performance</button>
        </div>

        <div id="steps" class="tab-content active">
            <h2>Execution Steps</h2>
            {kwargs['steps_html']}
        </div>

        <div id="api" class="tab-content">
            <h2>API Calls</h2>
            {kwargs['api_calls_html']}
        </div>

        <div id="transitions" class="tab-content">
            <h2>Panel Transitions</h2>
            {kwargs['transitions_html']}
        </div>

        <div id="phases" class="tab-content">
            <h2>Workflow Phases</h2>
            {kwargs['phases_html']}
        </div>

        <div id="performance" class="tab-content">
            <h2>Performance Metrics</h2>
            {kwargs['perf_html']}
        </div>
    </div>

    <script>
        function showTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            document.querySelector('[onclick*=\"' + tabId + '\"]').classList.add('active');
        }}
    </script>
</body>
</html>
"""

    def export_report(self, output_path: Path | None = None) -> Path:
        """
        Export trace to both JSON and HTML reports.

        Args:
            output_path: Base output path (without extension).

        Returns:
            Path to the HTML report.
        """
        self.export_json()
        return self.export_html(output_path)
