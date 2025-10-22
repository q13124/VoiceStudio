# workers/ops/engine_dispatch.py
# Usage: python engine_dispatch.py --text "Hello" --dst C:\out.wav --lang en --opts '{"stability":0.6}'
import argparse, json, os, sys, subprocess, time

def call_worker(engine:str, text:str, dst:str, opts:dict):
    py = os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"), "VoiceStudio","pyenv","Scripts","python.exe")
    wr = os.path.join(os.environ.get("ProgramData", r"C:\ProgramData"), "VoiceStudio","workers","worker_router.py")
    args = [py, wr, "tts", "--a", text, "--b", dst, "--c", json.dumps({**opts, "engine": engine})]
    p = subprocess.run(args, capture_output=True, text=True)
    ok = (p.returncode==0) and os.path.exists(dst)
    return ok, p.stdout + "\n" + p.stderr

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--dst", required=True)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--chain", default="")
    ap.add_argument("--opts", default="{}")
    args = ap.parse_args()
    try:
        opts = json.loads(args.opts)
    except Exception:
        opts = {}
    # chain comes from service router (engine, fallback list)
    chain = [e.strip() for e in args.chain.split(",") if e.strip()]
    last_log=""
    for eng in chain:
        ok, log = call_worker(eng, args.text, args.dst, opts)
        last_log += f"\n[{eng}] -> {ok}\n{log}"
        if ok:
            print(json.dumps({"ok": True, "engine": eng, "dst": args.dst}))
            return 0
    print(json.dumps({"ok": False, "error": "all_engines_failed", "log": last_log}))
    return 2

if __name__=="__main__":
    sys.exit(main())
