from typing import Iterable
from sqlalchemy.orm import Session
from app.core.ab.models import AbSummaryRow
from app.core.models.ab import EngineStats

def persist_summary(sess: Session, session_id: str, rows: Iterable[EngineStats]) -> None:
    for r in rows:
        sess.add(AbSummaryRow(
            session_id=session_id,
            engine=r.engine,
            n_items=r.n_items,
            wins=r.wins,
            win_rate=r.win_rate,
            ci_low=r.win_rate_ci95_low,
            ci_high=r.win_rate_ci95_high,
            mean_score=r.mean_score,
            median_lufs=r.median_lufs,
            clip_hit_rate=r.clip_hit_rate,
        ))
    sess.commit()