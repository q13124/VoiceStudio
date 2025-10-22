
from __future__ import annotations
import os, socket, subprocess
from typing import Dict, Any
from services.telemetry.metrics import metrics

def _run(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT).strip()
    except Exception as e:
        return f"ERR: {e}"

def collect_signals() -> Dict[str, Any]:
    # Best-effort signals that match the notification template
    def _safe(cmd: str, default: str = "") -> str:
        out = _run(cmd)
        return default if out.startswith("ERR:") else out
    branch = _safe("git branch --show-current", "unknown")
    commits = _safe('git log --since=\"24 hours ago\" --pretty=%h', "")
    commits_24h = 0 if commits == "" else len(commits.splitlines())
    changes_out = _safe("git status -s", "")
    changes_count = 0 if changes_out == "" else len(changes_out.splitlines())
    netstat = _safe("netstat -ano | findstr LISTENING | findstr :5071", "")
    port_5071 = "LISTENING" if netstat else "closed"
    tasks = _safe("tasklist", "")
    cloudflared = "running" if ("cloudflared" in tasks) else "stopped"
    gpu = _safe('nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader -L', "unavailable")
    return dict(branch=branch, commits_24h=commits_24h, changes_count=changes_count, port_5071_status=port_5071, cloudflared_status=cloudflared, gpu=gpu)

def emit_report() -> Dict[str, Any]:
    sig = collect_signals()
    m = metrics.snapshot()
    return {
        "alignment_summary": "OK (baseline skeleton)",
        "phase": os.environ.get("VS_PHASE", "Bootstrap"),
        "last_milestone": os.environ.get("VS_LAST_MILESTONE", "Skeleton created"),
        "next_step_1": "Connect CI logs",
        "next_step_2": "Verify schema migrations",
        "next_step_3": "Run golden-set eval",
        "drift": "low",
        "drift_fix": "n/a",
        "cursor_actions": "n/a",
        "cursor_diffs": "n/a",
        **sig,
        "build_status": "unknown",
        "pipelines_summary": "idle",
        "action_1": "Connect CI logs",
        "action_2": "Verify schema migrations",
        "action_3": "Run golden-set eval",
        "escalation_tier": 2,
        "config_ok": True,
        "metrics": m,
        "host": socket.gethostname(),
    }
