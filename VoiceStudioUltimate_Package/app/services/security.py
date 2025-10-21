#!/usr/bin/env python3
"""
VoiceStudio Authentication and Security System
Handles JWT tokens, API keys, and service authentication.
"""

import json
import logging
import time
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass
import secrets
import jwt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class User:
    """User information structure"""
    user_id: str
    username: str
    email: str
    roles: List[str]
    api_key: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True

@dataclass
class ServiceToken:
    """Service token structure"""
    service_id: str
    service_name: str
    token: str
    expires_at: datetime
    permissions: List[str]

class SecurityManager:
    """Manages authentication and security"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.users: Dict[str, User] = {}
        self.service_tokens: Dict[str, ServiceToken] = {}
        self.api_keys: Dict[str, str] = {}  # api_key -> user_id
        self.blacklisted_tokens: set = set()
        
        # Initialize with default admin user
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user"""
        admin_api_key = secrets.token_urlsafe(32)
        admin_user = User(
            user_id="admin",
            username="admin",
            email="admin@voicestudio.local",
            roles=["admin", "user"],
            api_key=admin_api_key,
            created_at=datetime.now()
        )
        
        self.users["admin"] = admin_user
        self.api_keys[admin_api_key] = "admin"
        logger.info("Created default admin user")
    
    def create_user(self, username: str, email: str, roles: List[str] = None) -> User:
        """Create a new user"""
        user_id = secrets.token_urlsafe(16)
        api_key = secrets.token_urlsafe(32)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            roles=roles or ["user"],
            api_key=api_key,
            created_at=datetime.now()
        )
        
        self.users[user_id] = user
        self.api_keys[api_key] = user_id
        logger.info(f"Created user: {username}")
        return user
    
    def authenticate_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate using API key"""
        if api_key in self.api_keys:
            user_id = self.api_keys[api_key]
            user = self.users.get(user_id)
            if user and user.is_active:
                user.last_login = datetime.now()
                return user
        return None
    
    def generate_jwt_token(self, user: User, expires_hours: int = 24) -> str:
        """Generate JWT token for user"""
        payload = {
            "user_id": user.user_id,
            "username": user.username,
            "roles": user.roles,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=expires_hours)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token"""
        if token in self.blacklisted_tokens:
            return None
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def create_service_token(self, service_id: str, service_name: str, 
                           permissions: List[str] = None) -> ServiceToken:
        """Create a service-to-service token"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        service_token = ServiceToken(
            service_id=service_id,
            service_name=service_name,
            token=token,
            expires_at=expires_at,
            permissions=permissions or ["read", "write"]
        )
        
        self.service_tokens[token] = service_token
        logger.info(f"Created service token for: {service_name}")
        return service_token
    
    def verify_service_token(self, token: str) -> Optional[ServiceToken]:
        """Verify service token"""
        service_token = self.service_tokens.get(token)
        if service_token and service_token.expires_at > datetime.now():
            return service_token
        return None
    
    def blacklist_token(self, token: str):
        """Blacklist a token"""
        self.blacklisted_tokens.add(token)
        logger.info("Token blacklisted")
    
    def has_permission(self, user: User, permission: str) -> bool:
        """Check if user has specific permission"""
        if "admin" in user.roles:
            return True
        
        # Define permission mappings
        permission_map = {
            "read": ["user", "service"],
            "write": ["user", "service"],
            "admin": ["admin"],
            "service_call": ["service", "admin"]
        }
        
        required_roles = permission_map.get(permission, [])
        return any(role in user.roles for role in required_roles)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def list_users(self) -> List[User]:
        """List all users"""
        return list(self.users.values())

class SecurityMiddleware:
    """Middleware for handling authentication"""
    
    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager
    
    def authenticate_request(self, headers: Dict[str, str]) -> Optional[User]:
        """Authenticate incoming request"""
        # Check for API key
        api_key = headers.get("X-API-Key") or headers.get("Authorization", "").replace("Bearer ", "")
        if api_key:
            user = self.security_manager.authenticate_api_key(api_key)
            if user:
                return user
        
        # Check for JWT token
        auth_header = headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = self.security_manager.verify_jwt_token(token)
            if payload:
                user_id = payload.get("user_id")
                return self.security_manager.get_user_by_id(user_id)
        
        return None
    
    def check_permission(self, user: User, permission: str) -> bool:
        """Check if user has permission"""
        return self.security_manager.has_permission(user, permission)
    
    def create_auth_response(self, user: User) -> Dict:
        """Create authentication response"""
        jwt_token = self.security_manager.generate_jwt_token(user)
        return {
            "authenticated": True,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "roles": user.roles
            },
            "jwt_token": jwt_token,
            "api_key": user.api_key,
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }

# Global security manager instance
security_manager = SecurityManager()
security_middleware = SecurityMiddleware(security_manager)

def create_service_auth_token(service_id: str, service_name: str) -> str:
    """Create authentication token for service"""
    service_token = security_manager.create_service_token(
        service_id, service_name, ["service_call", "read", "write"]
    )
    return service_token.token

def authenticate_service_request(token: str) -> bool:
    """Authenticate service-to-service request"""
    service_token = security_manager.verify_service_token(token)
    return service_token is not None

if __name__ == "__main__":
    # Example usage
    logger.info("Security system initialized")
    
    # Create a test user
    user = security_manager.create_user("testuser", "test@example.com", ["user"])
    logger.info(f"Created user: {user.username}")
    
    # Test authentication
    auth_user = security_manager.authenticate_api_key(user.api_key)
    if auth_user:
        logger.info(f"Authentication successful: {auth_user.username}")
    
    # Test JWT token
    jwt_token = security_manager.generate_jwt_token(user)
    payload = security_manager.verify_jwt_token(jwt_token)
    if payload:
        logger.info(f"JWT verification successful: {payload['username']}")
