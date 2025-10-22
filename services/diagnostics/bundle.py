"""
VoiceStudio — Diagnostics Bundle

Collects config, environment, and logs into a ZIP file for support/debug.
Returns the file name (to be served via /diagnostics/download).
"""
from __future__ import annotations
import os
import platform
import subprocess
import sys
import time
from pathlib import Path
from typing import List
from zipfile import ZipFile, ZIP_DEFLATED

from services.voice_engine_router import CONFIG


def _safe_read(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except Exception:
        return b""


def make_bundle(outdir: Path) -> str:
    ts = time.strftime('%Y%m%d_%H%M%S')
    name = f"voicestudio_diag_{ts}.zip"
    outpath = outdir / name
    with ZipFile(outpath, 'w', ZIP_DEFLATED) as z:
        # System info
        info = [
            f"python: {sys.version}",
            f"platform: {platform.platform()}",
            f"executable: {sys.executable}",
            f"cwd: {os.getcwd()}",
        ]
        try:
            import torch  # type: ignore
            info.append(f"torch: {getattr(torch, '__version__', 'unknown')} cuda: {torch.cuda.is_available()}")
        except Exception:
            info.append("torch: not available")
        z.writestr('system.txt', "\n".join(info))

        # pip freeze (best effort)
        try:
            out = subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], timeout=30)
            z.writestr('pip_freeze.txt', out)
        except Exception:
            pass

        # Configs
        for p in [Path('config')/ 'voicestudio.yaml', Path('voicestudio.yaml')]:
            if p.exists():
                z.writestr(f'config/{p.name}', _safe_read(p))

        # Router health snapshot (if reachable locally)
        try:
            import requests  # type: ignore
            r = requests.get(f"http://{CONFIG.host}:{CONFIG.port}/health", timeout=3)
            z.writestr('health.json', r.content)
        except Exception:
            pass

        # AppData logs (best effort)
        appdata = os.path.expandvars(r"%APPDATA%\UltraClone\logs")
        p = Path(appdata)
        if p.exists():
            for log in p.glob('**/*'):
                if log.is_file() and log.stat().st_size < 5_000_000:
                    z.write(str(log), f"logs/{log.name}")

    return name
