from fastapi import FastAPI
from prometheus_client import (
    CollectorRegistry,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
from sqlalchemy import create_engine, text
import os

DB_URL = os.environ.get("DB_URL", "sqlite:///./app.db")
engine = create_engine(DB_URL, future=True)
app = FastAPI()


@app.get("/metrics")
def metrics():
    reg = CollectorRegistry()
    wr = Gauge(
        "voicestudio_wr",
        "Win rate by date and engine",
        ["engine", "date"],
        registry=reg,
    )
    clip = Gauge(
        "voicestudio_clip_rate",
        "Clip rate by date and engine",
        ["engine", "date"],
        registry=reg,
    )
    p50 = Gauge(
        "voicestudio_latency_p50_ms",
        "Latency p50 (ms)",
        ["engine", "date"],
        registry=reg,
    )
    p95 = Gauge(
        "voicestudio_latency_p95_ms",
        "Latency p95 (ms)",
        ["engine", "date"],
        registry=reg,
    )

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT date, engine, wr, clip_rate, latency_p50, latency_p95 FROM eval_runs"
            )
        )
        for d, engine_name, wr_v, clip_v, p50_v, p95_v in rows:
            ds = d.isoformat() if hasattr(d, "isoformat") else str(d)
            if wr_v is not None:
                wr.labels(engine_name, ds).set(float(wr_v))
            if clip_v is not None:
                clip.labels(engine_name, ds).set(float(clip_v))
            if p50_v is not None:
                p50.labels(engine_name, ds).set(float(p50_v))
            if p95_v is not None:
                p95.labels(engine_name, ds).set(float(p95_v))

    data = generate_latest(reg)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


from fastapi import Response
