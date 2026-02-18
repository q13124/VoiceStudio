"""
{{DISPLAY_NAME}} Plugin

A minimal backend plugin template demonstrating:
- Plugin lifecycle (initialize, cleanup)
- API endpoint registration
- Request/response validation with Pydantic
- Error handling and logging
"""

import logging
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

from app.core.plugins_api import Plugin

logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================

class MessageRequest(BaseModel):
    """Request model for message endpoint."""
    message: str


class MessageResponse(BaseModel):
    """Response model for message endpoint."""
    message: str
    processed_at: str


class StatusResponse(BaseModel):
    """Response model for status endpoint."""
    status: str
    plugin_name: str
    version: str


# ============================================================================
# Plugin Implementation
# ============================================================================

class {{CLASS_NAME}}Plugin(Plugin):
    """
    {{DISPLAY_NAME}} Plugin implementation.
    
    This is a minimal template demonstrating core plugin concepts.
    """
    
    def __init__(self, plugin_dir: Path):
        """Initialize the plugin."""
        super().__init__(plugin_dir)
        
        # Create router for API endpoints
        self.router = APIRouter(
            prefix="/api/plugin/{{PLUGIN_NAME}}",
            tags=["{{PLUGIN_NAME}}"]
        )
    
    def register(self, app) -> None:
        """
        Register plugin routes with FastAPI app.
        
        Args:
            app: FastAPI application instance
        """
        try:
            # Register routes
            self.router.get("/status")(self.get_status)
            self.router.post("/message")(self.post_message)
            
            # Include router in app
            app.include_router(self.router)
            
            logger.info(f"{self.name}: Registered {len(self.router.routes)} routes")
        except Exception as e:
            logger.error(f"Failed to register plugin routes: {e}", exc_info=True)
            raise
    
    def initialize(self) -> None:
        """Initialize plugin after registration."""
        try:
            super().initialize()
            logger.info(f"{self.name}: Initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing plugin: {e}", exc_info=True)
            raise
    
    def cleanup(self) -> None:
        """Cleanup plugin resources on shutdown."""
        try:
            super().cleanup()
            logger.info(f"{self.name}: Cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
    
    # ========================================================================
    # API Endpoints
    # ========================================================================
    
    async def get_status(self) -> StatusResponse:
        """
        Get plugin status.
        
        Returns:
            Status information
        """
        try:
            return StatusResponse(
                status="active" if self.is_initialized() else "inactive",
                plugin_name=self.name,
                version=self.version
            )
        except Exception as e:
            logger.error(f"Error in status endpoint: {e}", exc_info=True)
            return StatusResponse(
                status="error",
                plugin_name=self.name,
                version=self.version
            )
    
    async def post_message(self, request: MessageRequest) -> MessageResponse:
        """
        Process a message.
        
        Args:
            request: Message request
            
        Returns:
            Message response
        """
        try:
            if not request.message:
                logger.warning("Empty message received")
            
            from datetime import datetime
            
            return MessageResponse(
                message=f"Received: {request.message}",
                processed_at=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            raise


# ============================================================================
# Plugin Entry Point
# ============================================================================

def register(app, plugin_dir: Path) -> {{CLASS_NAME}}Plugin:
    """
    Plugin entry point called by the plugin loader.
    
    The function name and signature MUST match the entry_points.backend
    in manifest.json.
    
    Args:
        app: FastAPI application instance
        plugin_dir: Path to the plugin directory
        
    Returns:
        The plugin instance
    """
    try:
        plugin = {{CLASS_NAME}}Plugin(plugin_dir)
        plugin.register(app)
        plugin.initialize()
        logger.info(f"{{DISPLAY_NAME}} loaded successfully")
        return plugin
    except Exception as e:
        logger.error(f"Failed to load {{DISPLAY_NAME}}: {e}", exc_info=True)
        raise
