from __future__ import annotations
from collections import defaultdict
from statistics import median
from typing import Iterable, Dict, List, Tuple
import math

from app.core.models.ab import ABRating, EngineStats

def _wilson_ci95(successes: int, trials: int) -> Tuple[float, float]:
    """95% Wilson score interval; returns (low, high)."""
    if trials <= 0:
        return (0.0, 0.0)
    z = 1.959963984540054  # 95%
    phat = successes / trials
    denom = 1 + z*z/trials
    center = (phat + z*z/(2*trials)) / denom
    radius = z * math.sqrt((phat*(1-phat) + z*z/(4*trials)) / trials) / denom
    low, high = max(0.0, center - radius), min(1.0, center + radius)
    return (low, high)

def summarize_ratings(ratings: Iterable[ABRating]) -> List[EngineStats]:
    buckets: Dict[str, Dict[str, list]] = defaultdict(lambda: {
        "scores": [],
        "lufs": [],
        "clips": [],
        "n": 0,
        "wins": 0,
    })

    for r in ratings:
        b = buckets[r.engine]
        b["n"] += 1
        if r.winner:
            b["wins"] += 1
        if r.score is not None:
            b["scores"].append(float(r.score))
        if r.metrics is not None:
            if r.metrics.lufs is not None:
                b["lufs"].append(float(r.metrics.lufs))
            if r.metrics.clip_pct is not None:
                # Treat >0% as a "clip hit"
                b["clips"].append(1.0 if r.metrics.clip_pct > 0.0 else 0.0)

    out: List[EngineStats] = []
    for engine, d in buckets.items():
        n = int(d["n"])
        wins = int(d["wins"])
        wr = wins / n if n else 0.0
        lo, hi = _wilson_ci95(wins, n) if n else (0.0, 0.0)

        mean_score = None
        if d["scores"]:
            mean_score = sum(d["scores"]) / len(d["scores"])

        med_lufs = None
        if d["lufs"]:
            med_lufs = median(d["lufs"])

        clip_hit_rate = None
        if d["clips"]:
            clip_hit_rate = sum(d["clips"]) / len(d["clips"])

        out.append(EngineStats(
            engine=engine,
            n_items=n,
            wins=wins,
            win_rate=wr,
            win_rate_ci95_low=lo,
            win_rate_ci95_high=hi,
            mean_score=mean_score,
            median_lufs=med_lufs,
            clip_hit_rate=clip_hit_rate,
        ))

    # Sort by win rate desc, then mean score desc
    out.sort(key=lambda x: (x.win_rate, x.mean_score or 0.0), reverse=True)
    return out
