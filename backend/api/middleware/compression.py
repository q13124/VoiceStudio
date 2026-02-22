"""
Compression Middleware.

Task 1.4.3: LZ4 compression for large payloads.
Compresses responses to reduce bandwidth usage.
"""

from __future__ import annotations

import gzip
import io
import logging
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for response compression.

    Features:
    - Automatic compression based on content type
    - Minimum size threshold
    - Multiple compression algorithms
    - Accept-Encoding negotiation
    """

    def __init__(
        self,
        app: ASGIApp,
        minimum_size: int = 1024,  # Only compress if > 1KB
        compression_level: int = 6,
        compressible_types: set | None = None,
    ):
        super().__init__(app)
        self.minimum_size = minimum_size
        self.compression_level = compression_level
        self.compressible_types = compressible_types or {
            "application/json",
            "text/html",
            "text/plain",
            "text/css",
            "text/javascript",
            "application/javascript",
            "application/xml",
            "text/xml",
        }

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request and optionally compress response."""

        # Check if client accepts compression
        accept_encoding = request.headers.get("accept-encoding", "")

        # Get response
        response: Response = await call_next(request)

        # Skip if streaming response
        if isinstance(response, StreamingResponse):
            return response

        # Skip if already encoded
        if response.headers.get("content-encoding"):
            return response

        # Check content type
        content_type = response.headers.get("content-type", "").split(";")[0]
        if content_type not in self.compressible_types:
            return response

        # Get body (call_next returns a response with body_iterator)
        body_iter = getattr(response, "body_iterator", None)
        if body_iter is None:
            return response
        body = b""
        async for chunk in body_iter:
            body += chunk

        # Check minimum size
        if len(body) < self.minimum_size:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        # Compress with gzip (most compatible)
        if "gzip" in accept_encoding:
            compressed = self._gzip_compress(body)

            headers = dict(response.headers)
            headers["content-encoding"] = "gzip"
            headers["content-length"] = str(len(compressed))

            return Response(
                content=compressed,
                status_code=response.status_code,
                headers=headers,
                media_type=response.media_type,
            )

        # Try LZ4 if available and client supports
        if "lz4" in accept_encoding:
            try:
                import lz4.frame

                compressed = lz4.frame.compress(body)

                headers = dict(response.headers)
                headers["content-encoding"] = "lz4"
                headers["content-length"] = str(len(compressed))

                return Response(
                    content=compressed,
                    status_code=response.status_code,
                    headers=headers,
                    media_type=response.media_type,
                )
            except ImportError:
                logger.debug("Brotli compression not available")

        # Return uncompressed
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    def _gzip_compress(self, data: bytes) -> bytes:
        """Compress data with gzip."""
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=self.compression_level) as f:
            f.write(data)
        return buf.getvalue()
