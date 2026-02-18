"""Compressor plugin."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from fastapi import APIRouter
from processor import compress_samples
from pydantic import BaseModel, Field

from app.core.plugins_api import Plugin

logger = logging.getLogger(__name__)


class CompressorRequest(BaseModel):
    samples: list[float] = Field(default_factory=list)
    sample_rate: int = Field(..., gt=0)
    threshold_db: float = -20.0
    ratio: float = Field(default=4.0, gt=1.0)
    attack_ms: float = Field(default=10.0, gt=0.0)
    release_ms: float = Field(default=100.0, gt=0.0)
    knee_db: float = Field(default=6.0, ge=0.0)
    makeup_gain_db: float = 0.0


class CompressorResponse(BaseModel):
    samples: list[float]
    sample_rate: int
    frame_count: int


class CompressorPlugin(Plugin):
    """Dynamic range compressor plugin.

    Delegates DSP work to :func:`processor.compress_samples` and exposes
    ``POST /process`` and ``GET /health`` endpoints.
    """

    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)
        self.router = APIRouter(prefix="/api/plugin/compressor", tags=["compressor"])

    def register(self, app) -> None:
        self.router.post("/process", response_model=CompressorResponse)(self.process_endpoint)
        self.router.get("/health")(self.health)
        app.include_router(self.router)

    def initialize(self) -> None:
        super().initialize()
        logger.info("%s initialized", self.name)

    def cleanup(self) -> None:
        super().cleanup()
        logger.info("%s cleaned up", self.name)

    async def process_endpoint(self, request: CompressorRequest) -> CompressorResponse:
        samples = np.asarray(request.samples, dtype=np.float32)
        processed = compress_samples(
            samples=samples,
            sample_rate=request.sample_rate,
            threshold_db=request.threshold_db,
            ratio=request.ratio,
            attack_ms=request.attack_ms,
            release_ms=request.release_ms,
            knee_db=request.knee_db,
            makeup_gain_db=request.makeup_gain_db,
        )
        return CompressorResponse(
            samples=processed.tolist(),
            sample_rate=request.sample_rate,
            frame_count=len(processed),
        )

    async def health(self) -> dict[str, str]:
        return {"status": "healthy", "plugin": self.name}


def register(app, plugin_dir: Path):
    try:
        plugin = CompressorPlugin(plugin_dir)
        plugin.register(app)
        plugin.initialize()
        return plugin
    except Exception as e:
        logger.exception("Failed to register plugin %s: %s", plugin_dir.name, e)
        raise
