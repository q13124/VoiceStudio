"""Audio effect processor plugin template."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.plugins_api import Plugin, ProcessorMixin
from parameters import EffectParameters
from processor import process_samples

logger = logging.getLogger(__name__)


class ProcessRequest(BaseModel):
    samples: list[float] = Field(default_factory=list)
    sample_rate: int = Field(..., gt=0)
    options: dict[str, Any] = Field(default_factory=dict)


class ProcessResponse(BaseModel):
    samples: list[float]
    sample_rate: int
    frame_count: int


class {{CLASS_NAME}}ProcessorPlugin(Plugin, ProcessorMixin):
    """ProcessorPlugin contract implementation for audio effects."""

    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)
        self.router = APIRouter(
            prefix="/api/plugin/{{PLUGIN_NAME}}",
            tags=["{{PLUGIN_NAME}}", "audio", "processor"],
        )

    def register(self, app) -> None:
        """Register plugin routes with FastAPI."""
        self.router.post("/process", response_model=ProcessResponse)(self.process_endpoint)
        self.router.get("/health")(self.health_endpoint)
        app.include_router(self.router)

    async def process(
        self,
        audio_data: bytes,
        sample_rate: int,
        options: dict[str, Any],
    ) -> bytes:
        params = EffectParameters(**options)
        samples = np.frombuffer(audio_data, dtype=np.float32)
        processed = process_samples(samples, params)
        return processed.tobytes()

    async def process_endpoint(self, request: ProcessRequest) -> ProcessResponse:
        input_samples = np.asarray(request.samples, dtype=np.float32)
        output_bytes = await self.process(
            input_samples.tobytes(),
            request.sample_rate,
            request.options,
        )
        output_samples = np.frombuffer(output_bytes, dtype=np.float32)
        return ProcessResponse(
            samples=output_samples.tolist(),
            sample_rate=request.sample_rate,
            frame_count=len(output_samples),
        )

    async def health_endpoint(self) -> dict[str, str]:
        return {
            "status": "healthy" if self._initialized else "inactive",
            "plugin": self.metadata.name,
        }


def register(app, plugin_dir: Path):
    """Entry point used by the plugin loader."""
    try:
        plugin = {{CLASS_NAME}}ProcessorPlugin(plugin_dir)
        plugin.register(app)
        plugin.initialize()
        logger.info("%s: activated via register()", plugin.metadata.name)
        return plugin
    except Exception as e:
        logger.exception("Failed to register plugin %s: %s", plugin_dir.name, e)
        raise
