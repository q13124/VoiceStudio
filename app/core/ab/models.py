from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.core.db import Base

class AbSummaryRow(Base):
    __tablename__ = "ab_summary"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    engine = Column(String(128), index=True, nullable=False)
    n_items = Column(Integer, nullable=False)
    wins = Column(Integer, nullable=False)
    win_rate = Column(Float, nullable=False)
    ci_low = Column(Float, nullable=True)
    ci_high = Column(Float, nullable=True)
    mean_score = Column(Float, nullable=True)
    median_lufs = Column(Float, nullable=True)
    clip_hit_rate = Column(Float, nullable=True)
    created_utc = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)