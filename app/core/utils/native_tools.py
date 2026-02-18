"""
Native tool discovery for VoiceStudio.

Centralizes deterministic lookup for external binaries (ffmpeg, etc.) so clean
machines don't depend on PATH hacks.

GAP-PY-002: Delegates to backend.config.path_config when available.
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
    1) backend.config.path_config.get_ffmpeg_path() (GAP-PY-002)
    2) VOICESTUDIO_FFMPEG_PATH (explicit override)
    3) PATH (shutil.which)
    4) Common Windows install locations
    """
    # GAP-PY-002: Try centralized path_config first
    try:
        from backend.config.path_config import get_ffmpeg_path
        return str(get_ffmpeg_path())
    except (ImportError, RuntimeError):
        pass  # Fall through to legacy lookup

    env = os.getenv(ENV_FFMPEG_PATH)
    if env:
        p = Path(env)
        if p.exists():
            return str(p)

    which = shutil.which("ffmpeg")
    if which:
        return which

    # Windows common locations (fallback with env var expansion)
    candidates = [
        Path(os.getenv("PROGRAMDATA", "C:\\ProgramData")) / "VoiceStudio" / "bin" / "ffmpeg.exe",
        Path(os.getenv("PROGRAMFILES", "C:\\Program Files")) / "ffmpeg" / "bin" / "ffmpeg.exe",
        Path(os.getenv("PROGRAMFILES(X86)", "C:\\Program Files (x86)")) / "ffmpeg" / "bin" / "ffmpeg.exe",
    ]

    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        candidates.append(Path(local_app_data) / "ffmpeg" / "bin" / "ffmpeg.exe")
        candidates.append(Path(local_app_data) / "Programs" / "ffmpeg" / "bin" / "ffmpeg.exe")

    for c in candidates:
        if c.exists():
            return str(c)

    return None

