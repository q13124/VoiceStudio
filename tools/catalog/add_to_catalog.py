#!/usr/bin/env python3
"""
Add a validated plugin to the catalog.

Creates or updates the catalog entry for an approved plugin and
generates the necessary PR artifacts.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Catalog file location
CATALOG_DIR = Path(__file__).parent.parent.parent / "shared" / "catalog"
CATALOG_FILE = CATALOG_DIR / "plugins.json"


def load_catalog() -> Dict[str, Any]:
    """Load the current catalog."""
    if CATALOG_FILE.exists():
        return json.loads(CATALOG_FILE.read_text())
    
    # Return empty catalog structure
    return {
        "version": "1.0.0",
        "last_updated": "",
        "plugins": [],
    }


def save_catalog(catalog: Dict[str, Any]) -> None:
    """Save the catalog."""
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    
    catalog["last_updated"] = datetime.now(timezone.utc).isoformat()
    
    with open(CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
        f.write("\n")


def find_plugin_index(catalog: Dict[str, Any], plugin_id: str) -> Optional[int]:
    """Find the index of a plugin in the catalog."""
    for i, plugin in enumerate(catalog.get("plugins", [])):
        if plugin.get("id") == plugin_id:
            return i
    return None


def create_catalog_entry(
    submission: Dict[str, Any],
    manifest: Dict[str, Any],
    security_scan: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a catalog entry from submission data."""
    now = datetime.now(timezone.utc).isoformat()
    
    # Extract author info
    author = manifest.get("author", {})
    if isinstance(author, str):
        author_name = author
        author_email = submission.get("author_email", "")
    else:
        author_name = author.get("name", submission.get("author_name", ""))
        author_email = author.get("email", submission.get("author_email", ""))
    
    entry = {
        "id": manifest.get("id") or submission.get("plugin_id"),
        "name": manifest.get("name") or submission.get("plugin_name"),
        "version": manifest.get("version") or submission.get("version"),
        "description": manifest.get("description") or submission.get("description"),
        "plugin_type": manifest.get("plugin_type") or submission.get("plugin_type", "").lower(),
        "author": {
            "name": author_name,
            "email": author_email,
        },
        "license": manifest.get("license") or submission.get("license"),
        "category": manifest.get("catalog", {}).get("category") or submission.get("category"),
        "repository": manifest.get("repository") or submission.get("repository"),
        "homepage": manifest.get("homepage") or submission.get("homepage"),
        "package_url": submission.get("package_url"),
        "manifest_url": submission.get("manifest_url"),
        "permissions": manifest.get("permissions", submission.get("permissions", [])),
        "capabilities": manifest.get("capabilities", []),
        "min_voicestudio_version": manifest.get("min_voicestudio_version", "0.9.0"),
        "keywords": manifest.get("catalog", {}).get("keywords", []),
        "screenshots": manifest.get("catalog", {}).get("screenshots", []),
        "pricing": manifest.get("distribution", {}).get("pricing", "free"),
        "trust": {
            "verified": True,
            "security_scan_passed": security_scan.get("pass", False),
            "risk_score": security_scan.get("risk_score", 0),
            "last_scanned": now,
        },
        "statistics": {
            "downloads": 0,
            "rating": 0.0,
            "rating_count": 0,
        },
        "dates": {
            "created": now,
            "updated": now,
            "last_release": now,
        },
        "versions": [
            {
                "version": manifest.get("version") or submission.get("version"),
                "released": now,
                "package_url": submission.get("package_url"),
                "changelog": submission.get("changelog", ""),
            }
        ],
    }
    
    return entry


def update_catalog_entry(
    existing: Dict[str, Any],
    submission: Dict[str, Any],
    manifest: Dict[str, Any],
    security_scan: Dict[str, Any]
) -> Dict[str, Any]:
    """Update an existing catalog entry with new version."""
    now = datetime.now(timezone.utc).isoformat()
    new_version = manifest.get("version") or submission.get("version")
    
    # Update basic fields
    existing["version"] = new_version
    existing["description"] = manifest.get("description") or existing.get("description")
    existing["package_url"] = submission.get("package_url")
    existing["manifest_url"] = submission.get("manifest_url")
    existing["permissions"] = manifest.get("permissions", existing.get("permissions", []))
    existing["capabilities"] = manifest.get("capabilities", existing.get("capabilities", []))
    
    # Update optional fields if provided
    if manifest.get("min_voicestudio_version"):
        existing["min_voicestudio_version"] = manifest["min_voicestudio_version"]
    
    if manifest.get("catalog", {}).get("keywords"):
        existing["keywords"] = manifest["catalog"]["keywords"]
    
    if manifest.get("catalog", {}).get("screenshots"):
        existing["screenshots"] = manifest["catalog"]["screenshots"]
    
    # Update trust info
    existing["trust"]["security_scan_passed"] = security_scan.get("pass", False)
    existing["trust"]["risk_score"] = security_scan.get("risk_score", 0)
    existing["trust"]["last_scanned"] = now
    
    # Update dates
    existing["dates"]["updated"] = now
    existing["dates"]["last_release"] = now
    
    # Add new version to versions list
    version_entry = {
        "version": new_version,
        "released": now,
        "package_url": submission.get("package_url"),
        "changelog": submission.get("changelog", ""),
    }
    
    # Check if version already exists
    versions = existing.get("versions", [])
    version_exists = False
    for i, v in enumerate(versions):
        if v.get("version") == new_version:
            versions[i] = version_entry
            version_exists = True
            break
    
    if not version_exists:
        versions.insert(0, version_entry)  # Add to front
    
    existing["versions"] = versions[:10]  # Keep last 10 versions
    
    return existing


def generate_pr_body(
    submission: Dict[str, Any],
    manifest: Dict[str, Any],
    is_update: bool
) -> str:
    """Generate PR body for catalog update."""
    action = "Update" if is_update else "Add"
    plugin_id = manifest.get("id") or submission.get("plugin_id")
    version = manifest.get("version") or submission.get("version")
    
    body = f"""## {action} Plugin: {plugin_id} v{version}

### Plugin Details
- **Name**: {manifest.get("name") or submission.get("plugin_name")}
- **Version**: {version}
- **Type**: {manifest.get("plugin_type") or submission.get("plugin_type")}
- **Author**: {submission.get("author_name")}
- **License**: {manifest.get("license") or submission.get("license")}

### Description
{manifest.get("description") or submission.get("description")}

### Permissions
{chr(10).join(f"- {p}" for p in manifest.get("permissions", submission.get("permissions", []))) or "None"}

### Changelog
{submission.get("changelog", "No changelog provided")}

### Verification
- [x] Manifest validated
- [x] Security scan passed
- [x] Submission requirements met

### Source Issue
Closes #{os.environ.get("ISSUE_NUMBER", "N/A")}

---
*This PR was automatically generated by the plugin submission workflow.*
"""
    return body


def main():
    """Main entry point."""
    # Get input data
    submission_json = os.environ.get("SUBMISSION_DATA", "")
    validation_json = os.environ.get("VALIDATION_DATA", "")
    security_json = os.environ.get("SECURITY_DATA", "")
    
    # Try reading from files if not in env
    for var_name, env_var in [
        ("submission", "SUBMISSION_DATA"),
        ("validation", "VALIDATION_DATA"),
        ("security", "SECURITY_DATA"),
    ]:
        file_var = f"{env_var.replace('_DATA', '_FILE')}"
        file_path = os.environ.get(file_var, "")
        if not os.environ.get(env_var) and file_path and Path(file_path).exists():
            os.environ[env_var] = Path(file_path).read_text()
    
    # Reload from env after potential file reads
    submission_json = os.environ.get("SUBMISSION_DATA", "")
    validation_json = os.environ.get("VALIDATION_DATA", "")
    security_json = os.environ.get("SECURITY_DATA", "")
    
    if not all([submission_json, validation_json, security_json]):
        print("Error: Missing required input data", file=sys.stderr)
        print(f"  submission: {'present' if submission_json else 'missing'}", file=sys.stderr)
        print(f"  validation: {'present' if validation_json else 'missing'}", file=sys.stderr)
        print(f"  security: {'present' if security_json else 'missing'}", file=sys.stderr)
        sys.exit(1)
    
    try:
        submission = json.loads(submission_json)
        validation = json.loads(validation_json)
        security = json.loads(security_json)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Get manifest from validation data
    manifest = validation.get("manifest", {})
    if not manifest:
        print("Error: No manifest in validation data", file=sys.stderr)
        sys.exit(1)
    
    # Load current catalog
    catalog = load_catalog()
    
    # Check if plugin already exists
    plugin_id = manifest.get("id") or submission.get("plugin_id")
    existing_index = find_plugin_index(catalog, plugin_id)
    is_update = existing_index is not None
    
    # Create or update entry
    if is_update:
        existing = catalog["plugins"][existing_index]
        entry = update_catalog_entry(existing, submission, manifest, security)
        catalog["plugins"][existing_index] = entry
    else:
        entry = create_catalog_entry(submission, manifest, security)
        catalog["plugins"].append(entry)
    
    # Save catalog
    save_catalog(catalog)
    
    # Generate PR body
    pr_body = generate_pr_body(submission, manifest, is_update)
    
    # Output results
    result = {
        "success": True,
        "action": "update" if is_update else "add",
        "plugin_id": plugin_id,
        "version": manifest.get("version") or submission.get("version"),
        "catalog_path": str(CATALOG_FILE),
        "pr_body": pr_body,
    }
    
    print(json.dumps(result, indent=2))
    
    # Write PR body to file for GitHub Actions
    pr_body_file = os.environ.get("PR_BODY_FILE", "")
    if pr_body_file:
        Path(pr_body_file).write_text(pr_body)
    
    # Also output to GitHub Actions outputs if available
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"action={result['action']}\n")
            f.write(f"plugin_id={result['plugin_id']}\n")
            f.write(f"version={result['version']}\n")


if __name__ == "__main__":
    main()
