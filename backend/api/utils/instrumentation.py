"""
Structured Event Instrumentation
Instruments key backend flows with structured events and request IDs.
"""

import logging
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Event types for key flows
class EventType:
    """Event type constants."""
    IMPORT_START = "import.start"
    IMPORT_COMPLETE = "import.complete"
    IMPORT_ERROR = "import.error"
    EDIT_START = "edit.start"
    EDIT_COMPLETE = "edit.complete"
    EDIT_ERROR = "edit.error"
    SYNTHESIS_START = "synthesis.start"
    SYNTHESIS_COMPLETE = "synthesis.complete"
    SYNTHESIS_ERROR = "synthesis.error"
    EXPORT_START = "export.start"
    EXPORT_COMPLETE = "export.complete"
    EXPORT_ERROR = "export.error"


class StructuredEvent:
    """Structured event for logging."""
    
    def __init__(
        self,
        event_type: str,
        request_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize structured event.
        
        Args:
            event_type: Type of event
            request_id: Request ID (if available)
            **kwargs: Additional event data
        """
        self.event_type = event_type
        self.request_id = request_id or str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat()
        self.data = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_type": self.event_type,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            **self.data
        }
    
    def log(self, level: int = logging.INFO):
        """Log the event."""
        event_dict = self.to_dict()
        logger.log(level, f"Event: {self.event_type}", extra=event_dict)


def log_event(
    event_type: str,
    request_id: Optional[str] = None,
    level: int = logging.INFO,
    **kwargs
):
    """
    Log a structured event.
    
    Args:
        event_type: Type of event
        request_id: Request ID (if available)
        level: Log level
        **kwargs: Additional event data
    """
    event = StructuredEvent(event_type, request_id=request_id, **kwargs)
    event.log(level=level)


@contextmanager
def instrument_flow(
    event_type_start: str,
    event_type_complete: str,
    event_type_error: str,
    request_id: Optional[str] = None,
    **start_data
):
    """
    Context manager to instrument a flow with start/complete/error events.
    
    Args:
        event_type_start: Event type for start
        event_type_complete: Event type for completion
        event_type_error: Event type for error
        request_id: Request ID (if available)
        **start_data: Additional data for start event
    
    Yields:
        Request ID
    """
    flow_request_id = request_id or str(uuid.uuid4())
    start_time = time.time()
    
    # Log start event
    log_event(
        event_type_start,
        request_id=flow_request_id,
        level=logging.INFO,
        **start_data
    )
    
    try:
        yield flow_request_id
        # Log complete event
        duration = time.time() - start_time
        log_event(
            event_type_complete,
            request_id=flow_request_id,
            level=logging.INFO,
            duration_seconds=duration,
            **start_data
        )
    except Exception as e:
        # Log error event
        duration = time.time() - start_time
        log_event(
            event_type_error,
            request_id=flow_request_id,
            level=logging.ERROR,
            duration_seconds=duration,
            error=str(e),
            error_type=type(e).__name__,
            **start_data
        )
        raise


def instrument_endpoint(
    event_type_start: str,
    event_type_complete: str,
    event_type_error: str
):
    """
    Decorator to instrument an endpoint with structured events.
    
    Args:
        event_type_start: Event type for start
        event_type_complete: Event type for completion
        event_type_error: Event type for error
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get request_id from request object
            request_id = None
            for arg in args:
                if hasattr(arg, 'state') and hasattr(arg.state, 'request_id'):
                    request_id = arg.state.request_id
                    break
            
            with instrument_flow(
                event_type_start,
                event_type_complete,
                event_type_error,
                request_id=request_id,
                endpoint=func.__name__
            ):
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator
