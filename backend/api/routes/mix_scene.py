from fastapi import APIRouter
from ..models_additional import SceneMixAnalyzeRequest

router = APIRouter(prefix="/api/mix/scene", tags=["mix", "scene"])

@router.post("/analyze")
def analyze(req: SceneMixAnalyzeRequest) -> dict:
    return {"graph": "ok"}

