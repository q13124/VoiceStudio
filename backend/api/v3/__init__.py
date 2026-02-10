"""
API v3 - Breaking Changes Release.

Task 3.4.1: API versioning v3 implementation.

Breaking changes from v2:
- Unified synthesis endpoint (replaces separate TTS/cloning endpoints)
- Streaming-first responses for real-time operations
- gRPC support for high-performance engine communication
- New error response format with machine-readable codes
- Pagination uses cursor-based instead of offset-based
"""

from fastapi import APIRouter

from .engines import router as engines_router
from .synthesis import router as synthesis_router
from .voices import router as voices_router
from .projects import router as projects_router

# Create main v3 router
router = APIRouter(prefix="/v3", tags=["v3"])

# Include sub-routers
router.include_router(engines_router)
router.include_router(synthesis_router)
router.include_router(voices_router)
router.include_router(projects_router)

__all__ = ["router"]
