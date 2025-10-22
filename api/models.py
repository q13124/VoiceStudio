# api/models.py
# Pydantic models for VoiceStudio API

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class EngineType(str, Enum):
    XTTS = "xtts"
    OPENVOICE = "openvoice"
    COSYVOICE2 = "cosyvoice2"
    COQUI = "coqui"

class QualityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class LatencyMode(str, Enum):
    ULTRA = "ultra"
    LOW = "low"
    NORMAL = "normal"

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VoiceCloneRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    reference_audio: str = Field(..., description="Base64 encoded reference audio")
    engine: EngineType = Field(default=EngineType.XTTS, description="Voice cloning engine")
    language: str = Field(default="en", description="Language code")
    quality: QualityLevel = Field(default=QualityLevel.HIGH, description="Quality level")
    latency: LatencyMode = Field(default=LatencyMode.NORMAL, description="Latency mode")
    prosody_overrides: Optional[Dict[str, Any]] = Field(None, description="Prosody overrides")
    watermark: bool = Field(default=False, description="Apply watermark")
    policy_key: Optional[str] = Field(None, description="Policy key for watermarking")

class VoiceCloneResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Job status")
    estimated_time: Optional[float] = Field(None, description="Estimated processing time")
    error: Optional[str] = Field(None, description="Error message if failed")

class JobStatusResponse(BaseModel):
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Job status")
    created_at: datetime = Field(..., description="Job creation time")
    completed_at: Optional[datetime] = Field(None, description="Job completion time")
    result: Optional[Dict[str, Any]] = Field(None, description="Job result")
    error: Optional[str] = Field(None, description="Error message if failed")

class AudioProcessRequest(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio data")
    dsp_chain: Dict[str, Any] = Field(default_factory=dict, description="DSP processing chain")
    output_format: str = Field(default="wav", description="Output audio format")

class AudioProcessResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    job_id: str = Field(..., description="Job identifier")
    status: JobStatus = Field(..., description="Job status")
    error: Optional[str] = Field(None, description="Error message if failed")

class EngineInfo(BaseModel):
    name: str = Field(..., description="Engine name")
    display_name: str = Field(..., description="Display name")
    status: str = Field(..., description="Engine status")
    languages: List[str] = Field(..., description="Supported languages")
    quality: str = Field(..., description="Quality level")
    latency: str = Field(..., description="Latency mode")

class EngineStatusResponse(BaseModel):
    engines: List[EngineInfo] = Field(..., description="List of available engines")

class RealtimeSessionRequest(BaseModel):
    reference_audio: str = Field(..., description="Base64 encoded reference audio")
    engine: EngineType = Field(default=EngineType.XTTS, description="Voice cloning engine")
    quality: QualityLevel = Field(default=QualityLevel.HIGH, description="Quality level")

class RealtimeSessionResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    session_id: str = Field(..., description="Session identifier")
    status: str = Field(..., description="Session status")
    websocket_url: str = Field(..., description="WebSocket URL for real-time communication")
    error: Optional[str] = Field(None, description="Error message if failed")

class BatchCloneRequest(BaseModel):
    batch_data: List[Dict[str, str]] = Field(..., description="Batch data items")
    engine: EngineType = Field(default=EngineType.XTTS, description="Voice cloning engine")
    quality: QualityLevel = Field(default=QualityLevel.HIGH, description="Quality level")

class BatchCloneResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    batch_id: str = Field(..., description="Batch identifier")
    status: JobStatus = Field(..., description="Batch status")
    total_items: int = Field(..., description="Total number of items")
    error: Optional[str] = Field(None, description="Error message if failed")

class QualityAnalysisRequest(BaseModel):
    audio_data: str = Field(..., description="Base64 encoded audio data")
    reference_audio: Optional[str] = Field(None, description="Base64 encoded reference audio")

class QualityAnalysisResponse(BaseModel):
    success: bool = Field(..., description="Success status")
    analysis: Dict[str, Any] = Field(..., description="Quality analysis results")
    error: Optional[str] = Field(None, description="Error message if failed")

class SystemStatusResponse(BaseModel):
    system: Dict[str, Any] = Field(..., description="System information")
    performance: Dict[str, Any] = Field(..., description="Performance metrics")
    jobs: Dict[str, Any] = Field(..., description="Job statistics")
    engines: Dict[str, Any] = Field(..., description="Engine status")

class MetricsResponse(BaseModel):
    metrics: Dict[str, Any] = Field(..., description="Performance metrics")
