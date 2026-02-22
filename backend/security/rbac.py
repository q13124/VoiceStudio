"""
Role-Based Access Control.

Task 2.1.2: RBAC for multi-user scenarios.
Provides role-based authorization for API access.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Available permissions."""

    # Voice operations
    VOICE_READ = "voice:read"
    VOICE_CREATE = "voice:create"
    VOICE_UPDATE = "voice:update"
    VOICE_DELETE = "voice:delete"
    VOICE_CLONE = "voice:clone"

    # Project operations
    PROJECT_READ = "project:read"
    PROJECT_CREATE = "project:create"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"

    # Engine operations
    ENGINE_READ = "engine:read"
    ENGINE_EXECUTE = "engine:execute"
    ENGINE_CONFIG = "engine:config"

    # Admin operations
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"
    ADMIN_AUDIT = "admin:audit"

    # Settings
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"


@dataclass
class Role:
    """A role with permissions."""

    name: str
    description: str
    permissions: set[Permission]
    is_default: bool = False
    is_admin: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def has_permission(self, permission: Permission) -> bool:
        """Check if role has a permission."""
        if self.is_admin:
            return True
        return permission in self.permissions


@dataclass
class UserRoles:
    """Roles assigned to a user."""

    user_id: str
    roles: set[str]
    direct_permissions: set[Permission] = field(default_factory=set)
    denied_permissions: set[Permission] = field(default_factory=set)
    assigned_at: datetime = field(default_factory=datetime.now)


class RBACService:
    """
    Role-Based Access Control service.

    Features:
    - Role management
    - Permission checking
    - User-role assignments
    - Permission inheritance
    - Permission denial
    """

    # Default roles
    DEFAULT_ROLES = {
        "admin": Role(
            name="admin",
            description="Full system access",
            permissions=set(Permission),
            is_admin=True,
        ),
        "user": Role(
            name="user",
            description="Standard user access",
            permissions={
                Permission.VOICE_READ,
                Permission.VOICE_CREATE,
                Permission.VOICE_UPDATE,
                Permission.PROJECT_READ,
                Permission.PROJECT_CREATE,
                Permission.PROJECT_UPDATE,
                Permission.ENGINE_READ,
                Permission.ENGINE_EXECUTE,
                Permission.SETTINGS_READ,
            },
            is_default=True,
        ),
        "viewer": Role(
            name="viewer",
            description="Read-only access",
            permissions={
                Permission.VOICE_READ,
                Permission.PROJECT_READ,
                Permission.ENGINE_READ,
                Permission.SETTINGS_READ,
            },
        ),
        "operator": Role(
            name="operator",
            description="Engine operations only",
            permissions={
                Permission.ENGINE_READ,
                Permission.ENGINE_EXECUTE,
                Permission.ENGINE_CONFIG,
            },
        ),
    }

    def __init__(self):
        self._roles: dict[str, Role] = dict(self.DEFAULT_ROLES)
        self._user_roles: dict[str, UserRoles] = {}

    def create_role(
        self,
        name: str,
        description: str,
        permissions: set[Permission],
        is_admin: bool = False,
    ) -> Role:
        """Create a new role."""
        if name in self._roles:
            raise ValueError(f"Role already exists: {name}")

        role = Role(
            name=name,
            description=description,
            permissions=permissions,
            is_admin=is_admin,
        )

        self._roles[name] = role
        logger.info(f"Created role: {name}")
        return role

    def get_role(self, name: str) -> Role | None:
        """Get a role by name."""
        return self._roles.get(name)

    def delete_role(self, name: str) -> bool:
        """Delete a role."""
        if name in self.DEFAULT_ROLES:
            raise ValueError(f"Cannot delete default role: {name}")

        if name in self._roles:
            del self._roles[name]
            logger.info(f"Deleted role: {name}")
            return True
        return False

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign a role to a user."""
        if role_name not in self._roles:
            return False

        if user_id not in self._user_roles:
            self._user_roles[user_id] = UserRoles(user_id=user_id, roles=set())

        self._user_roles[user_id].roles.add(role_name)
        logger.info(f"Assigned role {role_name} to user {user_id}")
        return True

    def remove_role(self, user_id: str, role_name: str) -> bool:
        """Remove a role from a user."""
        if user_id not in self._user_roles:
            return False

        if role_name in self._user_roles[user_id].roles:
            self._user_roles[user_id].roles.remove(role_name)
            logger.info(f"Removed role {role_name} from user {user_id}")
            return True
        return False

    def grant_permission(self, user_id: str, permission: Permission) -> None:
        """Grant a direct permission to a user."""
        if user_id not in self._user_roles:
            self._user_roles[user_id] = UserRoles(user_id=user_id, roles=set())

        self._user_roles[user_id].direct_permissions.add(permission)
        logger.info(f"Granted {permission.value} to user {user_id}")

    def deny_permission(self, user_id: str, permission: Permission) -> None:
        """Explicitly deny a permission to a user."""
        if user_id not in self._user_roles:
            self._user_roles[user_id] = UserRoles(user_id=user_id, roles=set())

        self._user_roles[user_id].denied_permissions.add(permission)
        logger.info(f"Denied {permission.value} for user {user_id}")

    def get_user_permissions(self, user_id: str) -> set[Permission]:
        """Get all effective permissions for a user."""
        user_roles = self._user_roles.get(user_id)

        if not user_roles:
            # Return default role permissions
            default_role = next((r for r in self._roles.values() if r.is_default), None)
            return default_role.permissions if default_role else set()

        permissions: set[Permission] = set()

        # Collect from roles
        for role_name in user_roles.roles:
            role = self._roles.get(role_name)
            if role:
                if role.is_admin:
                    return set(Permission)  # Admin gets everything
                permissions.update(role.permissions)

        # Add direct permissions
        permissions.update(user_roles.direct_permissions)

        # Remove denied permissions
        permissions -= user_roles.denied_permissions

        return permissions

    def check_permission(
        self,
        user_id: str,
        permission: Permission,
    ) -> bool:
        """Check if a user has a permission."""
        user_permissions = self.get_user_permissions(user_id)
        return permission in user_permissions

    def check_any_permission(
        self,
        user_id: str,
        permissions: list[Permission],
    ) -> bool:
        """Check if user has any of the permissions."""
        user_permissions = self.get_user_permissions(user_id)
        return bool(user_permissions & set(permissions))

    def check_all_permissions(
        self,
        user_id: str,
        permissions: list[Permission],
    ) -> bool:
        """Check if user has all permissions."""
        user_permissions = self.get_user_permissions(user_id)
        return set(permissions) <= user_permissions

    def get_user_roles(self, user_id: str) -> list[str]:
        """Get role names for a user."""
        user_roles = self._user_roles.get(user_id)
        if not user_roles:
            return []
        return list(user_roles.roles)

    def list_roles(self) -> list[Role]:
        """List all roles."""
        return list(self._roles.values())

    def get_stats(self) -> dict:
        """Get RBAC statistics."""
        return {
            "total_roles": len(self._roles),
            "total_users": len(self._user_roles),
            "roles": list(self._roles.keys()),
        }


# Global RBAC service
_rbac: RBACService | None = None


def get_rbac_service() -> RBACService:
    """Get or create the global RBAC service."""
    global _rbac
    if _rbac is None:
        _rbac = RBACService()
    return _rbac
