import re
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, validator


class AbxStartRequest(BaseModel):
    items: List[str]


class AbxResult(BaseModel):
    item: str
    mos: float
    pref: str


class DatasetScoreRequest(BaseModel):
    clips: List[str]


class ScoreResult(BaseModel):
    clip: str
    snr: float
    lufs: float
    quality: float


class Telemetry(BaseModel):
    engine_ms: float
    underruns: int
    vram_pct: float


class AdrAlignRequest(BaseModel):
    video_id: str
    audio_id: str


class ProsodyQuantizeRequest(BaseModel):
    audio_id: str
    grid: str = "1/8"


class EmotionApplyRequest(BaseModel):
    audio_id: str
    curve: List[float]


class FormantEditRequest(BaseModel):
    audio_id: str
    shifts: Dict[str, float]


class SpectralInpaintRequest(BaseModel):
    audio_id: str
    mask: str


class ModelInspectRequest(BaseModel):
    layer: int


class GranularRenderRequest(BaseModel):
    audio_id: str
    params: Dict[str, Any]


class RvcStartRequest(BaseModel):
    target_voice: str


class DubTranslateRequest(BaseModel):
    audio_id: str
    lang: str


class ArticulationAnalyzeRequest(BaseModel):
    audio_id: str


class NrApplyRequest(BaseModel):
    audio_id: str
    noise_print_id: str


class RepairClippingRequest(BaseModel):
    audio_id: str


class SceneMixAnalyzeRequest(BaseModel):
    tracks: List[str]


class RmTrainRequest(BaseModel):
    ratings: List[Dict[str, Any]]


class SafetyScanRequest(BaseModel):
    text: str


class ImgSamplerRequest(BaseModel):
    prompt: str
    sampler: str = "ddim"


class AssistantRunRequest(BaseModel):
    action_id: str
    params: Optional[Dict[str, Any]] = None


# Voice Cloning Models
class VoiceSynthesizeRequest(BaseModel):
    """Request model for voice synthesis with validation."""

    model_config = ConfigDict(
        # Optimize validation performance
        validate_assignment=False,  # Skip validation on assignment
        use_enum_values=True,  # Use enum values directly
        str_strip_whitespace=True,  # Strip whitespace automatically
        validate_default=False,  # Skip validation for default values
    )

    engine: str = Field(
        ...,
        description="Engine name (e.g., chatterbox, xtts, tortoise)",
        min_length=1,
        max_length=50,
    )
    profile_id: str = Field(
        ..., description="Voice profile ID", min_length=1, max_length=100
    )
    text: str = Field(
        ..., description="Text to synthesize", min_length=1, max_length=10000
    )
    language: Optional[str] = Field(
        default="en", description="Language code (ISO 639-1)", max_length=10
    )
    emotion: Optional[str] = Field(
        default=None, description="Emotion to apply", max_length=50
    )
    enhance_quality: Optional[bool] = Field(
        default=False, description="Enable quality enhancement pipeline"
    )

    @validator("engine")
    def validate_engine(cls, v):
        """Validate engine name format."""
        if not re.match(r"^[a-z0-9_-]+$", v.lower()):
            raise ValueError(
                "Engine name must contain only lowercase letters, numbers, hyphens, and underscores"
            )
        return v.lower()

    @validator("profile_id")
    def validate_profile_id(cls, v):
        """Validate profile ID format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Profile ID must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v

    @validator("language")
    def validate_language(cls, v):
        """Validate language code format."""
        if v and not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", v.lower()):
            raise ValueError(
                "Language must be a valid ISO 639-1 code (e.g., 'en', 'en-US')"
            )
        return v.lower() if v else v

    @validator("text")
    def validate_text(cls, v):
        """Validate text content."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        if len(v.strip()) > 10000:
            raise ValueError("Text cannot exceed 10000 characters")
        return v.strip()


class QualityMetrics(BaseModel):
    """Detailed quality metrics for voice cloning."""

    mos_score: Optional[float] = None  # Mean Opinion Score (1.0-5.0)
    similarity: Optional[float] = None  # Voice similarity (0.0-1.0)
    naturalness: Optional[float] = None  # Naturalness score (0.0-1.0)
    snr_db: Optional[float] = None  # Signal-to-noise ratio (dB)
    artifact_score: Optional[float] = None  # Artifact score (0.0-1.0, lower is better)
    has_clicks: Optional[bool] = None  # Whether clicks detected
    has_distortion: Optional[bool] = None  # Whether distortion detected
    voice_profile_match: Optional[Dict[str, Any]] = (
        None  # Voice profile matching results
    )


class VoiceSynthesizeResponse(BaseModel):
    audio_id: str
    audio_url: str
    duration: float
    quality_score: float  # Overall quality score (0.0-1.0)
    quality_metrics: Optional[QualityMetrics] = None  # Detailed quality metrics


class ABTestRequest(BaseModel):
    """Request for A/B testing two synthesis configurations.

    Implements IDEA 46: A/B Testing Interface for Quality Comparison.
    """

    profile_id: str = Field(..., description="Voice profile ID")
    text: str = Field(..., description="Text to synthesize for both A and B")
    language: Optional[str] = Field(default="en", description="Language code")

    # Configuration A
    engine_a: str = Field(..., description="Engine for sample A")
    emotion_a: Optional[str] = Field(None, description="Emotion for sample A")
    enhance_quality_a: bool = Field(
        default=True, description="Enable quality enhancement for A"
    )

    # Configuration B
    engine_b: str = Field(..., description="Engine for sample B")
    emotion_b: Optional[str] = Field(None, description="Emotion for sample B")
    enhance_quality_b: bool = Field(
        default=True, description="Enable quality enhancement for B"
    )


class ABTestResult(BaseModel):
    """Result for one side of A/B test."""

    sample_label: str = Field(..., description="Sample label (A or B)")
    audio_id: str = Field(..., description="Audio identifier")
    audio_url: str = Field(..., description="URL to access audio")
    duration: float = Field(..., description="Audio duration in seconds")
    engine: str = Field(..., description="Engine used")
    emotion: Optional[str] = Field(None, description="Emotion applied")
    quality_score: Optional[float] = Field(None, description="Overall quality score")
    quality_metrics: Optional[QualityMetrics] = Field(
        None, description="Detailed quality metrics"
    )


class ABTestResponse(BaseModel):
    """Response from A/B test."""

    sample_a: ABTestResult = Field(..., description="Result for sample A")
    sample_b: ABTestResult = Field(..., description="Result for sample B")
    comparison: Dict[str, Any] = Field(
        default_factory=dict, description="Quality comparison metrics"
    )
    test_id: str = Field(..., description="Unique test identifier")


class VoiceAnalyzeResponse(BaseModel):
    metrics: Dict[str, float]  # mos, similarity, naturalness, snr, lufs, etc.
    quality_score: float


class VoiceCloneRequest(BaseModel):
    """Request model for voice cloning with validation and advanced features."""

    reference_audio: Union[str, List[str]] = Field(
        ...,
        description="Reference audio file path(s) or ID(s) for single or multi-reference cloning",
        min_length=1,
    )
    text: Optional[str] = Field(
        default=None, description="Optional text for synthesis", max_length=10000
    )
    engine: str = Field(
        default="xtts", description="Engine to use", min_length=1, max_length=50
    )
    quality_mode: str = Field(
        default="standard", description="Quality mode: fast, standard, high, ultra"
    )
    enhance_quality: bool = Field(
        default=False, description="Apply advanced quality enhancement pipeline"
    )
    use_multi_reference: bool = Field(
        default=False,
        description="Use ensemble approach when multiple references provided",
    )
    prosody_params: Optional[Dict[str, float]] = Field(
        default=None,
        description="Advanced prosody control: pitch (semitones), tempo (multiplier), formant_shift (factor), energy (multiplier)",
    )
    use_rvc_postprocessing: bool = Field(
        default=False,
        description="Apply RVC post-processing for enhanced voice similarity",
    )
    language: str = Field(default="en", description="Language code for synthesis")

    @validator("engine")
    def validate_engine(cls, v):
        """Validate engine name format."""
        if not re.match(r"^[a-z0-9_-]+$", v.lower()):
            raise ValueError(
                "Engine name must contain only lowercase letters, numbers, hyphens, and underscores"
            )
        return v.lower()

    @validator("quality_mode")
    def validate_quality_mode(cls, v):
        """Validate quality mode."""
        valid_modes = ["fast", "standard", "high", "ultra"]
        if v.lower() not in valid_modes:
            raise ValueError(f"Quality mode must be one of: {', '.join(valid_modes)}")
        return v.lower()

    @validator("text")
    def validate_text(cls, v):
        """Validate text if provided."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
            if len(v) > 10000:
                raise ValueError("Text cannot exceed 10000 characters")
        return v

    @validator("prosody_params")
    def validate_prosody_params(cls, v):
        """Validate prosody parameters if provided."""
        if v is not None:
            valid_keys = {"pitch", "tempo", "formant_shift", "energy"}
            invalid_keys = set(v.keys()) - valid_keys
            if invalid_keys:
                raise ValueError(
                    f"Invalid prosody parameters: {', '.join(invalid_keys)}"
                )

            # Validate ranges
            if "pitch" in v and not (-12 <= v["pitch"] <= 12):
                raise ValueError("Pitch must be between -12 and +12 semitones")
            if "tempo" in v and not (0.5 <= v["tempo"] <= 2.0):
                raise ValueError("Tempo must be between 0.5 and 2.0")
            if "formant_shift" in v and not (0.5 <= v["formant_shift"] <= 2.0):
                raise ValueError("Formant shift must be between 0.5 and 2.0")
            if "energy" in v and not (0.5 <= v["energy"] <= 2.0):
                raise ValueError("Energy must be between 0.5 and 2.0")
        return v


class VoiceCloneResponse(BaseModel):
    profile_id: str
    audio_id: Optional[str] = None
    audio_url: Optional[str] = None
    quality_score: float  # Overall quality score (0.0-1.0)
    quality_metrics: Optional[QualityMetrics] = None  # Detailed quality metrics


# Quality Improvement Models (IDEA 61-70)
class MultiPassSynthesisRequest(BaseModel):
    """Request model for multi-pass synthesis with quality refinement."""

    engine: str = Field(..., description="Engine name", min_length=1, max_length=50)
    profile_id: str = Field(
        ..., description="Voice profile ID", min_length=1, max_length=100
    )
    text: str = Field(
        ..., description="Text to synthesize", min_length=1, max_length=10000
    )
    language: Optional[str] = Field(default="en", description="Language code")
    emotion: Optional[str] = Field(default=None, description="Emotion to apply")
    max_passes: Optional[int] = Field(
        default=3, description="Maximum number of passes", ge=1, le=10
    )
    min_quality_improvement: Optional[float] = Field(
        default=0.02,
        description="Minimum quality improvement to continue (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    pass_preset: Optional[str] = Field(
        default=None,
        description="Pass preset: naturalness_focus, similarity_focus, artifact_focus",
    )
    adaptive: Optional[bool] = Field(
        default=True, description="Adaptively determine optimal pass count"
    )

    @validator("engine")
    def validate_engine(cls, v):
        if not re.match(r"^[a-z0-9_-]+$", v.lower()):
            raise ValueError(
                "Engine name must contain only lowercase letters, numbers, hyphens, and underscores"
            )
        return v.lower()


class PassResult(BaseModel):
    """Result from a single synthesis pass."""

    pass_number: int
    audio_id: str
    audio_url: str
    quality_metrics: QualityMetrics
    quality_score: float
    improvement: Optional[float] = None  # Improvement over previous pass


class MultiPassSynthesisResponse(BaseModel):
    """Response model for multi-pass synthesis."""

    audio_id: str  # Final selected audio
    audio_url: str
    duration: float
    quality_score: float
    quality_metrics: QualityMetrics
    passes_completed: int
    passes: List[PassResult]  # All passes for comparison
    best_pass: int  # Pass number with best quality
    improvement_tracking: List[float]  # Quality improvement per pass


class ReferenceAudioPreprocessRequest(BaseModel):
    """Request model for reference audio pre-processing."""

    profile_id: Optional[str] = Field(
        default=None, description="Profile ID if processing existing profile"
    )
    reference_audio_path: Optional[str] = Field(
        default=None, description="Path to reference audio file"
    )
    auto_enhance: Optional[bool] = Field(
        default=True, description="Automatically enhance reference audio"
    )
    select_optimal_segments: Optional[bool] = Field(
        default=True, description="Select optimal segments for cloning"
    )
    min_segment_duration: Optional[float] = Field(
        default=1.0, description="Minimum segment duration in seconds", ge=0.5, le=10.0
    )
    max_segments: Optional[int] = Field(
        default=5, description="Maximum number of segments to select", ge=1, le=20
    )


class ReferenceAudioAnalysis(BaseModel):
    """Analysis results for reference audio."""

    quality_score: float  # Overall quality score (1-10)
    has_noise: bool
    has_clipping: bool
    has_distortion: bool
    sample_rate: int
    duration: float
    channels: int
    recommendations: List[str]  # List of recommended improvements
    optimal_segments: Optional[List[Dict[str, Any]]] = None  # Selected optimal segments


class ReferenceAudioPreprocessResponse(BaseModel):
    """Response model for reference audio pre-processing."""

    processed_audio_id: str
    processed_audio_url: str
    original_analysis: ReferenceAudioAnalysis
    processed_analysis: Optional[ReferenceAudioAnalysis] = None
    improvements_applied: List[str]  # List of enhancements applied
    quality_improvement: float  # Quality improvement score (0.0-1.0)


class ArtifactRemovalRequest(BaseModel):
    """Request model for artifact removal."""

    audio_id: str = Field(..., description="Audio ID to process")
    artifact_types: Optional[List[str]] = Field(
        default=None,
        description="Specific artifact types to remove: clicks, pops, distortion, glitches, phase_issues",
    )
    preview: Optional[bool] = Field(
        default=False, description="Preview removal without applying"
    )
    repair_preset: Optional[str] = Field(
        default=None,
        description="Repair preset: click_removal, distortion_repair, comprehensive",
    )


class ArtifactDetection(BaseModel):
    """Artifact detection results."""

    artifact_type: str
    severity: float  # Severity score (1-10)
    location: Optional[float] = None  # Time location in seconds
    confidence: float  # Detection confidence (0.0-1.0)


class ArtifactRemovalResponse(BaseModel):
    """Response model for artifact removal."""

    audio_id: str  # Original audio ID
    repaired_audio_id: Optional[str] = None  # Repaired audio ID (if not preview)
    repaired_audio_url: Optional[str] = None
    artifacts_detected: List[ArtifactDetection]
    artifacts_removed: List[str]  # Types of artifacts removed
    quality_improvement: float  # Quality improvement score (0.0-1.0)
    preview_available: bool  # Whether preview is available


# Image Generation Models
class ImageGenerateRequest(BaseModel):
    """Request model for image generation with validation."""

    engine: str = Field(
        ...,
        description="Engine name (e.g., sdxl, comfyui, automatic1111)",
        min_length=1,
        max_length=50,
    )
    prompt: str = Field(
        ...,
        description="Text prompt for image generation",
        min_length=1,
        max_length=2000,
    )
    negative_prompt: Optional[str] = Field(
        default="", description="Negative prompt", max_length=2000
    )
    width: Optional[int] = Field(default=512, description="Image width", ge=64, le=2048)
    height: Optional[int] = Field(
        default=512, description="Image height", ge=64, le=2048
    )
    steps: Optional[int] = Field(
        default=20, description="Number of sampling steps", ge=1, le=150
    )
    cfg_scale: Optional[float] = Field(
        default=7.0, description="Classifier-free guidance scale", ge=1.0, le=30.0
    )
    sampler: Optional[str] = Field(default=None, description="Sampling method")
    seed: Optional[int] = Field(default=None, description="Random seed (-1 for random)")
    additional_params: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional engine-specific parameters"
    )

    @validator("engine")
    def validate_engine(cls, v):
        """Validate engine name format."""
        if not re.match(r"^[a-z0-9_-]+$", v.lower()):
            raise ValueError(
                "Engine name must contain only lowercase letters, numbers, hyphens, and underscores"
            )
        return v.lower()

    @validator("prompt")
    def validate_prompt(cls, v):
        """Validate prompt content."""
        if not v or not v.strip():
            raise ValueError("Prompt cannot be empty")
        if len(v.strip()) > 2000:
            raise ValueError("Prompt cannot exceed 2000 characters")
        return v.strip()


class ImageGenerateResponse(BaseModel):
    """Response model for image generation."""

    image_id: str
    image_url: str
    image_base64: str  # Base64-encoded image data URL
    width: int
    height: int
    format: str
    metadata: Optional[Dict[str, Any]] = None


class ImageUpscaleRequest(BaseModel):
    """Request model for image upscaling."""

    engine: Optional[str] = Field(
        default="realesrgan", description="Upscaling engine name"
    )
    image_id: Optional[str] = Field(
        default=None, description="ID of stored image to upscale"
    )
    scale: Optional[int] = Field(default=4, description="Upscaling factor", ge=2, le=8)
    additional_params: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional parameters"
    )


class ImageUpscaleResponse(BaseModel):
    """Response model for image upscaling."""

    image_id: str
    image_url: str
    image_base64: str  # Base64-encoded image data URL
    width: int
    height: int
    scale: int


# Video Generation Models
class VideoGenerateRequest(BaseModel):
    """Request model for video generation with validation."""

    engine: str = Field(
        ...,
        description="Engine name (e.g., svd, deforum, fomm)",
        min_length=1,
        max_length=50,
    )
    prompt: Optional[str] = Field(
        default=None, description="Text prompt for video generation", max_length=2000
    )
    image_id: Optional[str] = Field(
        default=None, description="ID of input image (for image-to-video)"
    )
    audio_id: Optional[str] = Field(
        default=None, description="ID of input audio (for audio-to-video)"
    )
    width: Optional[int] = Field(default=512, description="Video width", ge=64, le=2048)
    height: Optional[int] = Field(
        default=512, description="Video height", ge=64, le=2048
    )
    fps: Optional[float] = Field(
        default=24, description="Frames per second", ge=1, le=120
    )
    duration: Optional[float] = Field(
        default=5.0, description="Video duration in seconds", ge=0.1, le=60
    )
    steps: Optional[int] = Field(
        default=20, description="Number of sampling steps", ge=1, le=150
    )
    cfg_scale: Optional[float] = Field(
        default=7.0, description="Classifier-free guidance scale", ge=1.0, le=30.0
    )
    seed: Optional[int] = Field(default=None, description="Random seed (-1 for random)")
    additional_params: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional engine-specific parameters"
    )

    @validator("engine")
    def validate_engine(cls, v):
        """Validate engine name format."""
        if not re.match(r"^[a-z0-9_-]+$", v.lower()):
            raise ValueError(
                "Engine name must contain only lowercase letters, numbers, hyphens, and underscores"
            )
        return v.lower()


class VideoGenerateResponse(BaseModel):
    """Response model for video generation."""

    video_id: str
    video_url: str
    width: int
    height: int
    fps: float
    duration: float
    format: str
    metadata: Optional[Dict[str, Any]] = None


class VideoUpscaleRequest(BaseModel):
    """Request model for video upscaling."""

    engine: Optional[str] = Field(
        default="realesrgan", description="Upscaling engine name"
    )
    video_id: Optional[str] = Field(
        default=None, description="ID of stored video to upscale"
    )
    scale: Optional[int] = Field(default=4, description="Upscaling factor", ge=2, le=8)
    additional_params: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional parameters"
    )


class VideoUpscaleResponse(BaseModel):
    """Response model for video upscaling."""

    video_id: str
    video_url: str
    width: int
    height: int
    fps: float
    duration: float
    scale: int


# Additional Quality Improvement Models (IDEA 64-70)
class VoiceCharacteristicAnalysisRequest(BaseModel):
    """Request model for voice characteristic analysis."""

    audio_id: str = Field(..., description="Audio ID to analyze")
    reference_audio_id: Optional[str] = Field(
        default=None, description="Reference audio for comparison"
    )
    include_pitch: Optional[bool] = Field(
        default=True, description="Include pitch analysis"
    )
    include_formants: Optional[bool] = Field(
        default=True, description="Include formant analysis"
    )
    include_timbre: Optional[bool] = Field(
        default=True, description="Include timbre analysis"
    )
    include_prosody: Optional[bool] = Field(
        default=True, description="Include prosody analysis"
    )


class VoiceCharacteristicData(BaseModel):
    """Voice characteristic data."""

    pitch_mean: Optional[float] = None
    pitch_std: Optional[float] = None
    formants: Optional[List[float]] = None  # F1, F2, F3
    spectral_centroid: Optional[float] = None
    spectral_rolloff: Optional[float] = None
    mfcc: Optional[List[float]] = None
    prosody_patterns: Optional[Dict[str, Any]] = None


class VoiceCharacteristicAnalysisResponse(BaseModel):
    """Response model for voice characteristic analysis."""

    audio_id: str
    characteristics: VoiceCharacteristicData
    reference_characteristics: Optional[VoiceCharacteristicData] = None
    similarity_score: Optional[float] = None  # 0.0-1.0
    preservation_score: Optional[float] = None  # 0.0-1.0
    recommendations: List[str] = []


class ProsodyControlRequest(BaseModel):
    """Request model for prosody and intonation control."""

    audio_id: str = Field(..., description="Audio ID to process")
    pitch_contour: Optional[List[float]] = Field(
        default=None, description="Pitch contour adjustments"
    )
    rhythm_adjustments: Optional[Dict[str, float]] = Field(
        default=None, description="Rhythm adjustments"
    )
    stress_markers: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Word stress markers"
    )
    intonation_pattern: Optional[str] = Field(
        default=None, description="Intonation pattern: rising, falling, flat"
    )
    prosody_template: Optional[str] = Field(
        default=None, description="Prosody template name"
    )


class ProsodyControlResponse(BaseModel):
    """Response model for prosody control."""

    audio_id: str
    processed_audio_id: str
    processed_audio_url: str
    prosody_applied: Dict[str, Any]
    quality_improvement: float  # 0.0-1.0


class FaceEnhancementRequest(BaseModel):
    """Request model for face quality enhancement."""

    image_id: Optional[str] = Field(default=None, description="Image ID to enhance")
    video_id: Optional[str] = Field(default=None, description="Video ID to enhance")
    enhancement_preset: Optional[str] = Field(
        default=None, description="Enhancement preset: portrait, full_body, close_up"
    )
    multi_stage: Optional[bool] = Field(
        default=True, description="Apply multi-stage enhancement"
    )
    face_specific: Optional[bool] = Field(
        default=True, description="Apply face-specific enhancement"
    )


class FaceQualityAnalysis(BaseModel):
    """Face quality analysis results."""

    resolution_score: float  # 1-10
    artifact_score: float  # 1-10 (lower is better)
    alignment_score: float  # 1-10
    realism_score: float  # 1-10
    overall_quality: float  # 1-10
    recommendations: List[str] = []


class FaceEnhancementResponse(BaseModel):
    """Response model for face enhancement."""

    image_id: Optional[str] = None
    video_id: Optional[str] = None
    enhanced_image_id: Optional[str] = None
    enhanced_video_id: Optional[str] = None
    enhanced_image_url: Optional[str] = None
    enhanced_video_url: Optional[str] = None
    original_analysis: FaceQualityAnalysis
    enhanced_analysis: Optional[FaceQualityAnalysis] = None
    quality_improvement: float  # 0.0-1.0


class TemporalConsistencyRequest(BaseModel):
    """Request model for temporal consistency enhancement."""

    video_id: str = Field(..., description="Video ID to process")
    smoothing_strength: Optional[float] = Field(
        default=0.5, description="Temporal smoothing strength (0.0-1.0)", ge=0.0, le=1.0
    )
    motion_consistency: Optional[bool] = Field(
        default=True, description="Ensure motion consistency"
    )
    detect_artifacts: Optional[bool] = Field(
        default=True, description="Detect temporal artifacts"
    )


class TemporalAnalysis(BaseModel):
    """Temporal analysis results."""

    frame_stability: float  # 0.0-1.0
    motion_smoothness: float  # 0.0-1.0
    flicker_score: float  # 0.0-1.0 (lower is better)
    jitter_score: float  # 0.0-1.0 (lower is better)
    overall_consistency: float  # 0.0-1.0
    artifacts_detected: List[str] = []


class TemporalConsistencyResponse(BaseModel):
    """Response model for temporal consistency."""

    video_id: str
    processed_video_id: str
    processed_video_url: str
    original_analysis: TemporalAnalysis
    processed_analysis: Optional[TemporalAnalysis] = None
    quality_improvement: float  # 0.0-1.0


class TrainingDataOptimizationRequest(BaseModel):
    """Request model for training data optimization."""

    dataset_id: str = Field(..., description="Dataset ID to optimize")
    analyze_quality: Optional[bool] = Field(
        default=True, description="Analyze data quality"
    )
    select_optimal: Optional[bool] = Field(
        default=True, description="Select optimal samples"
    )
    suggest_augmentation: Optional[bool] = Field(
        default=True, description="Suggest augmentation strategies"
    )
    analyze_diversity: Optional[bool] = Field(
        default=True, description="Analyze data diversity"
    )


class TrainingDataAnalysis(BaseModel):
    """Training data analysis results."""

    quality_score: float  # 1-10
    diversity_score: float  # 1-10
    coverage_score: float  # 1-10
    optimal_samples: List[str] = []  # Sample IDs
    recommendations: List[str] = []
    augmentation_suggestions: List[str] = []


class TrainingDataOptimizationResponse(BaseModel):
    """Response model for training data optimization."""

    dataset_id: str
    analysis: TrainingDataAnalysis
    optimized_dataset_id: Optional[str] = None
    quality_improvement: float  # 0.0-1.0


class PostProcessingPipelineRequest(BaseModel):
    """Request model for post-processing enhancement pipeline."""

    audio_id: Optional[str] = Field(default=None, description="Audio ID to process")
    image_id: Optional[str] = Field(default=None, description="Image ID to process")
    video_id: Optional[str] = Field(default=None, description="Video ID to process")
    enhancement_stages: Optional[List[str]] = Field(
        default=None,
        description="Enhancement stages: denoise, normalize, enhance, repair",
    )
    optimize_order: Optional[bool] = Field(
        default=True, description="Optimize enhancement order"
    )
    preview: Optional[bool] = Field(
        default=False, description="Preview without applying"
    )


class EnhancementStageResult(BaseModel):
    """Result from a single enhancement stage."""

    stage_name: str
    quality_before: float
    quality_after: float
    improvement: float


class PostProcessingPipelineResponse(BaseModel):
    """Response model for post-processing pipeline."""

    audio_id: Optional[str] = None
    image_id: Optional[str] = None
    video_id: Optional[str] = None
    processed_audio_id: Optional[str] = None
    processed_image_id: Optional[str] = None
    processed_video_id: Optional[str] = None
    processed_audio_url: Optional[str] = None
    processed_image_url: Optional[str] = None
    processed_video_url: Optional[str] = None
    stages_applied: List[EnhancementStageResult]
    total_quality_improvement: float  # 0.0-1.0
    preview_available: bool
