# api/batch_endpoints.py
# API endpoints for batch processing

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional, Dict, Any
import json
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_batch_processor import BatchProcessor, BatchJobType
from api.models import *

router = APIRouter(prefix="/api/v1/batch", tags=["batch"])

# Initialize batch processor
batch_processor = BatchProcessor()

@router.post("/create-job")
async def create_batch_job(
    background_tasks: BackgroundTasks,
    job_type: str = Form(...),
    items_file: UploadFile = File(...),
    configuration: Optional[str] = Form(None)
):
    """Create a new batch processing job"""
    try:
        # Validate job type
        try:
            batch_job_type = BatchJobType(job_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid job type: {job_type}")
        
        # Save uploaded items file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        content = await items_file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Load items
        with open(temp_file.name, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        # Parse configuration
        config = {}
        if configuration:
            try:
                config = json.loads(configuration)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid configuration JSON")
        
        # Create batch job
        job_id = batch_processor.create_batch_job(batch_job_type, items, config)
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        return {
            "success": True,
            "job_id": job_id,
            "job_type": job_type,
            "total_items": len(items),
            "status": "queued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}/status")
async def get_batch_job_status(job_id: str):
    """Get batch job status"""
    try:
        result = batch_processor.get_job_status(job_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}/results")
async def get_batch_job_results(job_id: str):
    """Get batch job results"""
    try:
        result = batch_processor.get_job_results(job_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/cancel")
async def cancel_batch_job(job_id: str):
    """Cancel a batch job"""
    try:
        result = batch_processor.cancel_job(job_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/pause")
async def pause_batch_job(job_id: str):
    """Pause a batch job"""
    try:
        result = batch_processor.pause_job(job_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/jobs/{job_id}/resume")
async def resume_batch_job(job_id: str):
    """Resume a paused batch job"""
    try:
        result = batch_processor.resume_job(job_id)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/{job_id}/export")
async def export_batch_results(
    job_id: str,
    format: str = "json"
):
    """Export batch job results"""
    try:
        if format not in ["json", "csv", "excel"]:
            raise HTTPException(status_code=400, detail="Invalid format. Supported: json, csv, excel")
        
        result = batch_processor.export_results(job_id, format)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job-types")
async def get_job_types():
    """Get available batch job types"""
    return {
        "job_types": [
            {
                "name": "voice_cloning",
                "display_name": "Voice Cloning",
                "description": "Batch voice cloning operations",
                "max_items": 100,
                "timeout_per_item": 60
            },
            {
                "name": "audio_processing",
                "display_name": "Audio Processing",
                "description": "Batch audio processing with DSP chains",
                "max_items": 200,
                "timeout_per_item": 30
            },
            {
                "name": "similarity_analysis",
                "display_name": "Similarity Analysis",
                "description": "Batch voice similarity analysis",
                "max_items": 50,
                "timeout_per_item": 45
            },
            {
                "name": "quality_assessment",
                "display_name": "Quality Assessment",
                "description": "Batch audio quality assessment",
                "max_items": 100,
                "timeout_per_item": 20
            },
            {
                "name": "feature_extraction",
                "display_name": "Feature Extraction",
                "description": "Batch voice feature extraction",
                "max_items": 150,
                "timeout_per_item": 25
            },
            {
                "name": "mixed_operations",
                "display_name": "Mixed Operations",
                "description": "Batch mixed operations",
                "max_items": 75,
                "timeout_per_item": 90
            }
        ]
    }

@router.get("/status")
async def get_batch_processor_status():
    """Get batch processor status"""
    return {
        "processor_status": "running",
        "active_jobs": len(batch_processor.active_jobs),
        "queued_jobs": batch_processor.job_queue.qsize(),
        "max_workers": batch_processor.max_workers,
        "max_concurrent_jobs": batch_processor.max_concurrent_jobs
    }

@router.post("/upload-items")
async def upload_batch_items(
    items_file: UploadFile = File(...),
    validate_only: bool = Form(False)
):
    """Upload and validate batch items file"""
    try:
        # Save uploaded file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        content = await items_file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Load and validate items
        with open(temp_file.name, 'r', encoding='utf-8') as f:
            items = json.load(f)
        
        # Validate items structure
        validation_result = validate_batch_items(items)
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        if validate_only:
            return {
                "success": True,
                "validation": validation_result,
                "total_items": len(items)
            }
        else:
            return {
                "success": True,
                "items": items,
                "validation": validation_result,
                "total_items": len(items)
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def validate_batch_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate batch items structure"""
    validation = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    if not isinstance(items, list):
        validation["valid"] = False
        validation["errors"].append("Items must be a list")
        return validation
    
    if len(items) == 0:
        validation["valid"] = False
        validation["errors"].append("Items list cannot be empty")
        return validation
    
    if len(items) > 1000:
        validation["warnings"].append("Large number of items may impact performance")
    
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            validation["valid"] = False
            validation["errors"].append(f"Item {i} must be a dictionary")
            continue
        
        # Check required fields
        if "input_path" not in item:
            validation["valid"] = False
            validation["errors"].append(f"Item {i} missing required field: input_path")
        
        if "parameters" not in item:
            validation["valid"] = False
            validation["errors"].append(f"Item {i} missing required field: parameters")
        
        # Check optional fields
        if "output_path" not in item:
            validation["warnings"].append(f"Item {i} missing optional field: output_path")
    
    return validation
