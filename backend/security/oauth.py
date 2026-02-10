"""
OAuth2 Provider Integration.

Task 2.1.4: Support external identity providers.
Provides OAuth2 authentication with external providers.
"""

from __future__ import annotations

import hashlib
import logging
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class OAuthProvider(Enum):
    """Supported OAuth providers."""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    GITHUB = "github"
    CUSTOM = "custom"


@dataclass
class OAuthConfig:
    """Configuration for an OAuth provider."""
    provider: OAuthProvider
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    userinfo_url: str
    scopes: List[str] = field(default_factory=list)
    redirect_uri: str = ""
    
    # Provider-specific defaults
    @classmethod
    def google(cls, client_id: str, client_secret: str, redirect_uri: str) -> "OAuthConfig":
        return cls(
            provider=OAuthProvider.GOOGLE,
            client_id=client_id,
            client_secret=client_secret,
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            userinfo_url="https://www.googleapis.com/oauth2/v3/userinfo",
            scopes=["openid", "email", "profile"],
            redirect_uri=redirect_uri,
        )
    
    @classmethod
    def microsoft(cls, client_id: str, client_secret: str, redirect_uri: str) -> "OAuthConfig":
        return cls(
            provider=OAuthProvider.MICROSOFT,
            client_id=client_id,
            client_secret=client_secret,
            authorize_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
            token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
            userinfo_url="https://graph.microsoft.com/v1.0/me",
            scopes=["openid", "email", "profile", "User.Read"],
            redirect_uri=redirect_uri,
        )
    
    @classmethod
    def github(cls, client_id: str, client_secret: str, redirect_uri: str) -> "OAuthConfig":
        return cls(
            provider=OAuthProvider.GITHUB,
            client_id=client_id,
            client_secret=client_secret,
            authorize_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            userinfo_url="https://api.github.com/user",
            scopes=["read:user", "user:email"],
            redirect_uri=redirect_uri,
        )


@dataclass
class OAuthToken:
    """OAuth token response."""
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: Optional[str] = None
    scope: str = ""
    id_token: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.created_at + timedelta(seconds=self.expires_in)


@dataclass
class OAuthUser:
    """User info from OAuth provider."""
    provider: OAuthProvider
    provider_id: str
    email: Optional[str]
    name: Optional[str]
    picture_url: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)


class OAuthState:
    """Manage OAuth state parameters for CSRF protection."""
    
    def __init__(self, ttl_minutes: int = 10):
        self._states: Dict[str, tuple[datetime, str]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
    
    def generate(self, redirect_after: str = "/") -> str:
        """Generate a new state token."""
        state = secrets.token_urlsafe(32)
        self._states[state] = (datetime.now(), redirect_after)
        self._cleanup()
        return state
    
    def validate(self, state: str) -> Optional[str]:
        """Validate and consume a state token. Returns redirect URL if valid."""
        if state not in self._states:
            return None
        
        created_at, redirect_after = self._states.pop(state)
        
        if datetime.now() - created_at > self._ttl:
            return None
        
        return redirect_after
    
    def _cleanup(self) -> None:
        """Remove expired states."""
        now = datetime.now()
        expired = [
            s for s, (created, _) in self._states.items()
            if now - created > self._ttl
        ]
        for s in expired:
            del self._states[s]


class PKCEChallenge:
    """PKCE (Proof Key for Code Exchange) for enhanced security."""
    
    def __init__(self):
        self.code_verifier = secrets.token_urlsafe(64)[:128]
        self.code_challenge = self._generate_challenge()
        self.code_challenge_method = "S256"
    
    def _generate_challenge(self) -> str:
        """Generate S256 code challenge from verifier."""
        digest = hashlib.sha256(self.code_verifier.encode()).digest()
        import base64
        return base64.urlsafe_b64encode(digest).decode().rstrip("=")


class OAuthService:
    """
    OAuth2 authentication service.
    
    Features:
    - Multiple provider support
    - PKCE for enhanced security
    - State management for CSRF protection
    - Token refresh support
    """
    
    def __init__(self):
        self._providers: Dict[OAuthProvider, OAuthConfig] = {}
        self._state = OAuthState()
        self._pkce_challenges: Dict[str, PKCEChallenge] = {}
    
    def register_provider(self, config: OAuthConfig) -> None:
        """Register an OAuth provider."""
        self._providers[config.provider] = config
        logger.info(f"Registered OAuth provider: {config.provider.value}")
    
    def get_authorization_url(
        self,
        provider: OAuthProvider,
        redirect_after: str = "/",
        use_pkce: bool = True,
    ) -> tuple[str, str]:
        """
        Get OAuth authorization URL.
        
        Returns:
            Tuple of (authorization_url, state)
        """
        config = self._providers.get(provider)
        if not config:
            raise ValueError(f"Provider not registered: {provider}")
        
        state = self._state.generate(redirect_after)
        
        params = {
            "client_id": config.client_id,
            "redirect_uri": config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(config.scopes),
            "state": state,
        }
        
        if use_pkce:
            pkce = PKCEChallenge()
            self._pkce_challenges[state] = pkce
            params["code_challenge"] = pkce.code_challenge
            params["code_challenge_method"] = pkce.code_challenge_method
        
        url = f"{config.authorize_url}?{urlencode(params)}"
        return url, state
    
    async def exchange_code(
        self,
        provider: OAuthProvider,
        code: str,
        state: str,
    ) -> Optional[OAuthToken]:
        """
        Exchange authorization code for tokens.
        
        Args:
            provider: OAuth provider
            code: Authorization code from callback
            state: State parameter for validation
            
        Returns:
            OAuthToken if successful, None otherwise
        """
        # Validate state
        redirect_after = self._state.validate(state)
        if redirect_after is None:
            logger.warning("Invalid or expired OAuth state")
            return None
        
        config = self._providers.get(provider)
        if not config:
            return None
        
        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "code": code,
            "redirect_uri": config.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        # Add PKCE verifier if used
        pkce = self._pkce_challenges.pop(state, None)
        if pkce:
            data["code_verifier"] = pkce.code_verifier
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                headers = {"Accept": "application/json"}
                
                async with session.post(
                    config.token_url,
                    data=data,
                    headers=headers,
                ) as response:
                    if response.status != 200:
                        logger.error(f"Token exchange failed: {response.status}")
                        return None
                    
                    token_data = await response.json()
                    
                    return OAuthToken(
                        access_token=token_data["access_token"],
                        token_type=token_data.get("token_type", "Bearer"),
                        expires_in=token_data.get("expires_in", 3600),
                        refresh_token=token_data.get("refresh_token"),
                        scope=token_data.get("scope", ""),
                        id_token=token_data.get("id_token"),
                    )
                    
        except ImportError:
            logger.error("aiohttp not available for OAuth")
            return None
        except Exception as e:
            logger.error(f"Token exchange error: {e}")
            return None
    
    async def get_user_info(
        self,
        provider: OAuthProvider,
        token: OAuthToken,
    ) -> Optional[OAuthUser]:
        """
        Get user info from OAuth provider.
        
        Args:
            provider: OAuth provider
            token: Access token
            
        Returns:
            OAuthUser if successful, None otherwise
        """
        config = self._providers.get(provider)
        if not config:
            return None
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"{token.token_type} {token.access_token}",
                    "Accept": "application/json",
                }
                
                async with session.get(
                    config.userinfo_url,
                    headers=headers,
                ) as response:
                    if response.status != 200:
                        logger.error(f"User info request failed: {response.status}")
                        return None
                    
                    data = await response.json()
                    
                    # Parse based on provider
                    return self._parse_user_info(provider, data)
                    
        except ImportError:
            logger.error("aiohttp not available for OAuth")
            return None
        except Exception as e:
            logger.error(f"User info error: {e}")
            return None
    
    def _parse_user_info(
        self,
        provider: OAuthProvider,
        data: Dict[str, Any],
    ) -> OAuthUser:
        """Parse user info based on provider format."""
        if provider == OAuthProvider.GOOGLE:
            return OAuthUser(
                provider=provider,
                provider_id=data.get("sub", ""),
                email=data.get("email"),
                name=data.get("name"),
                picture_url=data.get("picture"),
                raw_data=data,
            )
        elif provider == OAuthProvider.MICROSOFT:
            return OAuthUser(
                provider=provider,
                provider_id=data.get("id", ""),
                email=data.get("mail") or data.get("userPrincipalName"),
                name=data.get("displayName"),
                picture_url=None,
                raw_data=data,
            )
        elif provider == OAuthProvider.GITHUB:
            return OAuthUser(
                provider=provider,
                provider_id=str(data.get("id", "")),
                email=data.get("email"),
                name=data.get("name") or data.get("login"),
                picture_url=data.get("avatar_url"),
                raw_data=data,
            )
        else:
            return OAuthUser(
                provider=provider,
                provider_id=data.get("sub") or data.get("id", ""),
                email=data.get("email"),
                name=data.get("name"),
                raw_data=data,
            )
    
    async def refresh_token(
        self,
        provider: OAuthProvider,
        refresh_token: str,
    ) -> Optional[OAuthToken]:
        """Refresh an access token."""
        config = self._providers.get(provider)
        if not config:
            return None
        
        data = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    config.token_url,
                    data=data,
                    headers={"Accept": "application/json"},
                ) as response:
                    if response.status != 200:
                        return None
                    
                    token_data = await response.json()
                    
                    return OAuthToken(
                        access_token=token_data["access_token"],
                        token_type=token_data.get("token_type", "Bearer"),
                        expires_in=token_data.get("expires_in", 3600),
                        refresh_token=token_data.get("refresh_token", refresh_token),
                        scope=token_data.get("scope", ""),
                    )
                    
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    def get_providers(self) -> List[OAuthProvider]:
        """Get list of registered providers."""
        return list(self._providers.keys())


# Global OAuth service
_oauth: Optional[OAuthService] = None


def get_oauth_service() -> OAuthService:
    """Get or create the global OAuth service."""
    global _oauth
    if _oauth is None:
        _oauth = OAuthService()
    return _oauth
