#!/usr/bin/env python3
"""
Parse plugin submission from GitHub issue body.

Extracts structured data from the issue template format and outputs
JSON for use by subsequent workflow steps.
"""

import json
import os
import re
import sys
from typing import Any, Dict, List, Optional


def parse_markdown_field(body: str, label: str) -> Optional[str]:
    """Extract a field value from the issue body."""
    # GitHub issue templates use ### Field Name format
    pattern = rf"### {re.escape(label)}\s*\n+(.+?)(?=\n### |\n## |\Z)"
    match = re.search(pattern, body, re.DOTALL)
    if match:
        value = match.group(1).strip()
        # Handle "No response" or "_No response_" placeholder
        if value.lower() in ("no response", "_no response_", "n/a", "_n/a_"):
            return None
        return value
    return None


def parse_checkbox_field(body: str, label: str) -> List[str]:
    """Extract checked items from a checkbox field."""
    section = parse_markdown_field(body, label)
    if not section:
        return []
    
    checked = []
    for line in section.split("\n"):
        # Match [x] or [X] checkbox items
        match = re.match(r"^\s*-\s*\[x\]\s*(.+)$", line, re.IGNORECASE)
        if match:
            checked.append(match.group(1).strip())
    return checked


def parse_list_field(body: str, label: str) -> List[str]:
    """Extract list items from a field."""
    section = parse_markdown_field(body, label)
    if not section:
        return []
    
    items = []
    for line in section.split("\n"):
        # Match list items starting with - or *
        match = re.match(r"^\s*[-*]\s*(.+)$", line)
        if match:
            items.append(match.group(1).strip())
    return items


def parse_submission(issue_body: str) -> Dict[str, Any]:
    """Parse a plugin submission from issue body."""
    submission = {
        "plugin_id": parse_markdown_field(issue_body, "Plugin ID"),
        "plugin_name": parse_markdown_field(issue_body, "Plugin Name"),
        "version": parse_markdown_field(issue_body, "Version"),
        "plugin_type": parse_markdown_field(issue_body, "Plugin Type"),
        "description": parse_markdown_field(issue_body, "Description"),
        "repository": parse_markdown_field(issue_body, "Source Repository"),
        "package_url": parse_markdown_field(issue_body, "Package URL"),
        "manifest_url": parse_markdown_field(issue_body, "Manifest URL"),
        "category": parse_markdown_field(issue_body, "Category"),
        "author_name": parse_markdown_field(issue_body, "Author Name"),
        "author_email": parse_markdown_field(issue_body, "Author Email"),
        "homepage": parse_markdown_field(issue_body, "Homepage"),
        "license": parse_markdown_field(issue_body, "License"),
        "permissions": parse_list_field(issue_body, "Required Permissions"),
        "privacy_policy": parse_markdown_field(issue_body, "Privacy Policy URL"),
        "changelog": parse_markdown_field(issue_body, "Changelog"),
        "additional_notes": parse_markdown_field(issue_body, "Additional Notes"),
    }
    
    # Parse checkbox fields
    requirements_checked = parse_checkbox_field(issue_body, "Submission Requirements")
    submission["requirements_met"] = {
        "validation_passed": any("validate" in r.lower() for r in requirements_checked),
        "package_signed": any("signed" in r.lower() for r in requirements_checked),
        "guidelines_agreed": any("guidelines" in r.lower() for r in requirements_checked),
        "no_malware": any("malware" in r.lower() for r in requirements_checked),
        "distribution_rights": any("right to distribute" in r.lower() for r in requirements_checked),
    }
    
    privacy_checked = parse_checkbox_field(issue_body, "Privacy Declaration")
    submission["collects_data"] = any("collects user data" in p.lower() for p in privacy_checked)
    
    return submission


def validate_required_fields(submission: Dict[str, Any]) -> List[str]:
    """Validate that required fields are present."""
    errors = []
    
    required_fields = [
        ("plugin_id", "Plugin ID"),
        ("plugin_name", "Plugin Name"),
        ("version", "Version"),
        ("plugin_type", "Plugin Type"),
        ("description", "Description"),
        ("repository", "Source Repository"),
        ("package_url", "Package URL"),
        ("manifest_url", "Manifest URL"),
        ("category", "Category"),
        ("author_name", "Author Name"),
        ("author_email", "Author Email"),
        ("license", "License"),
    ]
    
    for field_key, field_name in required_fields:
        if not submission.get(field_key):
            errors.append(f"Missing required field: {field_name}")
    
    # Validate plugin ID format
    plugin_id = submission.get("plugin_id", "")
    if plugin_id and not re.match(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)*(\.[a-z][a-z0-9-]*)?$", plugin_id, re.IGNORECASE):
        errors.append(f"Invalid plugin ID format: {plugin_id}. Use reverse domain notation (e.g., com.company.plugin)")
    
    # Validate version format
    version = submission.get("version", "")
    if version and not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$", version):
        errors.append(f"Invalid version format: {version}. Use semantic versioning (e.g., 1.0.0)")
    
    # Validate URLs
    url_fields = ["repository", "package_url", "manifest_url"]
    for field in url_fields:
        url = submission.get(field, "")
        if url and not url.startswith(("http://", "https://")):
            errors.append(f"Invalid URL in {field}: {url}")
    
    # Validate package URL ends with .vspkg
    package_url = submission.get("package_url", "")
    if package_url and not package_url.endswith(".vspkg"):
        errors.append("Package URL must end with .vspkg")
    
    # Validate email format
    email = submission.get("author_email", "")
    if email and not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        errors.append(f"Invalid email format: {email}")
    
    # Validate requirements checkboxes
    requirements = submission.get("requirements_met", {})
    if not all(requirements.values()):
        missing = [k for k, v in requirements.items() if not v]
        errors.append(f"Missing required confirmations: {', '.join(missing)}")
    
    # Validate privacy policy if collecting data
    if submission.get("collects_data") and not submission.get("privacy_policy"):
        errors.append("Privacy Policy URL is required when collecting user data")
    
    return errors


def main():
    """Main entry point."""
    # Get issue body from environment or stdin
    issue_body = os.environ.get("ISSUE_BODY", "")
    
    if not issue_body:
        # Try reading from stdin
        if not sys.stdin.isatty():
            issue_body = sys.stdin.read()
    
    if not issue_body:
        print("Error: No issue body provided", file=sys.stderr)
        sys.exit(1)
    
    # Parse submission
    submission = parse_submission(issue_body)
    
    # Validate required fields
    errors = validate_required_fields(submission)
    
    # Add validation results
    submission["validation"] = {
        "is_valid": len(errors) == 0,
        "errors": errors,
    }
    
    # Output JSON
    print(json.dumps(submission, indent=2))
    
    # Exit with error if validation failed
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
