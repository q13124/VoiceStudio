from datetime import date as _date
from typing import Dict
from sqlalchemy.orm import Session
from app.core.evals.models import EvalRunRow
from app.core.models.evals import EngineIngest

def persist_ingest(sess: Session, run_id: str, date_str: str, per_engine: Dict[str, EngineIngest]) -> int:
    y, m, d = [int(x) for x in date_str.split("-")]
    dt = _date(y, m, d)
    n = 0
    for engine, e in per_engine.items():
        sess.add(EvalRunRow(
            run_id=run_id,
            date=dt,
            engine=engine,
            wr=e.wr,
            latency_p50=e.latency_p50,
            latency_p95=e.latency_p95,
            clip_rate=e.clip_rate,
            lufs_med=e.lufs_med,
        ))
        n += 1
    sess.commit()
    return n