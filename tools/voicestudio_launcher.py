#!/usr/bin/env python
# tools/voicestudio_launcher.py
"""
Single entry for dev/prod:
  python tools/voicestudio_launcher.py --mode dev
  python tools/voicestudio_launcher.py --mode prod --services assistant,orchestrator,engine
  python tools/voicestudio_launcher.py --health-check
"""
import argparse, subprocess, sys, os, json, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CFG = os.path.join(ROOT, "config", "voicestudio.config.json")
ENG = os.path.join(ROOT, "config", "engines.config.json")
DEP = os.path.join(ROOT, "config", "deployment.config.json")

def load(p):
    with open(p,"r",encoding="utf-8") as f: return json.load(f)

def health():
    # best-effort: ping service health endpoints (customize)
    import urllib.request
    urls = [
        "http://127.0.0.1:5188/health",
        "http://127.0.0.1:5188/engines",
    ]
    ok = True
    for u in urls:
        try:
            with urllib.request.urlopen(u, timeout=3) as r:
                if r.status!=200: ok=False
        except Exception:
            ok=False
    print("healthy" if ok else "unhealthy")
    return 0 if ok else 1

def start_dev(svcs):
    # Dev: start orchestrator & engine in-tree; UI manually via dotnet run if needed
    env = os.environ.copy()
    dep = load(DEP)
    port = dep.get("service_port", 5188)
    cmds=[]
    if "engine" in svcs:
        cmds.append([sys.executable, os.path.join(dep.get("programdata","C:/ProgramData/VoiceStudio"), "workers","worker_router.py"), "serve", f"--port={port}"])
    if "orchestrator" in svcs:
        cmds.append([sys.executable, os.path.join(ROOT,"tools","orchestrator_stub.py"), "--port", str(port+1)])
    procs = [subprocess.Popen(c) for c in cmds]
    try:
        for p in procs: p.wait()
    finally:
        for p in procs:
            if p.poll() is None: p.terminate()

def start_prod():
    # Prod: rely on installed Windows Service + UI
    print("Starting Windows Service (VoiceStudio.Engine)...")
    subprocess.run(["sc","start","VoiceStudio.Engine"], check=False)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dev","prod"], default="dev")
    ap.add_argument("--services", default="engine,orchestrator")
    ap.add_argument("--health-check", action="store_true")
    args = ap.parse_args()
    if args.health_check:
        sys.exit(health())
    if args.mode=="dev":
        svcs = [s.strip() for s in args.services.split(",") if s.strip()]
        return start_dev(svcs)
    else:
        return start_prod()

if __name__=="__main__":
    sys.exit(main())