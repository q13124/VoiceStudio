#!/usr/bin/env python3
import argparse, pathlib, subprocess, time, sys, json, shlex, os
from datetime import datetime, timezone

WHITELIST = {
    "make test-python",
    "make test-frontend",
    "make test-api",
    "make test-all",
    # add more safe commands/targets here as you grow
}

def parse_tasks(md: str):
    tasks, grab = [], False
    for line in md.splitlines():
        s = line.strip()
        if s.lower().startswith("### tasks"):
            grab = True; continue
        if grab:
            if s.startswith("#"): break
            if s.startswith("- "):
                cmd = s[2:].strip()
                if cmd: tasks.append(cmd)
    return tasks

def run_cmd(cmd: str):
    start = time.time()
    try:
        if cmd not in WHITELIST:
            return {"cmd": cmd, "rc": 0, "skipped": True, "dur_s": 0.0, "out": "[skip: not whitelisted]"}
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        out, _ = p.communicate()
        rc = p.returncode
        return {"cmd": cmd, "rc": rc, "skipped": False, "dur_s": round(time.time() - start, 3), "out": out[-15000:]}
    except Exception as e:
        return {"cmd": cmd, "rc": 1, "skipped": False, "dur_s": round(time.time() - start, 3), "out": f"ERROR: {e}"}

def git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="docs/CURSOR_INSTRUCTIONS.md")
    ap.add_argument("--interval", type=int, default=20)
    ap.add_argument("--report", default="docs/CURSOR_RUN_REPORT.json")
    ap.add_argument("--log", default="docs/CURSOR_LOG.md")
    ap.add_argument("--push", action="store_true", help="commit & push report/log")
    args = ap.parse_args()

    inst = pathlib.Path(args.file)
    last_mtime = None
    print(f"[agent] watching {inst} every {args.interval}s")
    while True:
        try:
            if inst.exists():
                mt = inst.stat().st_mtime
                if last_mtime is None or mt > last_mtime:
                    last_mtime = mt
                    content = inst.read_text(encoding="utf-8", errors="ignore")
                    tasks = parse_tasks(content)
                    if not tasks:
                        print("[agent] no tasks found")
                    results = [run_cmd(t) for t in tasks]
                    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
                    report = {"ts_utc": stamp, "results": results}
                    # write/append reports
                    pathlib.Path("docs").mkdir(parents=True, exist_ok=True)
                    pathlib.Path(args.report).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
                    with open(args.log, "a", encoding="utf-8") as f:
                        f.write(f"\n## {stamp}\n")
                        for r in results:
                            f.write(f"- {r['cmd']} → rc={r['rc']} dur={r['dur_s']}s {'(skipped)' if r['skipped'] else ''}\n")
                    print("[agent] wrote report & log")

                    if args.push:
                        os.environ.setdefault("GIT_AUTHOR_NAME", "VS Cursor Agent")
                        os.environ.setdefault("GIT_AUTHOR_EMAIL", "cursor-agent@users.noreply.github.com")
                        os.environ.setdefault("GIT_COMMITTER_NAME", "VS Cursor Agent")
                        os.environ.setdefault("GIT_COMMITTER_EMAIL", "cursor-agent@users.noreply.github.com")
                        # pull-rebase then push to minimize conflicts
                        try:
                            git("pull", "--rebase")
                        except Exception as e:
                            print(f"[agent] pull warning: {e}", file=sys.stderr)
                        subprocess.check_call(["git","add",args.report,args.log])
                        subprocess.check_call(["git","commit","-m",f"cursor: run report {stamp} [skip ci]"])
                        subprocess.check_call(["git","push"])
                        print("[agent] pushed report/log")
            else:
                print("[agent] instructions file missing; waiting…")
        except Exception as e:
            print(f"[agent] error: {e}", file=sys.stderr)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
