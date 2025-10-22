from fastapi import APIRouter
from app.core.models.ab import ABSummaryRequest, ABSummaryResponse
from app.core.ab.summary import summarize_ratings
from services.settings import settings

# optional persistence
from app.core.db import SessionLocal, Base, engine
from app.core.ab.repo import persist_summary

Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.post("/v1/ab/summary", response_model=ABSummaryResponse)
def ab_summary(req: ABSummaryRequest) -> ABSummaryResponse:
    engines = summarize_ratings(req.ratings)
    if settings.ab_persist_enabled:
        with SessionLocal() as s:
            persist_summary(s, req.sessionId, engines)
    return ABSummaryResponse(
        sessionId=req.sessionId,
        engines=engines,
        total_items=sum(es.n_items for es in engines),
    )
