#!/usr/bin/env python3
"""
Security scan for plugin submissions.

Performs static analysis and security checks on plugin source code
before allowing it into the catalog.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

# Security rules - patterns that indicate potential issues
SECURITY_RULES = [
    {
        "id": "EXEC_DANGEROUS",
        "severity": "critical",
        # Negative lookbehind to avoid matching method calls like obj.exec()
        "pattern": r"(?<!\.)(?<!\w)(exec|eval)\s*\(",
        "message": "Use of exec() or eval() is prohibited",
        "description": "Dynamic code execution can lead to arbitrary code execution vulnerabilities",
        "case_sensitive": True,
    },
    {
        "id": "OS_COMMAND_INJECTION",
        "severity": "high",
        "pattern": r"\bos\.system\s*\(",
        "message": "os.system() is prohibited - use subprocess with shell=False",
        "description": "os.system() is vulnerable to command injection",
        "case_sensitive": True,  # Python module names are case-sensitive
    },
    {
        "id": "SHELL_TRUE",
        "severity": "high",
        "pattern": r"subprocess\.[a-z_]+\([^)]*shell\s*=\s*True",
        "message": "subprocess with shell=True is not allowed",
        "description": "shell=True enables command injection vulnerabilities",
        "case_sensitive": True,  # Python module names are case-sensitive
    },
    {
        "id": "PICKLE_UNSAFE",
        "severity": "high",
        "pattern": r"\bpickle\.loads?\s*\(",
        "message": "pickle.load() is prohibited - use json or safer alternatives",
        "description": "Pickle deserialization can execute arbitrary code",
        "case_sensitive": True,  # Python module names are case-sensitive
    },
    {
        "id": "YAML_UNSAFE",
        "severity": "high",
        "pattern": r"yaml\.(?:load|unsafe_load)\s*\([^)]*(?:Loader\s*=\s*yaml\.(?:Loader|UnsafeLoader|FullLoader))?[^)]*\)",
        "message": "Use yaml.safe_load() instead of yaml.load()",
        "description": "YAML load with unsafe loader can execute arbitrary code",
        "case_sensitive": True,  # Python module names are case-sensitive
    },
    {
        "id": "COMPILE_EXEC",
        "severity": "critical",
        "pattern": r"(?<!\.)(?<!\w)compile\s*\([^)]+['\"]exec['\"]",
        "message": "compile() with exec mode is prohibited",
        "description": "Compiling code for execution is a security risk",
        "case_sensitive": True,
    },
    {
        "id": "IMPORT_DANGEROUS",
        "severity": "high",
        "pattern": r"\b__import__\s*\(",
        "message": "Dynamic imports via __import__ are not allowed",
        "description": "Dynamic imports can load arbitrary modules",
        "case_sensitive": True,  # Python builtins are case-sensitive
    },
    {
        "id": "CTYPES_UNSAFE",
        "severity": "medium",
        "pattern": r"\bctypes\.(cdll|windll|CDLL|WinDLL|pydll|PyDLL|oledll|OleDLL)\s*[\.\[]",
        "message": "Direct C library loading requires review",
        "description": "Loading native libraries can bypass sandbox",
        "case_sensitive": True,  # Python module names are case-sensitive
    },
    {
        "id": "SOCKET_RAW",
        "severity": "medium",
        "pattern": r"socket\.socket\s*\([^)]*socket\.SOCK_RAW",
        "message": "Raw sockets are not allowed",
        "description": "Raw sockets can be used for network attacks",
        "case_sensitive": True,  # Python module names are case-sensitive
    },
    {
        "id": "NETWORK_BIND",
        "severity": "low",
        "pattern": r"\.bind\s*\(\s*\(['\"][^'\"]*['\"]\s*,\s*\d+\s*\)\s*\)",
        "message": "Network server binding detected - ensure network_local permission",
        "description": "Binding to ports requires explicit permission",
        "case_sensitive": True,
    },
    {
        "id": "FILE_TRAVERSAL",
        "severity": "high",
        "pattern": r"['\"]\.\.[\\/]",
        "message": "Path traversal pattern detected",
        "description": "Path traversal can access files outside plugin directory",
        "case_sensitive": True,  # Path patterns are case-sensitive on most filesystems
    },
    {
        "id": "HARDCODED_SECRETS",
        "severity": "high",
        "pattern": r"(?:api_key|password|secret|token|credential|auth_token|api_secret|private_key)\s*=\s*['\"][^'\"]{8,}['\"]",
        "message": "Potential hardcoded secret detected",
        "description": "Secrets should not be hardcoded in source",
        "case_sensitive": False,  # Variable names can vary in case
    },
    {
        "id": "CRYPTO_WEAK",
        "severity": "low",  # Downgraded: MD5/SHA1 are fine for non-security uses like checksums
        "pattern": r"hashlib\.(?:md5|sha1)\s*\(",
        "message": "Weak cryptographic hash detected - ensure not used for security",
        "description": "MD5 and SHA1 are cryptographically weak; acceptable for checksums only",
        "case_sensitive": True,  # Python module names are case-sensitive
    },
    {
        "id": "GETATTR_DANGEROUS",
        "severity": "medium",
        "pattern": r"(?<!\.)(?<!\w)getattr\s*\([^,]+,\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)",
        "message": "Dynamic attribute access with variable name",
        "description": "Can be used for attribute injection",
        "case_sensitive": True,  # Python builtins are case-sensitive
    },
]

# File patterns to scan
SCAN_PATTERNS = ["*.py", "*.pyw"]

# Files/patterns to skip
SKIP_PATTERNS = [
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "*.pyc",
    "*.pyo",
]


def download_and_extract_package(url: str, dest_dir: Path) -> Tuple[bool, Optional[str]]:
    """Download and extract a .vspkg package."""
    try:
        # Download package
        with urlopen(url, timeout=60) as response:
            content = response.read()
        
        # Save to temp file
        pkg_path = dest_dir / "plugin.vspkg"
        pkg_path.write_bytes(content)
        
        # Extract (vspkg is a zip file)
        extract_dir = dest_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(pkg_path, "r") as zf:
            # Security check - prevent zip slip
            for member in zf.namelist():
                member_path = extract_dir / member
                if not str(member_path.resolve()).startswith(str(extract_dir.resolve())):
                    return False, f"Zip slip attempt detected: {member}"
            
            zf.extractall(extract_dir)
        
        return True, None
        
    except HTTPError as e:
        return False, f"HTTP error downloading package: {e.code} {e.reason}"
    except URLError as e:
        return False, f"URL error downloading package: {e.reason}"
    except zipfile.BadZipFile:
        return False, "Invalid package file - not a valid zip/vspkg"
    except Exception as e:
        return False, f"Error downloading/extracting package: {e}"


def scan_file(file_path: Path) -> List[Dict[str, Any]]:
    """Scan a single file for security issues."""
    findings = []
    
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")
    except Exception as e:
        findings.append({
            "rule_id": "SCAN_ERROR",
            "severity": "error",
            "file": str(file_path),
            "line": 0,
            "message": f"Could not read file: {e}",
        })
        return findings
    
    for rule in SECURITY_RULES:
        # Use case-sensitive matching by default for Python code
        # Only use IGNORECASE if explicitly set to False
        flags = 0 if rule.get("case_sensitive", True) else re.IGNORECASE
        pattern = re.compile(rule["pattern"], flags)
        
        for line_num, line in enumerate(lines, start=1):
            # Skip comments
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            
            if pattern.search(line):
                findings.append({
                    "rule_id": rule["id"],
                    "severity": rule["severity"],
                    "file": str(file_path),
                    "line": line_num,
                    "message": rule["message"],
                    "description": rule["description"],
                    "code_snippet": line.strip()[:100],
                })
    
    return findings


def scan_directory(dir_path: Path) -> List[Dict[str, Any]]:
    """Scan all Python files in a directory."""
    all_findings = []
    
    for pattern in SCAN_PATTERNS:
        for file_path in dir_path.rglob(pattern):
            # Skip excluded patterns
            skip = False
            for skip_pattern in SKIP_PATTERNS:
                if skip_pattern in str(file_path):
                    skip = True
                    break
            
            if skip:
                continue
            
            findings = scan_file(file_path)
            all_findings.extend(findings)
    
    return all_findings


def run_bandit(dir_path: Path) -> List[Dict[str, Any]]:
    """Run bandit security scanner if available."""
    findings = []
    
    try:
        result = subprocess.run(
            ["bandit", "-r", str(dir_path), "-f", "json", "-q"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        if result.stdout:
            bandit_output = json.loads(result.stdout)
            for issue in bandit_output.get("results", []):
                findings.append({
                    "rule_id": f"BANDIT_{issue.get('test_id', 'UNKNOWN')}",
                    "severity": issue.get("issue_severity", "").lower(),
                    "file": issue.get("filename", ""),
                    "line": issue.get("line_number", 0),
                    "message": issue.get("issue_text", ""),
                    "description": issue.get("more_info", ""),
                    "confidence": issue.get("issue_confidence", ""),
                })
                
    except FileNotFoundError:
        # Bandit not installed, skip
        pass
    except subprocess.TimeoutExpired:
        findings.append({
            "rule_id": "BANDIT_TIMEOUT",
            "severity": "warning",
            "file": "",
            "line": 0,
            "message": "Bandit scan timed out",
        })
    except Exception as e:
        findings.append({
            "rule_id": "BANDIT_ERROR",
            "severity": "warning",
            "file": "",
            "line": 0,
            "message": f"Bandit scan error: {e}",
        })
    
    return findings


def calculate_risk_score(findings: List[Dict[str, Any]]) -> int:
    """Calculate overall risk score from findings."""
    severity_weights = {
        "critical": 100,
        "high": 25,
        "medium": 10,
        "low": 3,
        "warning": 1,
        "info": 0,
    }
    
    score = 0
    for finding in findings:
        severity = finding.get("severity", "low").lower()
        score += severity_weights.get(severity, 5)
    
    return min(score, 1000)  # Cap at 1000


def main():
    """Main entry point."""
    # Get submission data
    submission_json = os.environ.get("SUBMISSION_DATA", "")
    
    if not submission_json:
        submission_file = os.environ.get("SUBMISSION_FILE", "")
        if submission_file and Path(submission_file).exists():
            submission_json = Path(submission_file).read_text()
    
    if not submission_json:
        print("Error: No submission data provided", file=sys.stderr)
        sys.exit(1)
    
    try:
        submission = json.loads(submission_json)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid submission JSON: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get package URL
    package_url = submission.get("package_url")
    if not package_url:
        print("Error: No package URL in submission", file=sys.stderr)
        sys.exit(1)
    
    # Create temp directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Download and extract
        success, error = download_and_extract_package(package_url, temp_path)
        if not success:
            result = {
                "scan_completed": False,
                "error": error,
                "findings": [],
                "risk_score": 0,
                "pass": False,
            }
            print(json.dumps(result, indent=2))
            sys.exit(1)
        
        extract_dir = temp_path / "extracted"
        
        # Run custom security scan
        findings = scan_directory(extract_dir)
        
        # Run bandit if available
        bandit_findings = run_bandit(extract_dir)
        findings.extend(bandit_findings)
        
        # Calculate risk score
        risk_score = calculate_risk_score(findings)
        
        # Determine pass/fail
        # Fail if any critical issues or score > 100
        has_critical = any(f.get("severity") == "critical" for f in findings)
        scan_pass = not has_critical and risk_score <= 100
        
        # Build result
        result = {
            "scan_completed": True,
            "findings": findings,
            "findings_count": {
                "critical": sum(1 for f in findings if f.get("severity") == "critical"),
                "high": sum(1 for f in findings if f.get("severity") == "high"),
                "medium": sum(1 for f in findings if f.get("severity") == "medium"),
                "low": sum(1 for f in findings if f.get("severity") == "low"),
            },
            "risk_score": risk_score,
            "pass": scan_pass,
        }
        
        # Output JSON
        print(json.dumps(result, indent=2))
        
        # Exit with error if scan failed
        if not scan_pass:
            sys.exit(1)


if __name__ == "__main__":
    main()
