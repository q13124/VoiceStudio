# IDEA 55: Multi-Engine Ensemble - Implementation Plan

**Task:** TASK-W1-021 (Part 3/8 of W1-019 through W1-028)  
**IDEA:** IDEA 55 - Multi-Engine Ensemble for Maximum Quality  
**Status:** 📋 **PLANNING**  
**Priority:** Medium  

---

## 🎯 Overview

Implement a system that synthesizes text with multiple engines, evaluates quality, and combines the best segments for maximum quality output.

**Key Difference from Existing Ensemble:**
- **Existing Ensemble:** Multiple voices, one engine → sequential/parallel/layered mixing
- **IDEA 55:** One voice/text, multiple engines → quality-based selection/fusion

---

## 📋 Implementation Phases

### Phase 1: Backend - Multi-Engine Synthesis
**Status:** ⏳ Pending

1. **Ensemble Engine Selection**
   - Allow selecting multiple engines for ensemble
   - Support engine combinations (XTTS + Chatterbox, etc.)
   - Engine availability checking

2. **Parallel Synthesis**
   - Synthesize same text with multiple engines simultaneously
   - Store all engine outputs
   - Track synthesis progress per engine

3. **Quality Evaluation**
   - Evaluate quality metrics for each engine output
   - Compare MOS, similarity, naturalness scores
   - Identify quality strengths per engine

### Phase 2: Backend - Quality-Based Selection
**Status:** ⏳ Pending

1. **Segment-Level Analysis**
   - Break audio into segments (e.g., 0.5-1.0 second chunks)
   - Evaluate quality for each segment
   - Identify best segments per engine

2. **Engine Voting**
   - Vote for best quality segment at each time point
   - Use weighted voting based on quality metrics
   - Handle ties intelligently

3. **Quality-Based Selection**
   - Select best segments from each engine
   - Create hybrid output from selected segments
   - Smooth transitions between segments

### Phase 3: Backend - Quality Fusion
**Status:** ⏳ Pending

1. **Weighted Mixing**
   - Blend outputs with quality-weighted mixing
   - Calculate weights based on quality scores
   - Support different fusion strategies

2. **Ensemble Quality Metrics**
   - Calculate final quality metrics for ensemble output
   - Compare ensemble quality vs individual engines
   - Track quality improvements

3. **Ensemble Presets**
   - Pre-configured engine combinations
   - Presets for different quality goals:
     - "Maximum Quality" (all engines)
     - "Fast Quality" (XTTS + Chatterbox)
     - "Balanced" (Chatterbox + Tortoise)
   - Custom preset creation

### Phase 4: Frontend - UI Components
**Status:** ⏳ Pending

1. **Multi-Engine Selection**
   - Checkbox list for engine selection
   - Engine availability indicators
   - Preset selection dropdown

2. **Synthesis Progress**
   - Progress per engine
   - Quality scores per engine
   - Real-time updates

3. **Quality Comparison**
   - Side-by-side quality metrics
   - Visual comparison chart
   - Best engine highlights

4. **Ensemble Settings**
   - Selection mode (voting, hybrid, fusion)
   - Fusion strategy options
   - Segment size controls

### Phase 5: API & Integration
**Status:** ⏳ Pending

1. **Backend API Endpoints**
   - `POST /api/ensemble/multi-engine` - Start multi-engine ensemble
   - `GET /api/ensemble/multi-engine/{job_id}` - Get ensemble status
   - `GET /api/ensemble/presets` - List ensemble presets
   - `POST /api/ensemble/presets` - Create ensemble preset

2. **Frontend Integration**
   - New panel or extend VoiceSynthesisView
   - Ensemble mode toggle
   - Quality comparison UI

---

## 📊 Technical Requirements

### Backend Models

```python
class MultiEngineEnsembleRequest:
    text: str
    profile_id: str
    engines: List[str]  # ["xtts", "chatterbox", "tortoise"]
    selection_mode: str  # "voting", "hybrid", "fusion"
    fusion_strategy: Optional[str]  # "quality_weighted", "equal", "best_segment"
    segment_size: float = 0.5  # seconds
    quality_threshold: float = 0.85  # Minimum quality for selection

class MultiEngineEnsembleResponse:
    job_id: str
    status: str
    engines: List[str]
    engine_outputs: Dict[str, str]  # engine -> audio_id
    engine_qualities: Dict[str, QualityMetrics]  # engine -> quality
    ensemble_audio_id: Optional[str]
    ensemble_quality: Optional[QualityMetrics]
    
class EnsemblePreset:
    id: str
    name: str
    engines: List[str]
    selection_mode: str
    fusion_strategy: Optional[str]
    description: str
```

### Frontend Models

```csharp
public class MultiEngineEnsembleRequest
{
    public string Text { get; set; }
    public string ProfileId { get; set; }
    public List<string> Engines { get; set; }
    public string SelectionMode { get; set; }
    public string? FusionStrategy { get; set; }
    public double SegmentSize { get; set; } = 0.5;
    public double QualityThreshold { get; set; } = 0.85;
}

public class MultiEngineEnsembleStatus
{
    public string JobId { get; set; }
    public string Status { get; set; }
    public List<string> Engines { get; set; }
    public Dictionary<string, string> EngineOutputs { get; set; }
    public Dictionary<string, QualityMetrics> EngineQualities { get; set; }
    public string? EnsembleAudioId { get; set; }
    public QualityMetrics? EnsembleQuality { get; set; }
    public double Progress { get; set; }
}
```

---

## 🎯 Success Criteria

- ✅ Synthesize text with multiple engines in parallel
- ✅ Evaluate quality for each engine output
- ✅ Select best segments based on quality
- ✅ Create hybrid output from selected segments
- ✅ Blend outputs with quality-weighted mixing
- ✅ Calculate ensemble quality metrics
- ✅ Support ensemble presets
- ✅ UI for engine selection and quality comparison
- ✅ Real-time progress tracking per engine

---

## 🔄 Integration Points

### Existing Systems
- ✅ Voice synthesis API (`/api/voice/synthesize`)
- ✅ Quality metrics framework
- ✅ Engine router system
- ✅ Audio storage system

### New Components
- Multi-engine synthesis orchestrator
- Quality-based segment selector
- Audio segment blending/merging
- Ensemble preset system

---

## 📝 Implementation Notes

1. **Segment Analysis:**
   - Use audio segmentation (e.g., 0.5-1.0 second windows)
   - Evaluate quality per segment
   - Consider overlap to avoid artifacts

2. **Quality Voting:**
   - Weight votes by quality score
   - Consider multiple metrics (MOS, similarity, naturalness)
   - Handle edge cases (tied votes, low quality)

3. **Audio Merging:**
   - Smooth transitions between segments
   - Avoid clicks/pops at boundaries
   - Maintain consistent volume levels

4. **Performance:**
   - Parallel engine synthesis
   - Async processing
   - Progress tracking per engine

5. **User Experience:**
   - Clear progress indication per engine
   - Quality comparison visualization
   - One-click ensemble synthesis
   - Preset management

---

## 🚀 Estimated Effort

- **Backend:** ~3-4 hours
- **Frontend:** ~2-3 hours
- **Testing:** ~1-2 hours
- **Total:** ~6-9 hours

---

**Status:** 📋 Ready to implement

