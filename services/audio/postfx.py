from __future__ import annotations
from pathlib import Path
import shutil, subprocess, tempfile
from dataclasses import dataclass

from app.core.models.output_chain import OutputChain
from app.core.settings import settings

def _which(cmd: str) -> str | None:
    return shutil.which(cmd)

def _ffmpeg_bin() -> str | None:
    return settings.ffmpeg_path or _which("ffmpeg")

@dataclass
class PostFxResult:
    used_ffmpeg: bool
    out_path: Path

def apply_postfx_to_wav(
    wav_path: Path,
    chain: OutputChain | None,
) -> PostFxResult:
    """
    Applies trim/fade/dither in order. If chain is None or all disabled, returns original file.
    Prefers ffmpeg; if not found, returns original (no-op).
    """
    if not chain or (chain.trim_ms == 0 and chain.fade_ms == 0 and not chain.dither):
        return PostFxResult(False, wav_path)

    ffmpeg = _ffmpeg_bin()
    if not ffmpeg:
        # No ffmpeg installed — by design, silently keep original (minor-safe)
        return PostFxResult(False, wav_path)

    # Build filter chain
    filters: list[str] = []
    # 1) Trim leading/trailing silence by fixed ms on both sides (simple fade/trim approach)
    # We can't "magically" detect silence here; we apply hard fades/cuts by duration the user requests.
    # For "remove actual detected silence", use metrics step instead; here we honor the configured fixed window.

    # Hard trim: use atrim to cut head/tail by duration; we need duration. Probe with ffprobe.
    # If probing fails, we skip trim.
    trim_ms = max(0, int(chain.trim_ms or 0))
    fade_ms = max(0, int(chain.fade_ms or 0))
    dither = bool(chain.dither)

    tmp_out = Path(tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name)

    # Probe duration
    ffprobe = settings.ffprobe_path or _which("ffprobe")
    dur_sec = None
    if trim_ms > 0 and ffprobe:
        try:
            out = subprocess.run(
                f'"{ffprobe}" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{wav_path}"',
                shell=True, capture_output=True, text=True, timeout=10
            )
            dur_sec = float(out.stdout.strip())
        except Exception:
            dur_sec = None

    # atrim
    if trim_ms > 0 and dur_sec and dur_sec * 1000 > (2 * trim_ms):
        start = trim_ms / 1000.0
        end = max(0.0, dur_sec - (trim_ms / 1000.0))
        filters.append(f"atrim=start={start:.3f}:end={end:.3f},asetpts=N/SR/TB")

    # fades
    if fade_ms > 0 and dur_sec and dur_sec * 1000 > (2 * fade_ms):
        fi = fade_ms / 1000.0
        fo = fade_ms / 1000.0
        # fade in at t=0 for fi seconds; fade out ending at duration for fo seconds
        filters.append(f"afade=t=in:st=0:d={fi:.3f}")
        filters.append(f"afade=t=out:st={max(0.0, dur_sec - fo):.3f}:d={fo:.3f}")

    # dither (TPDF)
    if dither:
        # Use aformat to set sample format and apply tpdf_dither
        filters.append("aformat=s16:channel_layout=stereo,dither=tpdf")

    # Join filters
    filter_arg = ",".join(filters) if filters else "anull"

    cmd = f'"{ffmpeg}" -hide_banner -nostats -y -i "{wav_path}" -af "{filter_arg}" -c:a pcm_s16le "{tmp_out}"'
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if proc.returncode != 0 or not tmp_out.exists() or tmp_out.stat().st_size == 0:
        # Failed: keep original to remain safe
        try:
            if tmp_out.exists():
                tmp_out.unlink(missing_ok=True)
        except Exception:
            pass
        return PostFxResult(False, wav_path)

    return PostFxResult(True, tmp_out)
