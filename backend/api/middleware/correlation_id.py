# Copyright (c) VoiceStudio. All rights reserved.
# Licensed under the MIT License.

"""
Correlation ID Middleware for VoiceStudio API.

Adds correlation IDs to all requests for distributed tracing and debugging.
The correlation ID is:
- Accepted from X-Correlation-ID header if provided
- Generated as a new UUID if not provided
- Attached to request.state.correlation_id
- Returned in X-Correlation-ID response header
- Included in all log messages for the request

This enables end-to-end tracing from UI click to engine result.
"""

import uuid
import logging
from contextvars import ContextVar
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable for correlation ID (thread-safe)
correlation_id_var: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)

CORRELATION_ID_HEADER = "X-Correlation-ID"

logger = logging.getLogger(__name__)


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID from context."""
    return correlation_id_var.get()


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter that adds correlation_id to log records.
    
    Add to logging configuration:
        filter = CorrelationIdFilter()
        handler.addFilter(filter)
        
    Then use in format:
        "%(correlation_id)s - %(message)s"
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = get_correlation_id() or "no-correlation-id"
        return True


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages correlation IDs for request tracing.
    
    Usage:
        from backend.api.middleware.correlation_id import CorrelationIdMiddleware
        
        app = FastAPI()
        app.add_middleware(CorrelationIdMiddleware)
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Get correlation ID from header or generate new one
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)
        
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Set in context variable (for logging)
        token = correlation_id_var.set(correlation_id)
        
        # Set on request state (for handlers)
        request.state.correlation_id = correlation_id
        
        try:
            # Log request with correlation ID
            logger.info(
                "Request started",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "client_ip": request.client.host if request.client else "unknown",
                }
            )
            
            # Process request
            response = await call_next(request)
            
            # Add correlation ID to response headers
            response.headers[CORRELATION_ID_HEADER] = correlation_id
            
            # Log response
            logger.info(
                "Request completed",
                extra={
                    "correlation_id": correlation_id,
                    "status_code": response.status_code,
                    "method": request.method,
                    "path": request.url.path,
                }
            )
            
            return response
            
        except Exception as e:
            # Log exception with correlation ID
            logger.error(
                f"Request failed: {e}",
                extra={
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "exception_type": type(e).__name__,
                },
                exc_info=True
            )
            raise
            
        finally:
            # Reset context variable
            correlation_id_var.reset(token)


def setup_correlation_logging():
    """
    Configure the root logger to include correlation IDs.
    
    Call this during application startup:
        from backend.api.middleware.correlation_id import setup_correlation_logging
        setup_correlation_logging()
    """
    # Add filter to root logger
    root_logger = logging.getLogger()
    
    # Check if filter already added
    for f in root_logger.filters:
        if isinstance(f, CorrelationIdFilter):
            return
    
    root_logger.addFilter(CorrelationIdFilter())
    
    # Update formatter to include correlation ID
    for handler in root_logger.handlers:
        if handler.formatter:
            # Prepend correlation ID to format
            current_format = handler.formatter._fmt
            if "correlation_id" not in current_format:
                new_format = "[%(correlation_id)s] " + current_format
                handler.setFormatter(logging.Formatter(new_format))
