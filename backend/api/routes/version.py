"""
API Version Information Routes

Provides endpoints for API version discovery and negotiation.
Clients can use these endpoints to determine available API versions
and their capabilities.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Header, HTTPException, Request, Response
from pydantic import BaseModel

from backend.api.versioning import (
    VERSION_HEADER,
    APIVersion,
    get_all_versioned_endpoints,
    get_version_from_request,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/version", tags=["version"])


class VersionInfo(BaseModel):
    """API version information."""
    
    version: str
    status: str  # "current", "supported", "deprecated"
    deprecated: bool = False
    sunset_date: Optional[str] = None
    description: Optional[str] = None


class VersionsResponse(BaseModel):
    """Response for version listing endpoint."""
    
    current_version: str
    default_version: str
    supported_versions: List[str]
    versions: List[VersionInfo]
    timestamp: str


class NegotiateRequest(BaseModel):
    """Request for version negotiation."""
    
    preferred_versions: List[str]
    capabilities: Optional[List[str]] = None


class NegotiateResponse(BaseModel):
    """Response for version negotiation."""
    
    negotiated_version: str
    matched: bool
    all_supported: List[str]
    message: str


# Version metadata
VERSION_METADATA: Dict[str, Dict[str, Any]] = {
    "v1": {
        "status": "supported",
        "deprecated": False,
        "description": "Original API version. Stable and fully supported.",
    },
    "v2": {
        "status": "current",
        "deprecated": False,
        "description": "Enhanced API version with improved responses and versioning headers.",
    },
}


@router.get("/", response_model=VersionsResponse)
async def get_versions(response: Response) -> VersionsResponse:
    """
    Get information about available API versions.
    
    Returns:
        List of supported API versions with their status and metadata.
    """
    response.headers[VERSION_HEADER] = APIVersion.current().value
    
    versions = []
    for version in APIVersion.supported():
        metadata = VERSION_METADATA.get(version.value, {})
        versions.append(
            VersionInfo(
                version=version.value,
                status=metadata.get("status", "supported"),
                deprecated=metadata.get("deprecated", False),
                sunset_date=metadata.get("sunset_date"),
                description=metadata.get("description"),
            )
        )
    
    return VersionsResponse(
        current_version=APIVersion.current().value,
        default_version=APIVersion.default().value,
        supported_versions=[v.value for v in APIVersion.supported()],
        versions=versions,
        timestamp=datetime.utcnow().isoformat() + "Z",
    )


@router.get("/current")
async def get_current_version(response: Response) -> Dict[str, Any]:
    """
    Get the current (latest) API version.
    
    Returns:
        Information about the current API version.
    """
    response.headers[VERSION_HEADER] = APIVersion.current().value
    current = APIVersion.current()
    metadata = VERSION_METADATA.get(current.value, {})
    
    return {
        "version": current.value,
        "status": "current",
        "description": metadata.get("description", "Current API version"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/detect")
async def detect_version(
    request: Request,
    response: Response,
) -> Dict[str, Any]:
    """
    Detect the API version from the current request.
    
    Uses URL path and headers to determine the active version.
    
    Returns:
        The detected API version and detection method.
    """
    detected_version = get_version_from_request(request)
    response.headers[VERSION_HEADER] = detected_version.value
    
    # Determine how version was detected
    path = request.url.path
    header_version = request.headers.get(VERSION_HEADER)
    
    detection_method = "default"
    if any(path.startswith(f"/api/{v.value}/") for v in APIVersion):
        detection_method = "url_path"
    elif header_version:
        detection_method = "header"
    
    return {
        "detected_version": detected_version.value,
        "detection_method": detection_method,
        "url_path": path,
        "header_value": header_version,
        "is_current": detected_version == APIVersion.current(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.post("/negotiate", response_model=NegotiateResponse)
async def negotiate_version(
    request_body: NegotiateRequest,
    response: Response,
) -> NegotiateResponse:
    """
    Negotiate API version based on client preferences.
    
    The client provides a list of preferred versions in priority order,
    and the server responds with the best matching supported version.
    
    Args:
        request_body: Client's version preferences.
    
    Returns:
        The negotiated version and match status.
    """
    supported = {v.value for v in APIVersion.supported()}
    preferred = request_body.preferred_versions
    
    # Find the first preferred version that's supported
    negotiated = None
    for version in preferred:
        if version in supported:
            negotiated = version
            break
    
    if negotiated:
        try:
            api_version = APIVersion(negotiated)
            response.headers[VERSION_HEADER] = negotiated
            return NegotiateResponse(
                negotiated_version=negotiated,
                matched=True,
                all_supported=list(supported),
                message=f"Negotiated to {negotiated}",
            )
        # ALLOWED: bare except - Invalid version falls back to default
        except ValueError:
            pass
    
    # Fall back to default version
    default = APIVersion.default().value
    response.headers[VERSION_HEADER] = default
    
    return NegotiateResponse(
        negotiated_version=default,
        matched=False,
        all_supported=list(supported),
        message=f"No preferred version supported. Using default: {default}",
    )


@router.get("/endpoints")
async def get_versioned_endpoints(
    response: Response,
    version: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Get list of versioned endpoints.
    
    Args:
        version: Optional filter for a specific version.
    
    Returns:
        Dictionary of endpoints and their version mappings.
    """
    response.headers[VERSION_HEADER] = APIVersion.current().value
    
    all_endpoints = get_all_versioned_endpoints()
    
    if version:
        try:
            target_version = APIVersion(version)
            filtered = {}
            for endpoint_id, versions in all_endpoints.items():
                if target_version in versions:
                    filtered[endpoint_id] = {target_version.value: versions[target_version]}
            return {
                "filter": version,
                "endpoints": filtered,
                "count": len(filtered),
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid version: {version}. Supported: {[v.value for v in APIVersion.supported()]}",
            )
    
    # Convert APIVersion keys to strings for JSON serialization
    serializable = {}
    for endpoint_id, versions in all_endpoints.items():
        serializable[endpoint_id] = {v.value: path for v, path in versions.items()}
    
    return {
        "endpoints": serializable,
        "count": len(serializable),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/compatibility")
async def check_compatibility(
    response: Response,
    client_version: Optional[str] = Header(None, alias=VERSION_HEADER),
) -> Dict[str, Any]:
    """
    Check if a client version is compatible with the current API.
    
    Args:
        client_version: Client's declared API version from header.
    
    Returns:
        Compatibility information and upgrade recommendations.
    """
    response.headers[VERSION_HEADER] = APIVersion.current().value
    
    supported = APIVersion.supported()
    current = APIVersion.current()
    
    result = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "server_version": current.value,
        "supported_versions": [v.value for v in supported],
    }
    
    if not client_version:
        result.update({
            "client_version": None,
            "compatible": True,
            "message": "No client version specified. Using default.",
            "recommendation": None,
        })
        return result
    
    # Check if client version is supported
    try:
        client = APIVersion(client_version.lower())
        is_current = client == current
        
        result.update({
            "client_version": client_version,
            "compatible": True,
            "is_current": is_current,
            "message": "Client version is supported.",
            "recommendation": None if is_current else f"Consider upgrading to {current.value}",
        })
        
        # Add deprecation info if applicable
        metadata = VERSION_METADATA.get(client.value, {})
        if metadata.get("deprecated"):
            result["deprecated"] = True
            result["sunset_date"] = metadata.get("sunset_date")
            result["message"] = "Client version is deprecated."
            result["recommendation"] = f"Upgrade to {current.value} before sunset."
        
    except ValueError:
        result.update({
            "client_version": client_version,
            "compatible": False,
            "message": f"Client version '{client_version}' is not supported.",
            "recommendation": f"Use one of: {[v.value for v in supported]}",
        })
    
    return result
