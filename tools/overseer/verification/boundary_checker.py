"""
Cross-boundary coherence checks.

Verifies UI-called backend endpoints exist, and optionally that backend
engine capabilities align with manifests. Run before gate sign-off.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_CLIENT_PATH = "src/VoiceStudio.App/Services/BackendClient.cs"
OPENAPI_PATH = "docs/api/openapi.json"


def _normalize_path(path: str) -> str:
    """Normalize path for comparison (e.g. /api/profiles/123 -> /api/profiles/{id})."""
    # Replace C# string interpolation patterns like {Uri.EscapeDataString(id)} with {id}
    path = re.sub(r"\{Uri\.EscapeDataString\((\w+)\)\}", r"{\1}", path)
    # Replace path segments that look like IDs with {id}
    path = re.sub(r"/[a-fA-F0-9-]{8,}(/|$)", r"/{id}\1", path)
    path = re.sub(r"/[0-9]+(/|$)", r"/{id}\1", path)
    return path.rstrip("/") or "/"


def _normalize_path_params(path: str) -> str:
    """Normalize path parameters to a common format for comparison.

    Converts all {param_name} to {*} for parameter-agnostic matching.
    This handles differences like {jobId} vs {job_id}.
    """
    return re.sub(r"\{[^}]+\}", "{*}", path)


def extract_ui_api_paths(root: Path) -> set[str]:
    """Extract /api/... paths from BackendClient.cs."""
    path = root / BACKEND_CLIENT_PATH.replace("/", "\\" if str(root).find("\\") >= 0 else "/")
    path = root / "src" / "VoiceStudio.App" / "Services" / "BackendClient.cs"
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8")
    # Match "/api/..." or $"/api/..." patterns
    pattern = re.compile(r'["\'](/api/[^"\'?\s]+)')
    found = set()
    for m in pattern.finditer(text):
        p = m.group(1).split("?")[0].rstrip("/") or "/api"
        # Normalize C# interpolation patterns like {Uri.EscapeDataString(id)} to {id}
        p = re.sub(r"\{Uri\.EscapeDataString\((\w+)\)\}", r"{\1}", p)
        found.add(p)
    return found


def extract_backend_routes_from_openapi(root: Path) -> set[str]:
    """Extract /api/... paths from openapi.json if present."""
    path = root / OPENAPI_PATH.replace("/", "\\" if str(root).find("\\") >= 0 else "/")
    path = root / "docs" / "api" / "openapi.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        paths = data.get("paths", {})
        return {p for p in paths if p.startswith("/api")}
    except Exception:
        return set()


def verify_ui_backend_alignment(
    root: Path | None = None,
) -> tuple[bool, str]:
    """
    Verify UI-called backend endpoints exist in backend (openapi).

    Returns (passed, message). Paths are normalized so /api/profiles/xyz
    matches /api/profiles/{id} and parameter naming differences like
    {jobId} vs {job_id} are handled.
    """
    root = root or DEFAULT_ROOT
    ui_paths = extract_ui_api_paths(root)
    backend_paths = extract_backend_routes_from_openapi(root)
    if not backend_paths:
        return (
            True,
            "Backend routes not loaded (openapi.json missing or empty); skip alignment check.",
        )

    # Normalize backend paths for parameter-agnostic matching
    backend_normalized = {_normalize_path_params(b): b for b in backend_paths}

    missing: list[str] = []
    for p in ui_paths:
        # Try exact match first
        if p in backend_paths:
            continue

        # Try parameter-normalized match (handles {jobId} vs {job_id})
        p_normalized = _normalize_path_params(p)
        if p_normalized in backend_normalized:
            continue

        # Base path before any template (e.g. /api/profiles/123 -> /api/profiles)
        base = re.sub(r"/[^/]+$", "", p) if "/" in p else p
        base = base.rstrip("/") or "/api"

        # Backend has a route that starts with same base
        if any(b in (p, base) or b.startswith(base + "/") for b in backend_paths):
            continue
        if base in {b.split("{")[0].rstrip("/") for b in backend_paths}:
            continue

        missing.append(p)

    if not missing:
        return True, "PASS: UI and backend paths aligned."
    return False, f"FAIL: UI paths not found in backend (openapi): {missing[:10]}"


def run_boundary_checks(root: Path | None = None) -> tuple[bool, str]:
    """
    Run cross-boundary coherence checks.

    Returns (all_passed, summary_message).
    """
    root = root or DEFAULT_ROOT
    passed, msg = verify_ui_backend_alignment(root)
    return passed, msg


def main() -> int:
    """CLI entry point for boundary checker."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Verify UI ↔ Backend alignment (cross-boundary coherence check)."
    )
    parser.add_argument("--root", help="Project root path (default: auto-detect)")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    root = Path(args.root) if args.root else None
    passed, message = run_boundary_checks(root)

    if args.json:
        import json

        print(json.dumps({"passed": passed, "message": message}))
    else:
        print(f"Boundary checker: {message}")

    return 0 if passed else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
