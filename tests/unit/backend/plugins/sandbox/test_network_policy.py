"""
Tests for Plugin Network Policy Enforcer.

Phase 5A: Validates network egress policy enforcement.
"""

import os
import sys

import pytest

# Add backend to path
sys.path.insert(
    0, str(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..", "backend"))
)

from backend.plugins.sandbox.network_policy import (
    ConnectionAttempt,
    ConnectionType,
    NetworkAction,
    NetworkPermissions,
    NetworkPolicyEnforcer,
    SocketWrapper,
    create_enforcer,
    generate_socket_bootstrap,
    get_enforcer,
    remove_enforcer,
)


class TestNetworkPermissions:
    """Tests for NetworkPermissions configuration."""

    def test_default_permissions(self):
        """Test default values."""
        perms = NetworkPermissions()

        assert not perms.enabled
        assert perms.allow_localhost
        assert not perms.allow_all
        assert perms.allowed_hosts == []
        assert perms.allowed_ports == []
        assert "https" in perms.allowed_protocols

    def test_from_manifest_disabled(self):
        """Test parsing disabled network permissions."""
        manifest_perms = {"network": False}
        perms = NetworkPermissions.from_manifest(manifest_perms)

        assert not perms.enabled
        assert not perms.allow_all

    def test_from_manifest_enabled_all(self):
        """Test parsing unrestricted network permissions."""
        manifest_perms = {"network": True}
        perms = NetworkPermissions.from_manifest(manifest_perms)

        assert perms.enabled
        assert perms.allow_all

    def test_from_manifest_detailed(self):
        """Test parsing detailed network permissions."""
        manifest_perms = {
            "network": {
                "enabled": True,
                "allow_localhost": False,
                "allow_all": False,
                "allowed_hosts": ["api.example.com", "*.trusted.org"],
                "allowed_ports": [443, 8080],
                "allowed_protocols": ["https"],
            }
        }
        perms = NetworkPermissions.from_manifest(manifest_perms)

        assert perms.enabled
        assert not perms.allow_localhost
        assert not perms.allow_all
        assert "api.example.com" in perms.allowed_hosts
        assert "*.trusted.org" in perms.allowed_hosts
        assert 443 in perms.allowed_ports
        assert 8080 in perms.allowed_ports
        assert "https" in perms.allowed_protocols

    def test_allows_host_exact_match(self):
        """Test exact host matching."""
        perms = NetworkPermissions(
            enabled=True,
            allowed_hosts=["api.example.com"],
        )

        assert perms.allows_host("api.example.com")
        assert not perms.allows_host("other.example.com")
        assert not perms.allows_host("example.com")

    def test_allows_host_wildcard(self):
        """Test wildcard subdomain matching."""
        perms = NetworkPermissions(
            enabled=True,
            allowed_hosts=["*.example.com"],
        )

        assert perms.allows_host("api.example.com")
        assert perms.allows_host("www.example.com")
        assert perms.allows_host("sub.api.example.com")
        assert perms.allows_host("example.com")  # Base domain matches
        assert not perms.allows_host("notexample.com")

    def test_allows_localhost(self):
        """Test localhost handling."""
        perms_allow = NetworkPermissions(enabled=True, allow_localhost=True)
        perms_deny = NetworkPermissions(enabled=True, allow_localhost=False)

        for host in ["localhost", "127.0.0.1", "::1"]:
            assert perms_allow.allows_host(host)
            assert not perms_deny.allows_host(host)

    def test_allows_port(self):
        """Test port filtering."""
        perms = NetworkPermissions(
            enabled=True,
            allow_all=False,
            allowed_ports=[443, 8080],
        )

        assert perms.allows_port(443)
        assert perms.allows_port(8080)
        assert not perms.allows_port(80)
        assert not perms.allows_port(22)

    def test_allows_port_empty_means_all(self):
        """Test that empty port list allows all ports."""
        perms = NetworkPermissions(
            enabled=True,
            allowed_ports=[],
        )

        assert perms.allows_port(443)
        assert perms.allows_port(80)
        assert perms.allows_port(12345)

    def test_allows_protocol(self):
        """Test protocol filtering."""
        perms = NetworkPermissions(
            enabled=True,
            allowed_protocols=["https", "wss"],
        )

        assert perms.allows_protocol("https")
        assert perms.allows_protocol("HTTPS")  # Case insensitive
        assert perms.allows_protocol("wss")
        assert not perms.allows_protocol("http")
        assert not perms.allows_protocol("ftp")


class TestConnectionAttempt:
    """Tests for ConnectionAttempt data structure."""

    def test_to_dict(self):
        """Test serialization."""
        import time

        ts = time.time()

        attempt = ConnectionAttempt(
            timestamp=ts,
            plugin_id="test-plugin",
            host="api.example.com",
            port=443,
            connection_type=ConnectionType.TCP,
            action=NetworkAction.ALLOW,
            reason="allowed by policy",
        )

        data = attempt.to_dict()

        assert data["timestamp"] == ts
        assert data["plugin_id"] == "test-plugin"
        assert data["host"] == "api.example.com"
        assert data["port"] == 443
        assert data["connection_type"] == "tcp"
        assert data["action"] == "allow"
        assert data["reason"] == "allowed by policy"


class TestNetworkPolicyEnforcer:
    """Tests for NetworkPolicyEnforcer."""

    @pytest.fixture
    def enforcer_restricted(self):
        """Create an enforcer with restricted permissions."""
        perms = NetworkPermissions(
            enabled=True,
            allow_localhost=True,
            allowed_hosts=["api.example.com", "*.trusted.org"],
            allowed_ports=[443, 8080],
        )
        return NetworkPolicyEnforcer("test-plugin", perms)

    @pytest.fixture
    def enforcer_disabled(self):
        """Create an enforcer with disabled networking."""
        perms = NetworkPermissions(enabled=False)
        return NetworkPolicyEnforcer("test-plugin", perms)

    def test_check_connection_allowed(self, enforcer_restricted):
        """Test allowed connection."""
        allowed, reason = enforcer_restricted.check_connection("api.example.com", 443)

        assert allowed
        assert "allowed" in reason.lower()
        assert enforcer_restricted.allowed_count == 1
        assert enforcer_restricted.denied_count == 0

    def test_check_connection_denied_host(self, enforcer_restricted):
        """Test denied connection due to host."""
        allowed, reason = enforcer_restricted.check_connection("malicious.com", 443)

        assert not allowed
        assert "host" in reason.lower()
        assert enforcer_restricted.allowed_count == 0
        assert enforcer_restricted.denied_count == 1

    def test_check_connection_denied_port(self, enforcer_restricted):
        """Test denied connection due to port."""
        allowed, reason = enforcer_restricted.check_connection("api.example.com", 22)

        assert not allowed
        assert "port" in reason.lower()
        assert enforcer_restricted.denied_count == 1

    def test_check_connection_network_disabled(self, enforcer_disabled):
        """Test that all connections are denied when networking is disabled."""
        allowed, reason = enforcer_disabled.check_connection("localhost", 80)

        assert not allowed
        assert "not enabled" in reason.lower()

    def test_check_localhost(self, enforcer_restricted):
        """Test localhost connections."""
        allowed, reason = enforcer_restricted.check_connection("localhost", 8080)

        assert allowed

    def test_check_wildcard_host(self, enforcer_restricted):
        """Test wildcard host matching."""
        allowed, reason = enforcer_restricted.check_connection("api.trusted.org", 443)

        assert allowed

    def test_check_url(self, enforcer_restricted):
        """Test URL checking."""
        allowed, reason = enforcer_restricted.check_url("https://api.example.com/v1/data")

        assert allowed

    def test_check_url_denied_protocol(self, enforcer_restricted):
        """Test URL denied due to protocol."""
        allowed, reason = enforcer_restricted.check_url("http://api.example.com/v1/data")

        assert not allowed
        assert "protocol" in reason.lower()

    def test_attempts_recorded(self, enforcer_restricted):
        """Test that all attempts are recorded."""
        enforcer_restricted.check_connection("api.example.com", 443)
        enforcer_restricted.check_connection("malicious.com", 443)
        enforcer_restricted.check_connection("localhost", 8080)

        attempts = enforcer_restricted.attempts

        assert len(attempts) == 3
        assert attempts[0].action == NetworkAction.ALLOW
        assert attempts[1].action == NetworkAction.DENY
        assert attempts[2].action == NetworkAction.ALLOW


class TestSocketWrapper:
    """Tests for SocketWrapper."""

    def test_not_installed_by_default(self):
        """Test that wrapper is not installed by default."""
        assert not SocketWrapper._installed

    def test_install_uninstall(self):
        """Test installing and uninstalling wrapper."""
        import socket

        original = socket.socket

        perms = NetworkPermissions(enabled=True, allow_all=True)
        enforcer = NetworkPolicyEnforcer("test", perms)

        # Install
        SocketWrapper.install(enforcer)
        assert SocketWrapper._installed
        assert socket.socket != original

        # Uninstall
        SocketWrapper.uninstall()
        assert not SocketWrapper._installed
        assert socket.socket == original


class TestBootstrapGeneration:
    """Tests for subprocess bootstrap code generation."""

    def test_generate_bootstrap(self):
        """Test bootstrap code generation."""
        permissions = {
            "network": {
                "enabled": True,
                "allowed_hosts": ["api.example.com"],
            }
        }

        code = generate_socket_bootstrap("test-plugin", permissions)

        assert "test-plugin" in code
        assert "api.example.com" in code
        assert "_PolicySocket" in code
        assert "connect" in code

    def test_bootstrap_is_valid_python(self):
        """Test that generated code is valid Python."""
        permissions = {
            "network": {
                "enabled": True,
                "allowed_hosts": ["example.com"],
                "allowed_ports": [443],
            }
        }

        code = generate_socket_bootstrap("test", permissions)

        # Should not raise SyntaxError
        compile(code, "<string>", "exec")


class TestGlobalRegistry:
    """Tests for global enforcer registry."""

    def test_create_and_get_enforcer(self):
        """Test creating and retrieving enforcers."""
        permissions = {"network": {"enabled": True}}

        enforcer = create_enforcer("test-plugin", permissions)

        assert enforcer is not None
        assert get_enforcer("test-plugin") is enforcer

        # Cleanup
        remove_enforcer("test-plugin")
        assert get_enforcer("test-plugin") is None

    def test_remove_nonexistent(self):
        """Test removing non-existent enforcer doesn't error."""
        remove_enforcer("nonexistent")  # Should not raise
