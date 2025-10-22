"""
VoiceStudio — Router Diagnostics Bundle

Adds an endpoint to produce a support bundle (ZIP) with sanitized environment info:
  • GET /diagnostics  → { filename, b64_zip }

Included:
  - config/voicestudio.yaml (if present)
  - /health JSON snapshot
  - python/pip pkg list (top libs)
  - torch/cuda availability, TTS version
  - basic system info

Sensitive data: we avoid dumping full env vars; only selected ones are included.
"""
from __future__ import annotations

import base64
import io
import json
import os
import platform
import subprocess
import sys
import zipfile
from pathlib import Path

from fastapi import APIRouter

from workers.ops.voice_engine_router import app as base_app, CONFIG, REGISTRY

app = base_app
router = APIRouter()


def _safe_pip_freeze() -> str:
    try:
        out = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True, timeout=20)
        # keep only top libs of interest
        keep = ["torch", "torchaudio", "TTS", "fastapi", "uvicorn", "pydantic", "soundfile", "numpy"]
        lines = [ln for ln in out.splitlines() if any(k.lower() in ln.lower() for k in keep)]
        return "\n".join(lines)
    except Exception as e:
        return f"pip freeze error: {e}"


def _torch_info():
    try:
        import torch
        return {
            "version": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        }
    except Exception as e:
        return {"error": str(e)}


def _tts_version():
    try:
        import TTS
        return getattr(TTS, "__version__", "unknown")
    except Exception as e:
        return f"{e}"


@router.get("/diagnostics")
async def diagnostics():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        # basics
        z.writestr("system.json", json.dumps({
            "python": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }, indent=2))
        z.writestr("torch.json", json.dumps(_torch_info(), indent=2))
        z.writestr("tts_version.txt", str(_tts_version()))
        z.writestr("pip_top.txt", _safe_pip_freeze())
        # config
        for p in [Path("config/voicestudio.yaml"), Path("voicestudio.yaml")]:
            if p.exists():
                try:
                    z.write(p, arcname=str(p))
                except Exception:
                    pass
        # health snapshot
        try:
            z.writestr("health.json", json.dumps(REGISTRY.discover(), indent=2))
        except Exception:
            pass
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    return {"filename": "voicestudio_diagnostics.zip", "b64_zip": data}


app.include_router(router)
