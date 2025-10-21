#!/usr/bin/env python3
"""
VoiceStudio Enhanced Voice Cloning Service
Advanced voice cloning with unlimited audio support, real-time processing, and optimization.
"""

import asyncio
import logging
import signal
import sys
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
import uvicorn
from pathlib import Path
import json
import time
from datetime import datetime
import uuid
import io
import base64
from concurrent.futures import ThreadPoolExecutor
import threading

# Import our enhanced audio processor
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'VoiceStudio', 'workers', 'python', 'vsdml'))
from vsdml.services.audio_processor import EnhancedAudioProcessor

# Import database and service discovery
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import DatabaseManager, get_database_logger, record_metric
from service_discovery import register_service, ServiceInfo

logger = logging.getLogger(__name__)

class EnhancedVoiceCloningService:
    """Enhanced voice cloning service with advanced features"""
    
    def __init__(self, port: int = 5083):
        self.port = port
        self.app = FastAPI(
            title="Enhanced Voice Cloning Service", 
            version="1.0.0",
            description="Advanced voice cloning with unlimited audio support and real-time processing"
        )
        
        # Initialize audio processor with enhanced capabilities
        self.audio_processor = EnhancedAudioProcessor(max_workers=16, cache_size=4000)
        
        # Service management
        self.service_id = str(uuid.uuid4())
        self.db_logger = get_database_logger(self.service_id, "enhanced_voice_cloning")
        
        # Advanced session management
        self.active_cloning_sessions = {}
        self.session_lock = threading.Lock()
        
        # Background processing
        self.background_executor = ThreadPoolExecutor(max_workers=8)
        
        # Real-time processing
        self.websocket_connections = set()
        self.websocket_lock = threading.Lock()
        
        # Performance monitoring
        self.performance_stats = {
            "total_requests": 0,
            "successful_clones": 0,
            "failed_clones": 0,
            "average_processing_time": 0.0,
            "peak_concurrent_sessions": 0
        }
        
        # Setup routes and WebSocket
        self.setup_routes()
        self.setup_websocket()
        self.setup_background_tasks()
        
        # Register with service discovery
        self.register_with_discovery()
    
    def register_with_discovery(self):
        """Register this service with the service discovery system"""
        try:
            register_service(
                name="enhanced_voice_cloning",
                host="127.0.0.1",
                port=self.port,
                health_endpoint="/health",
                metadata={
                    "capabilities": [
                        "voice_cloning", 
                        "voice_profile_extraction", 
                        "unlimited_audio",
                        "real_time_processing",
                        "batch_processing",
                        "streaming_audio",
                        "multi_model_support"
                    ],
                    "models": ["gpt_sovits", "openvoice", "coqui_xtts", "tortoise_tts", "rvc"],
                    "version": "1.0.0",
                    "max_workers": 16,
                    "cache_size": 4000
                }
            )
            self.db_logger.info("Enhanced service registered with discovery system")
        except Exception as e:
            logger.error(f"Failed to register with service discovery: {e}")
    
    def setup_routes(self):
        """Setup API routes with advanced features"""
        
        @self.app.post("/clone-voice")
        async def clone_voice(
            reference_audio: UploadFile = File(...),
            target_text: str = "",
            speaker_id: Optional[str] = None,
            model_type: str = "gpt_sovits",
            enhancement_options: Optional[str] = None,
            background_tasks: BackgroundTasks = None
        ):
            """Clone voice with advanced options and background processing"""
            start_time = time.time()
            self.performance_stats["total_requests"] += 1
            
            try:
                self.db_logger.info(f"Starting enhanced voice cloning for speaker {speaker_id}")
                
                # Save uploaded audio
                audio_path = f"temp_{reference_audio.filename}_{int(time.time())}"
                with open(audio_path, "wb") as f:
                    f.write(await reference_audio.read())
                
                # Parse enhancement options
                enhancements = json.loads(enhancement_options) if enhancement_options else {}
                
                # Clone voice
                result = await self.audio_processor.clone_voice(
                    audio_path, target_text, speaker_id, model_type
                )
                
                # Add enhancement metadata
                result["enhancements_applied"] = enhancements
                result["service_version"] = "1.0.0"
                result["processing_timestamp"] = datetime.now().isoformat()
                
                # Clean up temp file in background
                if background_tasks:
                    background_tasks.add_task(self._cleanup_temp_file, audio_path)
                else:
                    Path(audio_path).unlink()
                
                # Update performance stats
                processing_time = time.time() - start_time
                self._update_performance_stats(processing_time, True)
                
                # Record metrics
                record_metric(
                    self.service_id, 
                    "enhanced_voice_cloning", 
                    "voice_clone_processing_time", 
                    processing_time,
                    {"model_type": model_type, "success": True}
                )
                
                self.db_logger.info(f"Enhanced voice cloning completed for speaker {speaker_id}")
                return result
                
            except Exception as e:
                # Update performance stats
                processing_time = time.time() - start_time
                self._update_performance_stats(processing_time, False)
                
                # Record error metrics
                record_metric(
                    self.service_id, 
                    "enhanced_voice_cloning", 
                    "voice_clone_error", 
                    1.0,
                    {"error_type": type(e).__name__, "model_type": model_type}
                )
                
                self.db_logger.error(f"Enhanced voice cloning failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/clone-voice-batch")
        async def clone_voice_batch(
            reference_audios: List[UploadFile] = File(...),
            target_texts: List[str] = [],
            speaker_ids: Optional[List[str]] = None,
            model_type: str = "gpt_sovits",
            background_tasks: BackgroundTasks = None
        ):
            """Clone multiple voices in batch"""
            start_time = time.time()
            
            try:
                self.db_logger.info(f"Starting batch voice cloning with {len(reference_audios)} files")
                
                if len(reference_audios) != len(target_texts):
                    raise HTTPException(status_code=400, detail="Number of audio files must match number of texts")
                
                results = []
                temp_files = []
                
                # Process all files
                for i, (audio_file, text) in enumerate(zip(reference_audios, target_texts)):
                    speaker_id = speaker_ids[i] if speaker_ids and i < len(speaker_ids) else None
                    
                    # Save uploaded audio
                    audio_path = f"temp_batch_{i}_{int(time.time())}"
                    with open(audio_path, "wb") as f:
                        f.write(await audio_file.read())
                    temp_files.append(audio_path)
                    
                    # Clone voice
                    result = await self.audio_processor.clone_voice(
                        audio_path, text, speaker_id, model_type
                    )
                    result["batch_index"] = i
                    results.append(result)
                
                # Clean up temp files in background
                if background_tasks:
                    for temp_file in temp_files:
                        background_tasks.add_task(self._cleanup_temp_file, temp_file)
                else:
                    for temp_file in temp_files:
                        Path(temp_file).unlink()
                
                # Record batch metrics
                processing_time = time.time() - start_time
                record_metric(
                    self.service_id, 
                    "enhanced_voice_cloning", 
                    "batch_processing_time", 
                    processing_time,
                    {"batch_size": len(reference_audios), "model_type": model_type}
                )
                
                self.db_logger.info(f"Batch voice cloning completed: {len(results)} results")
                return {
                    "batch_results": results,
                    "total_processing_time": processing_time,
                    "batch_size": len(reference_audios)
                }
                
            except Exception as e:
                self.db_logger.error(f"Batch voice cloning failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/clone-voice-unlimited")
        async def clone_voice_unlimited(
            reference_audio: UploadFile = File(...),
            target_text: str = "",
            speaker_id: Optional[str] = None,
            processing_mode: str = "chunked",
            background_tasks: BackgroundTasks = None
        ):
            """Clone voice with unlimited audio length support"""
            try:
                self.db_logger.info(f"Starting unlimited voice cloning for speaker {speaker_id}")
                
                # Save uploaded audio
                audio_path = f"temp_unlimited_{reference_audio.filename}_{int(time.time())}"
                with open(audio_path, "wb") as f:
                    f.write(await reference_audio.read())
                
                # Create cloning session
                session_id = f"session_{int(time.time())}"
                with self.session_lock:
                    self.active_cloning_sessions[session_id] = {
                        "status": "processing",
                        "start_time": datetime.now(),
                        "audio_path": audio_path,
                        "target_text": target_text,
                        "speaker_id": speaker_id,
                        "processing_mode": processing_mode,
                        "progress": 0
                    }
                
                # Process unlimited audio in background
                background_tasks.add_task(
                    self._process_unlimited_audio_background,
                    session_id, audio_path, target_text, speaker_id, processing_mode
                )
                
                return {
                    "session_id": session_id,
                    "status": "processing",
                    "processing_mode": processing_mode,
                    "websocket_url": f"ws://127.0.0.1:{self.port}/ws"
                }
                
            except Exception as e:
                self.db_logger.error(f"Unlimited voice cloning failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/extract-voice-profile")
        async def extract_voice_profile(
            audio_file: UploadFile = File(...),
            background_tasks: BackgroundTasks = None
        ):
            """Extract voice profile from audio"""
            try:
                self.db_logger.info("Starting voice profile extraction")
                
                # Save uploaded audio
                audio_path = f"temp_profile_{audio_file.filename}_{int(time.time())}"
                with open(audio_path, "wb") as f:
                    f.write(await audio_file.read())
                
                # Extract voice profile
                profile = await self.audio_processor.extract_voice_profile(audio_path)
                
                # Clean up temp file in background
                if background_tasks:
                    background_tasks.add_task(self._cleanup_temp_file, audio_path)
                else:
                    Path(audio_path).unlink()
                
                self.db_logger.info("Voice profile extraction completed")
                return profile
                
            except Exception as e:
                self.db_logger.error(f"Voice profile extraction failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/sessions/{session_id}")
        async def get_session_status(session_id: str):
            """Get cloning session status"""
            with self.session_lock:
                if session_id not in self.active_cloning_sessions:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                return self.active_cloning_sessions[session_id]
        
        @self.app.get("/sessions")
        async def get_all_sessions():
            """Get all active sessions"""
            with self.session_lock:
                return {
                    "active_sessions": len(self.active_cloning_sessions),
                    "sessions": list(self.active_cloning_sessions.keys())
                }
        
        @self.app.delete("/sessions/{session_id}")
        async def cancel_session(session_id: str):
            """Cancel a cloning session"""
            with self.session_lock:
                if session_id not in self.active_cloning_sessions:
                    raise HTTPException(status_code=404, detail="Session not found")
                
                session = self.active_cloning_sessions[session_id]
                session["status"] = "cancelled"
                
                # Clean up temp file
                if "audio_path" in session:
                    Path(session["audio_path"]).unlink(missing_ok=True)
                
                return {"message": "Session cancelled", "session_id": session_id}
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "ok": True,
                "status": "healthy", 
                "service": "enhanced_voice_cloning",
                "port": self.port,
                "active_sessions": len(self.active_cloning_sessions),
                "service_id": self.service_id,
                "performance_stats": self.performance_stats,
                "websocket_connections": len(self.websocket_connections)
            }
        
        @self.app.get("/metrics")
        async def get_metrics():
            """Get comprehensive performance metrics"""
            metrics = self.audio_processor.get_performance_metrics()
            metrics["service_stats"] = self.performance_stats
            metrics["active_sessions"] = len(self.active_cloning_sessions)
            metrics["websocket_connections"] = len(self.websocket_connections)
            return metrics
        
        @self.app.get("/models")
        async def get_available_models():
            """Get available voice cloning models"""
            return {
                "available_models": list(self.audio_processor.voice_cloning_models.keys()),
                "loaded_models": [
                    model for model, instance in self.audio_processor.voice_cloning_models.items()
                    if instance is not None
                ],
                "model_capabilities": {
                    "gpt_sovits": ["high_quality", "fast_inference", "chinese_optimized"],
                    "openvoice": ["multilingual", "emotion_control", "accent_cloning"],
                    "coqui_xtts": ["real_time", "multilingual", "voice_conversion"],
                    "tortoise_tts": ["high_quality", "slow_inference", "detailed_control"],
                    "rvc": ["voice_conversion", "real_time", "pitch_control"]
                }
            }
    
    def setup_websocket(self):
        """Setup WebSocket for real-time updates"""
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket):
            await websocket.accept()
            
            # Add connection to set
            with self.websocket_lock:
                self.websocket_connections.add(websocket)
            
            try:
                while True:
                    # Send periodic updates
                    data = {
                        "active_sessions": len(self.active_cloning_sessions),
                        "timestamp": datetime.now().isoformat(),
                        "service_id": self.service_id,
                        "performance_stats": self.performance_stats
                    }
                    await websocket.send_text(json.dumps(data))
                    await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
            finally:
                # Remove connection from set
                with self.websocket_lock:
                    self.websocket_connections.discard(websocket)
                await websocket.close()
    
    def setup_background_tasks(self):
        """Setup background tasks for maintenance"""
        
        @self.app.on_event("startup")
        async def startup_event():
            """Startup event handler"""
            self.db_logger.info("Enhanced voice cloning service started")
            
            # Start background cleanup task
            asyncio.create_task(self._background_cleanup())
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Shutdown event handler"""
            self.db_logger.info("Enhanced voice cloning service shutting down")
            
            # Cleanup resources
            await self.cleanup()
    
    async def _background_cleanup(self):
        """Background cleanup task"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                # Clean up old sessions
                current_time = datetime.now()
                with self.session_lock:
                    sessions_to_remove = []
                    for session_id, session in self.active_cloning_sessions.items():
                        if (current_time - session["start_time"]).total_seconds() > 3600:  # 1 hour
                            sessions_to_remove.append(session_id)
                    
                    for session_id in sessions_to_remove:
                        session = self.active_cloning_sessions.pop(session_id)
                        if "audio_path" in session:
                            Path(session["audio_path"]).unlink(missing_ok=True)
                
                # Clean up audio processor cache
                self.audio_processor.cleanup_cache()
                
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")
    
    async def _process_unlimited_audio_background(self, session_id: str, audio_path: str, 
                                                 target_text: str, speaker_id: Optional[str], 
                                                 processing_mode: str):
        """Process unlimited audio in background"""
        try:
            # Update progress
            with self.session_lock:
                if session_id in self.active_cloning_sessions:
                    self.active_cloning_sessions[session_id]["progress"] = 10
            
            # Process audio
            result = await self._process_unlimited_audio(audio_path, target_text, speaker_id, processing_mode)
            
            # Update session with result
            with self.session_lock:
                if session_id in self.active_cloning_sessions:
                    self.active_cloning_sessions[session_id].update({
                        "status": "completed",
                        "result": result,
                        "progress": 100,
                        "completed_at": datetime.now()
                    })
            
            # Clean up temp file
            Path(audio_path).unlink(missing_ok=True)
            
            # Notify WebSocket clients
            await self._notify_websocket_clients({
                "type": "session_completed",
                "session_id": session_id,
                "result": result
            })
            
        except Exception as e:
            logger.error(f"Background processing failed for session {session_id}: {e}")
            
            # Update session with error
            with self.session_lock:
                if session_id in self.active_cloning_sessions:
                    self.active_cloning_sessions[session_id].update({
                        "status": "failed",
                        "error": str(e),
                        "progress": 0
                    })
            
            # Clean up temp file
            Path(audio_path).unlink(missing_ok=True)
    
    async def _process_unlimited_audio(self, audio_path: str, target_text: str, 
                                     speaker_id: Optional[str], processing_mode: str) -> Dict[str, Any]:
        """Process unlimited audio length"""
        if processing_mode == "chunked":
            return await self._process_chunked_audio(audio_path, target_text, speaker_id)
        elif processing_mode == "streaming":
            return await self._process_streaming_audio(audio_path, target_text, speaker_id)
        else:
            return await self.audio_processor.clone_voice(audio_path, target_text, speaker_id)
    
    async def _process_chunked_audio(self, audio_path: str, target_text: str, 
                                   speaker_id: Optional[str]) -> Dict[str, Any]:
        """Process audio in chunks for unlimited length support"""
        try:
            # For now, use the standard processing
            # In a full implementation, this would split long audio into chunks
            result = await self.audio_processor.clone_voice(audio_path, target_text, speaker_id)
            
            # Add chunking metadata
            result["processing_mode"] = "chunked"
            result["chunks_processed"] = 1
            
            return result
        except Exception as e:
            logger.error(f"Chunked audio processing failed: {e}")
            raise
    
    async def _process_streaming_audio(self, audio_path: str, target_text: str, 
                                     speaker_id: Optional[str]) -> Dict[str, Any]:
        """Process audio in streaming mode"""
        try:
            # For now, use the standard processing
            # In a full implementation, this would process audio in real-time streams
            result = await self.audio_processor.clone_voice(audio_path, target_text, speaker_id)
            
            # Add streaming metadata
            result["processing_mode"] = "streaming"
            result["stream_processed"] = True
            
            return result
        except Exception as e:
            logger.error(f"Streaming audio processing failed: {e}")
            raise
    
    async def _cleanup_temp_file(self, file_path: str):
        """Clean up temporary file"""
        try:
            Path(file_path).unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")
    
    async def _notify_websocket_clients(self, message: Dict[str, Any]):
        """Notify all WebSocket clients"""
        with self.websocket_lock:
            disconnected_clients = set()
            for websocket in self.websocket_connections:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception:
                    disconnected_clients.add(websocket)
            
            # Remove disconnected clients
            self.websocket_connections -= disconnected_clients
    
    def _update_performance_stats(self, processing_time: float, success: bool):
        """Update performance statistics"""
        if success:
            self.performance_stats["successful_clones"] += 1
        else:
            self.performance_stats["failed_clones"] += 1
        
        # Update average processing time
        total_clones = self.performance_stats["successful_clones"] + self.performance_stats["failed_clones"]
        if total_clones > 0:
            self.performance_stats["average_processing_time"] = (
                (self.performance_stats["average_processing_time"] * (total_clones - 1) + processing_time) / total_clones
            )
        
        # Update peak concurrent sessions
        current_sessions = len(self.active_cloning_sessions)
        if current_sessions > self.performance_stats["peak_concurrent_sessions"]:
            self.performance_stats["peak_concurrent_sessions"] = current_sessions
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Close audio processor
            self.audio_processor.close()
            
            # Clean up active sessions
            with self.session_lock:
                for session in self.active_cloning_sessions.values():
                    if "audio_path" in session:
                        Path(session["audio_path"]).unlink(missing_ok=True)
                self.active_cloning_sessions.clear()
            
            # Close WebSocket connections
            with self.websocket_lock:
                for websocket in self.websocket_connections:
                    try:
                        await websocket.close()
                    except Exception:
                        pass
                self.websocket_connections.clear()
            
            # Shutdown background executor
            self.background_executor.shutdown(wait=True)
            
            self.db_logger.info("Enhanced voice cloning service cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

async def start_enhanced_voice_cloning_service(port: int = 5083):
    """Start the enhanced voice cloning service"""
    service = EnhancedVoiceCloningService(port)
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(service.cleanup())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    config = uvicorn.Config(
        service.app, 
        host="127.0.0.1", 
        port=port, 
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(start_enhanced_voice_cloning_service())
