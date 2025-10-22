from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Dict, Any
import statistics

class ABRating(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    
    item_id: str = Field(description="Unique identifier for the audio item")
    score: float = Field(ge=1.0, le=5.0, description="Rating score from 1-5")
    winner: Optional[bool] = Field(default=None, description="True if this item won, False if lost, None if tie")

class ABSummaryRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    
    ratings: List[ABRating] = Field(min_length=1, description="List of ratings to aggregate")
    session_id: Optional[str] = Field(default=None, description="Optional session identifier")

class EngineStats(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    
    wins: int = Field(ge=0, description="Number of wins")
    losses: int = Field(ge=0, description="Number of losses")
    ties: int = Field(ge=0, description="Number of ties")
    mean_score: float = Field(ge=1.0, le=5.0, description="Mean rating score")
    median_lufs: Optional[float] = Field(default=None, description="Median LUFS value")
    clip_hit_rate: float = Field(ge=0.0, le=1.0, description="Percentage of items with clipping")
    score_ci_95: Dict[str, float] = Field(description="95% confidence interval for scores")

class ABSummaryResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    
    total_ratings: int = Field(ge=0, description="Total number of ratings processed")
    engine_stats: Dict[str, EngineStats] = Field(description="Statistics per engine")
    session_id: Optional[str] = Field(default=None, description="Session identifier if provided")
