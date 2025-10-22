from fastapi import FastAPI
from app.core.api.ws_stream import router as ws_router

app = FastAPI()
app.include_router(ws_router, prefix="/v1")
