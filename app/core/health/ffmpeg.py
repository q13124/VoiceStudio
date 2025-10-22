"""
FFmpeg binary detection and version probing for health checks
"""

from __future__ import annotations
import subprocess
import shutil
from dataclasses import dataclass


@dataclass
class BinInfo:
    present: bool
    version: str | None


def _probe_version(cmd: str) -> str | None:
    """Probe version string from a binary command"""
    try:
        p = subprocess.run([cmd, "-version"], capture_output=True, text=True, timeout=5)
        if p.returncode == 0 and p.stdout:
            return p.stdout.splitlines()[0].strip()
    except Exception:
        pass
    return None


def ffmpeg_info(explicit: str | None = None) -> BinInfo:
    """Get FFmpeg binary info"""
    path = explicit or shutil.which("ffmpeg")
    if not path:
        return BinInfo(present=False, version=None)
    return BinInfo(present=True, version=_probe_version(path))


def ffprobe_info(explicit: str | None = None) -> BinInfo:
    """Get FFprobe binary info"""
    path = explicit or shutil.which("ffprobe")
    if not path:
        return BinInfo(present=False, version=None)
    return BinInfo(present=True, version=_probe_version(path))
