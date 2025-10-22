from fastapi import APIRouter
from app.core.models.ab import ABSummaryRequest, ABSummaryResponse
from app.core.services.ab_summary import summarize_ratings

router = APIRouter()

@router.post("/v1/ab/summary", response_model=ABSummaryResponse)
def ab_summary(req: ABSummaryRequest) -> ABSummaryResponse:
    """
    Aggregate blind A/B ratings into per-engine stats.
    Additive endpoint; does not alter existing APIs.
    """
    engines = summarize_ratings(req.ratings)
    return ABSummaryResponse(sessionId=req.sessionId, engines=engines, total_items=sum(es.n_items for es in engines))
