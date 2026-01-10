"""
Model pre-flight checks and optional auto-downloads for core engines.

Ensures required checkpoints exist (or are pulled) under the configured model
root (`VOICESTUDIO_MODELS_PATH`, default: E:\\VoiceStudio\\models).

Engines covered:
- XTTS (Coqui/XTTS-v2 via HF)
- Piper (rhasspy/piper-voices, voice-specific .onnx + .json)
- Whisper.cpp (GGUF model)
- So-VITS-SVC (manual checkpoints/config)

All functions return a dict with:
    {
        "ok": bool,
        "paths": [list of touched/validated paths],
        "downloaded": bool,
        "message": str
    }

Raise HTTPException with actionable guidance when a required asset is missing
and auto-download is disabled or fails.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import HTTPException

try:
    from huggingface_hub import hf_hub_download, snapshot_download

    HAS_HF = True
except ImportError:
    HAS_HF = False
    hf_hub_download = snapshot_download = None

from backend.services.EngineConfigService import get_engine_config_service

logger = logging.getLogger(__name__)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _fail(detail: str, status_code: int = 503) -> HTTPException:
    return HTTPException(status_code=status_code, detail=detail)


def ensure_xtts(auto_download: bool = True) -> Dict[str, object]:
    """
    Ensure XTTS model assets exist (Coqui/XTTS-v2).
    """
    cfg = get_engine_config_service()
    engine_cfg = cfg.get_engine_config("xtts_v2")
    model_name = (
        engine_cfg.get("parameters", {}).get("model_name") or "coqui/XTTS-v2"
    )
    base_dir = Path(
        engine_cfg.get("model_paths", {}).get("base")
        or os.path.join(os.environ.get("VOICESTUDIO_MODELS_PATH", r"E:\VoiceStudio\models"), "xtts")
    )
    cache_dir = Path(
        engine_cfg.get("model_paths", {}).get("cache")
        or base_dir / "cache"
    )
    _ensure_dir(base_dir)
    _ensure_dir(cache_dir)

    downloaded = False
    paths: List[str] = []

    # Heuristic: XTTS expects model files inside base_dir; if empty, download.
    has_files = any(base_dir.rglob("*"))
    if not has_files:
        if not HAS_HF:
            raise _fail(
                "XTTS model missing and huggingface_hub not installed. Install: pip install huggingface_hub",
                status_code=503,
            )
        if not auto_download:
            raise _fail(
                f"XTTS model missing at {base_dir}. Enable auto-download or place the model manually.",
                status_code=424,
            )
        logger.info(f"XTTS preflight: downloading {model_name} into {base_dir}")
        snapshot_download(
            repo_id=model_name,
            local_dir=str(base_dir),
            local_dir_use_symlinks=False,
        )
        downloaded = True

    for f in base_dir.glob("**/*"):
        if f.is_file():
            paths.append(str(f))

    return {
        "ok": True,
        "paths": paths,
        "downloaded": downloaded,
        "message": f"XTTS ready at {base_dir}",
    }


def ensure_piper(auto_download: bool = True) -> Dict[str, object]:
    """
    Ensure Piper voice model (.onnx + .json) exists.
    """
    cfg = get_engine_config_service()
    engine_cfg = cfg.get_engine_config("piper")
    base_dir = Path(
        engine_cfg.get("model_paths", {}).get("base")
        or os.path.join(os.environ.get("VOICESTUDIO_MODELS_PATH", r"E:\VoiceStudio\models"), "piper")
    )
    voice = engine_cfg.get("parameters", {}).get("voice", "en_US-amy-medium")
    model_path = Path(
        engine_cfg.get("parameters", {}).get("model_path")
        or base_dir / f"{voice}.onnx"
    )
    config_path = model_path.with_suffix(model_path.suffix + ".json")
    _ensure_dir(base_dir)

    def _dl(file_rel: str) -> str:
        if not HAS_HF:
            raise _fail(
                "huggingface_hub required for Piper auto-download. Install: pip install huggingface_hub",
                status_code=503,
            )
        return hf_hub_download(
            repo_id="rhasspy/piper-voices",
            filename=file_rel,
            local_dir=str(base_dir),
            local_dir_use_symlinks=False,
        )

    downloaded = False
    if not model_path.exists():
        if not auto_download:
            raise _fail(
                f"Piper model missing at {model_path}. Place the voice or enable auto-download.",
                status_code=424,
            )
        logger.info(f"Piper preflight: downloading voice {voice} into {base_dir}")
        rel = f"en/en_US/amy/medium/{voice}.onnx"
        _dl(rel)
        downloaded = True

    if not config_path.exists():
        if not auto_download:
            raise _fail(
                f"Piper config missing at {config_path}. Place the .json or enable auto-download.",
                status_code=424,
            )
        rel_json = f"en/en_US/amy/medium/{voice}.onnx.json"
        _dl(rel_json)
        downloaded = True

    return {
        "ok": True,
        "paths": [str(model_path), str(config_path)],
        "downloaded": downloaded,
        "message": f"Piper voice ready: {voice}",
    }


def ensure_whisper_cpp(auto_download: bool = True) -> Dict[str, object]:
    """
    Ensure whisper.cpp GGUF model exists.
    """
    cfg = get_engine_config_service()
    engine_cfg = cfg.get_engine_config("whisper_cpp")
    model_path = Path(
        engine_cfg.get("parameters", {}).get("model_path")
        or os.path.join(
            os.environ.get("VOICESTUDIO_MODELS_PATH", r"E:\VoiceStudio\models"),
            "whisper",
            "whisper-medium.en.gguf",
        )
    )
    _ensure_dir(model_path.parent)

    downloaded = False
    if not model_path.exists():
        if not auto_download:
            raise _fail(
                f"Whisper.cpp model missing at {model_path}. Place the GGUF or enable auto-download.",
                status_code=424,
            )
        if not HAS_HF:
            raise _fail(
                "huggingface_hub required for Whisper.cpp auto-download. Install: pip install huggingface_hub",
                status_code=503,
            )
        logger.info(f"Whisper.cpp preflight: downloading GGUF to {model_path}")
        hf_hub_download(
            repo_id="TheBloke/whisper-medium.en-GGUF",
            filename="whisper-medium.en.gguf",
            local_dir=str(model_path.parent),
            local_dir_use_symlinks=False,
        )
        downloaded = True

    return {
        "ok": True,
        "paths": [str(model_path)],
        "downloaded": downloaded,
        "message": "Whisper.cpp model ready",
    }


def ensure_sovits(auto_download: bool = False) -> Dict[str, object]:
    """
    Validate So-VITS-SVC checkpoint + config (no auto-download; manual).
    """
    cfg = get_engine_config_service()
    engine_cfg = cfg.get_engine_config("gpt_sovits")
    model_path = Path(
        engine_cfg.get("parameters", {}).get("model_path")
        or os.path.join(
            os.environ.get("VOICESTUDIO_MODELS_PATH", r"E:\VoiceStudio\models"),
            "checkpoints",
            "MyVoiceProj",
            "model.pth",
        )
    )
    config_path = Path(
        engine_cfg.get("parameters", {}).get("config_path")
        or model_path.parent / "config.json"
    )

    missing: List[str] = []
    if not model_path.exists():
        missing.append(str(model_path))
    if not config_path.exists():
        missing.append(str(config_path))

    if missing:
        raise _fail(
            "So-VITS checkpoints/config missing. Place files here: "
            + "; ".join(missing),
            status_code=424,
        )

    return {
        "ok": True,
        "paths": [str(model_path), str(config_path)],
        "downloaded": False,
        "message": "So-VITS checkpoints present",
    }


def run_preflight(auto_download: bool = True) -> Dict[str, object]:
    """
    Run all pre-flight checks. Returns a summary dict.
    """
    results = {}
    checks = {
        "xtts_v2": ensure_xtts,
        "piper": ensure_piper,
        "whisper_cpp": ensure_whisper_cpp,
        "gpt_sovits": ensure_sovits,
    }

    for name, fn in checks.items():
        try:
            results[name] = fn(auto_download=auto_download)
        except HTTPException as exc:  # pass through as structured failure
            results[name] = {
                "ok": False,
                "downloaded": False,
                "message": str(exc.detail),
                "status_code": exc.status_code,
            }
        except Exception as e:
            results[name] = {
                "ok": False,
                "downloaded": False,
                "message": f"{type(e).__name__}: {e}",
                "status_code": 500,
            }

    return {"results": results}
