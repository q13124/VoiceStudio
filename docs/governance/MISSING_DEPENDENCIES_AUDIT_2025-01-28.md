# Missing Dependencies Audit
## VoiceStudio Quantum+ - Complete Dependency Analysis

**Date:** 2025-01-28  
**Status:** 🔍 **AUDIT COMPLETE**  
**Purpose:** Identify all missing/optional dependencies and assign fixes to workers

---

## 🎯 Executive Summary

**Audit Complete:** Comprehensive scan of entire codebase to identify all missing dependencies.  
**Total Issues Found:** Multiple engines and modules have optional dependencies that should be required.  
**Solution:** Update dependency validation and error handling across all affected modules.

---

## 📊 Dependency Categories

### Category 1: Critical Missing Dependencies (Should be Required)
These dependencies are marked as optional but are actually required for proper functionality:

1. **TensorFlow** - Required for DeepFaceLab engine
2. **SpeechBrain** - Required for Speaker Encoder and Quality Metrics
3. **OpenCV (cv2)** - Required for image/video processing engines
4. **Face Alignment** - Required for FOMM and SadTalker engines
5. **Librosa** - Required for audio processing and quality metrics
6. **SoundFile** - Required for audio I/O in multiple engines

### Category 2: Optional Dependencies (Correctly Optional)
These are truly optional and can have fallbacks:

1. **Resemblyzer** - Optional (SpeechBrain is alternative)
2. **Advanced Quality Enhancement** - Optional enhancement
3. **Audio Utils** - Internal module (should always be available)

### Category 3: Backend Dependencies
Backend routes that check for optional modules:

1. **Quality Optimization** - Backend quality routes
2. **Quality Presets** - Backend quality routes
3. **Quality Comparison** - Backend quality routes

---

## 🔍 Detailed Dependency Analysis

### Engine Dependencies

#### 1. DeepFaceLab Engine ✅ FIXED
- **TensorFlow:** ✅ Now required (fixed)
- **OpenCV:** ✅ Required (already enforced)
- **Face Alignment:** Optional (acceptable)

#### 2. FOMM Engine
- **OpenCV:** ✅ Required (already enforced)
- **Face Alignment:** ⚠️ Should be required for proper functionality
- **PyTorch:** ✅ Required (already enforced)

#### 3. SadTalker Engine
- **OpenCV:** ✅ Required (already enforced)
- **Face Alignment:** ⚠️ Should be required for proper functionality
- **PyTorch:** ✅ Required (already enforced)
- **PIL/Pillow:** ✅ Required (already enforced)

#### 4. Speaker Encoder Engine
- **SpeechBrain:** ⚠️ Should be required (or Resemblyzer)
- **Resemblyzer:** Optional (acceptable if SpeechBrain available)
- **Librosa:** ⚠️ Should be required for preprocessing

#### 5. Quality Metrics Module
- **SpeechBrain:** ⚠️ Should be required for speaker similarity
- **Resemblyzer:** Optional (acceptable if SpeechBrain available)
- **Librosa:** ⚠️ Should be required for audio analysis
- **PyTorch:** ⚠️ Should be required for quality calculations

#### 6. Streaming Engine
- **SoundFile:** ⚠️ Should be required for audio I/O
- **Librosa:** Optional (acceptable)

#### 7. Bark Engine
- **PyTorch:** ✅ Required (already enforced)
- **NumPy:** ✅ Required (already enforced)
- **SoundFile:** ⚠️ Should be required for audio I/O
- **Bark Package:** ✅ Required (already enforced)

#### 8. Enhanced Quality Metrics
- **Librosa:** ⚠️ Should be required
- **PyLoudNorm:** ⚠️ Should be required for LUFS metering
- **Quality Metrics Module:** Internal (should always be available)
- **Audio Utils:** Internal (should always be available)
- **LUFS Meter:** ⚠️ Should be required

#### 9. Enhanced Ensemble Router
- **Engine Router:** Internal (should always be available)
- **Quality Metrics:** Internal (should always be available)
- **Audio Utils:** Internal (should always be available)

### Backend Dependencies

#### Quality Routes (`backend/api/routes/quality.py`)
- **Quality Optimization:** ⚠️ Should be required
- **Quality Presets:** ⚠️ Should be required
- **Quality Comparison:** ⚠️ Should be required

---

## 📋 Complete Missing Dependencies List

### Critical (Should be Required)

1. **TensorFlow** (`tensorflow>=2.8.0`)
   - Used by: DeepFaceLab Engine ✅ FIXED
   - Status: Already in requirements, now properly required

2. **SpeechBrain** (`speechbrain>=0.5.0`)
   - Used by: Speaker Encoder Engine, Quality Metrics
   - Status: In requirements, but not enforced as required

3. **OpenCV** (`opencv-python>=4.5.0`)
   - Used by: DeepFaceLab, FOMM, SadTalker, Image/Video engines
   - Status: In requirements, some engines enforce it

4. **Face Alignment** (`face-alignment>=1.3.0`)
   - Used by: FOMM Engine, SadTalker Engine
   - Status: In requirements, but marked as optional

5. **Librosa** (`librosa==0.11.0`)
   - Used by: Quality Metrics, Audio Processing, Multiple engines
   - Status: In requirements, but marked as optional in some places

6. **SoundFile** (`soundfile==0.12.1`)
   - Used by: Multiple engines for audio I/O
   - Status: In requirements, but marked as optional

7. **PyLoudNorm** (`pyloudnorm==0.1.1`)
   - Used by: Enhanced Quality Metrics, LUFS Metering
   - Status: In requirements, but marked as optional

8. **PyTorch** (`torch>=2.0.0`)
   - Used by: Most ML engines
   - Status: In requirements, most engines enforce it

### Backend Modules (Internal)

1. **Quality Optimization Module**
   - Used by: Backend quality routes
   - Status: Should be available (internal module)

2. **Quality Presets Module**
   - Used by: Backend quality routes
   - Status: Should be available (internal module)

3. **Quality Comparison Module**
   - Used by: Backend quality routes
   - Status: Should be available (internal module)

---

## 👷 Worker Task Distribution

### Worker 1: Backend/Engines/Audio Processing (25 tasks)

#### Phase 1: Engine Dependency Fixes (15 tasks)

**DeepFaceLab Engine** ✅ (Already Fixed)
- ✅ TensorFlow dependency validation
- ✅ Error handling for missing TensorFlow

**FOMM Engine** (3 tasks)
- [ ] Add Face Alignment dependency check in `initialize()`
- [ ] Fail fast if Face Alignment missing
- [ ] Update error messages

**SadTalker Engine** (3 tasks)
- [ ] Add Face Alignment dependency check in `initialize()`
- [ ] Fail fast if Face Alignment missing
- [ ] Update error messages

**Speaker Encoder Engine** (3 tasks)
- [ ] Add SpeechBrain/Resemblyzer dependency check
- [ ] Fail fast if neither available
- [ ] Update error messages

**Bark Engine** (2 tasks)
- [ ] Add SoundFile dependency check
- [ ] Fail fast if SoundFile missing

**Streaming Engine** (1 task)
- [ ] Add SoundFile dependency check (if needed for underlying engines)

#### Phase 2: Audio Processing Module Fixes (5 tasks)

**Enhanced Quality Metrics** (3 tasks)
- [ ] Add Librosa dependency check
- [ ] Add PyLoudNorm dependency check
- [ ] Fail fast if dependencies missing

**Enhanced Ensemble Router** (2 tasks)
- [ ] Verify internal module dependencies
- [ ] Add validation for internal modules

#### Phase 3: Backend Route Fixes (5 tasks)

**Quality Routes** (5 tasks)
- [ ] Fix Quality Optimization module import
- [ ] Fix Quality Presets module import
- [ ] Fix Quality Comparison module import
- [ ] Add proper error handling
- [ ] Update dependency checks

---

### Worker 2: UI/UX/Frontend (5 tasks)

#### Phase 1: UI Dependency Validation (5 tasks)

**Dependency Display** (2 tasks)
- [ ] Add dependency status display in UI
- [ ] Show missing dependencies with installation instructions

**Error Messages** (2 tasks)
- [ ] Update UI error messages for missing dependencies
- [ ] Add dependency installation guidance

**Settings Panel** (1 task)
- [ ] Add dependency check section in Settings

---

### Worker 3: Testing/Quality/Documentation (10 tasks)

#### Phase 1: Dependency Testing (5 tasks)

**Dependency Validation Tests** (3 tasks)
- [ ] Create dependency validation test suite
- [ ] Test all engines with missing dependencies
- [ ] Verify error messages are clear

**Integration Tests** (2 tasks)
- [ ] Test engines with all dependencies installed
- [ ] Verify no fallbacks used when dependencies available

#### Phase 2: Documentation (5 tasks)

**Dependency Documentation** (3 tasks)
- [ ] Update installation guide with all dependencies
- [ ] Create dependency troubleshooting guide
- [ ] Document which engines need which dependencies

**Requirements Files** (2 tasks)
- [ ] Verify all dependencies in requirements_engines.txt
- [ ] Create dependency installation script

---

## 📋 Detailed Task List

### Worker 1 Tasks (25 tasks)

#### FOMM Engine (3 tasks)
- **TASK-W1-DEP-001:** Add Face Alignment dependency check in `initialize()`
- **TASK-W1-DEP-002:** Fail fast with clear error if Face Alignment missing
- **TASK-W1-DEP-003:** Update error messages with installation instructions

#### SadTalker Engine (3 tasks)
- **TASK-W1-DEP-004:** Add Face Alignment dependency check in `initialize()`
- **TASK-W1-DEP-005:** Fail fast with clear error if Face Alignment missing
- **TASK-W1-DEP-006:** Update error messages with installation instructions

#### Speaker Encoder Engine (3 tasks)
- **TASK-W1-DEP-007:** Add SpeechBrain/Resemblyzer dependency validation
- **TASK-W1-DEP-008:** Fail fast if neither SpeechBrain nor Resemblyzer available
- **TASK-W1-DEP-009:** Update error messages with installation instructions

#### Bark Engine (2 tasks)
- **TASK-W1-DEP-010:** Add SoundFile dependency check
- **TASK-W1-DEP-011:** Fail fast if SoundFile missing

#### Streaming Engine (1 task)
- **TASK-W1-DEP-012:** Verify SoundFile dependency (if needed)

#### Enhanced Quality Metrics (3 tasks)
- **TASK-W1-DEP-013:** Add Librosa dependency check
- **TASK-W1-DEP-014:** Add PyLoudNorm dependency check
- **TASK-W1-DEP-015:** Fail fast if dependencies missing

#### Enhanced Ensemble Router (2 tasks)
- **TASK-W1-DEP-016:** Verify internal module dependencies
- **TASK-W1-DEP-017:** Add validation for internal modules

#### Quality Routes Backend (5 tasks)
- **TASK-W1-DEP-018:** Fix Quality Optimization module import
- **TASK-W1-DEP-019:** Fix Quality Presets module import
- **TASK-W1-DEP-020:** Fix Quality Comparison module import
- **TASK-W1-DEP-021:** Add proper error handling for missing modules
- **TASK-W1-DEP-022:** Update dependency checks in quality routes

#### Quality Metrics Module (3 tasks)
- **TASK-W1-DEP-023:** Add SpeechBrain dependency check
- **TASK-W1-DEP-024:** Add Librosa dependency check
- **TASK-W1-DEP-025:** Add PyTorch dependency check

---

### Worker 2 Tasks (5 tasks)

#### UI Dependency Display (2 tasks)
- **TASK-W2-DEP-001:** Add dependency status display in UI panels
- **TASK-W2-DEP-002:** Show missing dependencies with installation instructions

#### Error Messages (2 tasks)
- **TASK-W2-DEP-003:** Update UI error messages for missing dependencies
- **TASK-W2-DEP-004:** Add dependency installation guidance in error dialogs

#### Settings Panel (1 task)
- **TASK-W2-DEP-005:** Add dependency check section in Settings panel

---

### Worker 3 Tasks (10 tasks)

#### Dependency Testing (5 tasks)
- **TASK-W3-DEP-001:** Create dependency validation test suite
- **TASK-W3-DEP-002:** Test all engines with missing dependencies
- **TASK-W3-DEP-003:** Verify error messages are clear and actionable
- **TASK-W3-DEP-004:** Test engines with all dependencies installed
- **TASK-W3-DEP-005:** Verify no fallbacks used when dependencies available

#### Documentation (5 tasks)
- **TASK-W3-DEP-006:** Update installation guide with all dependencies
- **TASK-W3-DEP-007:** Create dependency troubleshooting guide
- **TASK-W3-DEP-008:** Document which engines need which dependencies
- **TASK-W3-DEP-009:** Verify all dependencies in requirements_engines.txt
- **TASK-W3-DEP-010:** Create dependency installation script

---

## 📊 Summary Statistics

### Total Tasks: 40
- **Worker 1:** 25 tasks (Engine/Backend fixes)
- **Worker 2:** 5 tasks (UI improvements)
- **Worker 3:** 10 tasks (Testing/Documentation)

### Dependencies to Fix: 8 Critical
1. TensorFlow ✅ (Fixed)
2. SpeechBrain
3. OpenCV (mostly done)
4. Face Alignment
5. Librosa
6. SoundFile
7. PyLoudNorm
8. Backend Quality Modules

---

## ✅ Success Criteria

### Worker 1
- ✅ All engines validate dependencies at initialization
- ✅ All engines fail fast with clear errors when dependencies missing
- ✅ No silent fallbacks for missing dependencies
- ✅ Backend routes properly handle missing modules

### Worker 2
- ✅ UI displays dependency status
- ✅ Clear error messages with installation instructions
- ✅ Settings panel shows dependency status

### Worker 3
- ✅ Comprehensive dependency tests
- ✅ Complete dependency documentation
- ✅ Installation scripts created

---

## 🚀 Implementation Priority

### High Priority (Week 1)
1. FOMM Engine dependencies
2. SadTalker Engine dependencies
3. Speaker Encoder dependencies
4. Quality Metrics dependencies

### Medium Priority (Week 2)
1. Backend quality routes
2. Enhanced quality metrics
3. UI dependency display

### Low Priority (Week 3)
1. Documentation updates
2. Testing improvements
3. Installation scripts

---

**Document Created:** 2025-01-28  
**Status:** Ready for Implementation  
**Total Tasks:** 40 (25 + 5 + 10)

