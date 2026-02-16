"""
Approval Manager

Manages approval requests for high-risk agent actions.
Provides both synchronous and asynchronous approval flows.
"""

from __future__ import annotations

import json
import threading
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class ApprovalStatus(str, Enum):
    """Status of an approval request."""

    PENDING = "Pending"
    APPROVED = "Approved"
    DENIED = "Denied"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"


@dataclass
class ApprovalRequest:
    """
    An approval request for a high-risk action.

    Attributes:
        request_id: Unique identifier for this request
        agent_id: ID of the requesting agent
        user_id: ID of the user associated with the agent
        correlation_id: Cross-layer tracing ID
        tool_name: Name of the tool to execute
        parameters: Tool parameters
        risk_tier: Risk tier of the action
        reason: Why approval is required
        created_at: When the request was created
        expires_at: When the request expires
        status: Current status
        decided_by: Who made the approval decision
        decided_at: When the decision was made
        decision_reason: Reason for the decision
    """

    request_id: str
    agent_id: str
    user_id: str
    correlation_id: str
    tool_name: str
    parameters: dict[str, Any]
    risk_tier: str
    reason: str
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_by: str | None = None
    decided_at: datetime | None = None
    decision_reason: str = ""

    def __post_init__(self):
        if self.expires_at is None:
            # Default expiration: 1 hour
            self.expires_at = self.created_at + timedelta(hours=1)

    @property
    def is_expired(self) -> bool:
        """Check if the request has expired."""
        return datetime.now() > self.expires_at

    @property
    def is_pending(self) -> bool:
        """Check if the request is still pending."""
        return self.status == ApprovalStatus.PENDING and not self.is_expired

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "risk_tier": self.risk_tier,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status.value,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
            "decision_reason": self.decision_reason,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ApprovalRequest:
        """Create from dictionary."""
        return cls(
            request_id=data["request_id"],
            agent_id=data["agent_id"],
            user_id=data["user_id"],
            correlation_id=data["correlation_id"],
            tool_name=data["tool_name"],
            parameters=data["parameters"],
            risk_tier=data["risk_tier"],
            reason=data["reason"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            status=ApprovalStatus(data["status"]),
            decided_by=data.get("decided_by"),
            decided_at=datetime.fromisoformat(data["decided_at"]) if data.get("decided_at") else None,
            decision_reason=data.get("decision_reason", ""),
        )


@dataclass
class ApprovalRecord:
    """
    A record of an approval decision (for audit purposes).
    """

    request_id: str
    agent_id: str
    user_id: str
    tool_name: str
    parameters_hash: str
    risk_tier: str
    status: ApprovalStatus
    decided_by: str
    decided_at: datetime
    decision_reason: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "tool_name": self.tool_name,
            "parameters_hash": self.parameters_hash,
            "risk_tier": self.risk_tier,
            "status": self.status.value,
            "decided_by": self.decided_by,
            "decided_at": self.decided_at.isoformat(),
            "decision_reason": self.decision_reason,
        }


class ApprovalManager:
    """
    Manages approval requests for high-risk agent actions.

    Supports:
    - Synchronous approval (blocking)
    - Asynchronous approval (callback-based)
    - Persistence of approval records
    - Approval history querying
    """

    def __init__(
        self,
        storage_path: Path | None = None,
        default_timeout_minutes: int = 60,
        on_request: Callable[[ApprovalRequest], None] | None = None,
    ):
        """
        Initialize the approval manager.

        Args:
            storage_path: Path for storing approval records
            default_timeout_minutes: Default request expiration
            on_request: Callback when new request is created
        """
        if storage_path:
            self._storage_path = storage_path
        else:
            import os
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            self._storage_path = Path(appdata) / "VoiceStudio" / "approvals"

        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._default_timeout = timedelta(minutes=default_timeout_minutes)
        self._on_request = on_request

        # Active requests
        self._requests: dict[str, ApprovalRequest] = {}
        self._lock = threading.RLock()

        # Condition for waiting on approval
        self._conditions: dict[str, threading.Condition] = {}

    def create_request(
        self,
        agent_id: str,
        user_id: str,
        correlation_id: str,
        tool_name: str,
        parameters: dict[str, Any],
        risk_tier: str,
        reason: str,
        timeout_minutes: int | None = None,
    ) -> ApprovalRequest:
        """
        Create a new approval request.

        Args:
            agent_id: ID of the requesting agent
            user_id: ID of the associated user
            correlation_id: Cross-layer tracing ID
            tool_name: Name of the tool
            parameters: Tool parameters
            risk_tier: Risk tier of the action
            reason: Why approval is required
            timeout_minutes: Custom timeout (uses default if not specified)

        Returns:
            The created approval request
        """
        request_id = str(uuid.uuid4())

        timeout = (
            timedelta(minutes=timeout_minutes)
            if timeout_minutes
            else self._default_timeout
        )

        request = ApprovalRequest(
            request_id=request_id,
            agent_id=agent_id,
            user_id=user_id,
            correlation_id=correlation_id,
            tool_name=tool_name,
            parameters=parameters,
            risk_tier=risk_tier,
            reason=reason,
            expires_at=datetime.now() + timeout,
        )

        with self._lock:
            self._requests[request_id] = request
            self._conditions[request_id] = threading.Condition()

        # Notify callback
        if self._on_request:
            self._on_request(request)

        return request

    def get_request(self, request_id: str) -> ApprovalRequest | None:
        """Get an approval request by ID."""
        with self._lock:
            return self._requests.get(request_id)

    def get_pending_requests(
        self,
        user_id: str | None = None,
    ) -> list[ApprovalRequest]:
        """Get all pending requests, optionally filtered by user."""
        with self._lock:
            requests = []
            for request in self._requests.values():
                if request.is_expired:
                    request.status = ApprovalStatus.EXPIRED
                    continue
                if request.status != ApprovalStatus.PENDING:
                    continue
                if user_id and request.user_id != user_id:
                    continue
                requests.append(request)
            return requests

    def approve(
        self,
        request_id: str,
        decided_by: str,
        reason: str = "",
    ) -> bool:
        """
        Approve a request.

        Args:
            request_id: ID of the request to approve
            decided_by: Who is approving
            reason: Reason for approval

        Returns:
            True if approval succeeded, False otherwise
        """
        return self._decide(
            request_id,
            ApprovalStatus.APPROVED,
            decided_by,
            reason,
        )

    def deny(
        self,
        request_id: str,
        decided_by: str,
        reason: str = "",
    ) -> bool:
        """
        Deny a request.

        Args:
            request_id: ID of the request to deny
            decided_by: Who is denying
            reason: Reason for denial

        Returns:
            True if denial succeeded, False otherwise
        """
        return self._decide(
            request_id,
            ApprovalStatus.DENIED,
            decided_by,
            reason,
        )

    def _decide(
        self,
        request_id: str,
        status: ApprovalStatus,
        decided_by: str,
        reason: str,
    ) -> bool:
        """Internal method to record a decision."""
        with self._lock:
            request = self._requests.get(request_id)
            if request is None:
                return False

            if request.is_expired:
                request.status = ApprovalStatus.EXPIRED
                return False

            if request.status != ApprovalStatus.PENDING:
                return False

            # Update request
            request.status = status
            request.decided_by = decided_by
            request.decided_at = datetime.now()
            request.decision_reason = reason

            # Save approval record
            self._save_record(request)

            # Notify waiters
            condition = self._conditions.get(request_id)
            if condition:
                with condition:
                    condition.notify_all()

            return True

    def wait_for_decision(
        self,
        request_id: str,
        timeout_seconds: float | None = None,
    ) -> ApprovalStatus:
        """
        Wait for a decision on a request.

        Args:
            request_id: ID of the request
            timeout_seconds: How long to wait

        Returns:
            The final status of the request
        """
        condition = self._conditions.get(request_id)
        if condition is None:
            return ApprovalStatus.CANCELLED

        request = self._requests.get(request_id)
        if request is None:
            return ApprovalStatus.CANCELLED

        with condition:
            while request.status == ApprovalStatus.PENDING:
                if request.is_expired:
                    request.status = ApprovalStatus.EXPIRED
                    break

                # Calculate remaining time
                remaining = timeout_seconds or (request.expires_at - datetime.now()).total_seconds()

                if remaining <= 0:
                    request.status = ApprovalStatus.EXPIRED
                    break

                condition.wait(timeout=min(remaining, 1.0))

        return request.status

    def cancel(self, request_id: str) -> bool:
        """Cancel a pending request."""
        with self._lock:
            request = self._requests.get(request_id)
            if request is None or request.status != ApprovalStatus.PENDING:
                return False

            request.status = ApprovalStatus.CANCELLED

            condition = self._conditions.get(request_id)
            if condition:
                with condition:
                    condition.notify_all()

            return True

    def _save_record(self, request: ApprovalRequest) -> None:
        """Save an approval record to storage."""
        import hashlib

        params_hash = hashlib.sha256(
            json.dumps(request.parameters, sort_keys=True).encode()
        ).hexdigest()[:16]

        record = ApprovalRecord(
            request_id=request.request_id,
            agent_id=request.agent_id,
            user_id=request.user_id,
            tool_name=request.tool_name,
            parameters_hash=params_hash,
            risk_tier=request.risk_tier,
            status=request.status,
            decided_by=request.decided_by or "system",
            decided_at=request.decided_at or datetime.now(),
            decision_reason=request.decision_reason,
        )

        # Append to daily record file
        date_str = record.decided_at.strftime("%Y-%m-%d")
        record_file = self._storage_path / f"approvals_{date_str}.jsonl"

        with open(record_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def get_history(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        user_id: str | None = None,
        status: ApprovalStatus | None = None,
        limit: int = 100,
    ) -> list[ApprovalRecord]:
        """
        Get approval history.

        Args:
            start_date: Filter by start date
            end_date: Filter by end date
            user_id: Filter by user
            status: Filter by status
            limit: Maximum records to return

        Returns:
            List of approval records
        """
        records = []

        # Get relevant files
        for record_file in sorted(self._storage_path.glob("approvals_*.jsonl"), reverse=True):
            try:
                date_str = record_file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if start_date and file_date.date() < start_date.date():
                    continue
                if end_date and file_date.date() > end_date.date():
                    continue
            except (IndexError, ValueError):
                continue

            # Read records from file
            try:
                with open(record_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        try:
                            data = json.loads(line)
                            record = ApprovalRecord(
                                request_id=data["request_id"],
                                agent_id=data["agent_id"],
                                user_id=data["user_id"],
                                tool_name=data["tool_name"],
                                parameters_hash=data["parameters_hash"],
                                risk_tier=data["risk_tier"],
                                status=ApprovalStatus(data["status"]),
                                decided_by=data["decided_by"],
                                decided_at=datetime.fromisoformat(data["decided_at"]),
                                decision_reason=data.get("decision_reason", ""),
                            )

                            # Apply filters
                            if user_id and record.user_id != user_id:
                                continue
                            if status and record.status != status:
                                continue

                            records.append(record)

                            if len(records) >= limit:
                                return records

                        except (json.JSONDecodeError, KeyError):
                            continue
            except OSError:
                continue

        return records

    def cleanup_old_records(self, older_than_days: int = 90) -> int:
        """
        Remove approval records older than specified days.

        Returns:
            Number of files removed
        """
        cutoff = datetime.now() - timedelta(days=older_than_days)
        removed = 0

        for record_file in self._storage_path.glob("approvals_*.jsonl"):
            try:
                date_str = record_file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")

                if file_date < cutoff:
                    record_file.unlink()
                    removed += 1
            except (IndexError, ValueError, OSError):
                continue

        return removed
