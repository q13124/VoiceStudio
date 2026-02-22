#!/usr/bin/env python3
r"""
Ensure engines ready: one-shot script to check engine model readiness.

Calls /api/engines/preflight and reports missing models in E:\VoiceStudio\models.

Usage:
    python -m backend.scripts.ensure_engines_ready [--base-url URL] [--auto-download]

Exit codes:
    0: All engines ready
    1: Missing models detected
    2: Backend not reachable
    3: Invalid response from backend
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print(
        "ERROR: requests not installed. Install with: pip install requests",
        file=sys.stderr,
    )
    sys.exit(2)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check engine model readiness via backend preflight endpoint"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Backend API base URL (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--auto-download",
        action="store_true",
        help="Enable auto-download of missing models (default: False)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (default: human-readable text)",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    preflight_url = f"{base_url}/api/engines/preflight"
    auto_download = "true" if args.auto_download else "false"

    try:
        response = requests.get(
            preflight_url,
            params={"auto_download": auto_download},
            timeout=30,
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(
            f"ERROR: Cannot connect to backend at {base_url}",
            file=sys.stderr,
        )
        print(
            "Make sure the backend is running: python -m uvicorn backend.api.main:app",
            file=sys.stderr,
        )
        return 2
    except requests.exceptions.Timeout:
        print(
            f"ERROR: Backend at {base_url} did not respond within 30 seconds",
            file=sys.stderr,
        )
        return 2
    except requests.exceptions.HTTPError as e:
        print(
            f"ERROR: Backend returned HTTP {e.response.status_code}: {e}",
            file=sys.stderr,
        )
        return 3
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        return 3

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON response from backend: {e}", file=sys.stderr)
        return 3

    if not isinstance(data, dict):
        print(f"ERROR: Expected dict response, got {type(data)}", file=sys.stderr)
        return 3

    # Parse preflight results
    all_ok = True
    missing_models: list[dict[str, Any]] = []
    ready_engines: list[str] = []

    # Expected structure: { "engines": { "engine_id": { "ok": bool, "message": str, ... } } }
    engines = data.get("engines", {})
    if not engines:
        # Fallback: check if data itself is a per-engine result
        if "ok" in data:
            engines = {"unknown": data}

    for engine_id, result in engines.items():
        if not isinstance(result, dict):
            continue

        ok = result.get("ok", False)
        message = result.get("message", "")
        paths = result.get("paths", [])
        downloaded = result.get("downloaded", False)

        if ok:
            ready_engines.append(engine_id)
        else:
            all_ok = False
            missing_models.append(
                {
                    "engine_id": engine_id,
                    "message": message,
                    "paths": paths,
                    "downloaded": downloaded,
                }
            )

    # Output results
    if args.json:
        output = {
            "all_ok": all_ok,
            "ready_engines": ready_engines,
            "missing_models": missing_models,
            "models_path": str(
                Path(os.environ.get("VOICESTUDIO_MODELS_PATH", r"E:\VoiceStudio\models"))
            ),
        }
        print(json.dumps(output, indent=2))
    else:
        models_path = Path(os.environ.get("VOICESTUDIO_MODELS_PATH", r"E:\VoiceStudio\models"))
        print(f"Engine readiness check (models path: {models_path})")
        print("=" * 70)

        if all_ok:
            print("✅ All engines ready")
            if ready_engines:
                print(f"Ready engines: {', '.join(ready_engines)}")
        else:
            print("❌ Missing models detected:")
            for model in missing_models:
                print(f"\n  Engine: {model['engine_id']}")
                print(f"  Status: {model['message']}")
                if model.get("paths"):
                    print(f"  Expected paths: {len(model['paths'])} files")
                    if len(model["paths"]) <= 3:
                        for p in model["paths"]:
                            print(f"    - {p}")
                    else:
                        for p in model["paths"][:3]:
                            print(f"    - {p}")
                        print(f"    ... and {len(model['paths']) - 3} more")

            print("\nTo download missing models:")
            print("  python -m backend.scripts.ensure_engines_ready --auto-download")

    return 0 if all_ok else 1


if __name__ == "__main__":
    import os

    sys.exit(main())
