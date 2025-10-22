"""
VoiceStudio — Router Extensions (Upload refs, Diagnostics, Output chain hook)
"""

from __future__ import annotations
import hashlib
from pathlib import Path
from fastapi import APIRouter, FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from services.voice_engine_router import app as base_app, ROUTER, CONFIG
from services.effects.effect_chain import ChainCfg, process_wav_bytes
import yaml

app: FastAPI = base_app
router = APIRouter()

_original_generate = ROUTER.generate


def _load_chain_cfg() -> ChainCfg:
    paths = [Path("config") / "voicestudio.yaml", Path("voicestudio.yaml")]
    data = {}
    for p in paths:
        if p.exists():
            try:
                data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                break
            except Exception:
                pass

    oc = (data.get("engines") or {}).get("output_chain", {})
    return ChainCfg(
        enabled=bool(oc.get("enabled", False)),
        target_lufs=oc.get("target_lufs"),
        deess=bool(oc.get("deess", False)),
        noise_reduction=bool(oc.get("noise_reduction", False)),
    )


_CHAIN_CFG = _load_chain_cfg()


def _generate_with_fx(
    *, engine_id: str, text: str, voice_profile: dict, params: dict
) -> bytes:
    wav = _original_generate(
        engine_id=engine_id, text=text, voice_profile=voice_profile, params=params
    )
    if _CHAIN_CFG.enabled:
        try:
            wav = process_wav_bytes(wav, _CHAIN_CFG)
        except Exception:
            pass
    return wav


ROUTER.generate = _generate_with_fx  # type: ignore


@router.post("/upload_ref")
async def upload_ref(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".wav", ".mp3", ".flac", ".m4a", ".ogg")):
        raise HTTPException(status_code=400, detail="unsupported file type")

    cache = Path(CONFIG.cache_dir)
    target = cache / "refs"
    target.mkdir(parents=True, exist_ok=True)

    data = await file.read()
    h = hashlib.sha1(data).hexdigest()[:16]
    name = f"ref_{h}.wav"
    path = target / name

    try:
        from pydub import AudioSegment
        from io import BytesIO

        seg = AudioSegment.from_file(BytesIO(data))
        seg.export(str(path), format="wav")
    except Exception:
        with open(path, "wb") as f:
            f.write(data)

    return {"token": name, "path": str(path)}


from services.diagnostics.bundle import make_bundle


@router.post("/diagnostics/bundle")
async def diagnostics_bundle():
    outdir = Path(CONFIG.cache_dir) / "diagnostics"
    outdir.mkdir(parents=True, exist_ok=True)
    fname = make_bundle(outdir)
    return {"file": fname}


@router.get("/diagnostics/download")
async def diagnostics_download(file: str):
    p = Path(CONFIG.cache_dir) / "diagnostics" / file
    if not p.exists():
        raise HTTPException(status_code=404, detail="not found")
    return FileResponse(str(p), media_type="application/zip", filename=p.name)


app.include_router(router)
