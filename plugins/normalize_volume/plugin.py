"""Normalize volume plugin."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from fastapi import APIRouter
from processor import normalize_samples
from pydantic import BaseModel, Field

from app.core.plugins_api import Plugin

logger = logging.getLogger(__name__)


class NormalizeRequest(BaseModel):
    samples: list[float] = Field(default_factory=list)
    sample_rate: int = Field(..., gt=0)
    mode: str = Field(default="peak")
    target_lufs: float = Field(default=-23.0)


class NormalizeResponse(BaseModel):
    samples: list[float]
    sample_rate: int
    frame_count: int


class NormalizeVolumePlugin(Plugin):
    """Audio normalization plugin supporting peak mode.

    Exposes ``POST /process`` to normalize float32 sample arrays in-place
    and ``GET /health`` for liveness checks.
    """

    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)
        self.router = APIRouter(prefix="/api/plugin/normalize_volume", tags=["normalize_volume"])

    def register(self, app) -> None:
        self.router.post("/process", response_model=NormalizeResponse)(self.process_endpoint)
        self.router.get("/health")(self.health)
        app.include_router(self.router)

    def initialize(self) -> None:
        super().initialize()
        logger.info("%s initialized", self.name)

    def cleanup(self) -> None:
        super().cleanup()
        logger.info("%s cleaned up", self.name)

    async def process_endpoint(self, request: NormalizeRequest) -> NormalizeResponse:
        samples = np.asarray(request.samples, dtype=np.float32)
        processed = normalize_samples(samples, request.sample_rate, request.mode, request.target_lufs)
        return NormalizeResponse(
            samples=processed.tolist(),
            sample_rate=request.sample_rate,
            frame_count=len(processed),
        )

    async def health(self) -> dict[str, str]:
        return {"status": "healthy", "plugin": self.name}


def register(app, plugin_dir: Path):
    try:
        plugin = NormalizeVolumePlugin(plugin_dir)
        plugin.register(app)
        plugin.initialize()
        return plugin
    except Exception as e:
        logger.exception("Failed to register plugin %s: %s", plugin_dir.name, e)
        raise
