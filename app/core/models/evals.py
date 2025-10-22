from typing import Dict, Optional
from pydantic import Field
from app.core.models.base import StrictModel

class EngineIngest(StrictModel):
    wr: float = Field(ge=0.0, le=1.0, description="Win rate 0..1")
    latency_p50: float | None = Field(default=None, ge=0.0, description="Median latency ms")
    latency_p95: float | None = Field(default=None, ge=0.0, description="p95 latency ms")
    clip_rate: float | None = Field(default=None, ge=0.0, le=1.0)
    lufs_med: float | None = Field(default=None)

class EvalIngestRequest(StrictModel):
    runId: str = Field(min_length=1)
    date: str = Field(min_length=8, description="YYYY-MM-DD")
    perEngine: Dict[str, EngineIngest]

class EvalIngestResponse(StrictModel):
    accepted: bool
    stored: int