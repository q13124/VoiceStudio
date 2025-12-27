"""
Example VoiceStudio Plugin

This plugin demonstrates how to create a VoiceStudio plugin.
"""

from pathlib import Path
from app.core.plugins_api.base import BasePlugin, PluginMetadata
from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)


class ExamplePlugin(BasePlugin):
    """Example plugin implementation"""
    
    def __init__(self, plugin_dir: Path):
        """Initialize example plugin"""
        manifest_path = plugin_dir / "manifest.json"
        metadata = PluginMetadata(manifest_path)
        super().__init__(metadata)
        self.router = APIRouter(prefix="/api/plugin/example", tags=["plugin", "example"])
    
    def register(self, app):
        """Register plugin routes with FastAPI app"""
        # Register routes
        self.router.get("/hello")(self.hello)
        self.router.get("/info")(self.info)
        
        # Include router in app
        app.include_router(self.router)
        logger.info(f"Example plugin registered with {len(self.router.routes)} routes")
    
    async def hello(self):
        """Example endpoint"""
        return {"message": "Hello from Example Plugin!"}
    
    async def info(self):
        """Get plugin info"""
        return self.get_info()


# Plugin entry point
def register(app, plugin_dir: Path):
    """
    Register the plugin with the FastAPI app.
    
    This function is called by the plugin loader.
    
    Args:
        app: FastAPI application instance
        plugin_dir: Path to plugin directory
    """
    plugin = ExamplePlugin(plugin_dir)
    plugin.register(app)
    plugin.initialize()
    return plugin

