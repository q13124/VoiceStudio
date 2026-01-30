# Phase 4: Visual Components - Implementation Plan
## VoiceStudio Quantum+ - Timeline Visualizations & Audio Analysis

**Date:** 2025-01-27  
**Status:** Planning Phase  
**Priority:** High (Next Phase After Phase 2 Completion)

---

## 🎯 Executive Summary

**Goal:** Transform placeholder visualizations into real-time audio waveforms, spectrograms, and analysis charts. Replace static placeholders with professional DAW-grade visual components.

---

## 📋 Phase 4 Components

### 1. Backend Audio Analysis Endpoints (Foundation)

**Priority:** High - Required before visual components

#### 1.1 Waveform Data Endpoint
- **Endpoint:** `GET /api/audio/waveform`
- **Purpose:** Return downsampled waveform data for rendering
- **Parameters:**
  - `audio_id` - Audio file identifier
  - `width` - Target pixel width (for downsampling)
  - `mode` - "peak" or "rms" (waveform type)
- **Response:** JSON array of sample points
- **File:** `backend/api/routes/audio.py` (new)

#### 1.2 Spectrogram Data Endpoint
- **Endpoint:** `GET /api/audio/spectrogram`
- **Purpose:** Return FFT data for spectrogram rendering
- **Parameters:**
  - `audio_id` - Audio file identifier
  - `width` - Target pixel width
  - `height` - Target pixel height (frequency bins)
- **Response:** JSON array of FFT frames
- **File:** `backend/api/routes/audio.py`

#### 1.3 Audio Meters Endpoint
- **Endpoint:** `GET /api/audio/meters`
- **Purpose:** Return real-time audio level data
- **Parameters:**
  - `audio_id` - Audio file identifier
  - `channels` - Number of channels
- **Response:** Peak, RMS, LUFS values
- **File:** `backend/api/routes/audio.py`

### 2. Frontend Visual Controls

#### 2.1 WaveformControl (Win2D)
- **Technology:** Win2D CanvasControl
- **Purpose:** Render audio waveforms in timeline
- **Features:**
  - Peak/RMS waveform rendering
  - Zoom and pan support
  - Playhead position indicator
  - Multi-track display
- **File:** `src/VoiceStudio.App/Controls/WaveformControl.xaml`
- **Dependencies:** Win2D NuGet package

#### 2.2 SpectrogramControl (Win2D)
- **Technology:** Win2D CanvasControl
- **Purpose:** Render frequency spectrograms
- **Features:**
  - FFT-based visualization
  - Color mapping (frequency → color)
  - Zoom and scroll
  - Real-time updates
- **File:** `src/VoiceStudio.App/Controls/SpectrogramControl.xaml`
- **Dependencies:** Win2D NuGet package

#### 2.3 Analyzer Charts
- **Technology:** Win2D or LiveCharts
- **Purpose:** Display audio analysis data
- **Charts:**
  - Waveform chart (time domain)
  - Spectral chart (frequency domain)
  - Radar chart (polar frequency response)
  - LUFS/loudness chart
  - Phase chart
- **File:** `src/VoiceStudio.App/Controls/AnalyzerCharts.xaml`

#### 2.4 VU Meters
- **Technology:** Custom WinUI 3 controls
- **Purpose:** Real-time audio level meters
- **Features:**
  - Peak and RMS indicators
  - Visual feedback per channel
  - Smooth animations
- **File:** `src/VoiceStudio.App/Controls/VUMeter.xaml`

### 3. Timeline Integration

#### 3.1 Timeline Waveform Rendering
- **Integration:** Replace clip placeholders with WaveformControl
- **File:** `src/VoiceStudio.App/Views/Panels/TimelineView.xaml`
- **Features:**
  - Waveform per clip
  - Zoom controls wired
  - Playhead synchronization

#### 3.2 Timeline Spectrogram
- **Integration:** Replace bottom placeholder with SpectrogramControl
- **File:** `src/VoiceStudio.App/Views/Panels/TimelineView.xaml`
- **Features:**
  - Full timeline spectrogram
  - Zoom and scroll
  - Playhead synchronization

### 4. Zoom Controls Implementation

#### 4.1 Timeline Zoom
- **Features:**
  - Zoom in/out buttons functional
  - Mouse wheel zoom
  - Zoom level display
  - Pan support
- **File:** `src/VoiceStudio.App/Views/Panels/TimelineViewModel.cs`

---

## 🗺️ Implementation Roadmap

### Phase 4A: Backend Foundation (Week 1) ✅ COMPLETE
1. ✅ Create `backend/api/routes/audio.py`
2. ✅ Implement waveform data endpoint
3. ✅ Implement spectrogram data endpoint
4. ✅ Implement audio meters endpoint
5. ✅ Add audio analysis utilities
6. ✅ Test endpoints with sample audio

### Phase 4B: Win2D Integration (Week 1-2) ✅ COMPLETE
1. ✅ Add Win2D NuGet package (guide created)
2. ✅ Create WaveformControl skeleton
3. ✅ Create SpectrogramControl skeleton
4. ✅ Test Win2D rendering (controls ready)

### Phase 4C: Timeline Integration (Week 2) ✅ COMPLETE
1. ✅ Create C# models (WaveformData, SpectrogramData, AudioMeters)
2. ✅ Add backend client methods
3. ✅ Update TimelineView.xaml
4. ✅ Update TimelineViewModel.cs
5. ✅ Wire zoom controls
6. ✅ Waveform loading for clips
7. ✅ Spectrogram loading

### Phase 4C: Waveform Control (Week 2)
1. ✅ Implement waveform data loading
2. ✅ Implement peak/RMS rendering
3. ✅ Add zoom and pan
4. ✅ Add playhead indicator
5. ✅ Integrate into TimelineView

### Phase 4D: AnalyzerView Integration (Week 3) 🚧 IN PROGRESS
1. ✅ AnalyzerView waveform tab working
2. ✅ AnalyzerView spectrogram tab working
3. ⏳ Radar chart control (pending)
4. ⏳ Loudness chart control (pending)
5. ⏳ Phase chart control (pending)
6. ⏳ Data loading for charts (pending)

### Phase 4E: Analyzer Charts (Week 3)
1. ✅ Implement analyzer chart controls
2. ✅ Wire to backend data
3. ✅ Integrate into AnalyzerView
4. ✅ Test all chart types

### Phase 4F: VU Meters (Week 3-4)
1. ✅ Implement VU meter control
2. ✅ Wire to real-time data
3. ✅ Integrate into EffectsMixerView
4. ✅ Test meter updates

### Phase 4G: Timeline Integration (Week 4)
1. ✅ Replace clip placeholders with waveforms
2. ✅ Replace spectrogram placeholder
3. ✅ Wire zoom controls
4. ✅ Test end-to-end flow

---

## 📦 Dependencies

### NuGet Packages
- **Win2D.WinUI** - For custom rendering
- **Microsoft.Graphics.Win2D** - Win2D core library

### Backend Libraries
- **librosa** - Audio analysis (already installed)
- **numpy** - Array operations (already installed)
- **scipy** - FFT operations (may need to add)

---

## 🔧 Technical Specifications

### Waveform Data Format
```json
{
  "samples": [0.5, -0.3, 0.8, ...],
  "sample_rate": 22050,
  "duration": 5.2,
  "channels": 1,
  "width": 1024
}
```

### Spectrogram Data Format
```json
{
  "frames": [
    {"time": 0.0, "frequencies": [0.1, 0.5, 0.8, ...]},
    {"time": 0.1, "frequencies": [0.2, 0.6, 0.9, ...]},
    ...
  ],
  "sample_rate": 22050,
  "fft_size": 2048,
  "hop_length": 512
}
```

### Audio Meters Format
```json
{
  "peak": 0.95,
  "rms": 0.65,
  "lufs": -18.5,
  "channels": [
    {"peak": 0.95, "rms": 0.65},
    {"peak": 0.92, "rms": 0.62}
  ]
}
```

---

## ✅ Success Criteria

- [ ] Waveforms render in timeline for all clips
- [ ] Spectrogram displays real audio data
- [ ] Zoom controls functional
- [ ] Playhead synchronized with playback
- [ ] Analyzer charts display real data
- [ ] VU meters update in real-time
- [ ] Performance acceptable (60fps target)
- [ ] All backend endpoints tested

---

## 📚 Key Files & Locations

### Backend
- `backend/api/routes/audio.py` - Audio analysis endpoints (new)
- `app/core/audio/audio_utils.py` - Audio utilities (existing)

### Frontend
- `src/VoiceStudio.App/Controls/WaveformControl.xaml` - Waveform control (new)
- `src/VoiceStudio.App/Controls/SpectrogramControl.xaml` - Spectrogram control (new)
- `src/VoiceStudio.App/Controls/VUMeter.xaml` - VU meter control (new)
- `src/VoiceStudio.App/Views/Panels/TimelineView.xaml` - Timeline integration
- `src/VoiceStudio.App/Views/Panels/AnalyzerView.xaml` - Analyzer integration

---

## 🎯 Next Steps

1. **Start with Backend Foundation** (Phase 4A)
   - Create audio analysis endpoints
   - Test with sample audio files
   - Verify data format compatibility

2. **Add Win2D Package** (Phase 4B)
   - Add Win2D.WinUI NuGet package
   - Create control skeletons
   - Test basic rendering

3. **Implement Waveform Control** (Phase 4C)
   - Start with simple waveform rendering
   - Add zoom/pan functionality
   - Integrate into timeline

---

**Last Updated:** 2025-01-27  
**Status:** Planning Complete - Ready for Implementation  
**Next Action:** Begin Phase 4A - Backend Foundation

