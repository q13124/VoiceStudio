"""Full-stack {{DISPLAY_NAME}} Plugin - Backend"""

import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.plugins_api import Plugin

logger = logging.getLogger(__name__)


class ProcessRequest(BaseModel):
    data: str


class StatusResponse(BaseModel):
    status: str
    processed_at: str


class {{CLASS_NAME}}Plugin(Plugin):
    def __init__(self, plugin_dir: Path):
        super().__init__(plugin_dir)
        self.router = APIRouter(prefix="/api/plugin/{{PLUGIN_NAME}}", tags=["{{PLUGIN_NAME}}"])
    
    def register(self, app) -> None:
        self.router.get("/status")(self.get_status)
        self.router.post("/process")(self.process)
        app.include_router(self.router)
        logger.info(f"{self.name}: Registered")
    
    def initialize(self) -> None:
        super().initialize()
        logger.info(f"{self.name}: Initialized")
    
    def cleanup(self) -> None:
        super().cleanup()
        logger.info(f"{self.name}: Cleaned up")
    
    async def get_status(self) -> dict:
        return {"status": "active" if self.is_initialized() else "inactive"}
    
    async def process(self, request: ProcessRequest) -> StatusResponse:
        return StatusResponse(
            status=f"Processed: {request.data}",
            processed_at=datetime.now().isoformat()
        )

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
