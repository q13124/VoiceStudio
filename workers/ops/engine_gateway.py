# workers/ops/engine_gateway.py
# Persistent FastAPI gateway for engine dispatch at 127.0.0.1:59120

import os
import json
import uvicorn
import subprocess
import tempfile
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

# Configuration
PD = os.environ.get("ProgramData", r"C:\ProgramData")
PY = os.path.join(PD, "VoiceStudio", "pyenv", "Scripts", "python.exe")
WR = os.path.join(PD, "VoiceStudio", "workers", "worker_router.py")

# Fallback to current directory if ProgramData doesn't exist
if not os.path.exists(PY):
    PY = "python"
if not os.path.exists(WR):
    WR = os.path.join(os.path.dirname(__file__), "..", "worker_router.py")

class DispatchRequest(BaseModel):
    text: str
    dst: str
    opts: dict = {}
    chain: List[str] = []

app = FastAPI(title="VoiceStudio Engine Gateway", version="1.0.0")

def call_engine(engine: str, text: str, dst: str, opts: dict):
    """Call a specific engine via worker_router.py"""
    args = [
        PY, WR, "tts", 
        "--a", text, 
        "--b", dst, 
        "--c", json.dumps({**opts, "engine": engine})
    ]
    
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=300)
        ok = (p.returncode == 0 and os.path.exists(dst))
        log = f"stdout: {p.stdout}\nstderr: {p.stderr}"
        return ok, log
    except subprocess.TimeoutExpired:
        return False, "Engine call timed out"
    except Exception as e:
        return False, f"Engine call failed: {str(e)}"

@app.post("/dispatch")
def dispatch(request: DispatchRequest):
    """Dispatch voice cloning job to engine chain"""
    log = ""
    
    # Default engine chain if none provided
    engines = request.chain or ["xtts", "openvoice", "cosyvoice2", "coqui"]
    
    for engine in engines:
        tmp_dst = request.dst
        ok, engine_log = call_engine(engine, request.text, tmp_dst, request.opts)
        log += f"\n[{engine}] -> {ok}\n{engine_log}"
        
        if ok:
            return {
                "ok": True, 
                "engine": engine, 
                "dst": tmp_dst,
                "log": log
            }
    
    return {
        "ok": False, 
        "error": "all_engines_failed", 
        "log": log
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "engine_gateway"}

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "VoiceStudio Engine Gateway", "version": "1.0.0"}

def main():
    """Start the engine gateway server"""
    print("Starting VoiceStudio Engine Gateway on 127.0.0.1:59120")
    uvicorn.run(app, host="127.0.0.1", port=59120, log_level="warning")

if __name__ == "__main__":
    main()
