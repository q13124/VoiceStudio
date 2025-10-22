"""
VoiceStudio — Realtime Add-On (WebSocket + Async Jobs)
"""

from __future__ import annotations
import asyncio, base64, json, time
from dataclasses import dataclass, field
from typing import Dict, Optional
from fastapi import APIRouter, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from services.api.voice_engine_router import app as base_app, ROUTER, CONFIG, TTSRequest

app: FastAPI = base_app
router = APIRouter()


class ConnectionManager:
    def __init__(self) -> None:
        self.active: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.add(ws)

    async def disconnect(self, ws: WebSocket) -> None:
        self.active.discard(ws)

    async def broadcast(self, message: dict) -> None:
        dead = []
        data = json.dumps(message)
        for ws in list(self.active):
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.active.discard(ws)


MANAGER = ConnectionManager()


@dataclass
class Job:
    id: str
    status: str = "queued"
    progress: float = 0.0
    engine: Optional[str] = None
    result_b64_wav: Optional[str] = None
    error: Optional[str] = None
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None


JOBS: Dict[str, Job] = {}


async def _run_tts_job(job: Job, req: TTSRequest) -> None:
    try:
        job.status = "running"
        await MANAGER.broadcast({"type": "job", "phase": "start", "id": job.id})

        engine_id, tried = ROUTER.select_engine(
            text=req.text, language=req.language, tier=req.quality
        )
        job.engine = engine_id
        await MANAGER.broadcast(
            {
                "type": "job",
                "phase": "select",
                "id": job.id,
                "engine": engine_id,
                "tried": tried,
            }
        )

        for p in (0.2, 0.45, 0.7):
            await asyncio.sleep(0.25)
            job.progress = p
            await MANAGER.broadcast(
                {"type": "job", "phase": "progress", "id": job.id, "progress": p}
            )

        audio = ROUTER.generate(
            engine_id=engine_id,
            text=req.text,
            voice_profile=req.voice_profile,
            params=req.params,
        )
        job.result_b64_wav = base64.b64encode(audio).decode("ascii")
        job.progress = 1.0
        job.status = "done"
        job.finished_at = time.time()
        await MANAGER.broadcast(
            {
                "type": "job",
                "phase": "done",
                "id": job.id,
                "engine": engine_id,
                "progress": 1.0,
            }
        )
    except Exception as e:
        job.status = "error"
        job.error = str(e)
        job.finished_at = time.time()
        await MANAGER.broadcast(
            {"type": "job", "phase": "error", "id": job.id, "error": job.error}
        )


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await MANAGER.connect(ws)
    try:
        await ws.send_text(
            json.dumps({"type": "hello", "router": "VoiceStudio", "version": "1.0.0"})
        )
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await MANAGER.disconnect(ws)


@router.post("/tts_async")
async def tts_async(req: TTSRequest):
    job_id = f"job_{abs(hash(json.dumps(req.dict())))%10_000_000}"
    job = Job(id=job_id)
    JOBS[job_id] = job
    asyncio.create_task(_run_tts_job(job, req))
    return {"job_id": job_id}


@router.get("/jobs/{job_id}")
async def job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return {
        "id": job.id,
        "status": job.status,
        "progress": job.progress,
        "engine": job.engine,
        "result_b64_wav": job.result_b64_wav,
        "error": job.error,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
    }


app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=CONFIG.host, port=CONFIG.port, log_level="info")
