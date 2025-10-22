from __future__ import annotations
from typing import List
from pydantic import Field
from app.core.models.base import StrictModel
from app.core.models.audio import AudioMetrics

class ABRating(StrictModel):
    # Minimal payload from UI after a blind round
    itemId: str = Field(min_length=1, description="UI-local id for the candidate")
    engine: str = Field(min_length=1, description="Engine label (still blind to the user)")
    score: float | None = Field(default=None, ge=0.0, le=5.0, description="User rating (0..5), optional")
    winner: bool | None = Field(default=None, description="True if this item was picked as winner in this round")
    metrics: AudioMetrics | None = Field(default=None, description="Objective audio metrics returned with the item")

class ABSummaryRequest(StrictModel):
    sessionId: str = Field(min_length=1, description="Client session or run id")
    ratings: List[ABRating] = Field(min_length=1, description="Batch of ratings from one or more rounds")

class EngineStats(StrictModel):
    engine: str
    n_items: int = Field(ge=0)
    wins: int = Field(ge=0)
    win_rate: float = Field(ge=0.0, le=1.0)
    win_rate_ci95_low: float | None = Field(default=None, ge=0.0, le=1.0)
    win_rate_ci95_high: float | None = Field(default=None, ge=0.0, le=1.0)
    mean_score: float | None = None
    median_lufs: float | None = None
    clip_hit_rate: float | None = Field(default=None, ge=0.0, le=1.0)

class ABSummaryResponse(StrictModel):
    sessionId: str
    engines: List[EngineStats]
    total_items: int = Field(ge=1)
