# Phase 4D: Analyzer Charts - Implementation Roadmap
## VoiceStudio Quantum+ - Advanced Visualization Charts

**Date:** 2025-01-27  
**Status:** 📋 Planning - Ready for Implementation  
**Priority:** High - Next Phase 4 Task

---

## 🎯 Executive Summary

**Mission:** Implement the remaining three analyzer charts (Radar, Loudness, Phase) in AnalyzerView. Currently, only Waveform and Spectral tabs are functional. The Radar, Loudness, and Phase tabs need custom chart controls created.

---

## ✅ Current Status

### Working Components (50%)

**AnalyzerView.xaml:**
- ✅ TabView with 5 tabs (Waveform, Spectral, Radar, Loudness, Phase)
- ✅ WaveformControl integrated and working
- ✅ SpectrogramControl integrated and working
- ✅ Tab switching logic functional
- ⏳ Radar tab - placeholder only
- ⏳ Loudness tab - placeholder only
- ⏳ Phase tab - placeholder only

**AnalyzerViewModel.cs:**
- ✅ Tab selection logic
- ✅ Visibility properties for all tabs
- ✅ Data loading for Waveform tab
- ✅ Data loading for Spectral tab
- ⏳ Data loading for Radar tab (TODO)
- ⏳ Data loading for Loudness tab (TODO)
- ⏳ Data loading for Phase tab (TODO)

---

## 📋 Implementation Plan

### Step 1: Radar Chart Control (2-3 days)

**Purpose:** Multi-dimensional voice characteristic visualization (e.g., MOS, Similarity, Naturalness, SNR, etc.)

**Requirements:**
- Custom Win2D-based control
- Radial axis system (5-8 axes)
- Data points connected to form polygon
- Color gradient for quality tiers
- Interactive hover tooltips

**Implementation:**
1. Create `RadarChartControl.xaml` with CanvasControl
2. Create `RadarChartControl.xaml.cs` with rendering logic
3. Define `RadarChartData` model:
   ```csharp
   public class RadarChartData
   {
       public List<RadarAxis> Axes { get; set; }  // e.g., MOS, Similarity, Naturalness
       public List<RadarDataPoint> Points { get; set; }  // Value for each axis (0-1)
       public string Label { get; set; }
       public Color Color { get; set; }
   }
   ```
4. Add backend endpoint: `GET /api/audio/radar?audio_id={id}`
5. Wire data loading in `AnalyzerViewModel`
6. Replace placeholder in AnalyzerView.xaml

**Backend Data Source:**
- Quality metrics from `/api/voice/analyze`
- Normalize values to 0-1 range
- Create radar axes: MOS, Similarity, Naturalness, SNR, Pitch Stability, etc.

### Step 2: Loudness Chart Control (2-3 days)

**Purpose:** LUFS (Loudness Units Full Scale) visualization over time

**Requirements:**
- Win2D-based line chart
- Time-based X-axis
- LUFS value Y-axis (typically -70 to 0 LUFS)
- Target loudness indicators (e.g., -16 LUFS for streaming)
- Color coding (green = good, yellow = warn, red = too loud)

**Implementation:**
1. Create `LoudnessChartControl.xaml` with CanvasControl
2. Create `LoudnessChartControl.xaml.cs` with rendering logic
3. Define `LoudnessChartData` model:
   ```csharp
   public class LoudnessChartData
   {
       public List<LoudnessPoint> Points { get; set; }  // (time, lufs)
       public double? TargetLUFS { get; set; }  // e.g., -16.0
       public double? IntegratedLUFS { get; set; }  // Overall loudness
       public double Duration { get; set; }
   }
   ```
4. Add backend endpoint: `GET /api/audio/loudness?audio_id={id}`
5. Wire data loading in `AnalyzerViewModel`
6. Replace placeholder in AnalyzerView.xaml

**Backend Data Source:**
- Use `pyloudnorm` library for LUFS calculation
- Analyze audio file and return time-series LUFS values
- Calculate integrated LUFS (overall loudness)

### Step 3: Phase Chart Control (2-3 days)

**Purpose:** Phase analysis visualization (stereo correlation, phase issues)

**Requirements:**
- Win2D-based polar/phase scope visualization
- Lissajous-style phase correlation display
- Time-based scrolling
- Mono/stereo indicators
- Phase coherence visualization

**Implementation:**
1. Create `PhaseChartControl.xaml` with CanvasControl
2. Create `PhaseChartControl.xaml.cs` with rendering logic
3. Define `PhaseChartData` model:
   ```csharp
   public class PhaseChartData
   {
       public List<PhasePoint> Points { get; set; }  // (left_sample, right_sample)
       public double Correlation { get; set; }  // -1 to 1
       public bool IsMono { get; set; }
       public List<PhaseIssue> Issues { get; set; }  // Phase problems detected
   }
   ```
4. Add backend endpoint: `GET /api/audio/phase?audio_id={id}`
5. Wire data loading in `AnalyzerViewModel`
6. Replace placeholder in AnalyzerView.xaml

**Backend Data Source:**
- Analyze stereo audio for phase correlation
- Detect phase issues (out-of-phase, polarity issues)
- Return phase data for visualization

---

## 🔧 Technical Details

### Chart Control Pattern

All chart controls should follow the same pattern as WaveformControl and SpectrogramControl:

```csharp
public sealed partial class ChartControl : UserControl
{
    private ChartData _data;
    private CanvasControl _canvas;
    
    public ChartData Data
    {
        get => _data;
        set
        {
            _data = value;
            _canvas?.Invalidate();
        }
    }
    
    private void Canvas_Draw(CanvasControl sender, CanvasDrawEventArgs args)
    {
        // Rendering logic
    }
}
```

### Backend Endpoint Pattern

All endpoints should follow the pattern in `backend/api/routes/audio.py`:

```python
@router.get("/radar")
async def get_radar_data(
    audio_id: str,
    width: int = 512
) -> RadarChartResponse:
    # Load audio
    # Analyze metrics
    # Return radar data
    pass
```

### Data Loading Pattern

In `AnalyzerViewModel.cs`:

```csharp
if (SelectedTab == "Radar")
{
    var radarData = await _backendClient.GetRadarChartDataAsync(SelectedAudioId);
    RadarChartData = radarData;
}
```

---

## 📊 Data Models Needed

### Radar Chart Models

```csharp
// src/VoiceStudio.Core/Models/RadarChartData.cs
public class RadarChartData
{
    public List<RadarAxis> Axes { get; set; } = new();
    public List<RadarDataPoint> Points { get; set; } = new();
    public string Label { get; set; } = string.Empty;
    public Color Color { get; set; } = Colors.Cyan;
}

public class RadarAxis
{
    public string Name { get; set; } = string.Empty;
    public double MaxValue { get; set; } = 1.0;
}

public class RadarDataPoint
{
    public string AxisName { get; set; } = string.Empty;
    public double Value { get; set; }  // 0.0 to 1.0 normalized
}
```

### Loudness Chart Models

```csharp
// src/VoiceStudio.Core/Models/LoudnessChartData.cs
public class LoudnessChartData
{
    public List<LoudnessPoint> Points { get; set; } = new();
    public double? TargetLUFS { get; set; }
    public double? IntegratedLUFS { get; set; }
    public double Duration { get; set; }
}

public class LoudnessPoint
{
    public double Time { get; set; }  // seconds
    public double LUFS { get; set; }  // -70 to 0
}
```

### Phase Chart Models

```csharp
// src/VoiceStudio.Core/Models/PhaseChartData.cs
public class PhaseChartData
{
    public List<PhasePoint> Points { get; set; } = new();
    public double Correlation { get; set; }  // -1.0 to 1.0
    public bool IsMono { get; set; }
    public List<PhaseIssue> Issues { get; set; } = new();
}

public class PhasePoint
{
    public double LeftSample { get; set; }  // -1.0 to 1.0
    public double RightSample { get; set; }  // -1.0 to 1.0
    public double Time { get; set; }  // seconds
}

public class PhaseIssue
{
    public double Time { get; set; }
    public string Type { get; set; } = string.Empty;  // "out_of_phase", "polarity", etc.
    public double Severity { get; set; }  // 0.0 to 1.0
}
```

---

## 📚 Files to Create/Modify

### New Files to Create

**Controls:**
- `src/VoiceStudio.App/Controls/RadarChartControl.xaml`
- `src/VoiceStudio.App/Controls/RadarChartControl.xaml.cs`
- `src/VoiceStudio.App/Controls/LoudnessChartControl.xaml`
- `src/VoiceStudio.App/Controls/LoudnessChartControl.xaml.cs`
- `src/VoiceStudio.App/Controls/PhaseChartControl.xaml`
- `src/VoiceStudio.App/Controls/PhaseChartControl.xaml.cs`

**Models:**
- `src/VoiceStudio.Core/Models/RadarChartData.cs`
- `src/VoiceStudio.Core/Models/LoudnessChartData.cs`
- `src/VoiceStudio.Core/Models/PhaseChartData.cs`

**Backend:**
- Update `backend/api/routes/audio.py` with new endpoints

### Files to Modify

**ViewModels:**
- `src/VoiceStudio.App/Views/Panels/AnalyzerViewModel.cs`
  - Add properties: `RadarChartData`, `LoudnessChartData`, `PhaseChartData`
  - Add data loading methods for each chart

**Views:**
- `src/VoiceStudio.App/Views/Panels/AnalyzerView.xaml`
  - Replace placeholder TextBlocks with chart controls
  - Add data bindings

**Services:**
- `src/VoiceStudio.Core/Services/IBackendClient.cs`
  - Add methods: `GetRadarChartDataAsync()`, `GetLoudnessChartDataAsync()`, `GetPhaseChartDataAsync()`
- `src/VoiceStudio.App/Services/BackendClient.cs`
  - Implement the new methods

---

## ✅ Success Criteria

### Phase 4D Completion Checklist

- [ ] RadarChartControl created and rendering
- [ ] LoudnessChartControl created and rendering
- [ ] PhaseChartControl created and rendering
- [ ] All three charts integrated into AnalyzerView
- [ ] Backend endpoints implemented
- [ ] Data loading working for all three charts
- [ ] Charts update when audio selected
- [ ] Charts update when tab switched
- [ ] Error handling with placeholders
- [ ] Performance acceptable (30fps+ rendering)

---

## 🚀 Implementation Order

### Recommended Sequence

1. **Radar Chart** (Start here - uses existing quality metrics)
   - Easiest data source (already available from `/api/voice/analyze`)
   - Most visually impactful
   - Good for demonstrating multi-dimensional analysis

2. **Loudness Chart** (Medium complexity)
   - Requires audio analysis library (`pyloudnorm`)
   - Time-series data visualization
   - Useful for audio production workflows

3. **Phase Chart** (Most complex)
   - Requires stereo audio analysis
   - Advanced signal processing
   - Specialized use case

---

## 📈 Estimated Timeline

**Total Effort:** 6-9 days

- Radar Chart: 2-3 days
- Loudness Chart: 2-3 days
- Phase Chart: 2-3 days

**Dependencies:**
- Backend audio analysis endpoints
- Win2D rendering expertise
- Audio signal processing knowledge

---

## 🎯 Next Steps

1. **Review and approve this roadmap**
2. **Create RadarChartControl** (start with this)
3. **Implement backend radar endpoint**
4. **Wire Radar chart into AnalyzerView**
5. **Test and iterate**
6. **Repeat for Loudness and Phase charts**

---

**Status:** 📋 Ready for Implementation  
**Priority:** High - Completes AnalyzerView functionality  
**Dependencies:** Win2D controls pattern, backend audio analysis

