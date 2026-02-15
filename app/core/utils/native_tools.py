"""
Native tool discovery for VoiceStudio.

Centralizes deterministic lookup for external binaries (ffmpeg, etc.) so clean
machines don't depend on PATH hacks.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

ENV_FFMPEG_PATH = "VOICESTUDIO_FFMPEG_PATH"


def find_ffmpeg() -> str | None:
    """
    Locate ffmpeg executable deterministically.

    Search order:
    1) VOICESTUDIO_FFMPEG_PATH (explicit override)
    2) PATH (shutil.which)
    3) Common Windows install locations
    """
    env = os.getenv(ENV_FFMPEG_PATH)
    if env:
        p = Path(env)
        if p.exists():
            return str(p)

    which = shutil.which("ffmpeg")
    if which:
        return which

    # Windows common locations
    candidates = [
        Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
        Path(r"C:\Program Files\ffmpeg\bin\ffmpeg.exe"),
        Path(r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe"),
    ]

    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "ffmpeg" / "bin" / "ffmpeg.exe")

    for c in candidates:
        if c.exists():
            return str(c)

    return None

