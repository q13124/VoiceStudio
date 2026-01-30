"""
Automated verification agent loop.

When a task is marked complete, run verification (gate, ledger, optional build).
If FAIL, use reflexion_loop to build a reflection prompt and retry (caller re-invokes
agent and calls again). After max_retries (default 3), escalate to Overseer.
Integrates with closure-protocol Step 0 (invoke Skeptical Validator).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

from .reflexion_loop import ReflexionResult, build_reflection_prompt, run_verification_step

DEFAULT_VERIFICATION_SCRIPT = "scripts/run_verification.py"
LAST_RUN_JSON = ".buildlogs/verification/last_run.json"


def _project_root() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root


def run_verification_step_impl(
    root: Optional[Path] = None,
    build: bool = False,
) -> Tuple[bool, str]:
    """
    Run the verification script and return (passed, diagnosis).

    Runs scripts/run_verification.py (gate, ledger, optional build),
    then reads .buildlogs/verification/last_run.json for result.
    """
    root = root or _project_root()
    script = root / DEFAULT_VERIFICATION_SCRIPT.replace("/", "\\" if sys.platform == "win32" else "/")
    script = root / "scripts" / "run_verification.py"
    if not script.exists():
        return False, "Verification script not found: scripts/run_verification.py"
    cmd = [sys.executable, str(script)]
    if build:
        cmd.append("--build")
    cmd.append("--json-only")
    try:
        r = subprocess.run(
            cmd,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return False, "Verification timed out."
    except Exception as e:
        return False, f"Verification failed to run: {e}"
    path_last = root / LAST_RUN_JSON.replace("/", "\\" if sys.platform == "win32" else "/")
    path_last = root / ".buildlogs" / "verification" / "last_run.json"
    if not path_last.exists():
        return False, (r.stderr or r.stdout or "last_run.json not written")
    try:
        report = json.loads(path_last.read_text(encoding="utf-8"))
        all_passed = report.get("all_passed", False)
        checks = report.get("checks", [])
        if all_passed:
            return True, "All checks passed."
        failed = [c for c in checks if not c.get("passed", True)]
        diagnosis = "; ".join(
            f"{c.get('name', '?')} failed (exit {c.get('exit_code', -1)})"
            for c in failed[:5]
        )
        return False, diagnosis or "One or more checks failed."
    except Exception as e:
        return False, f"Failed to parse last_run.json: {e}"


def run_auto_verify(
    root: Optional[Path] = None,
    build: bool = False,
    attempt: int = 1,
    max_retries: int = 3,
) -> ReflexionResult:
    """
    Run one verification step and return a ReflexionResult.

    Caller can use result.reflection_prompt(max_retries) to re-prompt the agent,
    then call again with attempt+1 until result.passed or result.should_escalate(max_retries).
    """
    def verify_fn() -> Tuple[bool, str]:
        return run_verification_step_impl(root=root, build=build)
    return run_verification_step(verify_fn, attempt=attempt)
