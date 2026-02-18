"""Reverb plugin."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
from fastapi import APIRouter
from processor import apply_reverb
from pydantic import BaseModel, Field

from app.core.plugins_api import Plugin

logger = logging.getLogger(__name__)


class ReverbRequest(BaseModel):
    samples: list[float] = Field(default_factory=list)
    sample_rate: int = Field(..., gt=0)
    room_size: float = Field(default=0.5, ge=0.0, le=1.0)
    damping: float = Field(default=0.5, ge=0.0, le=1.0)
    wet_dry_mix: float = Field(default=1.0, ge=0.0, le=1.0)
    pre_delay_ms: float = Field(default=20.0, ge=0.0, le=500.0)
    stereo_width: float = Field(default=1.0, ge=0.0, le=1.0)
    decay_time: float = Field(default=2.0, ge=0.1, le=10.0)


class ReverbResponse(BaseModel):
    samples: list[float]
    sample_rate: int
    frame_count: int


class ReverbPlugin(Plugin):
    """Algorithmic reverb plugin.

    Delegates DSP work to :func:`processor.apply_reverb` and exposes
    ``POST /process`` and ``GET /health`` endpoints.
    """

    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)
        self.router = APIRouter(prefix="/api/plugin/reverb", tags=["reverb"])

    def register(self, app) -> None:
        self.router.post("/process", response_model=ReverbResponse)(self.process_endpoint)
        self.router.get("/health")(self.health)
        app.include_router(self.router)

    def initialize(self) -> None:
        super().initialize()
        logger.info("%s initialized", self.name)

    def cleanup(self) -> None:
        super().cleanup()
        logger.info("%s cleaned up", self.name)

    async def process_endpoint(self, request: ReverbRequest) -> ReverbResponse:
        samples = np.asarray(request.samples, dtype=np.float32)
        processed = apply_reverb(
            samples=samples,
            sample_rate=request.sample_rate,
            room_size=request.room_size,
            damping=request.damping,
            wet_dry_mix=request.wet_dry_mix,
            pre_delay_ms=request.pre_delay_ms,
            stereo_width=request.stereo_width,
            decay_time=request.decay_time,
        )
        return ReverbResponse(
            samples=processed.tolist(),
            sample_rate=request.sample_rate,
            frame_count=len(processed),
        )

    async def health(self) -> dict[str, str]:
        return {"status": "healthy", "plugin": self.name}


def register(app, plugin_dir: Path):
    try:
        plugin = ReverbPlugin(plugin_dir)
        plugin.register(app)
        plugin.initialize()
        return plugin
    except Exception as e:
        logger.exception("Failed to register plugin %s: %s", plugin_dir.name, e)
        raise
