"""
Request Recorder Middleware

Records HTTP requests and responses for debugging and reproduction.
Captured sessions can be replayed for regression testing.
"""

import gzip
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)

# Global recording state
_recording_enabled = False
_current_session: Optional["RecordingSession"] = None
_output_dir = Path(".buildlogs/repro_sessions")


@dataclass
class RecordedRequest:
    """A recorded HTTP request."""

    timestamp: str
    method: str
    path: str
    query_string: str
    headers: Dict[str, str]
    body: Optional[str]
    correlation_id: Optional[str]


@dataclass
class RecordedResponse:
    """A recorded HTTP response."""

    status_code: int
    headers: Dict[str, str]
    body: Optional[str]
    duration_ms: float


@dataclass
class RecordedExchange:
    """A complete request/response exchange."""

    request: RecordedRequest
    response: RecordedResponse
    error: Optional[str] = None


@dataclass
class RecordingSession:
    """A recording session containing multiple exchanges."""

    session_id: str
    started_at: str
    ended_at: Optional[str] = None
    exchanges: List[RecordedExchange] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "exchange_count": len(self.exchanges),
            "metadata": self.metadata,
            "exchanges": [
                {
                    "request": asdict(ex.request),
                    "response": asdict(ex.response),
                    "error": ex.error,
                }
                for ex in self.exchanges
            ],
        }


def enable_recording(
    session_id: Optional[str] = None,
    output_dir: Optional[Path] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Enable request recording.
    
    Args:
        session_id: Optional session ID (auto-generated if not provided)
        output_dir: Directory to save recordings
        metadata: Additional metadata to include in session
    
    Returns:
        The session ID
    """
    global _recording_enabled, _current_session, _output_dir
    
    if output_dir:
        _output_dir = Path(output_dir)
    _output_dir.mkdir(parents=True, exist_ok=True)
    
    if session_id is None:
        session_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    _current_session = RecordingSession(
        session_id=session_id,
        started_at=datetime.utcnow().isoformat(),
        metadata=metadata or {},
    )
    _recording_enabled = True
    
    logger.info(f"Recording enabled: session={session_id}")
    return session_id


def disable_recording() -> Optional[Path]:
    """
    Disable recording and save the session.
    
    Returns:
        Path to the saved session file, or None if no session was active
    """
    global _recording_enabled, _current_session
    
    if not _current_session:
        return None
    
    _current_session.ended_at = datetime.utcnow().isoformat()
    
    # Save session to file
    session_file = _output_dir / f"session_{_current_session.session_id}.json.gz"
    with gzip.open(session_file, "wt", encoding="utf-8") as f:
        json.dump(_current_session.to_dict(), f, indent=2)
    
    logger.info(
        f"Recording disabled: session={_current_session.session_id}, "
        f"exchanges={len(_current_session.exchanges)}, "
        f"file={session_file}"
    )
    
    _recording_enabled = False
    saved_session = _current_session
    _current_session = None
    
    return session_file


def is_recording() -> bool:
    """Check if recording is currently enabled."""
    return _recording_enabled


def get_current_session() -> Optional[RecordingSession]:
    """Get the current recording session."""
    return _current_session


class RequestRecorderMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware that records requests and responses.
    
    Usage:
        from tools.repro import RequestRecorderMiddleware
        
        app.add_middleware(RequestRecorderMiddleware)
        
        # Enable recording
        from tools.repro import enable_recording, disable_recording
        enable_recording()
        
        # ... make requests ...
        
        # Save session
        session_file = disable_recording()
    """

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: Optional[List[str]] = None,
        max_body_size: int = 1024 * 1024,  # 1MB default
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/api/health",
            "/api/docs",
            "/api/openapi.json",
        ]
        self.max_body_size = max_body_size

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Skip recording if disabled or path excluded
        if not _recording_enabled or not _current_session:
            return await call_next(request)
        
        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)
        
        start_time = time.perf_counter()
        
        # Record request
        try:
            request_body = await self._get_request_body(request)
        except Exception:
            request_body = None
        
        recorded_request = RecordedRequest(
            timestamp=datetime.utcnow().isoformat(),
            method=request.method,
            path=request.url.path,
            query_string=str(request.url.query) if request.url.query else "",
            headers=self._sanitize_headers(dict(request.headers)),
            body=request_body,
            correlation_id=request.headers.get("X-Correlation-ID"),
        )
        
        # Execute request
        error_message = None
        try:
            response = await call_next(request)
        except Exception as e:
            error_message = str(e)
            raise
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        
        # Record response
        try:
            response_body = await self._get_response_body(response)
        except Exception:
            response_body = None
        
        recorded_response = RecordedResponse(
            status_code=response.status_code,
            headers=self._sanitize_headers(dict(response.headers)),
            body=response_body,
            duration_ms=duration_ms,
        )
        
        # Add exchange to session
        exchange = RecordedExchange(
            request=recorded_request,
            response=recorded_response,
            error=error_message,
        )
        _current_session.exchanges.append(exchange)
        
        return response

    async def _get_request_body(self, request: Request) -> Optional[str]:
        """Get request body as string."""
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return f"<body too large: {content_length} bytes>"
        
        body = await request.body()
        if not body:
            return None
        
        # Try to decode as UTF-8
        try:
            return body.decode("utf-8")
        except UnicodeDecodeError:
            return f"<binary: {len(body)} bytes>"

    async def _get_response_body(self, response: Response) -> Optional[str]:
        """Get response body as string."""
        # Note: This is tricky with streaming responses
        # For now, we skip body capture for responses
        return None

    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive headers."""
        sensitive_keys = {"authorization", "cookie", "x-api-key", "api-key"}
        return {
            k: "<redacted>" if k.lower() in sensitive_keys else v
            for k, v in headers.items()
        }
