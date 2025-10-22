"""
VoiceStudio — Router Uploads (reference WAV ingestion)

Provides a simple endpoint to upload reference WAVs and store them on the server,
so web clients can supply speaker references without filesystem access.

  • POST /upload_ref  (multipart/form-data, field "file") → { id, path }

Files are stored under CONFIG.cache_dir / "refs". The response includes the server-side
path that can be passed as voice_profile.speaker_wavs to the TTS endpoints.
"""
from __future__ import annotations
import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from workers.ops.voice_engine_router import app as base_app, CONFIG

app = base_app
router = APIRouter()


@router.post("/upload_ref")
async def upload_ref(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".wav", ".flac", ".mp3", ".m4a")):
        raise HTTPException(status_code=400, detail="unsupported file type")
    ref_dir = Path(CONFIG.cache_dir) / "refs"
    ref_dir.mkdir(parents=True, exist_ok=True)
    rid = uuid4().hex[:12]
    ext = os.path.splitext(file.filename)[1]
    out = ref_dir / f"ref_{rid}{ext}"
    data = await file.read()
    out.write_bytes(data)
    return {"id": rid, "path": str(out)}


app.include_router(router)
