from fastapi import APIRouter, HTTPException, Header
from app.core.models.evals import EvalIngestRequest, EvalIngestResponse
from services.settings import settings
from app.core.db import SessionLocal, Base, engine
from app.core.evals.repo import persist_ingest

Base.metadata.create_all(bind=engine)
router = APIRouter()

# Simple flag-gated + bearer token check for ingestion
@router.post("/v1/evals/ingest", response_model=EvalIngestResponse)
def evals_ingest(req: EvalIngestRequest, authorization: str | None = Header(default=None)) -> EvalIngestResponse:
    if not getattr(settings, "evals_ingest_enabled", False):
        raise HTTPException(status_code=404, detail="Ingest disabled")
    # Basic token check (replace with your auth)
    expected = getattr(settings, "evals_ingest_token", None)
    if expected:
        if not authorization or not authorization.lower().startswith("bearer ") or authorization.split(" ", 1)[1] != expected:
            raise HTTPException(status_code=401, detail="Unauthorized")

    with SessionLocal() as s:
        stored = persist_ingest(s, req.runId, req.date, req.perEngine)
    return EvalIngestResponse(accepted=True, stored=stored)