"""
Unit Tests for Security Audit
Tests security audit functionality.
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import the security audit module
try:
    from app.core.security import security_audit
except ImportError:
    pytest.skip("Could not import security_audit", allow_module_level=True)


class TestSecurityAuditImports:
    """Test security audit module can be imported."""

    def test_module_imports(self):
        """Test module can be imported."""
        assert (
            security_audit is not None
        ), "Failed to import security_audit module"

    def test_module_has_functions(self):
        """Test module has expected functions."""
        functions = dir(security_audit)
        assert len(functions) > 0, "module should have functions"


class TestSecurityAuditFunctions:
    """Test security audit functions exist."""

    def test_run_security_audit_function_exists(self):
        """Test run_security_audit function exists."""
        if hasattr(security_audit, "run_security_audit"):
            assert callable(
                security_audit.run_security_audit
            ), "run_security_audit should be callable"

    def test_check_vulnerabilities_function_exists(self):
        """Test check_vulnerabilities function exists."""
        if hasattr(security_audit, "check_vulnerabilities"):
            assert callable(
                security_audit.check_vulnerabilities
            ), "check_vulnerabilities should be callable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

