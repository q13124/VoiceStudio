#!/usr/bin/env python3
import argparse, json, os, pathlib, re, subprocess, sys, time
from datetime import datetime, timezone

# ===== Heuristic mapping: changed files -> commands =====
RULES = [
    # Backend Python changes → run fast unit tests, then API smoke
    (re.compile(r"^(app/|workers/|services/|common/).*\.(py)$"), ["make test-python", "make test-api"]),
    # Pydantic/OpenAPI/models → also run schema checks (if you have a target)
    (re.compile(r"^(app/core/models|app/web/api_|app/core/settings|openapi\.ya?ml|schemas?/).*"), ["make test-python", "make test-api"]),
    # Alembic/migrations → upgrade + smoke
    (re.compile(r"^(alembic/|migrations?/).*"), ["make db-upgrade", "make test-api"]),
    # Frontend changes → FE tests/build then API smoke
    (re.compile(r"^(web/frontend/|web/.*\.(tsx?|jsx?|css|json|lock))"), ["make test-frontend", "make test-api"]),
    # Ops/exporter/agent → build exporter and agent sanity
    (re.compile(r"^(ops/sqlite_metrics_exporter/|ops/agent/|docker-compose\..*|ops/grafana/|ops/alerts/)"), ["make exporter-build", "make exporter-logs"]),
    # Only docs/ci tweaks → cheap API smoke
    (re.compile(r"^(\.github/workflows/|docs/|README\.md)"), ["make test-api"]),
]

# Allowed commands (safety)
WHITELIST = {
    "make test-python",
    "make test-frontend",
    "make test-api",
    "make test-all",
    "make db-upgrade",
    "make exporter-build",
    "make exporter-logs",
}

STATE_DIR = pathlib.Path(".cursor_state")
STATE_DIR.mkdir(exist_ok=True)
LAST_COMMIT_FILE = STATE_DIR / "last_processed_commit.txt"
REPORT_FILE = pathlib.Path("docs/CURSOR_RUN_REPORT.json")
LOG_FILE = pathlib.Path("docs/CURSOR_LOG.md")

def sh(cmd, check=True, text=True):
    return subprocess.run(cmd, shell=True, check=check, text=True, capture_output=True)

def git(*args, check=True):
    return subprocess.run(["git", *args], check=check, text=True, capture_output=True)

def determine_changed_files(since_ref: str | None) -> list[str]:
    if since_ref:
        r = git("diff", "--name-only", f"{since_ref}..HEAD")
    else:
        r = git("show", "--name-only", "--pretty=", "HEAD")
    files = [f.strip() for f in r.stdout.splitlines() if f.strip()]
    return files

def choose_commands(files: list[str]) -> list[str]:
    # Collapse by first matching rule group, dedupe, order by appearance
    chosen = []
    matched_any = False
    for f in files:
        for pat, cmds in RULES:
            if pat.search(f):
                matched_any = True
                for c in cmds:
                    if c in WHITELIST and c not in chosen:
                        chosen.append(c)
                break
    if not matched_any:
        # Default to a cheap sanity smoke
        chosen = ["make test-api"]
    return chosen

def run_cmd(cmd: str) -> dict:
    start = time.time()
    if cmd not in WHITELIST:
        return {"cmd": cmd, "rc": 0, "skipped": True, "dur_s": 0.0, "out": "[skip: not whitelisted]"}
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out, _ = p.communicate()
    rc = p.returncode
    return {"cmd": cmd, "rc": rc, "skipped": False, "dur_s": round(time.time() - start, 3), "out": out[-15000:]}

def write_report(results: list[dict]):
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    report = {"ts_utc": stamp, "results": results}
    REPORT_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n## {stamp}\n")
        for r in results:
            f.write(f"- {r['cmd']} → rc={r['rc']} dur={r['dur_s']}s {'(skipped)' if r['skipped'] else ''}\n")

def maybe_push(report_only: bool):
    # Push the report/log; skip if user doesn't want commits from agent
    git("add", str(REPORT_FILE), str(LOG_FILE), check=False)
    subprocess.run(["git", "commit", "-m", "cursor: run report [skip ci]"], text=True)
    subprocess.run(["git", "push"], text=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=60, help="seconds between checks")
    ap.add_argument("--push", action="store_true", help="commit & push report/log")
    args = ap.parse_args()

    print("[agent] starting (no new workflows). watching repo changes every", args.interval, "s")
    while True:
        try:
            # Stay in sync with origin
            git("pull", "--rebase", check=False)
            cur_head = git("rev-parse", "HEAD").stdout.strip()
            prev = LAST_COMMIT_FILE.read_text().strip() if LAST_COMMIT_FILE.exists() else None
            if prev == cur_head:
                time.sleep(args.interval)
                continue

            changed = determine_changed_files(prev)
            cmds = choose_commands(changed)
            print("[agent] head changed; files:", len(changed), "→ cmds:", cmds)

            results = []
            for c in cmds:
                results.append(run_cmd(c))

            # If everything passed (no nonzero rc among non-skipped), run full test suite last
            non_skipped = [r for r in results if not r["skipped"]]
            all_passed = (len(non_skipped) > 0) and all(r["rc"] == 0 for r in non_skipped)
            if all_passed and "make test-all" in WHITELIST and "make test-all" not in cmds:
                tail = run_cmd("make test-all")
                results.append(tail)

            write_report(results)
            LAST_COMMIT_FILE.write_text(cur_head)

            if args.push:
                os.environ.setdefault("GIT_AUTHOR_NAME", "VS Cursor Agent")
                os.environ.setdefault("GIT_AUTHOR_EMAIL", "cursor-agent@users.noreply.github.com")
                os.environ.setdefault("GIT_COMMITTER_NAME", "VS Cursor Agent")
                os.environ.setdefault("GIT_COMMITTER_EMAIL", "cursor-agent@users.noreply.github.com")
                # One best-effort push
                maybe_push(report_only=True)

            # Print a quick summary to the terminal
            worst = max((r["rc"] for r in results if not r["skipped"]), default=0)
            print(f"[agent] done. worst_rc={worst}. waiting…")
        except Exception as e:
            print("[agent] error:", e, file=sys.stderr)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
