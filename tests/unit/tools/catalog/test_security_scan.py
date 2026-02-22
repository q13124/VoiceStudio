"""Tests for security_scan.py catalog tool."""

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add catalog tools to path
CATALOG_PATH = Path(__file__).parent.parent.parent.parent.parent / "tools" / "catalog"
sys.path.insert(0, str(CATALOG_PATH))

from security_scan import (
    SECURITY_RULES,
    calculate_risk_score,
    scan_directory,
    scan_file,
)


class TestSecurityRules:
    """Tests for security rule definitions."""

    def test_rules_have_required_fields(self):
        """Test that all rules have required fields."""
        required_fields = ["id", "severity", "pattern", "message"]
        for rule in SECURITY_RULES:
            for field in required_fields:
                assert field in rule, f"Rule {rule.get('id', 'unknown')} missing {field}"

    def test_rules_have_valid_severity(self):
        """Test that all rules have valid severity levels."""
        valid_severities = ["critical", "high", "medium", "low", "info"]
        for rule in SECURITY_RULES:
            assert (
                rule["severity"] in valid_severities
            ), f"Rule {rule['id']} has invalid severity: {rule['severity']}"


class TestScanFile:
    """Tests for scan_file function."""

    def test_detect_exec(self):
        """Test detection of exec() usage."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("exec('print(1)')")
            f.flush()
            findings = scan_file(Path(f.name))

        assert len(findings) > 0
        assert any(f["rule_id"] == "EXEC_DANGEROUS" for f in findings)

    def test_detect_eval(self):
        """Test detection of eval() usage."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("result = eval(user_input)")
            f.flush()
            findings = scan_file(Path(f.name))

        assert len(findings) > 0
        assert any(f["rule_id"] == "EXEC_DANGEROUS" for f in findings)

    def test_detect_os_system(self):
        """Test detection of os.system() usage."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import os\nos.system('rm -rf /')")
            f.flush()
            findings = scan_file(Path(f.name))

        assert len(findings) > 0
        assert any(f["rule_id"] == "OS_COMMAND_INJECTION" for f in findings)

    def test_detect_shell_true(self):
        """Test detection of subprocess with shell=True."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("subprocess.run('cmd', shell=True)")
            f.flush()
            findings = scan_file(Path(f.name))

        assert len(findings) > 0
        assert any(f["rule_id"] == "SHELL_TRUE" for f in findings)

    def test_detect_pickle(self):
        """Test detection of pickle.load() usage."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("import pickle\ndata = pickle.load(f)")
            f.flush()
            findings = scan_file(Path(f.name))

        assert len(findings) > 0
        assert any(f["rule_id"] == "PICKLE_UNSAFE" for f in findings)

    def test_detect_path_traversal(self):
        """Test detection of path traversal patterns."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("path = '../../../etc/passwd'")
            f.flush()
            findings = scan_file(Path(f.name))

        assert len(findings) > 0
        assert any(f["rule_id"] == "FILE_TRAVERSAL" for f in findings)

    def test_detect_hardcoded_secret(self):
        """Test detection of hardcoded secrets."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("api_key = 'sk-1234567890abcdef'")
            f.flush()
            findings = scan_file(Path(f.name))

        assert len(findings) > 0
        assert any(f["rule_id"] == "HARDCODED_SECRETS" for f in findings)

    def test_ignore_comments(self):
        """Test that comments are ignored."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# exec('this is a comment')\nprint('safe')")
            f.flush()
            findings = scan_file(Path(f.name))

        # Should not detect exec in comment
        assert not any(f["rule_id"] == "EXEC_DANGEROUS" for f in findings)

    def test_clean_file(self):
        """Test that clean file has no findings."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(
                """
def safe_function(x):
    return x * 2

class SafeClass:
    def __init__(self):
        self.value = 0
"""
            )
            f.flush()
            findings = scan_file(Path(f.name))

        # Should have no critical or high findings
        critical_high = [f for f in findings if f["severity"] in ("critical", "high")]
        assert len(critical_high) == 0


class TestScanDirectory:
    """Tests for scan_directory function."""

    def test_scan_multiple_files(self):
        """Test scanning multiple files in directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create safe file
            (tmppath / "safe.py").write_text("print('hello')")

            # Create unsafe file
            (tmppath / "unsafe.py").write_text("exec(user_input)")

            findings = scan_directory(tmppath)

            assert len(findings) > 0
            assert any("unsafe.py" in str(f["file"]) for f in findings)

    def test_skip_pycache(self):
        """Test that __pycache__ is skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create pycache directory with unsafe file
            pycache = tmppath / "__pycache__"
            pycache.mkdir()
            (pycache / "unsafe.py").write_text("exec(user_input)")

            findings = scan_directory(tmppath)

            # Should not find anything in pycache
            assert not any("__pycache__" in str(f["file"]) for f in findings)


class TestCalculateRiskScore:
    """Tests for calculate_risk_score function."""

    def test_empty_findings(self):
        """Test score with no findings."""
        score = calculate_risk_score([])
        assert score == 0

    def test_critical_finding(self):
        """Test score with critical finding."""
        findings = [{"severity": "critical"}]
        score = calculate_risk_score(findings)
        assert score >= 100

    def test_multiple_findings(self):
        """Test score with multiple findings."""
        findings = [
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "low"},
        ]
        score = calculate_risk_score(findings)
        # high=25 + medium=10 + low=3 = 38
        assert score == 38

    def test_score_cap(self):
        """Test that score is capped at 1000."""
        # Create many critical findings
        findings = [{"severity": "critical"} for _ in range(20)]
        score = calculate_risk_score(findings)
        assert score == 1000

    def test_severity_weights(self):
        """Test that severity weights are correct."""
        # One of each severity
        critical = calculate_risk_score([{"severity": "critical"}])
        high = calculate_risk_score([{"severity": "high"}])
        medium = calculate_risk_score([{"severity": "medium"}])
        low = calculate_risk_score([{"severity": "low"}])

        assert critical > high > medium > low
