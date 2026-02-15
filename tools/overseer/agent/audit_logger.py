"""
Audit Logger

High-level interface for logging agent actions with automatic context capture.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .audit_store import AuditEntry, AuditStore
from .identity import AgentIdentity


@dataclass
class LogContext:
    """Context for a logged operation."""

    start_time: datetime
    agent: AgentIdentity
    tool_name: str
    parameters: dict
    correlation_id: str
    risk_tier: str = "low"


class AuditLogger:
    """
    High-level audit logging interface.

    Provides context managers and decorators for automatic logging
    of agent actions with timing and error capture.
    """

    def __init__(
        self,
        store: AuditStore | None = None,
        on_entry: Callable[[AuditEntry], None] | None = None,
    ):
        """
        Initialize the audit logger.

        Args:
            store: Audit store instance. Creates default if not provided.
            on_entry: Optional callback invoked for each logged entry.
        """
        self._store = store or AuditStore()
        self._on_entry = on_entry

    @staticmethod
    def _hash_data(data: Any) -> str:
        """Compute hash of data for large payloads."""
        import json
        if data is None:
            return ""
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.sha256(data_str.encode()).hexdigest()[:16]
        except (TypeError, ValueError):
            return hashlib.sha256(str(data).encode()).hexdigest()[:16]

    def log(
        self,
        agent: AgentIdentity,
        tool_name: str,
        parameters: dict,
        result: str = "success",
        error_stack: str | None = None,
        input_data: Any = None,
        output_data: Any = None,
        approval_id: str | None = None,
        duration_ms: int = 0,
        risk_tier: str = "low",
    ) -> AuditEntry:
        """
        Log an agent action.

        Args:
            agent: The agent performing the action
            tool_name: Name of the tool invoked
            parameters: Tool parameters
            result: Result status (success/failure/denied)
            error_stack: Error traceback if failed
            input_data: Input data for hashing
            output_data: Output data for hashing
            approval_id: Approval record ID if applicable
            duration_ms: Execution duration
            risk_tier: Risk tier of the action

        Returns:
            The created audit entry
        """
        entry = AuditEntry(
            timestamp=datetime.now(),
            agent_id=agent.agent_id,
            user_id=agent.user_id,
            correlation_id=agent.correlation_id,
            tool_name=tool_name,
            parameters=parameters,
            result=result,
            error_stack=error_stack,
            input_hash=self._hash_data(input_data) if input_data else None,
            output_hash=self._hash_data(output_data) if output_data else None,
            approval_id=approval_id,
            duration_ms=duration_ms,
            risk_tier=risk_tier,
            session_id=agent.session_id,
        )

        self._store.append(entry)

        if self._on_entry:
            self._on_entry(entry)

        return entry

    def log_success(
        self,
        agent: AgentIdentity,
        tool_name: str,
        parameters: dict,
        output_data: Any = None,
        duration_ms: int = 0,
        risk_tier: str = "low",
    ) -> AuditEntry:
        """Log a successful action."""
        return self.log(
            agent=agent,
            tool_name=tool_name,
            parameters=parameters,
            result="success",
            output_data=output_data,
            duration_ms=duration_ms,
            risk_tier=risk_tier,
        )

    def log_failure(
        self,
        agent: AgentIdentity,
        tool_name: str,
        parameters: dict,
        error: Exception,
        duration_ms: int = 0,
        risk_tier: str = "low",
    ) -> AuditEntry:
        """Log a failed action."""
        import traceback
        return self.log(
            agent=agent,
            tool_name=tool_name,
            parameters=parameters,
            result="failure",
            error_stack=traceback.format_exc(),
            duration_ms=duration_ms,
            risk_tier=risk_tier,
        )

    def log_denied(
        self,
        agent: AgentIdentity,
        tool_name: str,
        parameters: dict,
        reason: str,
        risk_tier: str = "low",
    ) -> AuditEntry:
        """Log a denied action."""
        return self.log(
            agent=agent,
            tool_name=tool_name,
            parameters=parameters,
            result="denied",
            error_stack=f"Action denied: {reason}",
            risk_tier=risk_tier,
        )

    @contextmanager
    def track(
        self,
        agent: AgentIdentity,
        tool_name: str,
        parameters: dict,
        risk_tier: str = "low",
    ):
        """
        Context manager for tracking an operation.

        Automatically logs success or failure with timing.

        Usage:
            with logger.track(agent, "WriteFile", {"path": "foo.txt"}) as ctx:
                # Do the operation
                result = write_file("foo.txt", content)
                ctx.set_output(result)

        Args:
            agent: The agent performing the action
            tool_name: Name of the tool
            parameters: Tool parameters
            risk_tier: Risk tier of the action
        """
        ctx = _TrackingContext(
            logger=self,
            agent=agent,
            tool_name=tool_name,
            parameters=parameters,
            risk_tier=risk_tier,
        )

        try:
            yield ctx

            # Log success if not already logged
            if not ctx._logged:
                duration_ms = int((time.time() - ctx._start_time) * 1000)
                self.log_success(
                    agent=agent,
                    tool_name=tool_name,
                    parameters=parameters,
                    output_data=ctx._output_data,
                    duration_ms=duration_ms,
                    risk_tier=risk_tier,
                )
                ctx._logged = True

        except Exception as e:
            # Log failure
            if not ctx._logged:
                duration_ms = int((time.time() - ctx._start_time) * 1000)
                self.log_failure(
                    agent=agent,
                    tool_name=tool_name,
                    parameters=parameters,
                    error=e,
                    duration_ms=duration_ms,
                    risk_tier=risk_tier,
                )
                ctx._logged = True
            raise

    def get_store(self) -> AuditStore:
        """Get the underlying audit store."""
        return self._store


class _TrackingContext:
    """Context object for tracked operations."""

    def __init__(
        self,
        logger: AuditLogger,
        agent: AgentIdentity,
        tool_name: str,
        parameters: dict,
        risk_tier: str,
    ):
        self._logger = logger
        self._agent = agent
        self._tool_name = tool_name
        self._parameters = parameters
        self._risk_tier = risk_tier
        self._start_time = time.time()
        self._output_data = None
        self._logged = False

    def set_output(self, data: Any) -> None:
        """Set the output data for hashing."""
        self._output_data = data

    def mark_denied(self, reason: str) -> None:
        """Mark the operation as denied."""
        if not self._logged:
            self._logger.log_denied(
                agent=self._agent,
                tool_name=self._tool_name,
                parameters=self._parameters,
                reason=reason,
                risk_tier=self._risk_tier,
            )
            self._logged = True
