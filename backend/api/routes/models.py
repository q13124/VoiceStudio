"""
Model Management Routes

CRUD operations for model storage and management.
Provides model fetching, updating, and checksum verification.
"""

import json
import logging
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..auth import require_auth_if_enabled
from backend.core.security.file_validation import (
    FileValidationError,
    validate_archive_file,
)
from ..models import ApiOk
from ..optimization import cache_response

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))
from app.core.models.storage import ModelInfo, ModelStorage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/models", tags=["models"])

# Initialize model storage
_model_storage = ModelStorage()

# Initialize model cache
try:
    from app.core.models.cache import get_model_cache

    _model_cache = get_model_cache(max_models=10, max_memory_mb=4096.0)  # 4GB max
    HAS_MODEL_CACHE = True
except ImportError:
    HAS_MODEL_CACHE = False
    _model_cache = None


class ModelInfoResponse(BaseModel):
    """Model information response."""

    engine: str
    model_name: str
    model_path: str
    checksum: str
    size: int
    version: Optional[str] = None
    downloaded_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[dict] = None


class ModelRegisterRequest(BaseModel):
    """Request to register a model."""

    engine: str
    model_name: str
    model_path: str
    version: Optional[str] = None
    metadata: Optional[dict] = None


class ModelVerifyResponse(BaseModel):
    """Model verification response."""

    is_valid: bool
    error_message: Optional[str] = None
    expected_checksum: Optional[str] = None
    current_checksum: Optional[str] = None


class StorageStatsResponse(BaseModel):
    """Storage statistics response."""

    total_models: int
    total_size: int
    total_size_mb: float
    total_size_gb: float
    engines: dict
    base_dir: str


class CacheStatsResponse(BaseModel):
    """Model cache statistics response."""

    cache_size: int
    max_models: int
    current_memory_mb: float
    max_memory_mb: Optional[float]
    hits: int
    misses: int
    hit_rate: float
    evictions: int
    total_loaded: int
    cached_models: List[dict]


@router.get("", response_model=List[ModelInfoResponse])
@cache_response(ttl=60)  # Cache for 60 seconds (model list doesn't change frequently)
async def list_models(engine: Optional[str] = None):
    """List all registered models, optionally filtered by engine."""
    try:
        models = _model_storage.list_models(engine=engine)
        return [ModelInfoResponse(**m.to_dict()) for m in models]
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{engine}/{model_name}", response_model=ModelInfoResponse)
@cache_response(ttl=300)  # Cache for 5 minutes (model info is relatively static)
async def get_model(engine: str, model_name: str):
    """Get information about a specific model."""
    try:
        model = _model_storage.get_model(engine, model_name)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return ModelInfoResponse(**model.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ModelInfoResponse)
async def register_model(
    request: ModelRegisterRequest,
    _: None = Depends(require_auth_if_enabled),  # GAP-CRIT-004: Auth required
):
    """Register a model in the storage system."""
    try:
        model = _model_storage.register_model(
            engine=request.engine,
            model_name=request.model_name,
            model_path=request.model_path,
            version=request.version,
            metadata=request.metadata,
        )
        return ModelInfoResponse(**model.to_dict())
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to register model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{engine}/{model_name}/verify", response_model=ModelVerifyResponse)
async def verify_model(engine: str, model_name: str):
    """Verify a model's checksum."""
    try:
        model = _model_storage.get_model(engine, model_name)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        is_valid, error_message = _model_storage.verify_model(engine, model_name)

        return ModelVerifyResponse(
            is_valid=is_valid,
            error_message=error_message,
            expected_checksum=model.checksum if model else None,
            current_checksum=None,  # Could calculate if needed
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to verify model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{engine}/{model_name}/update-checksum", response_model=ModelInfoResponse)
async def update_model_checksum(
    engine: str,
    model_name: str,
    _: None = Depends(require_auth_if_enabled),  # GAP-CRIT-004: Auth required
):
    """Update a model's checksum (e.g., after model update)."""
    try:
        model = _model_storage.update_model_checksum(engine, model_name)
        if not model:
            raise HTTPException(status_code=404, detail="Model not found")
        return ModelInfoResponse(**model.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update model checksum: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{engine}/{model_name}", response_model=ApiOk)
async def delete_model(
    engine: str,
    model_name: str,
    _: None = Depends(require_auth_if_enabled),  # GAP-CRIT-004: Auth required
):
    """Delete a model from the registry (does not delete files)."""
    try:
        deleted = _model_storage.delete_model(engine, model_name)
        if not deleted:
            raise HTTPException(status_code=404, detail="Model not found")
        return ApiOk(message="Model deleted from registry")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/storage", response_model=StorageStatsResponse)
@cache_response(ttl=60)  # Cache for 60 seconds (storage stats don't change frequently)
async def get_storage_stats():
    """Get storage statistics."""
    try:
        stats = _model_storage.get_storage_stats()
        return StorageStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/cache", response_model=CacheStatsResponse)
@cache_response(ttl=10)  # Cache for 10 seconds (cache stats change more frequently)
async def get_cache_stats():
    """Get model cache statistics."""
    try:
        if not HAS_MODEL_CACHE or _model_cache is None:
            raise HTTPException(status_code=503, detail="Model cache not available")

        stats = _model_cache.get_stats()
        cached_models = _model_cache.list_cached_models()

        return CacheStatsResponse(**stats, cached_models=cached_models)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{engine}/{model_name}/export")
async def export_model(engine: str, model_name: str, request: Request):
    """Export a model as a ZIP archive."""
    # Get request ID from middleware
    request_id = getattr(request.state, "request_id", None)

    # Instrument export flow
    from ..utils.instrumentation import EventType, instrument_flow

    with instrument_flow(
        EventType.EXPORT_START,
        EventType.EXPORT_COMPLETE,
        EventType.EXPORT_ERROR,
        request_id=request_id,
        engine=engine,
        model_name=model_name,
    ):
        try:
            model = _model_storage.get_model(engine, model_name)
            if not model:
                raise HTTPException(status_code=404, detail="Model not found")

            model_path = Path(model.model_path)
            if not model_path.exists():
                raise HTTPException(status_code=404, detail="Model files not found")

            # Create temporary ZIP file
            temp_dir = tempfile.mkdtemp()
            zip_path = Path(temp_dir) / f"{engine}_{model_name}.zip"

            try:
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    # Add model files
                    if model_path.is_file():
                        zipf.write(model_path, model_path.name)
                    elif model_path.is_dir():
                        for root, dirs, files in os.walk(model_path):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = file_path.relative_to(model_path.parent)
                                zipf.write(file_path, arcname)

                    # Add metadata
                    metadata = {
                        "engine": engine,
                        "model_name": model_name,
                        "version": model.version,
                        "checksum": model.checksum,
                        "size": model.size,
                        "metadata": model.metadata,
                    }
                    zipf.writestr("model_info.json", json.dumps(metadata, indent=2))

                # Return file response
                return FileResponse(
                    path=str(zip_path),
                    filename=f"{engine}_{model_name}.zip",
                    media_type="application/zip",
                )
            except Exception as e:
                # Cleanup on error
                if zip_path.exists():
                    zip_path.unlink()
                raise e
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to export model: {e}")
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/import")
async def import_model(
    request: Request,
    file: UploadFile = File(...),
    engine: Optional[str] = None,
    _: None = Depends(require_auth_if_enabled),  # GAP-CRIT-004: Auth required
):
    """Import a model from a ZIP archive."""
    # Get request ID from middleware
    request_id = (
        getattr(request.state, "request_id", None) if request is not None else None
    )

    # Instrument import flow
    from ..utils.instrumentation import EventType, instrument_flow

    with instrument_flow(
        EventType.IMPORT_START,
        EventType.IMPORT_COMPLETE,
        EventType.IMPORT_ERROR,
        request_id=request_id,
        engine=engine,
        filename=file.filename if file else None,
    ):
        try:
            # Read and validate archive file
            content = await file.read()
            try:
                validate_archive_file(content, filename=file.filename)
            except FileValidationError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid archive file: {e.message}",
                ) from e

            # Save uploaded file temporarily
            temp_dir = tempfile.mkdtemp()
            temp_file = Path(temp_dir) / file.filename

            try:
                # Write validated file
                with open(temp_file, "wb") as f:
                    f.write(content)

                # Extract ZIP
                extract_dir = Path(temp_dir) / "extracted"
                extract_dir.mkdir()

                with zipfile.ZipFile(temp_file, "r") as zipf:
                    zipf.extractall(extract_dir)

                # Read metadata
                metadata_file = extract_dir / "model_info.json"
                if not metadata_file.exists():
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid model archive: missing model_info.json",
                    )

                with open(metadata_file, "r") as f:
                    metadata = json.load(f)

                # Use provided engine or metadata engine
                model_engine = engine or metadata.get("engine")
                if not model_engine:
                    raise HTTPException(status_code=400, detail="Engine not specified")

                model_name = metadata.get("model_name")
                if not model_name:
                    raise HTTPException(
                        status_code=400, detail="Model name not found in metadata"
                    )

                # Find model files (exclude metadata file)
                model_files = [
                    f
                    for f in extract_dir.rglob("*")
                    if f.is_file() and f.name != "model_info.json"
                ]
                if not model_files:
                    raise HTTPException(
                        status_code=400, detail="No model files found in archive"
                    )

                # Determine model path (use first file's parent or the file itself)
                if len(model_files) == 1:
                    model_path = model_files[0]
                else:
                    # Multiple files - use common parent
                    model_path = extract_dir

                # Move to model storage location
                storage_base = Path(_model_storage.base_dir) / model_engine / model_name
                storage_base.parent.mkdir(parents=True, exist_ok=True)

                if model_path.is_file():
                    shutil.copy2(model_path, storage_base)
                else:
                    if storage_base.exists():
                        shutil.rmtree(storage_base)
                    shutil.copytree(model_path, storage_base)

                # Register model
                registered_model = _model_storage.register_model(
                    engine=model_engine,
                    model_name=model_name,
                    model_path=str(storage_base),
                    version=metadata.get("version"),
                    metadata=metadata.get("metadata"),
                )

                return ModelInfoResponse(**registered_model.to_dict())
            finally:
                # Cleanup
                shutil.rmtree(temp_dir, ignore_errors=True)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to import model: {e}")
            raise HTTPException(status_code=500, detail=str(e))
