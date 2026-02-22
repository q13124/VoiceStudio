"""
Security Policies for Engine Execution
File system and network access restrictions
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class SecurityPolicy:
    """Security policy for engine execution."""

    def __init__(
        self,
        allow_net: bool = False,
        allow_fs_roots: list[str] | None = None,
        allowed_hosts: list[str] | None = None,
        allowed_ports: list[int] | None = None,
    ):
        """
        Initialize security policy.

        Args:
            allow_net: Allow network access
            allow_fs_roots: Allowed file system roots (can use env vars)
            allowed_hosts: Allowed network hosts (if allow_net is True)
            allowed_ports: Allowed network ports (if allow_net is True)
        """
        self.allow_net = allow_net
        self.allow_fs_roots = allow_fs_roots or []
        self.allowed_hosts = allowed_hosts or ["127.0.0.1", "localhost"]
        self.allowed_ports = allowed_ports or []

        # Expand environment variables in paths
        self.allow_fs_roots = [os.path.expandvars(path) for path in self.allow_fs_roots]

    def check_file_access(self, file_path: str) -> bool:
        """
        Check if file access is allowed.

        Args:
            file_path: File path to check

        Returns:
            True if access is allowed, False otherwise
        """
        if not self.allow_fs_roots:
            logger.warning("No file system roots configured, denying access")
            return False

        # Normalize path
        path = Path(file_path).resolve()

        # Check if path is within any allowed root
        for root in self.allow_fs_roots:
            root_path = Path(root).resolve()
            try:
                path.relative_to(root_path)
                return True  # Path is within allowed root
            except ValueError:
                continue  # Path is not within this root

        logger.warning(f"File access denied: {file_path} (not in allowed roots)")
        return False

    def check_network_access(self, host: str, port: int | None = None) -> bool:
        """
        Check if network access is allowed.

        Args:
            host: Host to connect to
            port: Port to connect to (optional)

        Returns:
            True if access is allowed, False otherwise
        """
        if not self.allow_net:
            logger.warning(f"Network access denied: {host}:{port} (network disabled)")
            return False

        # Check host
        if host not in self.allowed_hosts:
            logger.warning(f"Network access denied: {host} (not in allowed hosts)")
            return False

        # Check port if specified
        if port is not None and self.allowed_ports and port not in self.allowed_ports:
            logger.warning(f"Network access denied: {host}:{port} (port not allowed)")
            return False

        return True

    def to_dict(self) -> dict:
        """Convert policy to dictionary."""
        return {
            "allow_net": self.allow_net,
            "allow_fs_roots": self.allow_fs_roots,
            "allowed_hosts": self.allowed_hosts,
            "allowed_ports": self.allowed_ports,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SecurityPolicy:
        """Create policy from dictionary."""
        return cls(
            allow_net=data.get("allow_net", False),
            allow_fs_roots=data.get("allow_fs_roots", []),
            allowed_hosts=data.get("allowed_hosts", ["127.0.0.1", "localhost"]),
            allowed_ports=data.get("allowed_ports", []),
        )


def load_security_policy(manifest: dict) -> SecurityPolicy:
    """
    Load security policy from manifest.

    Args:
        manifest: Engine manifest

    Returns:
        SecurityPolicy instance
    """
    security_config = manifest.get("security", {})

    return SecurityPolicy(
        allow_net=security_config.get("allow_net", False),
        allow_fs_roots=security_config.get(
            "allow_fs_roots", ["%PROGRAMDATA%/VoiceStudio/models", "%APPDATA%/VoiceStudio"]
        ),
        allowed_hosts=security_config.get("allowed_hosts", ["127.0.0.1", "localhost"]),
        allowed_ports=security_config.get("allowed_ports", []),
    )
