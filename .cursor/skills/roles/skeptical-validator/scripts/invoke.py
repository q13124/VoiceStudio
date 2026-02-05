#!/usr/bin/env python3
"""Role skill wrapper - invokes context allocator then onboarding CLI for Skeptical Validator."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[5]
ROLE_ID = "skeptical_validator"
ROLE_PROFILE = "validator"


def _ensure_utf8_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def main() -> int:
    """Run context allocate (--role profile) then onboarding; print combined output."""
    _ensure_utf8_stdout()
    parts = []
    r = subprocess.run(
        [sys.executable, "-m", "tools.context.cli.allocate", "--role", ROLE_PROFILE, "--preamble"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r.returncode == 0 and r.stdout:
        parts.append(r.stdout.strip())
    r2 = subprocess.run(
        [sys.executable, "-m", "tools.onboarding.cli.onboard", "--role", ROLE_ID],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r2.returncode != 0:
        sys.stderr.write(r2.stderr or "")
        return r2.returncode
    if r2.stdout:
        parts.append(r2.stdout.strip())
    if parts:
        print("\n\n".join(parts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
