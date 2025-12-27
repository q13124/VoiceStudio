# VoiceStudio Quantum+ Data Models Reference

Complete reference for all data models used in VoiceStudio Quantum+.

**Version:** 1.0  
**Last Updated:** 2025-01-28  
**Status:** Complete

---

## Table of Contents

1. [Overview](#overview)
2. [C# Models (Frontend)](#c-models-frontend)
3. [Python Models (Backend)](#python-models-backend)
4. [Model Relationships](#model-relationships)
5. [Model Validation](#model-validation)
6. [Model Serialization](#model-serialization)
7. [Model Reference Guide](#model-reference-guide)

---

## Overview

VoiceStudio Quantum+ uses a dual-model architecture:

- **C# Models** (`src/VoiceStudio.Core/Models/`): Frontend models for UI and business logic
- **Python Models** (`backend/api/models*.py`): Backend API models using Pydantic

Models are serialized to JSON for communication between frontend and backend.

### Model Categories

1. **Core Models**: VoiceProfile, Project, AudioTrack, AudioClip
2. **Quality Models**: QualityMetrics, EngineQualityEstimate, EngineRecommendation
3. **Audio Models**: WaveformData, SpectrogramData, LoudnessData, PhaseData
4. **Effect Models**: EffectChain, Effect, EffectParameter
5. **Macro Models**: Macro, MacroNode, MacroConnection, AutomationCurve
6. **Synthesis Models**: VoiceSynthesisRequest, VoiceSynthesizeResponse
7. **Image/Video Models**: ImageGenerateRequest, VideoGenerateRequest
8. **Training Models**: TrainingDataOptimizationRequest, TrainingDataAnalysis
9. **Utility Models**: ModelInfo, Telemetry, SettingsData

---

## C# Models (Frontend)

### Core Models

#### VoiceProfile

**Location:** `src/VoiceStudio.Core/Models/VoiceProfile.cs`

**Purpose:** Represents a voice profile for voice cloning.

**Properties:**
```csharp
public class VoiceProfile
{
    public string Id { get; set; }                    // Unique identifier
    public string Name { get; set; }                  // Profile name
    public string Language { get; set; }              // Language code (e.g., "en")
    public string Emotion { get; set; }               // Emotion tag
    public double QualityScore { get; set; }           // Quality score (0.0-1.0)
    public List<string> Tags { get; set; }            // Tags for categorization
}
```

**Validation:**
- `Id`: Required, non-empty
- `Name`: Required, non-empty
- `Language`: Required, ISO 639-1 code
- `QualityScore`: 0.0-1.0 range

**Serialization:** JSON (System.Text.Json)

---

#### Project

**Location:** `src/VoiceStudio.Core/Models/Project.cs`

**Purpose:** Represents a project containing tracks and voice profiles.

**Properties:**
```csharp
public class Project
{
    public string Id { get; set; }                     // Unique identifier
    public string Name { get; set; }                   // Project name
    public string? Description { get; set; }          // Optional description
    public string CreatedAt { get; set; }              // ISO 8601 timestamp
    public string UpdatedAt { get; set; }              // ISO 8601 timestamp
    public List<string> VoiceProfileIds { get; set; }  // Associated voice profiles
    public List<AudioTrack> Tracks { get; set; }      // Audio tracks
}
```

**Relationships:**
- Contains multiple `AudioTrack` objects
- References multiple `VoiceProfile` IDs

**Validation:**
- `Id`: Required, non-empty
- `Name`: Required, non-empty
- `CreatedAt`, `UpdatedAt`: ISO 8601 format

---

#### AudioTrack

**Location:** `src/VoiceStudio.Core/Models/AudioTrack.cs`

**Purpose:** Represents an audio track in the timeline.

**Properties:**
```csharp
public class AudioTrack
{
    public string Id { get; set; }                     // Unique identifier
    public string Name { get; set; }                   // Track name
    public string ProjectId { get; set; }              // Parent project ID
    public List<AudioClip> Clips { get; set; }        // Audio clips on track
    public int TrackNumber { get; set; }               // Track position
    public string? Engine { get; set; }                // Engine used for synthesis
}
```

**Relationships:**
- Belongs to `Project` (via `ProjectId`)
- Contains multiple `AudioClip` objects

---

#### AudioClip

**Location:** `src/VoiceStudio.Core/Models/AudioClip.cs`

**Purpose:** Represents a single audio clip in the timeline.

**Properties:**
```csharp
public class AudioClip
{
    public string Id { get; set; }                     // Unique identifier
    public string Name { get; set; }                   // Clip name
    public string ProfileId { get; set; }             // Voice profile ID
    public string AudioId { get; set; }                // Backend audio ID
    public string AudioUrl { get; set; }               // Backend audio URL
    public TimeSpan Duration { get; set; }             // Clip duration
    public double StartTime { get; set; }              // Position in timeline (seconds)
    public double EndTime => StartTime + Duration.TotalSeconds;  // Calculated end time
    public string? Engine { get; set; }                // Engine used
    public double? QualityScore { get; set; }          // Quality score (0.0-1.0)
    public List<float>? WaveformSamples { get; set; }  // Waveform data (-1.0 to 1.0)
}
```

**Relationships:**
- Belongs to `AudioTrack` (via parent track)
- References `VoiceProfile` (via `ProfileId`)

**Validation:**
- `StartTime`: >= 0
- `Duration`: > 0
- `QualityScore`: 0.0-1.0 if set
- `WaveformSamples`: Normalized -1.0 to 1.0

---

### Quality Models

#### QualityMetrics

**Location:** `src/VoiceStudio.Core/Models/QualityMetrics.cs`

**Purpose:** Detailed quality metrics for voice cloning evaluation.

**Properties:**
```csharp
public class QualityMetrics
{
    public double? MosScore { get; set; }              // Mean Opinion Score (1.0-5.0)
    public double? Similarity { get; set; }            // Voice similarity (0.0-1.0)
    public double? Naturalness { get; set; }           // Naturalness score (0.0-1.0)
    public double? SnrDb { get; set; }                 // Signal-to-noise ratio (dB)
    public double? ArtifactScore { get; set; }         // Artifact score (0.0-1.0, lower is better)
    public bool? HasClicks { get; set; }               // Clicks/pops detected
    public bool? HasDistortion { get; set; }          // Distortion/clipping detected
    public Dictionary<string, object>? VoiceProfileMatch { get; set; }  // Profile matching results
}
```

**Validation:**
- `MosScore`: 1.0-5.0 if set
- `Similarity`: 0.0-1.0 if set
- `Naturalness`: 0.0-1.0 if set
- `ArtifactScore`: 0.0-1.0 if set

---

### Audio Visualization Models

#### WaveformData

**Location:** `src/VoiceStudio.Core/Models/WaveformData.cs`

**Purpose:** Waveform data for visualization.

**Properties:**
```csharp
public class WaveformData
{
    public List<float> Samples { get; set; }          // Waveform samples (-1.0 to 1.0)
    public int SampleRate { get; set; }                // Sample rate (Hz)
    public int Channels { get; set; }                  // Number of channels
}
```

**Validation:**
- `Samples`: Normalized -1.0 to 1.0
- `SampleRate`: > 0
- `Channels`: 1 or 2

---

#### SpectrogramData

**Location:** `src/VoiceStudio.Core/Models/SpectrogramData.cs`

**Purpose:** Spectrogram data for rendering.

**Properties:**
```csharp
public class SpectrogramData
{
    public List<SpectrogramFrame> Frames { get; set; } // Spectrogram frames
    public int SampleRate { get; set; }                // Sample rate (Hz)
    public int FftSize { get; set; }                   // FFT size
    public int HopLength { get; set; }                 // Hop length
    public int Width { get; set; }                     // Width in pixels
    public int Height { get; set; }                    // Height in pixels
}

public class SpectrogramFrame
{
    public double Time { get; set; }                   // Time in seconds
    public List<float> Frequencies { get; set; }      // Frequency data
}
```

---

### Effect Models

#### EffectChain

**Location:** `src/VoiceStudio.Core/Models/EffectChain.cs`

**Purpose:** A chain of audio effects.

**Properties:**
```csharp
public class EffectChain
{
    public string Id { get; set; }                     // Unique identifier
    public string Name { get; set; }                   // Chain name
    public string? Description { get; set; }          // Optional description
    public string ProjectId { get; set; }              // Parent project ID
    public List<Effect> Effects { get; set; }         // Effects in chain
    public DateTime Created { get; set; }              // Creation timestamp
    public DateTime Modified { get; set; }            // Modification timestamp
}

public class Effect
{
    public string Id { get; set; }                     // Unique identifier
    public string Type { get; set; }                   // Effect type (eq, compressor, reverb, etc.)
    public string Name { get; set; }                   // Effect name
    public bool Enabled { get; set; }                 // Whether effect is enabled
    public int Order { get; set; }                     // Position in chain (0 = first)
    public List<EffectParameter> Parameters { get; set; }  // Effect parameters
}

public class EffectParameter
{
    public string Name { get; set; }                   // Parameter name
    public double Value { get; set; }                  // Parameter value
    public double MinValue { get; set; }               // Minimum value
    public double MaxValue { get; set; }               // Maximum value
    public string? Unit { get; set; }                  // Unit (dB, Hz, ms, etc.)
}
```

**Validation:**
- `Order`: >= 0, unique within chain
- `Value`: Between `MinValue` and `MaxValue`
- `Type`: Valid effect type

---

### Macro Models

#### Macro

**Location:** `src/VoiceStudio.Core/Models/Macro.cs`

**Purpose:** Represents a macro graph with nodes and connections.

**Properties:**
```csharp
public class Macro
{
    public string Id { get; set; }                     // Unique identifier
    public string Name { get; set; }                   // Macro name
    public string? Description { get; set; }          // Optional description
    public string ProjectId { get; set; }              // Parent project ID
    public List<MacroNode> Nodes { get; set; }         // Macro nodes
    public List<MacroConnection> Connections { get; set; }  // Node connections
    public bool IsEnabled { get; set; }               // Whether macro is enabled
    public DateTime Created { get; set; }             // Creation timestamp
    public DateTime Modified { get; set; }            // Modification timestamp
}

public class MacroNode
{
    public string Id { get; set; }                     // Unique identifier
    public string Type { get; set; }                   // Node type (source, processor, control, etc.)
    public string Name { get; set; }                   // Node name
    public double X { get; set; }                      // Canvas X position
    public double Y { get; set; }                     // Canvas Y position
    public Dictionary<string, object> Properties { get; set; }  // Node properties
    public List<MacroPort> InputPorts { get; set; }    // Input ports
    public List<MacroPort> OutputPorts { get; set; }   // Output ports
}

public class MacroConnection
{
    public string Id { get; set; }                     // Unique identifier
    public string SourceNodeId { get; set; }          // Source node ID
    public string SourcePortId { get; set; }           // Source port ID
    public string TargetNodeId { get; set; }           // Target node ID
    public string TargetPortId { get; set; }           // Target port ID
}

public class MacroPort
{
    public string Id { get; set; }                     // Unique identifier
    public string Name { get; set; }                   // Port name
    public string Type { get; set; }                   // Port type (audio, control, data)
    public bool IsRequired { get; set; }               // Whether port is required
}
```

**Validation:**
- `Connections`: Must reference valid node IDs
- `Ports`: Must match node type requirements

---

#### AutomationCurve

**Location:** `src/VoiceStudio.Core/Models/Macro.cs`

**Purpose:** Represents an automation curve for a parameter over time.

**Properties:**
```csharp
public class AutomationCurve
{
    public string Id { get; set; }                     // Unique identifier
    public string Name { get; set; }                   // Curve name
    public string ParameterId { get; set; }           // Parameter ID (e.g., "volume", "pitch")
    public string TrackId { get; set; }                // Track ID
    public List<AutomationPoint> Points { get; set; }  // Automation points
    public string Interpolation { get; set; }          // Interpolation type (linear, bezier, step)
}

public class AutomationPoint
{
    public double Time { get; set; }                   // Time in seconds
    public double Value { get; set; }                  // Parameter value (normalized or specific range)
    public double? BezierHandleInX { get; set; }       // Bezier handle (in)
    public double? BezierHandleInY { get; set; }
    public double? BezierHandleOutX { get; set; }      // Bezier handle (out)
    public double? BezierHandleOutY { get; set; }
}
```

**Validation:**
- `Time`: >= 0
- `Interpolation`: "linear", "bezier", or "step"
- `Points`: Sorted by time

---

### Request/Response Models

#### VoiceSynthesisRequest

**Location:** `src/VoiceStudio.Core/Models/VoiceSynthesisRequest.cs`

**Purpose:** Request model for voice synthesis.

**Properties:**
```csharp
public class VoiceSynthesisRequest
{
    public string Engine { get; set; }                 // Engine name
    public string ProfileId { get; set; }              // Voice profile ID
    public string Text { get; set; }                   // Text to synthesize
    public string? Language { get; set; }              // Language code
    public string? Emotion { get; set; }              // Emotion tag
    public bool? EnhanceQuality { get; set; }         // Enable quality enhancement
}
```

**Validation:**
- `Engine`: Required, valid engine name
- `ProfileId`: Required, non-empty
- `Text`: Required, 1-10000 characters
- `Language`: ISO 639-1 code if set

---

## Python Models (Backend)

### Core API Models

#### VoiceProfile (Python)

**Location:** `backend/api/routes/profiles.py`

**Purpose:** Voice profile model for API.

**Properties:**
```python
class VoiceProfile(BaseModel):
    id: str
    name: str
    language: str = "en"
    emotion: Optional[str] = None
    quality_score: float = 0.0
    tags: List[str] = []
    reference_audio_url: Optional[str] = None
```

**Validation:**
- `id`: Required, non-empty
- `name`: Required, non-empty
- `language`: ISO 639-1 code
- `quality_score`: 0.0-1.0

---

#### Project (Python)

**Location:** `backend/api/routes/projects.py`

**Purpose:** Project model for API.

**Properties:**
```python
class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str
    voice_profile_ids: List[str] = []
```

**Validation:**
- `id`: Required, non-empty
- `name`: Required, non-empty
- `created_at`, `updated_at`: ISO 8601 format

---

### Voice Synthesis Models

#### VoiceSynthesizeRequest

**Location:** `backend/api/models_additional.py`

**Purpose:** Request model for voice synthesis with validation.

**Properties:**
```python
class VoiceSynthesizeRequest(BaseModel):
    engine: str = Field(..., min_length=1, max_length=50)
    profile_id: str = Field(..., min_length=1, max_length=100)
    text: str = Field(..., min_length=1, max_length=10000)
    language: Optional[str] = Field(default="en", max_length=10)
    emotion: Optional[str] = Field(default=None, max_length=50)
    enhance_quality: Optional[bool] = Field(default=False)
```

**Validation:**
- `engine`: Lowercase alphanumeric, hyphens, underscores
- `profile_id`: Alphanumeric, hyphens, underscores
- `language`: ISO 639-1 code (e.g., "en", "en-US")
- `text`: Non-empty, max 10000 characters

**Validators:**
- Engine name format validation
- Profile ID format validation
- Language code format validation
- Text content validation

---

#### VoiceSynthesizeResponse

**Location:** `backend/api/models_additional.py`

**Purpose:** Response model for voice synthesis.

**Properties:**
```python
class VoiceSynthesizeResponse(BaseModel):
    audio_id: str
    audio_url: str
    duration: float
    quality_score: float  # 0.0-1.0
    quality_metrics: Optional[QualityMetrics] = None
```

---

#### QualityMetrics (Python)

**Location:** `backend/api/models_additional.py`

**Purpose:** Detailed quality metrics for voice cloning.

**Properties:**
```python
class QualityMetrics(BaseModel):
    mos_score: Optional[float] = None  # 1.0-5.0
    similarity: Optional[float] = None  # 0.0-1.0
    naturalness: Optional[float] = None  # 0.0-1.0
    snr_db: Optional[float] = None  # dB
    artifact_score: Optional[float] = None  # 0.0-1.0 (lower is better)
    has_clicks: Optional[bool] = None
    has_distortion: Optional[bool] = None
    voice_profile_match: Optional[Dict[str, Any]] = None
```

---

### A/B Testing Models

#### ABTestRequest

**Location:** `backend/api/models_additional.py`

**Purpose:** Request for A/B testing two synthesis configurations.

**Properties:**
```python
class ABTestRequest(BaseModel):
    profile_id: str
    text: str
    language: Optional[str] = "en"
    
    # Configuration A
    engine_a: str
    emotion_a: Optional[str] = None
    enhance_quality_a: bool = True
    
    # Configuration B
    engine_b: str
    emotion_b: Optional[str] = None
    enhance_quality_b: bool = True
```

---

#### ABTestResponse

**Location:** `backend/api/models_additional.py`

**Purpose:** Response from A/B test.

**Properties:**
```python
class ABTestResponse(BaseModel):
    sample_a: ABTestResult
    sample_b: ABTestResult
    comparison: Dict[str, Any] = {}
    test_id: str
```

---

### Quality Improvement Models

#### MultiPassSynthesisRequest

**Location:** `backend/api/models_additional.py`

**Purpose:** Request for multi-pass synthesis with quality refinement.

**Properties:**
```python
class MultiPassSynthesisRequest(BaseModel):
    engine: str
    profile_id: str
    text: str
    language: Optional[str] = "en"
    emotion: Optional[str] = None
    max_passes: Optional[int] = Field(default=3, ge=1, le=10)
    min_quality_improvement: Optional[float] = Field(default=0.02, ge=0.0, le=1.0)
    pass_preset: Optional[str] = None  # naturalness_focus, similarity_focus, artifact_focus
    adaptive: Optional[bool] = True
```

**Validation:**
- `max_passes`: 1-10
- `min_quality_improvement`: 0.0-1.0

---

#### ReferenceAudioPreprocessRequest

**Location:** `backend/api/models_additional.py`

**Purpose:** Request for reference audio pre-processing.

**Properties:**
```python
class ReferenceAudioPreprocessRequest(BaseModel):
    profile_id: Optional[str] = None
    reference_audio_path: Optional[str] = None
    auto_enhance: Optional[bool] = True
    select_optimal_segments: Optional[bool] = True
    min_segment_duration: Optional[float] = Field(default=1.0, ge=0.5, le=10.0)
    max_segments: Optional[int] = Field(default=5, ge=1, le=20)
```

---

### Image/Video Models

#### ImageGenerateRequest

**Location:** `backend/api/models_additional.py`

**Purpose:** Request for image generation.

**Properties:**
```python
class ImageGenerateRequest(BaseModel):
    engine: str = Field(..., min_length=1, max_length=50)
    prompt: str = Field(..., min_length=1, max_length=2000)
    negative_prompt: Optional[str] = Field(default="", max_length=2000)
    width: Optional[int] = Field(default=512, ge=64, le=2048)
    height: Optional[int] = Field(default=512, ge=64, le=2048)
    steps: Optional[int] = Field(default=20, ge=1, le=150)
    cfg_scale: Optional[float] = Field(default=7.0, ge=1.0, le=30.0)
    sampler: Optional[str] = None
    seed: Optional[int] = None
    additional_params: Optional[Dict[str, Any]] = None
```

**Validation:**
- `width`, `height`: 64-2048
- `steps`: 1-150
- `cfg_scale`: 1.0-30.0

---

#### VideoGenerateRequest

**Location:** `backend/api/models_additional.py`

**Purpose:** Request for video generation.

**Properties:**
```python
class VideoGenerateRequest(BaseModel):
    engine: str
    prompt: Optional[str] = None
    image_id: Optional[str] = None
    audio_id: Optional[str] = None
    width: Optional[int] = Field(default=512, ge=64, le=2048)
    height: Optional[int] = Field(default=512, ge=64, le=2048)
    fps: Optional[float] = Field(default=24, ge=1, le=120)
    duration: Optional[float] = Field(default=5.0, ge=0.1, le=60)
    steps: Optional[int] = Field(default=20, ge=1, le=150)
    cfg_scale: Optional[float] = Field(default=7.0, ge=1.0, le=30.0)
    seed: Optional[int] = None
    additional_params: Optional[Dict[str, Any]] = None
```

---

### Training Models

#### TrainingDataOptimizationRequest

**Location:** `backend/api/models_additional.py`

**Purpose:** Request for training data optimization.

**Properties:**
```python
class TrainingDataOptimizationRequest(BaseModel):
    dataset_id: str
    analyze_quality: Optional[bool] = True
    select_optimal: Optional[bool] = True
    suggest_augmentation: Optional[bool] = True
    analyze_diversity: Optional[bool] = True
```

---

#### TrainingDataAnalysis

**Location:** `backend/api/models_additional.py`

**Purpose:** Training data analysis results.

**Properties:**
```python
class TrainingDataAnalysis(BaseModel):
    quality_score: float  # 1-10
    diversity_score: float  # 1-10
    coverage_score: float  # 1-10
    optimal_samples: List[str] = []
    recommendations: List[str] = []
    augmentation_suggestions: List[str] = []
```

---

## Model Relationships

### Entity Relationship Diagram

```
Project
  ├── VoiceProfileIds (many-to-many)
  └── AudioTrack (one-to-many)
        └── AudioClip (one-to-many)
              └── ProfileId (many-to-one) → VoiceProfile
              └── QualityMetrics (one-to-one)

EffectChain
  └── ProjectId (many-to-one) → Project
  └── Effect (one-to-many)
        └── EffectParameter (one-to-many)

Macro
  └── ProjectId (many-to-one) → Project
  └── MacroNode (one-to-many)
        └── MacroPort (one-to-many)
  └── MacroConnection (one-to-many)
        ├── SourceNodeId → MacroNode
        └── TargetNodeId → MacroNode

AutomationCurve
  └── TrackId (many-to-one) → AudioTrack
  └── AutomationPoint (one-to-many)
```

### Key Relationships

1. **Project ↔ VoiceProfile**: Many-to-many (via `VoiceProfileIds`)
2. **Project → AudioTrack**: One-to-many
3. **AudioTrack → AudioClip**: One-to-many
4. **AudioClip → VoiceProfile**: Many-to-one
5. **Project → EffectChain**: One-to-many
6. **Project → Macro**: One-to-many
7. **AudioTrack → AutomationCurve**: One-to-many

---

## Model Validation

### C# Validation

**Validation Approach:**
- Property validation in setters
- Data annotations (if used)
- Manual validation in ViewModels

**Example:**
```csharp
public class VoiceProfile
{
    private string _name = string.Empty;
    
    public string Name
    {
        get => _name;
        set
        {
            if (string.IsNullOrWhiteSpace(value))
                throw new ArgumentException("Name cannot be empty");
            _name = value;
        }
    }
}
```

### Python Validation

**Validation Approach:**
- Pydantic field validators
- Custom validators using `@validator` decorator
- Type hints for type checking

**Example:**
```python
class VoiceSynthesizeRequest(BaseModel):
    engine: str = Field(..., min_length=1, max_length=50)
    
    @validator("engine")
    def validate_engine(cls, v):
        if not re.match(r"^[a-z0-9_-]+$", v.lower()):
            raise ValueError("Invalid engine name format")
        return v.lower()
```

### Common Validation Rules

**IDs:**
- Required, non-empty
- Alphanumeric, hyphens, underscores
- Max length: 100 characters

**Names:**
- Required, non-empty
- Max length: 200 characters

**Scores:**
- Quality scores: 0.0-1.0
- MOS scores: 1.0-5.0
- Similarity: 0.0-1.0

**Timestamps:**
- ISO 8601 format
- UTC timezone

**Text:**
- Max length: 10000 characters (synthesis text)
- Max length: 2000 characters (prompts)

---

## Model Serialization

### C# Serialization

**Library:** System.Text.Json

**Configuration:**
```csharp
var options = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
    WriteIndented = true,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
};
```

**Example:**
```csharp
var profile = new VoiceProfile { Id = "123", Name = "Test" };
var json = JsonSerializer.Serialize(profile, options);
```

**Naming Convention:** CamelCase (e.g., `profileId`, `qualityScore`)

---

### Python Serialization

**Library:** Pydantic (automatic JSON serialization)

**Configuration:**
```python
class VoiceProfile(BaseModel):
    id: str
    name: str
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Example:**
```python
profile = VoiceProfile(id="123", name="Test")
json_str = profile.json()
```

**Naming Convention:** Snake_case (e.g., `profile_id`, `quality_score`)

---

### Serialization Mapping

**C# → Python:**
- CamelCase → Snake_case
- `ProfileId` → `profile_id`
- `QualityScore` → `quality_score`

**Python → C#:**
- Snake_case → CamelCase
- `profile_id` → `ProfileId`
- `quality_score` → `QualityScore`

**Note:** Backend API uses snake_case, frontend uses camelCase. Conversion handled by serialization settings.

---

## Model Reference Guide

### Quick Reference Table

| Model | C# Location | Python Location | Purpose |
|-------|-------------|-----------------|---------|
| VoiceProfile | `Models/VoiceProfile.cs` | `routes/profiles.py` | Voice profile |
| Project | `Models/Project.cs` | `routes/projects.py` | Project |
| AudioTrack | `Models/AudioTrack.cs` | - | Audio track |
| AudioClip | `Models/AudioClip.cs` | - | Audio clip |
| QualityMetrics | `Models/QualityMetrics.cs` | `models_additional.py` | Quality metrics |
| EffectChain | `Models/EffectChain.cs` | - | Effect chain |
| Macro | `Models/Macro.cs` | - | Macro graph |
| VoiceSynthesizeRequest | `Models/VoiceSynthesisRequest.cs` | `models_additional.py` | Synthesis request |
| VoiceSynthesizeResponse | - | `models_additional.py` | Synthesis response |
| ABTestRequest | - | `models_additional.py` | A/B test request |
| ImageGenerateRequest | `Models/ImageGenerationRequest.cs` | `models_additional.py` | Image generation |
| VideoGenerateRequest | `Models/VideoGenerateRequest.cs` | `models_additional.py` | Video generation |

---

### Model Count Summary

**C# Models:** 40+ models
- Core: 4 models
- Quality: 5 models
- Audio: 8 models
- Effect: 4 models
- Macro: 6 models
- Request/Response: 13+ models

**Python Models:** 50+ models
- Core API: 10+ models
- Voice Synthesis: 15+ models
- Quality: 10+ models
- Image/Video: 8+ models
- Training: 5+ models
- Utility: 2+ models

---

## Best Practices

### Model Design

1. **Use Nullable Types:** Use `Optional`/`?` for optional fields
2. **Validation:** Validate at model level, not just API level
3. **Documentation:** Document all properties with XML comments/docstrings
4. **Naming:** Use consistent naming conventions (camelCase C#, snake_case Python)
5. **Relationships:** Use IDs for relationships, not nested objects

### Serialization

1. **Consistent Naming:** Use camelCase for C#, snake_case for Python
2. **Null Handling:** Use `JsonIgnoreCondition.WhenWritingNull` for C#
3. **Dates:** Use ISO 8601 format for timestamps
4. **Enums:** Serialize as strings, not integers

### Validation

1. **Early Validation:** Validate at model creation, not just API entry
2. **Clear Messages:** Provide clear error messages
3. **Type Safety:** Use strong types, avoid `object`/`Any` when possible
4. **Range Checks:** Validate numeric ranges (e.g., 0.0-1.0 for scores)

---

## Summary

This document provides comprehensive reference for all data models in VoiceStudio Quantum+:

1. **C# Models:** 40+ models for frontend
2. **Python Models:** 50+ models for backend API
3. **Relationships:** Documented entity relationships
4. **Validation:** Validation rules and examples
5. **Serialization:** JSON serialization configuration
6. **Reference Guide:** Quick reference table

**Key Takeaways:**
- Models use consistent naming (camelCase C#, snake_case Python)
- Validation occurs at model level
- Relationships use IDs, not nested objects
- Serialization handles naming conversion automatically

---

**Document Version:** 1.0  
**Last Updated:** 2025-01-28  
**Next Review:** After major model changes

