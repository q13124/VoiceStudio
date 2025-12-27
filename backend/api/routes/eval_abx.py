"""
ABX Evaluation Routes

Endpoints for ABX testing (audio comparison testing) to evaluate
voice synthesis quality through perceptual testing.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..models import ApiOk
from ..models_additional import AbxStartRequest, AbxResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/eval/abx", tags=["eval", "abx"])

# In-memory ABX test sessions (replace with database in production)
_abx_sessions: Dict[str, Dict] = {}
_abx_results: Dict[str, List[Dict]] = {}


class ABXSession(BaseModel):
    """ABX test session information."""

    session_id: str
    items: List[str]  # Audio IDs for comparison
    status: str  # pending, active, completed
    created: str
    completed: Optional[str] = None


class ABXTestResult(BaseModel):
    """Result of an ABX test."""

    session_id: str
    item: str
    mos: float  # Mean Opinion Score
    pref: str  # Preference (A, B, or X)
    confidence: Optional[float] = None
    timestamp: str


@router.post("/start", response_model=ABXSession)
async def start(req: AbxStartRequest) -> ABXSession:
    """
    Start an ABX evaluation test session.
    
    ABX testing compares audio samples where:
    - A and B are reference samples
    - X is the test sample
    - Users identify which reference (A or B) X is closer to
    
    Args:
        req: Request with list of audio IDs to test
        
    Returns:
        ABX session information
    """
    try:
        if not req.items or len(req.items) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 audio items are required for ABX testing"
            )
        
        # Validate audio files exist
        from .voice import _audio_storage
        
        missing_audio = []
        for audio_id in req.items:
            if audio_id not in _audio_storage:
                missing_audio.append(audio_id)
        
        if missing_audio:
            raise HTTPException(
                status_code=404,
                detail=f"Audio files not found: {', '.join(missing_audio)}"
            )
        
        # Create ABX session
        session_id = f"abx-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        
        session = {
            "session_id": session_id,
            "items": req.items,
            "status": "active",
            "created": now,
            "completed": None,
        }
        
        _abx_sessions[session_id] = session
        _abx_results[session_id] = []
        
        logger.info(f"Started ABX test session: {session_id} with {len(req.items)} items")
        
        return ABXSession(
            session_id=session_id,
            items=req.items,
            status="active",
            created=now,
            completed=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start ABX test: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start ABX test: {str(e)}"
        ) from e


@router.get("/results", response_model=List[AbxResult])
async def results(session_id: Optional[str] = None) -> List[AbxResult]:
    """
    Get ABX test results.
    
    Args:
        session_id: Optional session ID to filter results
        
    Returns:
        List of ABX test results
    """
    try:
        if session_id:
            # Return results for specific session
            if session_id not in _abx_results:
                raise HTTPException(
                    status_code=404,
                    detail=f"ABX session '{session_id}' not found"
                )
            
            results_data = _abx_results[session_id]
            return [
                AbxResult(
                    item=r.get("item", ""),
                    mos=r.get("mos", 0.0),
                    pref=r.get("pref", "X")
                )
                for r in results_data
            ]
        else:
            # Return all results from all sessions
            all_results = []
            for session_results in _abx_results.values():
                all_results.extend(session_results)
            
            return [
                AbxResult(
                    item=r.get("item", ""),
                    mos=r.get("mos", 0.0),
                    pref=r.get("pref", "X")
                )
                for r in all_results
            ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get ABX results: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get ABX results: {str(e)}"
        ) from e


@router.post("/submit")
async def submit_result(
    session_id: str,
    item: str,
    pref: str,
    confidence: Optional[float] = None
) -> ApiOk:
    """
    Submit an ABX test result.
    
    Args:
        session_id: ABX session ID
        item: Audio item ID that was tested
        pref: Preference (A, B, or X)
        confidence: Optional confidence score (0.0-1.0)
        
    Returns:
        Success response
    """
    try:
        if session_id not in _abx_sessions:
            raise HTTPException(
                status_code=404,
                detail=f"ABX session '{session_id}' not found"
            )
        
        if pref not in ["A", "B", "X"]:
            raise HTTPException(
                status_code=400,
                detail="pref must be 'A', 'B', or 'X'"
            )
        
        # Calculate MOS score based on preference
        # A = 5.0, B = 1.0, X = 3.0 (neutral)
        mos_map = {"A": 5.0, "B": 1.0, "X": 3.0}
        mos = mos_map.get(pref, 3.0)
        
        # Adjust MOS based on confidence if provided
        if confidence is not None:
            confidence = max(0.0, min(1.0, confidence))
            # Scale MOS based on confidence
            if pref == "A":
                mos = 3.0 + (2.0 * confidence)
            elif pref == "B":
                mos = 3.0 - (2.0 * confidence)
            else:
                mos = 3.0
        
        # Store result
        result = {
            "session_id": session_id,
            "item": item,
            "mos": mos,
            "pref": pref,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if session_id not in _abx_results:
            _abx_results[session_id] = []
        
        _abx_results[session_id].append(result)
        
        logger.info(
            f"ABX result submitted: session={session_id}, "
            f"item={item}, pref={pref}, mos={mos:.2f}"
        )
        
        return ApiOk()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit ABX result: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit ABX result: {str(e)}"
        ) from e


@router.get("/sessions/{session_id}", response_model=ABXSession)
async def get_session(session_id: str) -> ABXSession:
    """Get ABX session information."""
    if session_id not in _abx_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"ABX session '{session_id}' not found"
        )
    
    session = _abx_sessions[session_id]
    return ABXSession(
        session_id=session["session_id"],
        items=session["items"],
        status=session["status"],
        created=session["created"],
        completed=session.get("completed"),
    )


@router.post("/sessions/{session_id}/complete")
async def complete_session(session_id: str) -> ApiOk:
    """Mark an ABX session as completed."""
    if session_id not in _abx_sessions:
        raise HTTPException(
            status_code=404,
            detail=f"ABX session '{session_id}' not found"
        )
    
    _abx_sessions[session_id]["status"] = "completed"
    _abx_sessions[session_id]["completed"] = datetime.utcnow().isoformat()
    
    logger.info(f"ABX session completed: {session_id}")
    
    return ApiOk()
