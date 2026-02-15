"""
Authentication Routes

Endpoints for authentication, token management, and user management.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

if TYPE_CHECKING:
    from pydantic import EmailStr
else:
    # Runtime: use string if email-validator is not available
    try:
        from pydantic import EmailStr
    except ImportError:
        EmailStr = str  # type: ignore

from ..auth import User, UserRole, get_api_key_manager, get_jwt_manager
from ..middleware.auth_middleware import require_authentication

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])

security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    """Login request."""

    username: str
    password: str | None = None  # For future password support
    api_key: str | None = None


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """User response."""

    user_id: str
    username: str
    email: str | None = None
    role: str
    is_active: bool
    created_at: str
    last_login: str | None = None


class CreateUserRequest(BaseModel):
    """Create user request."""

    username: str
    email: str | None = None  # Using str instead of EmailStr to avoid email-validator dependency
    role: UserRole = UserRole.USER
    generate_api_key: bool = True


class CreateUserResponse(BaseModel):
    """Create user response."""

    user: UserResponse
    api_key: str | None = None  # Only returned on creation


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Login and get JWT tokens.

    Supports API key authentication for service-to-service communication.
    """
    if not get_jwt_manager():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT authentication is not available",
        )

    # Authenticate using API key if provided
    if request.api_key:
        user = get_api_key_manager().authenticate_api_key(request.api_key)
        if not user:
            logger.warning(
                f"Failed login attempt with API key for username: {request.username}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
            )
    else:
        # Authenticate using password if provided
        if request.password:
            user = get_api_key_manager().authenticate_password(
                request.username, request.password
            )
            if not user:
                logger.warning(
                    f"Failed login attempt with password for username: {request.username}"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )
        else:
            # No password provided - check if user exists, otherwise create guest
            user = get_api_key_manager().get_user(request.username)
            if not user:
                # Create a guest user for demo purposes (no password required)
                user, _ = get_api_key_manager().create_user(
                    username=request.username,
                    role=UserRole.GUEST,
                    generate_api_key=False,
                )

    # Create tokens
    access_token = get_jwt_manager().create_access_token(
        user_id=user.user_id,
        username=user.username,
        role=user.role,
    )

    refresh_token = get_jwt_manager().create_refresh_token(
        user_id=user.user_id,
        username=user.username,
    )

    # Update last login
    user.last_login = datetime.utcnow()

    logger.info(
        f"User {user.user_id} logged in successfully",
        extra={
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
        },
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=60 * 24 * 60,  # 24 hours in seconds
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Refresh access token using refresh token."""
    if not get_jwt_manager():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="JWT authentication is not available",
        )

    refresh_token = credentials.credentials

    access_token = get_jwt_manager().refresh_access_token(refresh_token)
    if not access_token:
        logger.warning("Failed to refresh token: invalid refresh token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Get new refresh token
    payload = get_jwt_manager().verify_token(refresh_token)
    if payload:
        new_refresh_token = get_jwt_manager().create_refresh_token(
            user_id=payload.get("sub"),
            username=payload.get("username"),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=60 * 24 * 60,  # 24 hours in seconds
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: User = Depends(require_authentication),
):
    """Get current authenticated user information."""
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at.isoformat(),
        last_login=user.last_login.isoformat() if user.last_login else None,
    )


@router.post("/users", response_model=CreateUserResponse)
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(require_authentication),
):
    """Create a new user (admin only)."""
    # Check if current user is admin
    if current_user.role != UserRole.ADMIN:
        logger.warning(
            f"Non-admin user {current_user.user_id} attempted to create user",
            extra={"user_id": current_user.user_id, "username": current_user.username},
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create users",
        )

    # Create user
    user, api_key = get_api_key_manager().create_user(
        username=request.username,
        email=request.email,
        role=request.role,
        generate_api_key=request.generate_api_key,
    )

    logger.info(
        f"User {user.user_id} created by admin {current_user.user_id}",
        extra={
            "created_user_id": user.user_id,
            "created_username": user.username,
            "created_by": current_user.user_id,
        },
    )

    return CreateUserResponse(
        user=UserResponse(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None,
        ),
        api_key=api_key,
    )


@router.post("/api-keys/generate")
async def generate_api_key(
    current_user: User = Depends(require_authentication),
):
    """Generate a new API key for the current user."""
    api_key_manager = get_api_key_manager()
    api_key = api_key_manager.generate_api_key()

    # Update user's API key
    current_user.api_key = api_key_manager.hash_api_key(api_key)
    api_key_manager._api_keys[api_key_manager.hash_api_key(api_key)] = current_user

    logger.info(
        f"API key generated for user {current_user.user_id}",
        extra={"user_id": current_user.user_id, "username": current_user.username},
    )

    return {
        "api_key": api_key,
        "message": "Store this API key securely. It will not be shown again.",
    }


@router.post("/api-keys/revoke")
async def revoke_api_key(
    api_key: str,
    current_user: User = Depends(require_authentication),
):
    """Revoke an API key."""
    api_key_manager = get_api_key_manager()

    # Check if API key belongs to current user or user is admin
    user = api_key_manager.authenticate_api_key(api_key)
    if not user or (
        user.user_id != current_user.user_id and current_user.role != UserRole.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only revoke your own API keys",
        )

    success = api_key_manager.revoke_api_key(api_key)

    if success:
        logger.info(
            f"API key revoked by user {current_user.user_id}",
            extra={"user_id": current_user.user_id, "username": current_user.username},
        )
        return {"message": "API key revoked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )
