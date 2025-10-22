"""
VoiceStudio — Quality/Eval Endpoints (Blind A/B + Ratings)

This module mounts a small set of endpoints on top of the existing router to run
**blind A/B tests with MOS-style ratings** and store results in a local SQLite DB.

Endpoints
---------
POST /abtest/blind
    Body: { text, language:"en", quality:"balanced", engines?: ["xtts",...], session_id?: str }
    Returns: { session_id, trial_id, clips: [{label:"A", b64}, {label:"B", b64}], shuffled: true }

POST /abtest/submit_rating
    Body: { session_id, trial_id, rating_a: 1-5, rating_b: 1-5, winner: "A"|"B"|"tie" }
    Returns: { ok: true }

GET  /abtest/summary
    Returns: { totals: {engine_id:{wins:int, losses:int, ties:int, mean_rating:float, n:int}}, updated_at }

Storage
-------
SQLite DB at <CONFIG.cache_dir>/ratings.db with two tables:
  trials(session_id, trial_id, engine_a, engine_b, text, language, quality, created_at)
  results(session_id, trial_id, rating_a, rating_b, winner, created_at)

Notes
-----
- Engines are selected using existing router selection or the provided candidate list.
- Audio is generated server-side; engine IDs are NOT revealed to the client.
- Summary aggregates per-engine wins/losses and average MOS.
"""
from __future__ import annotations

import base64
import hashlib
import os
import random
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel, Field

from services.voice_engine_router import app as base_app, ROUTER, CONFIG

DB_PATH = Path(CONFIG.cache_dir) / "ratings.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

router = APIRouter()
app: FastAPI = base_app

# ----------------------------- DB Helpers ------------------------------------
SCHEMA = """
BEGIN;
CREATE TABLE IF NOT EXISTS trials (
  session_id TEXT NOT NULL,
  trial_id   TEXT PRIMARY KEY,
  engine_a   TEXT NOT NULL,
  engine_b   TEXT NOT NULL,
  text       TEXT NOT NULL,
  language   TEXT NOT NULL,
  quality    TEXT NOT NULL,
  created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS results (
  session_id TEXT NOT NULL,
  trial_id   TEXT NOT NULL,
  rating_a   INTEGER NOT NULL,
  rating_b   INTEGER NOT NULL,
  winner     TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  FOREIGN KEY(trial_id) REFERENCES trials(trial_id)
);
COMMIT;
"""

def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

with _db() as c:
    c.executescript(SCHEMA)

# ------------------------------ Models ---------------------------------------
class BlindABRequest(BaseModel):
    text: str
    language: str = Field("en")
    quality: str = Field("balanced")
    engines: Optional[List[str]] = None
    session_id: Optional[str] = None

class BlindABResponse(BaseModel):
    session_id: str
    trial_id: str
    clips: List[Dict[str, str]]  # [{label: "A", b64: "..."}, {label: "B", b64: "..."}]
    shuffled: bool = True

class SubmitRatingRequest(BaseModel):
    session_id: str
    trial_id: str
    rating_a: int = Field(..., ge=1, le=5)
    rating_b: int = Field(..., ge=1, le=5)
    winner: str   = Field(..., regex="^(A|B|tie)$")

# ---------------------------- Core Logic -------------------------------------

def _pick_two_engines(candidates: Optional[List[str]], *, text: str, language: str, quality: str) -> Tuple[str, str]:
    if candidates:
        pool = [e for e in candidates if e in ROUTER.r.list()]
    else:
        # Use router ordering, take top-2
        _, order = ROUTER.select_engine(text=text, language=language, tier=quality)  # type: ignore
        pool = order
    if len(pool) < 2:
        # fill from fallback chain
        for e in ROUTER.fallback_chain():
            if e not in pool:
                pool.append(e)
            if len(pool) >= 2:
                break
    if len(pool) < 2:
        raise HTTPException(status_code=503, detail="Not enough engines available for A/B")
    return pool[0], pool[1]


def _b64(wav: bytes) -> str:
    return base64.b64encode(wav).decode("ascii")


def _new_session_id(existing: Optional[str]) -> str:
    return existing or f"sess_{int(time.time()*1000)}_{random.randint(1000,9999)}"


def _new_trial_id(session_id: str, text: str, engine_a: str, engine_b: str) -> str:
    raw = f"{session_id}|{text}|{engine_a}|{engine_b}|{time.time_ns()}".encode()
    return hashlib.sha1(raw).hexdigest()[:16]

# ----------------------------- Endpoints -------------------------------------
@router.post("/abtest/blind", response_model=BlindABResponse)
async def abtest_blind(req: BlindABRequest):
    engine1, engine2 = _pick_two_engines(req.engines, text=req.text, language=req.language, quality=req.quality)
    # randomize labels
    pairs = [("A", engine1), ("B", engine2)]
    random.shuffle(pairs)

    clips = []
    for label, engine_id in pairs:
        try:
            wav = ROUTER.generate(engine_id=engine_id, text=req.text, voice_profile={}, params={})
            clips.append({"label": label, "b64": _b64(wav)})
        except Exception:
            clips.append({"label": label, "b64": ""})

    session_id = _new_session_id(req.session_id)
    trial_id = _new_trial_id(session_id, req.text, engine1, engine2)

    with _db() as c:
        c.execute(
            "INSERT INTO trials(session_id, trial_id, engine_a, engine_b, text, language, quality, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (session_id, trial_id, engine1, engine2, req.text, req.language, req.quality, int(time.time())),
        )

    return BlindABResponse(session_id=session_id, trial_id=trial_id, clips=clips, shuffled=True)


@router.post("/abtest/submit_rating")
async def abtest_submit_rating(req: SubmitRatingRequest):
    with _db() as c:
        # ensure trial exists
        row = c.execute("SELECT trial_id FROM trials WHERE trial_id=? AND session_id=?", (req.trial_id, req.session_id)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="trial not found")
        c.execute(
            "INSERT INTO results(session_id, trial_id, rating_a, rating_b, winner, created_at) VALUES (?,?,?,?,?,?)",
            (req.session_id, req.trial_id, int(req.rating_a), int(req.rating_b), req.winner, int(time.time())),
        )
    return {"ok": True}


@router.get("/abtest/summary")
async def abtest_summary():
    # Aggregate per engine
    with _db() as c:
        trials = c.execute("SELECT trial_id, engine_a, engine_b FROM trials").fetchall()
        results = c.execute("SELECT trial_id, rating_a, rating_b, winner FROM results").fetchall()
    eng_stats: Dict[str, Dict[str, float]] = {}
    def _stat(e: str) -> Dict[str, float]:
        return eng_stats.setdefault(e, {"wins":0, "losses":0, "ties":0, "mos_sum":0.0, "n":0})
    tmap = {t[0]: (t[1], t[2]) for t in trials}
    for trial_id, ra, rb, winner in results:
        if trial_id not in tmap:
            continue
        ea, eb = tmap[trial_id]
        sa, sb = _stat(ea), _stat(eb)
        sa["mos_sum"] += float(ra); sa["n"] += 1
        sb["mos_sum"] += float(rb); sb["n"] += 1
        if winner == "A":
            sa["wins"] += 1; sb["losses"] += 1
        elif winner == "B":
            sb["wins"] += 1; sa["losses"] += 1
        else:
            sa["ties"] += 1; sb["ties"] += 1
    # build response
    out = {e: {"wins": int(s["wins"]), "losses": int(s["losses"]), "ties": int(s["ties"]),
               "mean_rating": (s["mos_sum"] / s["n"]) if s["n"] else None, "n": int(s["n"]) }
           for e, s in eng_stats.items()}
    return {"totals": out, "updated_at": int(time.time())}


# Mount into the app
app.include_router(router)

if __name__ == "__main__":
    # Quick manual run if needed
    import uvicorn
    uvicorn.run(app, host=CONFIG.host, port=CONFIG.port, log_level="info")
