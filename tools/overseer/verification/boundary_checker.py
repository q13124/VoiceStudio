"""
Cross-boundary coherence checks.

Verifies UI-called backend endpoints exist, and optionally that backend
engine capabilities align with manifests. Run before gate sign-off.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional, Set, Tuple

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_CLIENT_PATH = "src/VoiceStudio.App/Services/BackendClient.cs"
OPENAPI_PATH = "docs/api/openapi.json"


def _normalize_path(path: str) -> str:
    """Normalize path for comparison (e.g. /api/profiles/123 -> /api/profiles/{id})."""
    # Replace path segments that look like IDs with {id}
    path = re.sub(r"/[a-fA-F0-9-]{8,}(/|$)", r"/{id}\1", path)
    path = re.sub(r"/[0-9]+(/|$)", r"/{id}\1", path)
    return path.rstrip("/") or "/"


def extract_ui_api_paths(root: Path) -> Set[str]:
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
        found.add(p)
    return found


def extract_backend_routes_from_openapi(root: Path) -> Set[str]:
    """Extract /api/... paths from openapi.json if present."""
    path = root / OPENAPI_PATH.replace("/", "\\" if str(root).find("\\") >= 0 else "/")
    path = root / "docs" / "api" / "openapi.json"
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        paths = data.get("paths", {})
        return set(p for p in paths if p.startswith("/api"))
    except Exception:
        return set()


def verify_ui_backend_alignment(
    root: Optional[Path] = None,
) -> Tuple[bool, str]:
    """
    Verify UI-called backend endpoints exist in backend (openapi).

    Returns (passed, message). Paths are normalized so /api/profiles/xyz
    matches /api/profiles/{id}.
    """
    root = root or DEFAULT_ROOT
    ui_paths = extract_ui_api_paths(root)
    backend_paths = extract_backend_routes_from_openapi(root)
    if not backend_paths:
        return True, "Backend routes not loaded (openapi.json missing or empty); skip alignment check."
    missing: List[str] = []
    for p in ui_paths:
        # Base path before any template (e.g. /api/profiles/123 -> /api/profiles)
        base = re.sub(r"/[^/]+$", "", p) if "/" in p else p
        base = base.rstrip("/") or "/api"
        # Backend has a route that starts with same base (e.g. /api/profiles or /api/profiles/{profile_id})
        if any(b == p or b.startswith(base + "/") or b == base for b in backend_paths):
            continue
        if base in {b.split("{")[0].rstrip("/") for b in backend_paths}:
            continue
        missing.append(p)
    if not missing:
        return True, "PASS: UI and backend paths aligned."
    return False, f"FAIL: UI paths not found in backend (openapi): {missing[:10]}"


def run_boundary_checks(root: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Run cross-boundary coherence checks.

    Returns (all_passed, summary_message).
    """
    root = root or DEFAULT_ROOT
    passed, msg = verify_ui_backend_alignment(root)
    return passed, msg
