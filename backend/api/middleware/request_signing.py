"""
Request Signing Middleware

HMAC-based request signature verification for IPC security.
Implements Phase 6.1.3 request signing for UI-to-backend communication.

Security features:
- HMAC-SHA256 signature verification
- Timestamp-based replay attack prevention
- Body content verification to prevent tampering
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
from datetime import datetime, timezone

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

# Header names (must match C# RequestSigner)
SIGNATURE_HEADER = "X-HMAC-Signature"
TIMESTAMP_HEADER = "X-HMAC-Timestamp"
VERSION_HEADER = "X-HMAC-Version"

# Current supported signature version
SUPPORTED_VERSION = "1"

# Maximum age of a valid signature in seconds (5 minutes)
MAX_TIMESTAMP_AGE_SECONDS = 300

# Environment variable for the shared secret
SECRET_KEY_ENV_VAR = "VOICESTUDIO_IPC_SECRET"

# Feature flag environment variable
ENABLED_ENV_VAR = "VOICESTUDIO_IPC_SIGNING_ENABLED"


def get_secret_key() -> bytes | None:
    """
    Get the shared secret key from environment.

    Returns:
        Secret key bytes or None if not configured.
    """
    secret_b64 = os.environ.get(SECRET_KEY_ENV_VAR)
    if not secret_b64:
        return None

    try:
        return base64.b64decode(secret_b64)
    except Exception as e:
        logger.error(f"Failed to decode IPC secret key: {e}")
        return None


def is_signing_enabled() -> bool:
    """
    Check if request signing verification is enabled.

    Returns:
        True if signing is enabled.
    """
    enabled = os.environ.get(ENABLED_ENV_VAR, "false").lower()
    return enabled in ("true", "1", "yes")


def compute_signature(
    secret_key: bytes,
    method: str,
    path: str,
    timestamp: str,
    body: str = "",
) -> str:
    """
    Compute HMAC-SHA256 signature for a request.

    Args:
        secret_key: Shared secret key
        method: HTTP method (uppercase)
        path: Request path including query string
        timestamp: ISO 8601 timestamp
        body: Request body (empty string for bodyless requests)

    Returns:
        Base64-encoded HMAC-SHA256 signature
    """
    # Build payload: METHOD|PATH|TIMESTAMP|BODY
    payload = f"{method}|{path}|{timestamp}|{body}"

    signature = hmac.new(
        secret_key,
        payload.encode("utf-8"),
        hashlib.sha256
    ).digest()

    return base64.b64encode(signature).decode("ascii")


def verify_signature(
    secret_key: bytes,
    signature: str,
    method: str,
    path: str,
    timestamp: str,
    body: str = "",
) -> bool:
    """
    Verify HMAC signature for a request.

    Args:
        secret_key: Shared secret key
        signature: Base64-encoded signature from request
        method: HTTP method
        path: Request path
        timestamp: Timestamp from request
        body: Request body

    Returns:
        True if signature is valid.
    """
    expected = compute_signature(secret_key, method, path, timestamp, body)

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(signature, expected)


def validate_timestamp(timestamp_str: str, max_age_seconds: int = MAX_TIMESTAMP_AGE_SECONDS) -> bool:
    """
    Validate that a timestamp is recent enough.

    Args:
        timestamp_str: ISO 8601 timestamp string
        max_age_seconds: Maximum age in seconds

    Returns:
        True if timestamp is valid and recent.
    """
    try:
        # Parse ISO 8601 timestamp
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        # Ensure it has timezone info
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        age = abs((now - timestamp).total_seconds())

        return age <= max_age_seconds
    except Exception as e:
        logger.warning(f"Failed to parse timestamp '{timestamp_str}': {e}")
        return False


class RequestSigningMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify HMAC signatures on incoming requests.

    Configuration:
    - Set VOICESTUDIO_IPC_SECRET to the Base64-encoded shared secret
    - Set VOICESTUDIO_IPC_SIGNING_ENABLED=true to enable verification

    When enabled, requests to protected paths must include:
    - X-HMAC-Signature: Base64-encoded HMAC-SHA256 signature
    - X-HMAC-Timestamp: ISO 8601 timestamp
    - X-HMAC-Version: Signature version (currently "1")
    """

    def __init__(
        self,
        app,
        protected_paths: set[str] | None = None,
        exclude_paths: set[str] | None = None,
    ):
        """
        Initialize the middleware.

        Args:
            app: ASGI application
            protected_paths: Set of path prefixes that require signing.
                            If None, all paths are protected when enabled.
            exclude_paths: Set of path prefixes to exclude from verification.
                          Health checks and public endpoints can be excluded.
        """
        super().__init__(app)
        self.protected_paths = protected_paths
        self.exclude_paths = exclude_paths or {
            "/health",
            "/api/v1/health",
            "/docs",
            "/openapi.json",
            "/redoc",
        }
        self._secret_key: bytes | None = None
        self._enabled: bool | None = None

    def _is_enabled(self) -> bool:
        """Check if signing is enabled (cached)."""
        if self._enabled is None:
            self._enabled = is_signing_enabled()
        return self._enabled

    def _get_secret_key(self) -> bytes | None:
        """Get secret key (cached)."""
        if self._secret_key is None:
            self._secret_key = get_secret_key()
        return self._secret_key

    def _should_verify(self, path: str) -> bool:
        """
        Check if a path should be verified.

        Args:
            path: Request path

        Returns:
            True if the path requires signature verification.
        """
        # Check exclusions first
        for exclude in self.exclude_paths:
            if path.startswith(exclude):
                return False

        # If protected_paths is specified, only verify those
        if self.protected_paths:
            return any(path.startswith(protected) for protected in self.protected_paths)

        # Otherwise verify all non-excluded paths
        return True

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process request and verify signature if required."""

        # Skip if signing is not enabled
        if not self._is_enabled():
            return await call_next(request)

        path = request.url.path

        # Skip excluded paths
        if not self._should_verify(path):
            return await call_next(request)

        # Get secret key
        secret_key = self._get_secret_key()
        if not secret_key:
            logger.error("IPC signing enabled but secret key not configured")
            # Fail open in development, fail closed in production
            env = os.environ.get("ENVIRONMENT", "development")
            if env == "production":
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Server configuration error"},
                )
            return await call_next(request)

        # Extract headers
        signature = request.headers.get(SIGNATURE_HEADER)
        timestamp = request.headers.get(TIMESTAMP_HEADER)
        version = request.headers.get(VERSION_HEADER)

        # Check required headers
        if not signature or not timestamp:
            logger.warning(
                f"Missing signature headers for {request.method} {path}",
                extra={
                    "path": path,
                    "method": request.method,
                    "has_signature": bool(signature),
                    "has_timestamp": bool(timestamp),
                }
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Missing request signature"},
            )

        # Check version
        if version and version != SUPPORTED_VERSION:
            logger.warning(f"Unsupported signature version: {version}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": f"Unsupported signature version: {version}"},
            )

        # Validate timestamp (replay attack prevention)
        if not validate_timestamp(timestamp):
            logger.warning(
                f"Invalid or expired timestamp: {timestamp}",
                extra={"path": path, "timestamp": timestamp}
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Request timestamp expired or invalid"},
            )

        # Read body for verification
        body = await request.body()
        body_str = body.decode("utf-8") if body else ""

        # Build path with query string
        full_path = request.url.path
        if request.url.query:
            full_path = f"{full_path}?{request.url.query}"

        # Verify signature
        if not verify_signature(
            secret_key,
            signature,
            request.method.upper(),
            full_path,
            timestamp,
            body_str,
        ):
            logger.warning(
                f"Invalid signature for {request.method} {path}",
                extra={
                    "path": path,
                    "method": request.method,
                    "timestamp": timestamp,
                }
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid request signature"},
            )

        # Signature valid - proceed with request
        logger.debug(
            f"Signature verified for {request.method} {path}",
            extra={"path": path, "method": request.method}
        )

        return await call_next(request)


def require_signature(
    request: Request,
    secret_key: bytes | None = None,
) -> bool:
    """
    Dependency function to verify request signature.

    Use as a FastAPI dependency for endpoints that require signature:

    ```python
    @app.post("/api/v1/sensitive")
    async def sensitive_endpoint(
        verified: bool = Depends(require_signature),
    ):
        ...
    ```

    Args:
        request: FastAPI request
        secret_key: Optional secret key (defaults to env var)

    Returns:
        True if signature is valid.

    Raises:
        HTTPException: If signature is missing or invalid.
    """
    if not is_signing_enabled():
        return True

    key = secret_key or get_secret_key()
    if not key:
        logger.error("Signature required but secret key not configured")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error",
        )

    signature = request.headers.get(SIGNATURE_HEADER)
    timestamp = request.headers.get(TIMESTAMP_HEADER)

    if not signature or not timestamp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing request signature",
        )

    if not validate_timestamp(timestamp):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Request timestamp expired",
        )

    # For dependencies, we can't easily read the body
    # This is primarily for GET requests without bodies
    full_path = str(request.url.path)
    if request.url.query:
        full_path = f"{full_path}?{request.url.query}"

    if not verify_signature(
        key,
        signature,
        request.method.upper(),
        full_path,
        timestamp,
        "",  # Body verification happens in middleware
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid request signature",
        )

    return True
