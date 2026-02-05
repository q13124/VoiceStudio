# V2 API Routes
#
# This package contains API v2 endpoints.
# V2 endpoints may have enhanced functionality compared to v1.

from .health import router as health_router

__all__ = ["health_router"]
