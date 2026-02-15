"""
IPC Security.

Task 1.4.5: Token-based IPC authentication.
Secures IPC communications with token-based auth.
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import logging
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class IPCToken:
    """An IPC authentication token."""
    token_id: str
    secret: str
    client_id: str
    permissions: set[str]
    created_at: datetime
    expires_at: datetime
    last_used: datetime | None = None
    use_count: int = 0

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        return not self.is_expired


@dataclass
class SecurityConfig:
    """Configuration for IPC security."""
    secret_key: str = ""  # Master secret for HMAC
    token_lifetime_hours: int = 24
    max_tokens_per_client: int = 5
    require_auth: bool = True
    allowed_methods: list[str] = field(default_factory=list)
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60


class IPCSecurity:
    """
    Security layer for IPC communications.

    Features:
    - Token-based authentication
    - Permission-based authorization
    - Rate limiting
    - Token lifecycle management
    - Signature verification
    """

    def __init__(self, config: SecurityConfig | None = None):
        self.config = config or SecurityConfig()

        # Generate secret key if not provided
        if not self.config.secret_key:
            self.config.secret_key = secrets.token_hex(32)

        self._tokens: dict[str, IPCToken] = {}
        self._client_tokens: dict[str, list[str]] = {}
        self._rate_limits: dict[str, list[float]] = {}
        self._lock = asyncio.Lock()

    async def create_token(
        self,
        client_id: str,
        permissions: set[str] | None = None,
        lifetime_hours: int | None = None,
    ) -> IPCToken:
        """
        Create a new IPC token.

        Args:
            client_id: Client identifier
            permissions: Set of allowed methods
            lifetime_hours: Token lifetime (None for default)

        Returns:
            Created token
        """
        async with self._lock:
            # Check max tokens per client
            client_token_ids = self._client_tokens.get(client_id, [])
            if len(client_token_ids) >= self.config.max_tokens_per_client:
                # Remove oldest token
                oldest_id = client_token_ids[0]
                await self._revoke_token_internal(oldest_id)

            # Generate token
            token_id = secrets.token_urlsafe(16)
            secret = secrets.token_urlsafe(32)

            lifetime = lifetime_hours or self.config.token_lifetime_hours

            token = IPCToken(
                token_id=token_id,
                secret=secret,
                client_id=client_id,
                permissions=permissions or set(),
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=lifetime),
            )

            self._tokens[token_id] = token

            if client_id not in self._client_tokens:
                self._client_tokens[client_id] = []
            self._client_tokens[client_id].append(token_id)

            logger.info(f"Created IPC token for client: {client_id}")
            return token

    async def validate_token(
        self,
        token_id: str,
        secret: str,
    ) -> IPCToken | None:
        """
        Validate a token.

        Args:
            token_id: Token identifier
            secret: Token secret

        Returns:
            Token if valid, None otherwise
        """
        token = self._tokens.get(token_id)

        if not token:
            logger.warning(f"Token not found: {token_id}")
            return None

        if token.is_expired:
            logger.warning(f"Token expired: {token_id}")
            return None

        # Constant-time comparison
        if not secrets.compare_digest(token.secret, secret):
            logger.warning(f"Invalid token secret: {token_id}")
            return None

        # Update usage
        token.last_used = datetime.now()
        token.use_count += 1

        return token

    async def check_permission(
        self,
        token: IPCToken,
        method: str,
    ) -> bool:
        """
        Check if token has permission for a method.

        Args:
            token: The token
            method: Method name to check

        Returns:
            True if permitted
        """
        # Empty permissions = all allowed
        if not token.permissions:
            return True

        # Check wildcard
        if "*" in token.permissions:
            return True

        return method in token.permissions

    async def check_rate_limit(
        self,
        client_id: str,
    ) -> bool:
        """
        Check if client is within rate limits.

        Args:
            client_id: Client identifier

        Returns:
            True if within limits
        """
        async with self._lock:
            now = time.time()
            window_start = now - self.config.rate_limit_window_seconds

            # Get requests in window
            requests = self._rate_limits.get(client_id, [])
            requests = [t for t in requests if t > window_start]

            # Check limit
            if len(requests) >= self.config.rate_limit_requests:
                logger.warning(f"Rate limit exceeded for client: {client_id}")
                return False

            # Record request
            requests.append(now)
            self._rate_limits[client_id] = requests

            return True

    async def authenticate_request(
        self,
        token_id: str,
        secret: str,
        method: str,
        signature: str | None = None,
        payload: bytes | None = None,
    ) -> tuple[bool, str | None]:
        """
        Authenticate a request.

        Args:
            token_id: Token identifier
            secret: Token secret
            method: Method being called
            signature: Optional request signature
            payload: Optional payload for signature verification

        Returns:
            (success, error_message) tuple
        """
        if not self.config.require_auth:
            return True, None

        # Validate token
        token = await self.validate_token(token_id, secret)
        if not token:
            return False, "Invalid or expired token"

        # Check rate limit
        if not await self.check_rate_limit(token.client_id):
            return False, "Rate limit exceeded"

        # Check permission
        if not await self.check_permission(token, method):
            return False, f"Permission denied for method: {method}"

        # Verify signature if provided
        if signature and payload:
            expected_sig = self.compute_signature(payload, token.secret)
            if not secrets.compare_digest(signature, expected_sig):
                return False, "Invalid signature"

        return True, None

    def compute_signature(
        self,
        payload: bytes,
        secret: str,
    ) -> str:
        """Compute HMAC signature for payload."""
        return hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

    async def revoke_token(self, token_id: str) -> bool:
        """Revoke a token."""
        async with self._lock:
            return await self._revoke_token_internal(token_id)

    async def _revoke_token_internal(self, token_id: str) -> bool:
        """Internal token revocation (must hold lock)."""
        token = self._tokens.pop(token_id, None)
        if not token:
            return False

        # Remove from client list
        client_tokens = self._client_tokens.get(token.client_id, [])
        if token_id in client_tokens:
            client_tokens.remove(token_id)

        logger.info(f"Revoked IPC token: {token_id}")
        return True

    async def revoke_all_client_tokens(self, client_id: str) -> int:
        """Revoke all tokens for a client."""
        async with self._lock:
            token_ids = self._client_tokens.pop(client_id, [])

            for token_id in token_ids:
                self._tokens.pop(token_id, None)

            return len(token_ids)

    async def cleanup_expired(self) -> int:
        """Remove expired tokens."""
        async with self._lock:
            expired = [
                token_id for token_id, token in self._tokens.items()
                if token.is_expired
            ]

            for token_id in expired:
                await self._revoke_token_internal(token_id)

            return len(expired)

    def get_client_tokens(self, client_id: str) -> list[IPCToken]:
        """Get all tokens for a client."""
        token_ids = self._client_tokens.get(client_id, [])
        return [self._tokens[tid] for tid in token_ids if tid in self._tokens]

    def get_stats(self) -> dict:
        """Get security statistics."""
        active_tokens = sum(1 for t in self._tokens.values() if t.is_valid)

        return {
            "total_tokens": len(self._tokens),
            "active_tokens": active_tokens,
            "expired_tokens": len(self._tokens) - active_tokens,
            "clients": len(self._client_tokens),
            "rate_limit_config": {
                "requests": self.config.rate_limit_requests,
                "window_seconds": self.config.rate_limit_window_seconds,
            },
            "require_auth": self.config.require_auth,
        }


# Global security instance
_security: IPCSecurity | None = None


def get_ipc_security() -> IPCSecurity:
    """Get or create the global IPC security instance."""
    global _security
    if _security is None:
        _security = IPCSecurity()
    return _security
