# Worker 2: Support Worker 1 - UI Integration Plan
## Adding UI Controls for Route Enhancements

**Date:** 2025-01-28  
**Worker:** Worker 2 (UI/UX/Frontend)  
**Status:** 🎯 **IN PROGRESS**

---

## 📋 Overview

Worker 1 has enhanced 9 backend routes with new library integrations. Worker 2 needs to add UI controls to expose these new features to users.

---

## ✅ Route Enhancements Requiring UI Updates

### 1. Transcription Route - VAD Support
**Backend Enhancement:** Added `use_vad: bool = False` parameter  
**UI Panel:** `TranscribeView.xaml`  
**Status:** ⚠️ **NEEDS UPDATE**

**Required UI Changes:**
- Add checkbox: "Use Voice Activity Detection (VAD)"
- Add tooltip explaining VAD benefits
- Bind to new `UseVad` property in `TranscribeViewModel`
- Update `TranscribeAsync` to pass `use_vad` parameter to backend

**Files to Modify:**
- `src/VoiceStudio.App/Views/Panels/TranscribeView.xaml` - Add VAD checkbox
- `src/VoiceStudio.App/Views/Panels/TranscribeViewModel.cs` - Add `UseVad` property and pass to backend

---

### 2. Lexicon Route - Phonemization Integration
**Backend Enhancement:** Enhanced `/phoneme` endpoint with phonemizer/gruut libraries  
**UI Panel:** `LexiconView.xaml`  
**Status:** ⚠️ **NEEDS VERIFICATION**

**Required UI Changes:**
- Verify phoneme generation displays confidence scores (0.9 for phonemizer vs 0.85 for fallback)
- Add indicator showing which phonemization method was used (phonemizer/gruut/espeak-ng)
- Update UI to show improved confidence scores

**Files to Check:**
- `src/VoiceStudio.App/Views/Panels/LexiconView.xaml` - Verify phoneme display
- `src/VoiceStudio.App/Views/Panels/LexiconViewModel.cs` - Verify backend integration

---

### 3. ML Optimization Route - Error Handling
**Backend Enhancement:** Improved ray[tune] error handling  
**UI Panel:** Need to identify panel  
**Status:** ⚠️ **NEEDS IDENTIFICATION**

**Required UI Changes:**
- Verify error messages are clear and user-friendly
- Ensure ray[tune] errors are properly displayed

**Files to Check:**
- Identify which panel uses ML optimization route
- Verify error handling in UI

---

### 4. Voice Route - Pitch Tracking
**Backend Enhancement:** Added pitch tracking for pitch stability calculation  
**UI Panel:** `VoiceSynthesisView.xaml`  
**Status:** ⚠️ **NEEDS UPDATE**

**Required UI Changes:**
- Display pitch stability metrics (replaces placeholder 0.91)
- Show pitch tracking method used (crepe/pyin)
- Display coefficient of variation (CV) if available

**Files to Modify:**
- `src/VoiceStudio.App/Views/Panels/VoiceSynthesisView.xaml` - Add pitch stability display
- `src/VoiceStudio.App/Views/Panels/VoiceSynthesisViewModel.cs` - Update to show real pitch stability

---

### 5. Training Route - Hyperparameter Optimization
**Backend Enhancement:** Added `POST /api/training/hyperparameters/optimize` endpoint  
**UI Panel:** `TrainingView.xaml`  
**Status:** ⚠️ **NEEDS UPDATE**

**Required UI Changes:**
- Add "Optimize Hyperparameters" button/section
- Add controls for hyperparameter space configuration
- Add method selection (optuna/hyperopt/ray[tune])
- Display optimization results and recommendations

**Files to Modify:**
- `src/VoiceStudio.App/Views/Panels/TrainingView.xaml` - Add hyperparameter optimization section
- `src/VoiceStudio.App/Views/Panels/TrainingViewModel.cs` - Add optimization command and properties

---

### 6. Analytics Route - ModelExplainer Integration
**Backend Enhancement:** ModelExplainer integration (shap/lime)  
**UI Panel:** `AnalyticsDashboardView.xaml`  
**Status:** ⚠️ **NEEDS VERIFICATION**

**Required UI Changes:**
- Verify model explainability features are exposed
- Ensure SHAP/LIME visualizations are available

**Files to Check:**
- `src/VoiceStudio.App/Views/Panels/AnalyticsDashboardView.xaml` - Verify explainability features
- `src/VoiceStudio.App/Views/Panels/AnalyticsDashboardViewModel.cs` - Verify backend integration

---

### 7. Articulation Route - PitchTracker Integration
**Backend Enhancement:** PitchTracker integration (crepe/pyin)  
**UI Panel:** Need to identify panel  
**Status:** ⚠️ **NEEDS IDENTIFICATION**

**Required UI Changes:**
- Display pitch tracking results
- Show articulation metrics using pitch data

**Files to Check:**
- Identify which panel uses articulation route
- Verify pitch tracking display

---

### 8. Effects Route - PostFXProcessor Integration
**Backend Enhancement:** PostFXProcessor integration (pedalboard)  
**UI Panel:** `EffectsMixerView.xaml`  
**Status:** ⚠️ **NEEDS VERIFICATION**

**Required UI Changes:**
- Verify professional audio effects are available
- Ensure pedalboard effects are properly exposed in UI

**Files to Check:**
- `src/VoiceStudio.App/Views/Panels/EffectsMixerView.xaml` - Verify effects are available
- `src/VoiceStudio.App/Views/Panels/EffectsMixerViewModel.cs` - Verify backend integration

---

### 9. Prosody Route - pyrubberband & Phonemizer Integration
**Backend Enhancement:** pyrubberband for pitch/rate modification, Phonemizer for phoneme analysis  
**UI Panel:** `ProsodyView.xaml`  
**Status:** ⚠️ **NEEDS VERIFICATION**

**Required UI Changes:**
- Verify high-quality pitch/rate modification is available
- Verify phoneme analysis uses Phonemizer
- Display method used (pyrubberband vs fallback)

**Files to Check:**
- `src/VoiceStudio.App/Views/Panels/ProsodyView.xaml` - Verify features are exposed
- `src/VoiceStudio.App/Views/Panels/ProsodyViewModel.cs` - Verify backend integration

---

## 🎯 Implementation Priority

### High Priority (Immediate)
1. **Transcription Route - VAD Support** - Simple checkbox addition
2. **Training Route - Hyperparameter Optimization** - New feature, needs UI section

### Medium Priority
3. **Voice Route - Pitch Tracking** - Display real metrics
4. **Prosody Route - Features Verification** - Ensure features are exposed
5. **Lexicon Route - Phonemization** - Show improved confidence scores

### Low Priority (Verification)
6. **Effects Route - PostFXProcessor** - Verify existing UI
7. **Analytics Route - ModelExplainer** - Verify existing UI
8. **Articulation Route - PitchTracker** - Identify panel first
9. **ML Optimization Route - Error Handling** - Identify panel first

---

## 📝 Implementation Steps

### Step 1: High Priority Updates
1. Add VAD checkbox to TranscribeView
2. Add hyperparameter optimization section to TrainingView

### Step 2: Medium Priority Updates
3. Update VoiceSynthesisView to show pitch stability
4. Verify ProsodyView features
5. Update LexiconView to show phonemization method

### Step 3: Verification
6. Verify EffectsMixerView exposes PostFXProcessor features
7. Verify AnalyticsDashboardView exposes ModelExplainer features
8. Identify and verify Articulation panel
9. Identify and verify ML Optimization panel

---

## ✅ Quality Assurance

- All new UI controls must use VSQ.* design tokens
- All new UI controls must have accessibility properties
- All new UI controls must have tooltips
- All new features must have proper error handling
- All new features must have loading states

---

## 📊 Progress Tracking

- [ ] Transcription Route - VAD Support
- [ ] Lexicon Route - Phonemization Verification
- [ ] ML Optimization Route - Panel Identification
- [ ] Voice Route - Pitch Tracking Display
- [ ] Training Route - Hyperparameter Optimization
- [ ] Analytics Route - ModelExplainer Verification
- [ ] Articulation Route - Panel Identification
- [ ] Effects Route - PostFXProcessor Verification
- [ ] Prosody Route - Features Verification

---

**Status:** 🎯 **IN PROGRESS**  
**Next Action:** Start with high priority updates (VAD checkbox, hyperparameter optimization)  
**Estimated Time:** 2-3 days

