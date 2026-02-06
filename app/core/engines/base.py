"""
Base Engine Protocol for VoiceStudio.

All engines must implement this protocol/interface.
Includes @traced decorator for distributed tracing integration (Phase 5.1.4).
"""

from abc import ABC, abstractmethod
from functools import wraps
from typing import Optional, Any, Dict, Callable, TypeVar
import logging
import time
import uuid
import json
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# Type variable for generic function decorator
F = TypeVar('F', bound=Callable[..., Any])

# Trace storage directory for local-first operation
_TRACE_DIR = Path(".voicestudio/traces")


def traced(
    operation_name: Optional[str] = None,
    record_args: bool = False
) -> Callable[[F], F]:
    """
    Decorator for distributed tracing of engine operations.

    Phase 5.1.4: Engine Tracing Integration

    Args:
        operation_name: Custom operation name (defaults to function name).
        record_args: Whether to record function arguments in trace.

    Returns:
        Decorated function with tracing.

    Example:
        @traced(operation_name="synthesize_audio")
        def synthesize(self, text: str) -> bytes:
            ...
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            op_name = operation_name or func.__name__
            trace_id = uuid.uuid4().hex
            span_id = uuid.uuid4().hex[:16]
            start_time = time.perf_counter()
            start_timestamp = datetime.utcnow().isoformat()

            # Extract class name if method
            class_name = ""
            if args and hasattr(args[0], '__class__'):
                class_name = args[0].__class__.__name__

            span_data = {
                "trace_id": trace_id,
                "span_id": span_id,
                "operation_name": op_name,
                "class_name": class_name,
                "start_time": start_timestamp,
                "status": "IN_PROGRESS",
            }

            if record_args:
                # Safely serialize args (skip self)
                try:
                    safe_args = [
                        str(a)[:200] for a in args[1:]
                    ] if len(args) > 1 else []
                    safe_kwargs = {
                        k: str(v)[:200] for k, v in kwargs.items()
                    }
                    span_data["args"] = safe_args
                    span_data["kwargs"] = safe_kwargs
                except Exception:
                    span_data["args_error"] = "Could not serialize arguments"

            logger.debug(
                "Trace started: %s.%s [trace_id=%s]",
                class_name, op_name, trace_id
            )

            error_info = None
            result = None
            try:
                result = func(*args, **kwargs)
                span_data["status"] = "OK"
                return result
            except Exception as exc:
                span_data["status"] = "ERROR"
                error_info = {
                    "type": type(exc).__name__,
                    "message": str(exc)[:500]
                }
                span_data["error"] = error_info
                logger.error(
                    "Trace error: %s.%s [trace_id=%s] - %s: %s",
                    class_name, op_name, trace_id,
                    type(exc).__name__, str(exc)
                )
                raise
            finally:
                duration_ms = (time.perf_counter() - start_time) * 1000
                span_data["duration_ms"] = round(duration_ms, 2)
                span_data["end_time"] = datetime.utcnow().isoformat()

                logger.debug(
                    "Trace completed: %s.%s [trace_id=%s] "
                    "duration=%.2fms status=%s",
                    class_name, op_name, trace_id,
                    duration_ms, span_data["status"]
                )

                # Write trace to local file for offline operation
                _write_trace(span_data)

        return wrapper  # type: ignore[return-value]
    return decorator


def _write_trace(span_data: Dict[str, Any]) -> None:
    """
    Write trace span to local file storage.

    Traces are stored in .voicestudio/traces/ for local-first operation.
    """
    try:
        _TRACE_DIR.mkdir(parents=True, exist_ok=True)
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        trace_file = _TRACE_DIR / f"engine_traces_{date_str}.jsonl"
        with open(trace_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(span_data) + "\n")
    except Exception as exc:
        # Don't let trace writing failures affect engine operations
        logger.warning("Failed to write trace: %s", exc)


class EngineProtocol(ABC):
    """
    Base protocol that all VoiceStudio engines must implement.
    
    This ensures consistent interface across all engines (XTTS, Whisper, RVC, etc.)
    """
    
    def __init__(self, device: Optional[str] = None, gpu: bool = True):
        """
        Initialize engine with device selection.
        
        Args:
            device: Device to use ('cuda', 'cpu', or None for auto)
            gpu: Whether to use GPU if available
        """
        self.device = device or ("cuda" if gpu else "cpu")
        self._initialized = False
        logger.info(f"{self.__class__.__name__} initialized (device: {self.device})")
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the engine model.

        Returns:
            True if initialization successful, False otherwise

        Note:
            Implementations should apply @traced decorator for tracing.
        """
        ...

    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources and free memory.

        Note:
            Implementations should apply @traced decorator for tracing.
        """
        ...
    
    def is_initialized(self) -> bool:
        """Check if engine is initialized."""
        return self._initialized
    
    def get_device(self) -> str:
        """Get current device."""
        return self.device
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get engine information.
        
        Returns:
            Dictionary with engine metadata
        """
        return {
            "name": self.__class__.__name__,
            "device": self.device,
            "initialized": self._initialized
        }

