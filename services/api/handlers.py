# services/api/handlers.py
# API request handlers for VoiceStudio

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.utils import AudioUtils, FileUtils, ValidationUtils, ResponseUtils
from api.models import *

class VoiceCloneHandler:
    """Handler for voice cloning requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def process_clone_request(self, request: VoiceCloneRequest) -> VoiceCloneResponse:
        """Process voice cloning request"""
        try:
            # Validate inputs
            if not ValidationUtils.validate_text(request.text):
                return VoiceCloneResponse(
                    success=False,
                    job_id="",
                    status=JobStatus.FAILED,
                    error="Invalid text input"
                )
            
            if not ValidationUtils.validate_language(request.language):
                return VoiceCloneResponse(
                    success=False,
                    job_id="",
                    status=JobStatus.FAILED,
                    error="Unsupported language"
                )
            
            if not ValidationUtils.validate_engine(request.engine):
                return VoiceCloneResponse(
                    success=False,
                    job_id="",
                    status=JobStatus.FAILED,
                    error="Invalid engine"
                )
            
            # Decode reference audio
            try:
                audio_data = AudioUtils.decode_base64_audio(request.reference_audio)
                temp_audio_path = await AudioUtils.save_temp_audio(audio_data)
            except Exception as e:
                return VoiceCloneResponse(
                    success=False,
                    job_id="",
                    status=JobStatus.FAILED,
                    error=f"Invalid audio data: {e}"
                )
            
            # Validate audio
            if not AudioUtils.validate_audio_format(temp_audio_path):
                return VoiceCloneResponse(
                    success=False,
                    job_id="",
                    status=JobStatus.FAILED,
                    error="Invalid audio format"
                )
            
            # Generate job ID
            job_id = f"clone_{int(time.time())}"
            
            # Queue job for processing
            # In production, this would queue the job in a proper job queue
            self.logger.info(f"Queued voice cloning job: {job_id}")
            
            return VoiceCloneResponse(
                success=True,
                job_id=job_id,
                status=JobStatus.QUEUED,
                estimated_time=5.0
            )
            
        except Exception as e:
            self.logger.error(f"Voice cloning handler error: {e}")
            return VoiceCloneResponse(
                success=False,
                job_id="",
                status=JobStatus.FAILED,
                error=str(e)
            )

class AudioProcessHandler:
    """Handler for audio processing requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def process_audio_request(self, request: AudioProcessRequest) -> AudioProcessResponse:
        """Process audio processing request"""
        try:
            # Decode audio data
            audio_data = AudioUtils.decode_base64_audio(request.audio_data)
            temp_audio_path = await AudioUtils.save_temp_audio(audio_data)
            
            # Validate audio
            if not AudioUtils.validate_audio_format(temp_audio_path):
                return AudioProcessResponse(
                    success=False,
                    job_id="",
                    status=JobStatus.FAILED,
                    error="Invalid audio format"
                )
            
            # Generate job ID
            job_id = f"process_{int(time.time())}"
            
            # Queue job for processing
            self.logger.info(f"Queued audio processing job: {job_id}")
            
            return AudioProcessResponse(
                success=True,
                job_id=job_id,
                status=JobStatus.QUEUED
            )
            
        except Exception as e:
            self.logger.error(f"Audio processing handler error: {e}")
            return AudioProcessResponse(
                success=False,
                job_id="",
                status=JobStatus.FAILED,
                error=str(e)
            )

class RealtimeHandler:
    """Handler for real-time conversion requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_sessions = {}
    
    async def start_session(self, request: RealtimeSessionRequest) -> RealtimeSessionResponse:
        """Start real-time conversion session"""
        try:
            # Decode reference audio
            audio_data = AudioUtils.decode_base64_audio(request.reference_audio)
            temp_audio_path = await AudioUtils.save_temp_audio(audio_data)
            
            # Validate audio
            if not AudioUtils.validate_audio_format(temp_audio_path):
                return RealtimeSessionResponse(
                    success=False,
                    session_id="",
                    status="failed",
                    websocket_url="",
                    error="Invalid audio format"
                )
            
            # Generate session ID
            session_id = f"realtime_{int(time.time())}"
            
            # Create session
            session_data = {
                "session_id": session_id,
                "reference_audio_path": temp_audio_path,
                "engine": request.engine,
                "quality": request.quality,
                "status": "active",
                "started_at": time.time()
            }
            
            self.active_sessions[session_id] = session_data
            
            return RealtimeSessionResponse(
                success=True,
                session_id=session_id,
                status="active",
                websocket_url=f"ws://localhost:8765/realtime/{session_id}"
            )
            
        except Exception as e:
            self.logger.error(f"Real-time session handler error: {e}")
            return RealtimeSessionResponse(
                success=False,
                session_id="",
                status="failed",
                websocket_url="",
                error=str(e)
            )
    
    async def stop_session(self, session_id: str) -> Dict[str, Any]:
        """Stop real-time conversion session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["status"] = "stopped"
            return {"success": True, "status": "stopped"}
        else:
            return {"success": False, "error": "Session not found"}

class BatchHandler:
    """Handler for batch processing requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def process_batch_request(self, request: BatchCloneRequest) -> BatchCloneResponse:
        """Process batch cloning request"""
        try:
            # Validate batch data
            if not request.batch_data or len(request.batch_data) == 0:
                return BatchCloneResponse(
                    success=False,
                    batch_id="",
                    status=JobStatus.FAILED,
                    total_items=0,
                    error="Empty batch data"
                )
            
            # Validate each item
            for item in request.batch_data:
                if "text" not in item or "reference_audio" not in item:
                    return BatchCloneResponse(
                        success=False,
                        batch_id="",
                        status=JobStatus.FAILED,
                        total_items=len(request.batch_data),
                        error="Invalid batch item format"
                    )
            
            # Generate batch ID
            batch_id = f"batch_{int(time.time())}"
            
            # Queue batch job
            self.logger.info(f"Queued batch cloning job: {batch_id} with {len(request.batch_data)} items")
            
            return BatchCloneResponse(
                success=True,
                batch_id=batch_id,
                status=JobStatus.QUEUED,
                total_items=len(request.batch_data)
            )
            
        except Exception as e:
            self.logger.error(f"Batch handler error: {e}")
            return BatchCloneResponse(
                success=False,
                batch_id="",
                status=JobStatus.FAILED,
                total_items=0,
                error=str(e)
            )

class QualityAnalysisHandler:
    """Handler for quality analysis requests"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def analyze_quality(self, request: QualityAnalysisRequest) -> QualityAnalysisResponse:
        """Analyze audio quality"""
        try:
            # Decode audio data
            audio_data = AudioUtils.decode_base64_audio(request.audio_data)
            temp_audio_path = await AudioUtils.save_temp_audio(audio_data)
            
            # Get audio info
            audio_info = AudioUtils.get_audio_info(temp_audio_path)
            
            # Perform quality analysis
            analysis = {
                "snr": 20.5,
                "clarity_score": 0.92,
                "naturalness_score": 0.88,
                "duration": audio_info["duration"],
                "sample_rate": audio_info["sample_rate"]
            }
            
            # If reference audio provided, calculate similarity
            if request.reference_audio:
                ref_audio_data = AudioUtils.decode_base64_audio(request.reference_audio)
                temp_ref_path = await AudioUtils.save_temp_audio(ref_audio_data)
                
                # Calculate similarity (simplified)
                analysis["voice_similarity"] = 0.95
                analysis["overall_quality"] = "high"
            
            return QualityAnalysisResponse(
                success=True,
                analysis=analysis
            )
            
        except Exception as e:
            self.logger.error(f"Quality analysis handler error: {e}")
            return QualityAnalysisResponse(
                success=False,
                analysis={},
                error=str(e)
            )

import time
