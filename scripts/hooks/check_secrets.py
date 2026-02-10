#!/usr/bin/env python3
"""
check_secrets.py - Pre-commit hook to detect potential secrets in staged files.

Usage:
    python scripts/hooks/check_secrets.py <file1> <file2> ...

Exit codes:
    0: No secrets detected
    1: Potential secrets found
"""

import re
import sys
from pathlib import Path


# Patterns that indicate potential secrets
SECRET_PATTERNS = [
    # API keys and tokens
    (r'api[_-]?key\s*[=:]\s*["\'][a-zA-Z0-9+/=]{10,}["\']', 'API key'),
    (r'api[_-]?secret\s*[=:]\s*["\'][a-zA-Z0-9+/=]{10,}["\']', 'API secret'),
    (r'auth[_-]?token\s*[=:]\s*["\'][a-zA-Z0-9+/=]{10,}["\']', 'Auth token'),
    (r'access[_-]?token\s*[=:]\s*["\'][a-zA-Z0-9+/=]{10,}["\']', 'Access token'),
    
    # Passwords
    (r'password\s*[=:]\s*["\'][^"\']{8,}["\']', 'Password'),
    (r'passwd\s*[=:]\s*["\'][^"\']{8,}["\']', 'Password'),
    
    # Private keys
    (r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', 'Private key'),
    
    # AWS credentials
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    (r'aws_secret_access_key\s*[=:]\s*["\'][a-zA-Z0-9+/=]{40}["\']', 'AWS Secret Key'),
    
    # Database connection strings with passwords
    (r'(?:mysql|postgresql|mongodb|redis)://[^:]+:[^@]{8,}@', 'Database connection with password'),
]

# Files to skip
SKIP_PATTERNS = [
    r'\.secrets\.baseline$',
    r'package-lock\.json$',
    r'yarn\.lock$',
    r'\.buildlogs/',
    r'\.venv/',
    r'env/',
    r'node_modules/',
    r'runtime/external/',
]


def should_skip(file_path: str) -> bool:
    """Check if file should be skipped."""
    for pattern in SKIP_PATTERNS:
        if re.search(pattern, file_path):
            return True
    return False


def check_file(file_path: Path) -> list:
    """Check a file for potential secrets."""
    issues = []
    
    if should_skip(str(file_path)):
        return issues
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except (IOError, UnicodeDecodeError):
        return issues
    
    for line_num, line in enumerate(content.splitlines(), 1):
        for pattern, secret_type in SECRET_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                # Avoid false positives - check it's not a variable reference
                if not re.search(r'\$\{|\$\(|os\.getenv|environ\[', line):
                    issues.append((line_num, secret_type, line[:80]))
    
    return issues


def main() -> int:
    if len(sys.argv) < 2:
        return 0
    
    files = sys.argv[1:]
    found_secrets = False
    
    for file_path_str in files:
        file_path = Path(file_path_str)
        if not file_path.exists():
            continue
        
        issues = check_file(file_path)
        
        if issues:
            found_secrets = True
            print(f"\nPotential secrets in {file_path}:")
            for line_num, secret_type, line_preview in issues:
                print(f"  Line {line_num}: {secret_type}")
                print(f"    {line_preview}...")
    
    if found_secrets:
        print("\nERROR: Potential secrets detected in staged files!")
        print("Review the files above and remove any credentials before committing.")
        print("If these are false positives, use 'git commit --no-verify' to bypass.")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
