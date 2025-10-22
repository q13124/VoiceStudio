from fastapi import FastAPI
from services.api import tts_router
from app.web.api_ab import router as ab_router
from app.web.api_health import router as health_router
from app.web.api_evals import router as evals_router
from app.core.observability.prometheus import setup_prometheus

app = FastAPI(
    title="VoiceStudio API",
    version="1.0.0",
    openapi_version="3.1.0",  # ensure 3.1
)

# Routes
app.include_router(tts_router.router)
app.include_router(ab_router)  # A/B testing endpoints
app.include_router(health_router)  # Health metrics endpoint
app.include_router(evals_router)  # Evaluation ingest endpoint

# Observability (additive)
setup_prometheus(app)
