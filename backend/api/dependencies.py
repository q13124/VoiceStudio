# Copyright (c) VoiceStudio. All rights reserved.
# Licensed under the MIT License.

"""
FastAPI Dependencies for VoiceStudio API.

Provides reusable dependency injection functions for routes.
GAP-I08: Request context dependency for correlation and tracing.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, Request

from backend.api.middleware.correlation_id import get_correlation_id

logger = logging.getLogger(__name__)


@dataclass
class RequestContext:
    """
    Request context containing correlation and tracing IDs.

    GAP-I08: Provides unified context for logging and tracing.
    """

    correlation_id: str
    trace_id: str | None
    span_id: str | None

    def to_log_extra(self) -> dict[str, Any]:
        """Return dict suitable for logging extra parameter."""
        return {
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id or "N/A",
            "span_id": self.span_id or "N/A",
        }

    def __repr__(self) -> str:
        return f"RequestContext(correlation_id={self.correlation_id[:8]}...)"


def get_request_context(request: Request) -> RequestContext:
    """
    FastAPI dependency that provides request context for logging and tracing.

    GAP-I08: Enables consistent correlation across all route handlers.

    Usage:
        @router.post("/synthesize")
        async def synthesize(
            request: SynthesizeRequest,
            ctx: RequestContext = Depends(get_request_context)
        ):
            logger.info("Starting synthesis", extra=ctx.to_log_extra())

    Args:
        request: The FastAPI request object

    Returns:
        RequestContext with correlation_id, trace_id, and span_id
    """
    # Get correlation ID from context var (set by middleware)
    correlation_id = get_correlation_id() or getattr(request.state, "correlation_id", "unknown")

    # Get trace/span IDs from request state (set by tracing middleware)
    trace_id = getattr(request.state, "trace_id", None)
    span_id = getattr(request.state, "span_id", None)

    return RequestContext(
        correlation_id=correlation_id,
        trace_id=trace_id,
        span_id=span_id,
    )


def get_correlation_id_header(request: Request) -> str:
    """
    Simple dependency to get just the correlation ID.

    Usage:
        @router.get("/status")
        async def get_status(correlation_id: str = Depends(get_correlation_id_header)):
            return {"correlation_id": correlation_id}
    """
    return get_correlation_id() or getattr(request.state, "correlation_id", "unknown")
