from sqlalchemy import Column, Integer, String, Float, Date
from app.core.db import Base

class EvalRunRow(Base):
    __tablename__ = "eval_runs"
    id = Column(Integer, primary_key=True)
    run_id = Column(String(255), index=True, nullable=False)
    date = Column(Date, nullable=False)
    engine = Column(String(128), index=True, nullable=False)
    wr = Column(Float, nullable=False)
    latency_p50 = Column(Float, nullable=True)
    latency_p95 = Column(Float, nullable=True)
    clip_rate = Column(Float, nullable=True)
    lufs_med = Column(Float, nullable=True)