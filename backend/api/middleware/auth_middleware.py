"""
Authentication Middleware

Provides authentication and authorization middleware for FastAPI.
"""

import logging
from typing import Optional

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..auth import (
    get_current_user_from_token,
    get_current_user_from_api_key,
    User,
    Permission,
    UserRole,
)
from ..error_handling import create_error_response

logger = logging.getLogger(__name__)

# Security scheme for OpenAPI
security = HTTPBearer(auto_error=False)


async def get_current_user(request: Request) -> Optional[User]:
    """
    Get current authenticated user from request.
    
    Supports both API key (X-API-Key header) and JWT token (Authorization header).
    """
    # Try API key first
    api_key = request.headers.get("X-API-Key")
    if api_key:
        user = get_current_user_from_api_key(api_key)
        if user:
            # Log authentication
            logger.info(
                f"API key authentication successful for user {user.user_id}",
                extra={
                    "user_id": user.user_id,
                    "username": user.username,
                    "auth_method": "api_key",
                }
            )
            return user
    
    # Try JWT token
    credentials: Optional[HTTPAuthorizationCredentials] = await security(request)
    if credentials:
        token = credentials.credentials
        user = get_current_user_from_token(token)
        if user:
            # Log authentication
            logger.info(
                f"JWT authentication successful for user {user.user_id}",
                extra={
                    "user_id": user.user_id,
                    "username": user.username,
                    "auth_method": "jwt",
                }
            )
            return user
    
    return None


async def require_authentication(request: Request) -> User:
    """
    Require authentication and return user.
    
    Raises HTTPException if not authenticated.
    """
    user = await get_current_user(request)
    
    if not user:
        request_id = getattr(request.state, "request_id", None)
        
        # Log authentication failure
        logger.warning(
            f"Authentication required but not provided for {request.url.path}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def require_permission_middleware(
    request: Request,
    required_permission: Permission,
) -> User:
    """
    Require authentication and specific permission.
    
    Raises HTTPException if not authenticated or lacks permission.
    """
    user = await require_authentication(request)
    
    if not user.has_permission(required_permission):
        request_id = getattr(request.state, "request_id", None)
        
        # Log authorization failure
        logger.warning(
            f"Permission denied for user {user.user_id}: {required_permission.value}",
            extra={
                "user_id": user.user_id,
                "username": user.username,
                "required_permission": required_permission.value,
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: {required_permission.value}",
        )
    
    return user


async def require_role_middleware(
    request: Request,
    required_role: UserRole,
) -> User:
    """
    Require authentication and specific role.
    
    Raises HTTPException if not authenticated or lacks role.
    """
    user = await require_authentication(request)
    
    # Check role hierarchy (admin > user > guest)
    role_hierarchy = {
        UserRole.ADMIN: 3,
        UserRole.USER: 2,
        UserRole.GUEST: 1,
        UserRole.SERVICE: 2,
    }
    
    user_level = role_hierarchy.get(user.role, 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    if user_level < required_level:
        request_id = getattr(request.state, "request_id", None)
        
        # Log authorization failure
        logger.warning(
            f"Role denied for user {user.user_id}: required {required_role.value}, has {user.role.value}",
            extra={
                "user_id": user.user_id,
                "username": user.username,
                "required_role": required_role.value,
                "user_role": user.role.value,
                "path": request.url.path,
                "method": request.method,
                "request_id": request_id,
            }
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role denied: requires {required_role.value}",
        )
    
    return user


def get_optional_user(request: Request) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    
    Does not raise exceptions - use for optional authentication.
    """
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we need to handle this differently
            # For now, return None and let the route handle it
            return None
        else:
            return loop.run_until_complete(get_current_user(request))
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(get_current_user(request))
    except Exception:
        return None

