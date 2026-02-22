"""
Route-specific Pydantic models.

GAP-X06: Extracted from inline definitions in route files for:
- Centralized schema generation
- Contract versioning
- Frontend/backend synchronization

GAP-I16: New models should inherit from VoiceStudioBaseModel for consistent
null handling. Existing models are being migrated incrementally.

This module consolidates inline model definitions from backend/api/routes/*.py
into a single registry-friendly location.

See: docs/contracts/NULL_HANDLING_POLICY.md
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# GAP-I16: Import base model for consistent null handling
from backend.api.models import VoiceStudioBaseModel

# =============================================================================
# Timeline Models (from routes/timeline.py, GAP-I16)
# =============================================================================


class Clip(VoiceStudioBaseModel):
    """A clip on a timeline track."""

    id: str
    name: str
    audio_id: Optional[str] = None
    start_time: float = 0.0
    duration: float = 1.0
    volume: float = 1.0
    muted: bool = False
    locked: bool = False
    color: Optional[str] = None
    fade_in: float = 0.0
    fade_out: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Track(VoiceStudioBaseModel):
    """A track in the timeline (GAP-I16)."""

    id: str
    name: str
    track_type: str = "audio"
    clips: List[Clip] = Field(default_factory=list)
    volume: float = 1.0
    pan: float = 0.0
    muted: bool = False
    solo: bool = False
    locked: bool = False
    color: str | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TimelineState(VoiceStudioBaseModel):
    """Complete timeline state (GAP-I16)."""

    id: str
    name: str
    tracks: List[Track] = Field(default_factory=list)
    duration: float = 0.0
    playhead: float = 0.0
    loop_start: float | None = None
    loop_end: float | None = None
    playing: bool = False
    sample_rate: int = 44100
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AddTrackRequest(VoiceStudioBaseModel):
    """Request to add a track (GAP-I16)."""

    name: str
    track_type: str = "audio"
    position: int | None = None


class DeleteRequest(VoiceStudioBaseModel):
    """Request to delete a track or clip (GAP-I16)."""

    id: str
    force: bool = False


class DeleteResponse(VoiceStudioBaseModel):
    """Response from delete operation (GAP-I16)."""

    success: bool
    deleted_id: str
    message: str | None = None


class AddClipRequest(BaseModel):
    """Request to add a clip to a track."""

    track_id: str
    audio_id: str
    position: float
    name: Optional[str] = None
    duration: Optional[float] = None


class MoveClipRequest(BaseModel):
    """Request to move a clip."""

    clip_id: str
    new_position: float
    new_track: Optional[str] = None


class TrimClipRequest(BaseModel):
    """Request to trim a clip."""

    clip_id: str
    start_trim: float = 0.0
    end_trim: float = 0.0


class SplitClipRequest(BaseModel):
    """Request to split a clip at a position."""

    clip_id: str
    split_position: float


class SplitClipResponse(BaseModel):
    """Response from splitting a clip."""

    clip_1: Clip
    clip_2: Clip
    message: Optional[str] = None


class PlayheadRequest(BaseModel):
    """Request to set playhead position."""

    position: float
    snap_to_grid: bool = False


class LoopRequest(BaseModel):
    """Request to set loop region."""

    start: Optional[float] = None
    end: Optional[float] = None
    enabled: bool = True


class ExportRequest(BaseModel):
    """Request to export timeline."""

    format: str = "wav"
    sample_rate: int = 44100
    bit_depth: int = 16
    normalize: bool = False


class ExportResponse(BaseModel):
    """Response from export operation."""

    success: bool
    output_path: str
    duration: float
    file_size: int


class UndoResponse(BaseModel):
    """Response from undo/redo operation."""

    success: bool
    action: str
    state: Optional[TimelineState] = None


class UndoRedoState(BaseModel):
    """Current undo/redo state."""

    can_undo: bool
    can_redo: bool
    undo_description: Optional[str] = None
    redo_description: Optional[str] = None


# =============================================================================
# Project Models (from routes/projects.py)
# =============================================================================


class Project(BaseModel):
    """A project in the workspace."""

    id: str
    name: str
    description: Optional[str] = None
    sample_rate: int = 44100
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    path: Optional[str] = None


class ProjectCreateRequest(BaseModel):
    """Request to create a new project."""

    name: str
    description: Optional[str] = None
    sample_rate: int = 44100


class ProjectUpdateRequest(BaseModel):
    """Request to update project metadata."""

    name: Optional[str] = None
    description: Optional[str] = None


class ProjectAudioFile(BaseModel):
    """An audio file in a project."""

    id: str
    name: str
    path: str
    duration: float
    sample_rate: int
    channels: int
    created_at: Optional[datetime] = None


class ProjectAudioFileResponse(BaseModel):
    """Response with project audio files."""

    files: List[ProjectAudioFile]
    total: int


class SaveAudioRequest(BaseModel):
    """Request to save audio to project."""

    audio_id: str
    name: str
    format: str = "wav"


# =============================================================================
# Audio Models (from routes/audio.py)
# =============================================================================


class WaveformData(BaseModel):
    """Waveform visualization data."""

    min_values: List[float]
    max_values: List[float]
    rms_values: List[float]
    duration: float
    sample_rate: int
    samples_per_pixel: int


class SpectrogramFrame(BaseModel):
    """Single frame of spectrogram data."""

    frequencies: List[float]
    magnitudes: List[float]
    time: float


class SpectrogramData(BaseModel):
    """Complete spectrogram data."""

    frames: List[SpectrogramFrame]
    frequency_range: List[float]
    time_range: List[float]
    duration: float


class AudioMeters(BaseModel):
    """Audio metering values."""

    peak_left: float
    peak_right: float
    rms_left: float
    rms_right: float
    lufs: Optional[float] = None


class LoudnessData(BaseModel):
    """Loudness analysis data."""

    integrated: float
    short_term: List[float]
    momentary: List[float]
    range: float
    true_peak: float


class AudioUploadResponse(BaseModel):
    """Response from audio upload."""

    id: str
    name: str
    duration: float
    sample_rate: int
    channels: int
    format: str


class AudioExportRequest(BaseModel):
    """Request to export audio."""

    audio_id: str
    format: str = "wav"
    sample_rate: Optional[int] = None
    normalize: bool = False


class AudioExportResponse(BaseModel):
    """Response from audio export."""

    success: bool
    path: str
    size: int


# =============================================================================
# Training Models (from routes/training.py)
# =============================================================================


class TrainingDataset(BaseModel):
    """A training dataset configuration."""

    id: str
    name: str
    audio_files: List[str]
    transcript_path: Optional[str] = None
    speaker_id: Optional[str] = None
    total_duration: float = 0.0
    sample_rate: int = 22050
    created_at: Optional[datetime] = None


class TrainingRequest(BaseModel):
    """Request to start training."""

    dataset_id: str
    model_type: str = "rvc"
    epochs: int = 100
    batch_size: int = 8
    learning_rate: float = 1e-4
    resume_from: Optional[str] = None


class TrainingQualityMetrics(BaseModel):
    """Training quality metrics."""

    loss: float
    mel_loss: Optional[float] = None
    duration_loss: Optional[float] = None
    similarity_score: Optional[float] = None
    audio_quality: Optional[float] = None


class TrainingQualityAlert(BaseModel):
    """Alert about training quality."""

    severity: str
    message: str
    metric: str
    value: float
    threshold: float


class EarlyStoppingRecommendation(BaseModel):
    """Recommendation for early stopping."""

    should_stop: bool
    reason: Optional[str] = None
    best_epoch: int
    best_loss: float


class TrainingStatus(BaseModel):
    """Current training status."""

    id: str
    status: str
    epoch: int
    total_epochs: int
    loss: float
    progress: float
    eta_seconds: Optional[int] = None
    quality_metrics: Optional[TrainingQualityMetrics] = None
    alerts: List[TrainingQualityAlert] = Field(default_factory=list)
    recommendation: Optional[EarlyStoppingRecommendation] = None


class TrainingLogEntry(BaseModel):
    """A log entry from training."""

    timestamp: datetime
    level: str
    message: str
    epoch: Optional[int] = None
    loss: Optional[float] = None


class DatasetCreateRequest(BaseModel):
    """Request to create a training dataset."""

    name: str
    audio_paths: List[str]
    transcript_path: Optional[str] = None
    speaker_name: Optional[str] = None


class ModelExportRequest(BaseModel):
    """Request to export a trained model."""

    model_id: str
    format: str = "onnx"
    optimize: bool = True


class ModelExportResponse(BaseModel):
    """Response from model export."""

    success: bool
    path: str
    size: int
    format: str


# =============================================================================
# Voice Cloning Wizard Models (from routes/voice_cloning_wizard.py)
# =============================================================================


class WizardStepStatus(str, Enum):
    """Status of a wizard step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WizardJob(BaseModel):
    """A voice cloning wizard job."""

    id: str
    status: str
    current_step: str
    steps: Dict[str, str]
    progress: float
    voice_name: Optional[str] = None
    audio_files: List[str] = Field(default_factory=list)
    training_params: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class AudioValidationRequest(BaseModel):
    """Request to validate audio for voice cloning."""

    audio_path: str
    check_quality: bool = True


class AudioValidationResponse(BaseModel):
    """Response from audio validation."""

    valid: bool
    duration: float
    sample_rate: int
    channels: int
    issues: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class WizardStartRequest(BaseModel):
    """Request to start wizard."""

    voice_name: str
    audio_paths: List[str]
    model_type: str = "rvc"
    quality_preset: str = "balanced"


class WizardStartResponse(BaseModel):
    """Response from starting wizard."""

    job_id: str
    status: str
    estimated_time: Optional[int] = None


class WizardStatusResponse(BaseModel):
    """Response with wizard status."""

    job: WizardJob
    can_cancel: bool
    can_retry: bool


class WizardFinalizeRequest(BaseModel):
    """Request to finalize wizard."""

    job_id: str
    voice_name: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class WizardFinalizeResponse(BaseModel):
    """Response from finalizing wizard."""

    success: bool
    profile_id: str
    message: Optional[str] = None


# =============================================================================
# Voice Effects Models (from routes/voice_effects.py)
# =============================================================================


class ApplyEffectRequest(BaseModel):
    """Request to apply an audio effect."""

    audio_id: str
    effect_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class ApplyEffectResponse(BaseModel):
    """Response from applying effect."""

    success: bool
    output_id: str
    duration: float


class EffectPreset(BaseModel):
    """An effect preset configuration."""

    id: str
    name: str
    effect_type: str
    parameters: Dict[str, Any]
    description: Optional[str] = None


class HotkeyConfig(BaseModel):
    """Hotkey configuration for effects."""

    effect_id: str
    key_combo: str
    enabled: bool = True


class RealtimeSessionRequest(BaseModel):
    """Request to start realtime effect session."""

    input_device: str
    output_device: str
    effects: List[str] = Field(default_factory=list)


class RealtimeSessionResponse(BaseModel):
    """Response from realtime session."""

    session_id: str
    status: str
    latency_ms: float


# =============================================================================
# Transcription Models (from routes/transcribe.py)
# =============================================================================


class WordTimestamp(BaseModel):
    """A word with timing information."""

    word: str
    start: float
    end: float
    confidence: float = 1.0


class TranscriptionSegment(BaseModel):
    """A segment of transcription."""

    id: int
    start: float
    end: float
    text: str
    words: List[WordTimestamp] = Field(default_factory=list)
    speaker: Optional[str] = None


class TranscriptionRequest(BaseModel):
    """Request to transcribe audio."""

    audio_id: str
    language: Optional[str] = None
    model: str = "base"
    word_timestamps: bool = False
    diarize: bool = False


class TranscriptionResponse(BaseModel):
    """Response from transcription."""

    text: str
    segments: List[TranscriptionSegment]
    language: str
    duration: float
    confidence: float


class SupportedLanguage(BaseModel):
    """A supported transcription language."""

    code: str
    name: str
    native_name: str


class TranscriptionUpdateRequest(BaseModel):
    """Request to update transcription."""

    segment_id: int
    text: str


# =============================================================================
# Quality Analysis Models (from routes/quality.py)
# =============================================================================


class QualityAnalysisRequest(BaseModel):
    """Request to analyze audio quality."""

    audio_id: str
    reference_id: Optional[str] = None
    metrics: List[str] = Field(default_factory=list)


class QualityAnalysisResponse(BaseModel):
    """Response from quality analysis."""

    overall_score: float
    metrics: Dict[str, float]
    issues: List[str] = Field(default_factory=list)


class QualityOptimizationRequest(BaseModel):
    """Request to optimize audio quality."""

    audio_id: str
    target_metrics: Dict[str, float] = Field(default_factory=dict)


class QualityOptimizationResponse(BaseModel):
    """Response from optimization."""

    success: bool
    output_id: str
    improvements: Dict[str, float] = Field(default_factory=dict)


class BenchmarkRequest(BaseModel):
    """Request to run quality benchmark."""

    audio_ids: List[str]
    reference_id: Optional[str] = None
    metrics: List[str] = Field(default_factory=list)
    engine_id: Optional[str] = None


class BenchmarkResult(BaseModel):
    """A single benchmark result."""

    audio_id: str
    metrics: Dict[str, float]
    duration: float
    engine: Optional[str] = None


class BenchmarkResponse(BaseModel):
    """Response from benchmark."""

    results: List[BenchmarkResult]
    summary: Dict[str, Any]
    elapsed_time: float


# =============================================================================
# Workflow Models (from routes/workflows.py)
# =============================================================================


class WorkflowVariable(BaseModel):
    """A workflow variable definition."""

    name: str
    type: str
    default: Optional[Any] = None
    required: bool = False


class WorkflowStep(BaseModel):
    """A step in a workflow."""

    id: str
    type: str
    name: str
    config: Dict[str, Any] = Field(default_factory=dict)
    inputs: Dict[str, str] = Field(default_factory=dict)
    outputs: List[str] = Field(default_factory=list)


class Workflow(BaseModel):
    """A workflow definition."""

    id: str
    name: str
    description: Optional[str] = None
    variables: List[WorkflowVariable] = Field(default_factory=list)
    steps: List[WorkflowStep] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class WorkflowCreateRequest(BaseModel):
    """Request to create a workflow."""

    name: str
    description: Optional[str] = None
    variables: List[WorkflowVariable] = Field(default_factory=list)
    steps: List[WorkflowStep] = Field(default_factory=list)


class WorkflowUpdateRequest(BaseModel):
    """Request to update a workflow."""

    name: Optional[str] = None
    description: Optional[str] = None
    variables: Optional[List[WorkflowVariable]] = None
    steps: Optional[List[WorkflowStep]] = None


class WorkflowExecutionRequest(BaseModel):
    """Request to execute a workflow."""

    workflow_id: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    async_mode: bool = False


class WorkflowExecutionResult(BaseModel):
    """Result of workflow execution."""

    execution_id: str
    status: str
    outputs: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    elapsed_time: float


# =============================================================================
# Settings Models (from routes/settings.py)
# =============================================================================


class GeneralSettings(BaseModel):
    """General application settings."""

    theme: str = "system"
    language: str = "en"
    auto_save: bool = True
    auto_save_interval: int = 300


class EngineSettings(BaseModel):
    """Engine configuration settings."""

    default_engine: str = "piper"
    gpu_enabled: bool = True
    max_concurrent_jobs: int = 2


class AudioSettings(BaseModel):
    """Audio configuration settings."""

    sample_rate: int = 44100
    bit_depth: int = 16
    channels: int = 2
    format: str = "wav"


class TimelineSettings(BaseModel):
    """Timeline configuration settings."""

    snap_to_grid: bool = True
    grid_size: float = 0.1
    auto_scroll: bool = True
    show_waveforms: bool = True


class PerformanceSettings(BaseModel):
    """Performance configuration settings."""

    cache_size_mb: int = 512
    max_undo_steps: int = 50
    preload_audio: bool = True
    gpu_memory_fraction: float = 0.8


class SettingsData(BaseModel):
    """Complete settings data."""

    general: GeneralSettings = Field(default_factory=GeneralSettings)
    engine: EngineSettings = Field(default_factory=EngineSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    timeline: TimelineSettings = Field(default_factory=TimelineSettings)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)


# =============================================================================
# Search Models (from routes/search.py)
# =============================================================================


class SearchResultItem(BaseModel):
    """A single search result."""

    id: str
    type: str
    name: str
    description: Optional[str] = None
    path: Optional[str] = None
    score: float = 1.0
    highlights: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParsedQuery(BaseModel):
    """A parsed search query."""

    original: str
    tokens: List[str]
    filters: Dict[str, Any] = Field(default_factory=dict)
    operators: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Response from search."""

    query: ParsedQuery
    results: List[SearchResultItem]
    total: int
    page: int
    per_page: int
    elapsed_ms: float


# =============================================================================
# Model Registry for Schema Generation
# =============================================================================

# All models that should be exported as JSON schemas
ROUTE_MODELS = [
    # Timeline
    Clip,
    Track,
    TimelineState,
    AddTrackRequest,
    DeleteRequest,
    DeleteResponse,
    AddClipRequest,
    MoveClipRequest,
    TrimClipRequest,
    SplitClipRequest,
    SplitClipResponse,
    PlayheadRequest,
    LoopRequest,
    ExportRequest,
    ExportResponse,
    UndoResponse,
    UndoRedoState,
    # Project
    Project,
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectAudioFile,
    ProjectAudioFileResponse,
    SaveAudioRequest,
    # Audio
    WaveformData,
    SpectrogramFrame,
    SpectrogramData,
    AudioMeters,
    LoudnessData,
    AudioUploadResponse,
    AudioExportRequest,
    AudioExportResponse,
    # Training
    TrainingDataset,
    TrainingRequest,
    TrainingQualityMetrics,
    TrainingQualityAlert,
    EarlyStoppingRecommendation,
    TrainingStatus,
    TrainingLogEntry,
    DatasetCreateRequest,
    ModelExportRequest,
    ModelExportResponse,
    # Wizard
    WizardJob,
    AudioValidationRequest,
    AudioValidationResponse,
    WizardStartRequest,
    WizardStartResponse,
    WizardStatusResponse,
    WizardFinalizeRequest,
    WizardFinalizeResponse,
    # Effects
    ApplyEffectRequest,
    ApplyEffectResponse,
    EffectPreset,
    HotkeyConfig,
    RealtimeSessionRequest,
    RealtimeSessionResponse,
    # Transcription
    WordTimestamp,
    TranscriptionSegment,
    TranscriptionRequest,
    TranscriptionResponse,
    SupportedLanguage,
    TranscriptionUpdateRequest,
    # Quality
    QualityAnalysisRequest,
    QualityAnalysisResponse,
    QualityOptimizationRequest,
    QualityOptimizationResponse,
    BenchmarkRequest,
    BenchmarkResult,
    BenchmarkResponse,
    # Workflow
    WorkflowVariable,
    WorkflowStep,
    Workflow,
    WorkflowCreateRequest,
    WorkflowUpdateRequest,
    WorkflowExecutionRequest,
    WorkflowExecutionResult,
    # Settings
    GeneralSettings,
    EngineSettings,
    AudioSettings,
    TimelineSettings,
    PerformanceSettings,
    SettingsData,
    # Search
    SearchResultItem,
    ParsedQuery,
    SearchResponse,
]
