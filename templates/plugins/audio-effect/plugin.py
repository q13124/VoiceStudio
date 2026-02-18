"""Audio effect plugin."""

import logging
from pathlib import Path

import numpy as np
from fastapi import APIRouter

from app.core.plugins_api import Plugin
from models import ProcessAudioRequest, ProcessAudioResponse
from processing import apply_gain, normalize

logger = logging.getLogger(__name__)


class {{CLASS_NAME}}Plugin(Plugin):
    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)
        self.router = APIRouter(prefix="/api/plugin/{{PLUGIN_NAME}}", tags=["{{PLUGIN_NAME}}"])
    
    def register(self, app) -> None:
        self.router.post("/process")(self.process_audio)
        self.router.get("/health")(self.health)
        app.include_router(self.router)
        logger.info(f"{self.name}: Registered")
    
    def initialize(self) -> None:
        super().initialize()
        logger.info(f"{self.name}: Initialized")
    
    def cleanup(self) -> None:
        super().cleanup()
        logger.info(f"{self.name}: Cleaned up")
    
    async def process_audio(self, request: ProcessAudioRequest) -> ProcessAudioResponse:
        try:
            audio_array = np.array(request.samples, dtype=np.float32)
            processed = apply_gain(audio_array, request.gain_db)
            processed = normalize(processed)
            return ProcessAudioResponse(
                samples=processed.tolist(),
                sample_rate=request.sample_rate,
                duration_ms=len(processed) / request.sample_rate * 1000
            )
        except Exception as e:
            logger.error(f"Error processing audio: {e}", exc_info=True)
            raise
    
    async def health(self) -> dict:
        return {"status": "healthy", "plugin": self.name}

def register(app, plugin_dir: Path):
    """Plugin entry point called by the plugin loader."""
    try:
        plugin = {{CLASS_NAME}}Plugin(plugin_dir)
        plugin.register(app)
        plugin.initialize()
        return plugin
    except Exception as e:
        logger.exception("Failed to register plugin %s: %s", plugin_dir.name, e)
        raise
