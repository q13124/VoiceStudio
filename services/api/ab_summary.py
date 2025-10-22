"""
A/B Test Summary Models and Endpoint for VoiceStudio Voice Engine Router
"""
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Optional
import statistics
from scipy import stats
import numpy as np

class ABRating(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    
    item_id: str = Field(..., description="Unique identifier for the rated item")
    score: float = Field(..., ge=1.0, le=5.0, description="Rating score (1-5)")
    winner: Optional[bool] = Field(default=None, description="Whether this item was selected as winner")

class ABSummaryRequest(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    
    ratings: List[ABRating] = Field(..., min_length=1, description="List of ratings to aggregate")
    test_id: Optional[str] = Field(default=None, description="Optional test identifier")

class EngineStats(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    
    engine: str = Field(..., description="Engine identifier")
    wins: int = Field(..., ge=0, description="Number of wins")
    total_ratings: int = Field(..., ge=0, description="Total number of ratings")
    win_rate: float = Field(..., ge=0.0, le=1.0, description="Win rate (wins/total)")
    mean_score: Optional[float] = Field(default=None, description="Mean rating score")
    median_score: Optional[float] = Field(default=None, description="Median rating score")
    median_lufs: Optional[float] = Field(default=None, description="Median LUFS value")
    clip_hit_rate: Optional[float] = Field(default=None, description="Rate of clips with clipping issues")
    score_ci_95: Optional[Dict[str, float]] = Field(default=None, description="95% confidence interval for scores")

class ABSummaryResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    
    test_id: Optional[str] = Field(default=None, description="Test identifier")
    total_ratings: int = Field(..., ge=0, description="Total number of ratings")
    engines: List[EngineStats] = Field(..., description="Per-engine statistics")
    overall_stats: Dict[str, float] = Field(default_factory=dict, description="Overall test statistics")

def calculate_confidence_interval(scores: List[float], confidence: float = 0.95) -> Optional[Dict[str, float]]:
    """Calculate confidence interval for scores"""
    if len(scores) < 2:
        return None
    
    try:
        mean = np.mean(scores)
        sem = stats.sem(scores)
        ci = stats.t.interval(confidence, len(scores) - 1, loc=mean, scale=sem)
        return {
            "lower": float(ci[0]),
            "upper": float(ci[1]),
            "mean": float(mean)
        }
    except Exception:
        return None

def aggregate_ab_ratings(ratings: List[ABRating], item_metrics: Optional[Dict[str, Dict]] = None) -> ABSummaryResponse:
    """
    Aggregate A/B test ratings and return per-engine statistics
    """
    # Group ratings by engine (assuming item_id contains engine info)
    engine_ratings: Dict[str, List[ABRating]] = {}
    engine_wins: Dict[str, int] = {}
    
    for rating in ratings:
        # Extract engine from item_id (assuming format like "engine_itemid")
        engine = rating.item_id.split('_')[0] if '_' in rating.item_id else "unknown"
        
        if engine not in engine_ratings:
            engine_ratings[engine] = []
            engine_wins[engine] = 0
        
        engine_ratings[engine].append(rating)
        
        if rating.winner:
            engine_wins[engine] += 1
    
    # Calculate per-engine statistics
    engine_stats = []
    for engine, engine_rating_list in engine_ratings.items():
        scores = [r.score for r in engine_rating_list]
        wins = engine_wins[engine]
        total = len(engine_rating_list)
        
        # Basic stats
        mean_score = statistics.mean(scores) if scores else None
        median_score = statistics.median(scores) if scores else None
        win_rate = wins / total if total > 0 else 0.0
        
        # Audio metrics (if available)
        median_lufs = None
        clip_hit_rate = None
        
        if item_metrics:
            engine_metrics = item_metrics.get(engine, {})
            lufs_values = [m.get('lufs') for m in engine_metrics.values() if m.get('lufs') is not None]
            clip_values = [m.get('clip_pct', 0) for m in engine_metrics.values()]
            
            if lufs_values:
                median_lufs = statistics.median(lufs_values)
            
            if clip_values:
                clip_hit_rate = sum(1 for c in clip_values if c > 0.1) / len(clip_values)
        
        # Confidence interval
        score_ci_95 = calculate_confidence_interval(scores)
        
        engine_stats.append(EngineStats(
            engine=engine,
            wins=wins,
            total_ratings=total,
            win_rate=win_rate,
            mean_score=mean_score,
            median_score=median_score,
            median_lufs=median_lufs,
            clip_hit_rate=clip_hit_rate,
            score_ci_95=score_ci_95
        ))
    
    # Overall statistics
    all_scores = [r.score for r in ratings]
    overall_stats = {
        "total_ratings": len(ratings),
        "mean_score": statistics.mean(all_scores) if all_scores else 0.0,
        "median_score": statistics.median(all_scores) if all_scores else 0.0,
        "total_wins": sum(engine_wins.values()),
        "win_rate": sum(engine_wins.values()) / len(ratings) if ratings else 0.0
    }
    
    return ABSummaryResponse(
        test_id=None,  # Could be extracted from request
        total_ratings=len(ratings),
        engines=engine_stats,
        overall_stats=overall_stats
    )
