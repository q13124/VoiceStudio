from pydantic import Field
from app.core.models.base import StrictModel

class ABRating(StrictModel):
    itemId: str = Field(min_length=1)
    score: float = Field(ge=0, le=5)
    winner: bool | None = None

class ABSummaryRequest(StrictModel):
    sessionId: str = Field(min_length=1)
    ratings: list[ABRating]

class EngineStats(StrictModel):
    engine: str
    wins: int
    win_rate: float = Field(ge=0, le=1)
    mean_score: float | None = None
    median_lufs: float | None = None
    clip_hit_rate: float | None = Field(default=None, ge=0, le=1)

class ABSummaryResponse(StrictModel):
    engines: list[EngineStats]
