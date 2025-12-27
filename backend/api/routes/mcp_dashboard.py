"""
MCP Dashboard Routes

Endpoints for MCP (Model Context Protocol) server dashboard and management.
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from ..optimization import cache_response
except ImportError:
    def cache_response(ttl: int = 300):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/mcp-dashboard", tags=["mcp-dashboard"])

# In-memory storage for MCP servers (replace with database in production)
_mcp_servers: Dict[str, "MCPServer"] = {}


class MCPServer(BaseModel):
    """MCP server information."""

    server_id: str
    name: str
    description: str
    server_type: str  # figma, tts, analysis, etc.
    status: str  # connected, disconnected, error
    endpoint: Optional[str] = None
    version: Optional[str] = None
    capabilities: List[str] = []
    last_connected: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, str] = {}


class MCPServerCreateRequest(BaseModel):
    """Request to add a new MCP server."""

    name: str
    description: str
    server_type: str
    endpoint: Optional[str] = None
    version: Optional[str] = None
    capabilities: List[str] = []
    metadata: Dict[str, str] = {}


class MCPServerUpdateRequest(BaseModel):
    """Request to update an MCP server."""

    name: Optional[str] = None
    description: Optional[str] = None
    endpoint: Optional[str] = None
    metadata: Dict[str, str] = {}


class MCPServerResponse(BaseModel):
    """MCP server response."""

    server_id: str
    name: str
    description: str
    server_type: str
    status: str
    endpoint: Optional[str] = None
    version: Optional[str] = None
    capabilities: List[str] = []
    last_connected: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, str] = {}


class MCPOperation(BaseModel):
    """MCP operation information."""

    operation_id: str
    server_id: str
    operation_name: str
    description: str
    parameters: Dict[str, str] = {}
    result_type: str  # json, text, binary
    is_available: bool = True


class MCPDashboardSummary(BaseModel):
    """MCP dashboard summary."""

    total_servers: int
    connected_servers: int
    disconnected_servers: int
    error_servers: int
    total_operations: int
    available_operations: int


@router.get("", response_model=MCPDashboardSummary)
@cache_response(ttl=10)  # Cache for 10 seconds (dashboard updates frequently)
async def get_dashboard_summary():
    """Get MCP dashboard summary."""
    try:
        total = len(_mcp_servers)
        connected = len([
            s for s in _mcp_servers.values()
            if s.status == "connected"
        ])
        disconnected = len(
            [s for s in _mcp_servers.values() if s.status == "disconnected"]
        )
        error = len([s for s in _mcp_servers.values() if s.status == "error"])

        # Count operations from all servers
        total_ops = sum(len(s.capabilities) for s in _mcp_servers.values())
        available_ops = sum(
            len(s.capabilities)
            for s in _mcp_servers.values()
            if s.status == "connected"
        )

        return MCPDashboardSummary(
            total_servers=total,
            connected_servers=connected,
            disconnected_servers=disconnected,
            error_servers=error,
            total_operations=total_ops,
            available_operations=available_ops,
        )
    except Exception as e:
        logger.error(f"Failed to get MCP dashboard summary: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get MCP dashboard summary: {str(e)}",
        ) from e


@router.get("/servers", response_model=List[MCPServerResponse])
@cache_response(ttl=30)  # Cache for 30 seconds (server list changes moderately)
async def list_mcp_servers():
    """List all MCP servers."""
    try:
        servers = []
        for server in _mcp_servers.values():
            servers.append(
                MCPServerResponse(
                    server_id=server.server_id,
                    name=server.name,
                    description=server.description,
                    server_type=server.server_type,
                    status=server.status,
                    endpoint=server.endpoint,
                    version=server.version,
                    capabilities=server.capabilities,
                    last_connected=server.last_connected,
                    error_message=server.error_message,
                    metadata=server.metadata,
                )
            )
        return sorted(servers, key=lambda s: s.name)
    except Exception as e:
        logger.error(f"Failed to list MCP servers: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list MCP servers: {str(e)}",
        ) from e


@router.get("/servers/{server_id}", response_model=MCPServerResponse)
@cache_response(ttl=30)  # Cache for 30 seconds (server info changes moderately)
async def get_mcp_server(server_id: str):
    """Get a specific MCP server."""
    try:
        if server_id not in _mcp_servers:
            raise HTTPException(
                status_code=404, detail=f"MCP server '{server_id}' not found"
            )

        server = _mcp_servers[server_id]

        return MCPServerResponse(
            server_id=server.server_id,
            name=server.name,
            description=server.description,
            server_type=server.server_type,
            status=server.status,
            endpoint=server.endpoint,
            version=server.version,
            capabilities=server.capabilities,
            last_connected=server.last_connected,
            error_message=server.error_message,
            metadata=server.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get MCP server: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get MCP server: {str(e)}",
        ) from e


@router.post("/servers", response_model=MCPServerResponse, status_code=201)
async def create_mcp_server(request: MCPServerCreateRequest):
    """Add a new MCP server."""
    try:
        import uuid

        server_id = f"mcp-{uuid.uuid4().hex[:8]}"

        server = MCPServer(
            server_id=server_id,
            name=request.name,
            description=request.description,
            server_type=request.server_type,
            status="disconnected",
            endpoint=request.endpoint,
            version=request.version,
            capabilities=request.capabilities or [],
            metadata=request.metadata,
        )

        _mcp_servers[server_id] = server

        logger.info(f"Created MCP server: {server_id} - {server.name}")

        return MCPServerResponse(
            server_id=server.server_id,
            name=server.name,
            description=server.description,
            server_type=server.server_type,
            status=server.status,
            endpoint=server.endpoint,
            version=server.version,
            capabilities=server.capabilities,
            last_connected=server.last_connected,
            error_message=server.error_message,
            metadata=server.metadata,
        )
    except Exception as e:
        logger.error(f"Failed to create MCP server: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create MCP server: {str(e)}",
        ) from e


@router.put("/servers/{server_id}", response_model=MCPServerResponse)
async def update_mcp_server(server_id: str, request: MCPServerUpdateRequest):
    """Update an MCP server."""
    try:
        if server_id not in _mcp_servers:
            raise HTTPException(
                status_code=404, detail=f"MCP server '{server_id}' not found"
            )

        server = _mcp_servers[server_id]

        if request.name is not None:
            server.name = request.name
        if request.description is not None:
            server.description = request.description
        if request.endpoint is not None:
            server.endpoint = request.endpoint
        if request.metadata:
            server.metadata.update(request.metadata)

        _mcp_servers[server_id] = server

        logger.info(f"Updated MCP server: {server_id}")

        return MCPServerResponse(
            server_id=server.server_id,
            name=server.name,
            description=server.description,
            server_type=server.server_type,
            status=server.status,
            endpoint=server.endpoint,
            version=server.version,
            capabilities=server.capabilities,
            last_connected=server.last_connected,
            error_message=server.error_message,
            metadata=server.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update MCP server: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update MCP server: {str(e)}",
        ) from e


@router.post("/servers/{server_id}/connect", response_model=MCPServerResponse)
async def connect_mcp_server(server_id: str):
    """Connect to an MCP server."""
    try:
        if server_id not in _mcp_servers:
            raise HTTPException(
                status_code=404, detail=f"MCP server '{server_id}' not found"
            )

        server = _mcp_servers[server_id]

        # In a real implementation, this would attempt to connect
        # to the MCP server. For now, simulate connection.
        from datetime import datetime

        server.status = "connected"
        server.last_connected = datetime.utcnow().isoformat()
        server.error_message = None
        _mcp_servers[server_id] = server

        logger.info(f"Connected to MCP server: {server_id}")

        return MCPServerResponse(
            server_id=server.server_id,
            name=server.name,
            description=server.description,
            server_type=server.server_type,
            status=server.status,
            endpoint=server.endpoint,
            version=server.version,
            capabilities=server.capabilities,
            last_connected=server.last_connected,
            error_message=server.error_message,
            metadata=server.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to connect to MCP server: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to MCP server: {str(e)}",
        ) from e


@router.post(
    "/servers/{server_id}/disconnect", response_model=MCPServerResponse
)
async def disconnect_mcp_server(server_id: str):
    """Disconnect from an MCP server."""
    try:
        if server_id not in _mcp_servers:
            raise HTTPException(
                status_code=404, detail=f"MCP server '{server_id}' not found"
            )

        server = _mcp_servers[server_id]
        server.status = "disconnected"
        _mcp_servers[server_id] = server

        logger.info(f"Disconnected from MCP server: {server_id}")

        return MCPServerResponse(
            server_id=server.server_id,
            name=server.name,
            description=server.description,
            server_type=server.server_type,
            status=server.status,
            endpoint=server.endpoint,
            version=server.version,
            capabilities=server.capabilities,
            last_connected=server.last_connected,
            error_message=server.error_message,
            metadata=server.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disconnect from MCP server: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect from MCP server: {str(e)}",
        ) from e


@router.delete("/servers/{server_id}")
async def delete_mcp_server(server_id: str):
    """Delete an MCP server."""
    try:
        if server_id not in _mcp_servers:
            raise HTTPException(
                status_code=404, detail=f"MCP server '{server_id}' not found"
            )

        del _mcp_servers[server_id]
        logger.info(f"Deleted MCP server: {server_id}")

        return {"message": f"MCP server '{server_id}' deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete MCP server: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete MCP server: {str(e)}",
        ) from e


@router.get(
    "/servers/{server_id}/operations", response_model=List[MCPOperation]
)
async def list_server_operations(server_id: str):
    """List operations available from an MCP server."""
    try:
        if server_id not in _mcp_servers:
            raise HTTPException(
                status_code=404, detail=f"MCP server '{server_id}' not found"
            )

        server = _mcp_servers[server_id]
        operations = []

        # Convert capabilities to operations
        for i, capability in enumerate(server.capabilities):
            operations.append(
                MCPOperation(
                    operation_id=f"{server_id}-op-{i}",
                    server_id=server_id,
                    operation_name=capability,
                    description=f"Operation: {capability}",
                    parameters={},
                    result_type="json",
                    is_available=server.status == "connected",
                )
            )

        return operations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list server operations: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list server operations: {str(e)}",
        ) from e


@router.get("/server-types", response_model=List[str])
async def list_server_types():
    """List available MCP server types."""
    return [
        "figma",
        "tts",
        "analysis",
        "design",
        "code",
        "database",
        "pdf",
        "custom",
    ]
