# api/similarity_endpoints.py
# API endpoints for voice similarity scoring

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional, Dict, Any
import json
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from voice_studio_similarity_analyzer import VoiceSimilarityAnalyzer
from api.models import *

router = APIRouter(prefix="/api/v1/similarity", tags=["similarity"])

# Initialize analyzer
analyzer = VoiceSimilarityAnalyzer()

@router.post("/compare")
async def compare_voices(
    background_tasks: BackgroundTasks,
    reference_audio: UploadFile = File(...),
    comparison_audio: UploadFile = File(...),
    include_details: bool = Form(True),
    analysis_type: str = Form("comprehensive")
):
    """Compare two voice files for similarity"""
    try:
        # Save uploaded files
        ref_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        comp_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        
        # Write uploaded files
        ref_content = await reference_audio.read()
        comp_content = await comparison_audio.read()
        
        ref_temp.write(ref_content)
        comp_temp.write(comp_content)
        
        ref_temp.close()
        comp_temp.close()
        
        # Perform comparison
        results = analyzer.compare_voices(ref_temp.name, comp_temp.name)
        
        # Clean up temp files
        os.unlink(ref_temp.name)
        os.unlink(comp_temp.name)
        
        # Format response based on analysis type
        if analysis_type == "summary":
            response = {
                "overall_similarity": results["similarity_scores"]["overall"]["score"],
                "confidence": results["similarity_scores"]["overall"]["confidence"],
                "quality_level": get_quality_level(results["similarity_scores"]["overall"]["score"])
            }
        else:
            response = results
        
        return {
            "success": True,
            "analysis_type": analysis_type,
            "results": response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch-compare")
async def batch_compare_voices(
    background_tasks: BackgroundTasks,
    reference_audio: UploadFile = File(...),
    comparison_files: List[UploadFile] = File(...),
    max_comparisons: int = Form(10),
    analysis_type: str = Form("comprehensive")
):
    """Compare reference voice with multiple comparison voices"""
    try:
        if len(comparison_files) > max_comparisons:
            raise HTTPException(
                status_code=400, 
                detail=f"Too many comparison files. Maximum allowed: {max_comparisons}"
            )
        
        # Save reference file
        ref_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        ref_content = await reference_audio.read()
        ref_temp.write(ref_content)
        ref_temp.close()
        
        # Save comparison files
        comp_temps = []
        comp_paths = []
        
        for comp_file in comparison_files:
            comp_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            comp_content = await comp_file.read()
            comp_temp.write(comp_content)
            comp_temp.close()
            
            comp_temps.append(comp_temp)
            comp_paths.append(comp_temp.name)
        
        # Perform batch comparison
        results = analyzer.batch_compare_voices(ref_temp.name, comp_paths)
        
        # Clean up temp files
        os.unlink(ref_temp.name)
        for comp_temp in comp_temps:
            os.unlink(comp_temp.name)
        
        # Format response
        if analysis_type == "summary":
            summary_results = []
            for comp in results["comparisons"]:
                if "overall_similarity" in comp:
                    summary_results.append({
                        "file_name": os.path.basename(comp["comparison_path"]),
                        "similarity_score": comp["overall_similarity"],
                        "confidence": comp["confidence"],
                        "quality_level": get_quality_level(comp["overall_similarity"])
                    })
            
            response = {
                "reference_file": os.path.basename(results["reference_path"]),
                "total_comparisons": len(results["comparisons"]),
                "results": summary_results
            }
        else:
            response = results
        
        return {
            "success": True,
            "analysis_type": analysis_type,
            "results": response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-features")
async def analyze_voice_features(
    audio_file: UploadFile = File(...),
    feature_types: str = Form("all")
):
    """Analyze voice features from audio file"""
    try:
        # Save uploaded file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        content = await audio_file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Extract features
        features = analyzer.extract_voice_features(temp_file.name)
        
        # Clean up temp file
        os.unlink(temp_file.name)
        
        # Format response based on requested feature types
        response = {}
        
        if feature_types == "all" or "spectral" in feature_types:
            response["spectral_features"] = {
                "spectral_centroid_mean": float(np.mean(features.spectral_centroid)),
                "spectral_rolloff_mean": float(np.mean(features.spectral_rolloff)),
                "spectral_bandwidth_mean": float(np.mean(features.spectral_bandwidth))
            }
        
        if feature_types == "all" or "mfcc" in feature_types:
            response["mfcc_features"] = {
                "mfcc_mean": float(np.mean(features.mfcc)),
                "mfcc_std": float(np.std(features.mfcc))
            }
        
        if feature_types == "all" or "pitch" in feature_types:
            valid_pitches = features.pitch[features.pitch > 0]
            if len(valid_pitches) > 0:
                response["pitch_features"] = {
                    "pitch_mean": float(np.mean(valid_pitches)),
                    "pitch_std": float(np.std(valid_pitches)),
                    "pitch_range": float(np.max(valid_pitches) - np.min(valid_pitches))
                }
        
        if feature_types == "all" or "prosody" in feature_types:
            response["prosody_features"] = features.prosody_features
        
        if feature_types == "all" or "timbre" in feature_types:
            response["timbre_features"] = features.timbre_features
        
        return {
            "success": True,
            "file_name": audio_file.filename,
            "features": response
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quality-levels")
async def get_quality_levels():
    """Get quality level definitions"""
    return {
        "quality_levels": {
            "excellent": {"min_score": 0.9, "description": "Very high similarity"},
            "good": {"min_score": 0.8, "description": "High similarity"},
            "fair": {"min_score": 0.7, "description": "Moderate similarity"},
            "poor": {"min_score": 0.6, "description": "Low similarity"},
            "very_poor": {"min_score": 0.0, "description": "Very low similarity"}
        }
    }

@router.get("/metrics")
async def get_similarity_metrics():
    """Get available similarity metrics"""
    return {
        "metrics": [
            {
                "name": "spectral_similarity",
                "description": "Spectral characteristics similarity",
                "weight": 0.25
            },
            {
                "name": "mfcc_similarity", 
                "description": "MFCC feature similarity",
                "weight": 0.25
            },
            {
                "name": "pitch_similarity",
                "description": "Pitch characteristics similarity",
                "weight": 0.20
            },
            {
                "name": "prosody_similarity",
                "description": "Prosody and rhythm similarity",
                "weight": 0.15
            },
            {
                "name": "timbre_similarity",
                "description": "Timbre and voice quality similarity",
                "weight": 0.15
            }
        ]
    }

def get_quality_level(score: float) -> str:
    """Get quality level based on similarity score"""
    if score >= 0.9:
        return "excellent"
    elif score >= 0.8:
        return "good"
    elif score >= 0.7:
        return "fair"
    elif score >= 0.6:
        return "poor"
    else:
        return "very_poor"

import numpy as np
