"""
VoiceStudio — Router Effects Integration (Enhanced TTS endpoints)

Adds endpoints that apply a post-processing chain to generated audio.
  • POST /tts_enhanced (sync)
  • POST /tts_async_enhanced (async)

Pass `params.post_chain` as a list of effect names, e.g. ["lufs", "de_ess"].
"""
from __future__ import annotations
import base64
import io
import json
from typing import List, Optional

import numpy as np
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import soundfile as sf

from workers.ops.voice_engine_router import app as base_app, ROUTER, CONFIG, TTSRequest
from services.effects.post_processing import apply_chain
from services.router_realtime import JOBS, Job, MANAGER, _run_tts_job  # reuse job infra

app = base_app
router = APIRouter()


def _wav_bytes_to_np(b: bytes) -> tuple[np.ndarray, int]:
    data, sr = sf.read(io.BytesIO(b), dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    return data.astype(np.float32), int(sr)


def _np_to_wav_bytes(x: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, x, sr, format="WAV", subtype="PCM_16")
    return buf.getvalue()


@router.post("/tts_enhanced")
async def tts_enhanced(req: TTSRequest):
    engine_id, tried = ROUTER.select_engine(text=req.text, language=req.language, tier=req.quality)
    raw = ROUTER.generate(engine_id=engine_id, text=req.text, voice_profile=req.voice_profile, params=req.params)
    wav, sr = _wav_bytes_to_np(raw)
    chain: List[str] = req.params.get("post_chain", []) if isinstance(req.params, dict) else []
    if chain:
        wav = apply_chain(wav, sr, chain)
    out = _np_to_wav_bytes(wav, sr)
    return {
        "engine": engine_id,
        "tried_order": tried,
        "result_b64_wav": base64.b64encode(out).decode("ascii"),
    }


@router.post("/tts_async_enhanced")
async def tts_async_enhanced(req: TTSRequest):
    # piggyback on existing JOB infra, but we run locally to apply chain
    job_id = f"job_{abs(hash(json.dumps(req.dict())))%10_000_000}_fx"
    job = Job(id=job_id)
    JOBS[job_id] = job

    async def _work():
        try:
            job.status = "running"
            await MANAGER.broadcast({"type": "job", "phase": "start", "id": job.id})
            engine_id, tried = ROUTER.select_engine(text=req.text, language=req.language, tier=req.quality)
            job.engine = engine_id
            await MANAGER.broadcast({"type": "job", "phase": "select", "id": job.id, "engine": engine_id, "tried": tried})
            raw = ROUTER.generate(engine_id=engine_id, text=req.text, voice_profile=req.voice_profile, params=req.params)
            wav, sr = _wav_bytes_to_np(raw)
            chain: List[str] = req.params.get("post_chain", []) if isinstance(req.params, dict) else []
            if chain:
                await MANAGER.broadcast({"type": "job", "phase": "progress", "id": job.id, "progress": 0.8})
                wav = apply_chain(wav, sr, chain)
            out = _np_to_wav_bytes(wav, sr)
            job.result_b64_wav = base64.b64encode(out).decode("ascii")
            job.status = "done"
            await MANAGER.broadcast({"type": "job", "phase": "done", "id": job.id, "engine": engine_id, "progress": 1.0})
        except Exception as e:
            job.status = "error"
            job.error = str(e)
            await MANAGER.broadcast({"type": "job", "phase": "error", "id": job.id, "error": job.error})

    import asyncio
    asyncio.create_task(_work())
    return {"job_id": job_id}


app.include_router(router)
