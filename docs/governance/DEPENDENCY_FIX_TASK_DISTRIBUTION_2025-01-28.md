# Dependency Fix Task Distribution
## VoiceStudio Quantum+ - Fix All Missing Dependencies

**Date:** 2025-01-28  
**Status:** 📋 **TASK ASSIGNMENT COMPLETE**  
**Total Tasks:** 40  
**Goal:** Fix all missing dependencies so engines work correctly without relying on fallbacks

---

## 🎯 Overview

**Problem:** Multiple engines and modules have optional dependencies that should be required, causing silent fallbacks instead of clear errors.

**Solution:** Update all engines and modules to:
1. Validate required dependencies at initialization
2. Fail fast with clear errors when dependencies missing
3. Keep fallbacks only for exceptional runtime errors
4. Provide clear installation instructions

---

## 📊 Task Distribution

### Worker 1: Backend/Engines/Audio Processing (25 tasks)

**Focus:** Engine dependency validation and error handling

#### Phase 1: Engine Dependency Fixes (15 tasks)

**FOMM Engine** (3 tasks)
- **TASK-W1-DEP-001:** Add Face Alignment dependency check in `initialize()`
  - File: `app/core/engines/fomm_engine.py`
  - Check: `HAS_FACE_ALIGNMENT` at initialization
  - Action: Raise `ImportError` with clear message if missing
  - Message: "face-alignment is required for FOMM engine. Install with: pip install face-alignment>=1.3.0"

- **TASK-W1-DEP-002:** Update `_extract_keypoints()` to fail fast if Face Alignment missing
  - File: `app/core/engines/fomm_engine.py`
  - Action: Check dependency before use, raise error if missing
  - Remove fallback ORB detector usage when Face Alignment is required

- **TASK-W1-DEP-003:** Update error messages throughout FOMM engine
  - File: `app/core/engines/fomm_engine.py`
  - Action: Ensure all error messages include installation instructions

**SadTalker Engine** (3 tasks)
- **TASK-W1-DEP-004:** Add Face Alignment dependency check in `initialize()`
  - File: `app/core/engines/sadtalker_engine.py`
  - Check: `HAS_FACE_ALIGNMENT` at initialization
  - Action: Raise `ImportError` with clear message if missing
  - Message: "face-alignment is required for SadTalker engine. Install with: pip install face-alignment>=1.3.0"

- **TASK-W1-DEP-005:** Update face alignment methods to fail fast if missing
  - File: `app/core/engines/sadtalker_engine.py`
  - Action: Check dependency before use, raise error if missing
  - Remove fallback simple features when Face Alignment is required

- **TASK-W1-DEP-006:** Update error messages throughout SadTalker engine
  - File: `app/core/engines/sadtalker_engine.py`
  - Action: Ensure all error messages include installation instructions

**Speaker Encoder Engine** (3 tasks)
- **TASK-W1-DEP-007:** Update dependency validation in `__init__()`
  - File: `app/core/engines/speaker_encoder_engine.py`
  - Action: Ensure at least one backend (SpeechBrain or Resemblyzer) is available
  - Current: Already has good validation, verify it works correctly

- **TASK-W1-DEP-008:** Add Librosa dependency check for preprocessing
  - File: `app/core/engines/speaker_encoder_engine.py`
  - Action: Check Librosa at initialization if needed for preprocessing
  - Message: "librosa is required for speaker encoder preprocessing. Install with: pip install librosa==0.11.0"

- **TASK-W1-DEP-009:** Verify error messages are clear
  - File: `app/core/engines/speaker_encoder_engine.py`
  - Action: Review and update error messages if needed

**Bark Engine** (2 tasks)
- **TASK-W1-DEP-010:** Add SoundFile dependency check
  - File: `app/core/engines/bark_engine.py`
  - Action: Check SoundFile at initialization
  - Message: "soundfile is required for Bark engine. Install with: pip install soundfile==0.12.1"

- **TASK-W1-DEP-011:** Update audio I/O methods to fail fast if SoundFile missing
  - File: `app/core/engines/bark_engine.py`
  - Action: Check dependency before audio operations

**Streaming Engine** (1 task)
- **TASK-W1-DEP-012:** Verify SoundFile dependency (if needed for underlying engines)
  - File: `app/core/engines/streaming_engine.py`
  - Action: Check if SoundFile is needed, add validation if required

**Quality Metrics Module** (3 tasks)
- **TASK-W1-DEP-013:** Add Librosa dependency check
  - File: `app/core/engines/quality_metrics.py`
  - Action: Check Librosa at module level or function level
  - Message: "librosa is required for quality metrics. Install with: pip install librosa==0.11.0"

- **TASK-W1-DEP-014:** Add SpeechBrain dependency check
  - File: `app/core/engines/quality_metrics.py`
  - Action: Check SpeechBrain for speaker similarity calculations
  - Message: "speechbrain is required for speaker similarity. Install with: pip install speechbrain>=0.5.0"

- **TASK-W1-DEP-015:** Add PyTorch dependency check
  - File: `app/core/engines/quality_metrics.py`
  - Action: Check PyTorch for quality calculations
  - Message: "torch is required for quality metrics. Install with: pip install torch>=2.0.0"

#### Phase 2: Audio Processing Module Fixes (5 tasks)

**Enhanced Quality Metrics** (3 tasks)
- **TASK-W1-DEP-016:** Add Librosa dependency check
  - File: `app/core/audio/enhanced_quality_metrics.py`
  - Action: Check Librosa at initialization or function level
  - Message: "librosa is required for enhanced quality metrics. Install with: pip install librosa==0.11.0"

- **TASK-W1-DEP-017:** Add PyLoudNorm dependency check
  - File: `app/core/audio/enhanced_quality_metrics.py`
  - Action: Check PyLoudNorm for LUFS metering
  - Message: "pyloudnorm is required for LUFS metering. Install with: pip install pyloudnorm==0.1.1"

- **TASK-W1-DEP-018:** Fail fast if dependencies missing
  - File: `app/core/audio/enhanced_quality_metrics.py`
  - Action: Raise errors instead of silently degrading functionality

**Enhanced Ensemble Router** (2 tasks)
- **TASK-W1-DEP-019:** Verify internal module dependencies
  - File: `app/core/audio/enhanced_ensemble_router.py`
  - Action: Ensure engine_router, quality_metrics, audio_utils are available
  - These are internal modules, should always be available

- **TASK-W1-DEP-020:** Add validation for internal modules
  - File: `app/core/audio/enhanced_ensemble_router.py`
  - Action: Add checks and clear errors if internal modules missing

#### Phase 3: Backend Route Fixes (5 tasks)

**Quality Routes** (5 tasks)
- **TASK-W1-DEP-021:** Fix Quality Optimization module import
  - File: `backend/api/routes/quality.py`
  - Action: Ensure proper import path, add clear error if module missing
  - Current: Uses `HAS_QUALITY_OPTIMIZATION` flag

- **TASK-W1-DEP-022:** Fix Quality Presets module import
  - File: `backend/api/routes/quality.py`
  - Action: Ensure proper import path, add clear error if module missing
  - Current: Uses `HAS_QUALITY_PRESETS` flag

- **TASK-W1-DEP-023:** Fix Quality Comparison module import
  - File: `backend/api/routes/quality.py`
  - Action: Ensure proper import path, add clear error if module missing
  - Current: Uses `HAS_QUALITY_COMPARISON` flag

- **TASK-W1-DEP-024:** Add proper error handling for missing modules
  - File: `backend/api/routes/quality.py`
  - Action: Return clear error responses when modules unavailable
  - Status: 503 Service Unavailable with helpful message

- **TASK-W1-DEP-025:** Update dependency checks in quality routes
  - File: `backend/api/routes/quality.py`
  - Action: Verify all routes check dependencies before use

---

### Worker 2: UI/UX/Frontend (5 tasks)

**Focus:** UI improvements for dependency status and error messages

#### Phase 1: UI Dependency Display (2 tasks)

- **TASK-W2-DEP-001:** Add dependency status display in UI panels
  - Files: Various ViewModels and Views
  - Action: Add dependency status indicators
  - Location: Settings panel, Engine selection panels
  - Display: Show which engines are available based on dependencies

- **TASK-W2-DEP-002:** Show missing dependencies with installation instructions
  - Files: Error dialogs, Settings panel
  - Action: Display missing dependencies with pip install commands
  - Format: Clear list with copy-paste installation commands

#### Phase 2: Error Messages (2 tasks)

- **TASK-W2-DEP-003:** Update UI error messages for missing dependencies
  - Files: All ViewModels that interact with engines
  - Action: Update error messages to include dependency information
  - Format: "Engine X requires dependency Y. Install with: pip install Y"

- **TASK-W2-DEP-004:** Add dependency installation guidance in error dialogs
  - Files: Error dialog components
  - Action: Add "Install Dependencies" button or link
  - Functionality: Show installation commands or open terminal

#### Phase 3: Settings Panel (1 task)

- **TASK-W2-DEP-005:** Add dependency check section in Settings panel
  - File: `src/VoiceStudio.App/Views/Panels/SettingsView.xaml` and ViewModel
  - Action: Add section showing all dependencies and their status
  - Features:
    - List all required dependencies
    - Show installed/missing status
    - Provide installation commands
    - Test dependency availability

---

### Worker 3: Testing/Quality/Documentation (10 tasks)

**Focus:** Testing, documentation, and installation scripts

#### Phase 1: Dependency Testing (5 tasks)

- **TASK-W3-DEP-001:** Create dependency validation test suite
  - File: `tests/quality/test_dependency_validation.py`
  - Action: Create comprehensive test suite
  - Tests:
    - Test each engine with missing dependencies
    - Verify error messages are clear
    - Verify no silent fallbacks for missing dependencies

- **TASK-W3-DEP-002:** Test all engines with missing dependencies
  - File: `tests/quality/test_dependency_validation.py`
  - Action: Test each engine individually
  - Verify: All engines fail fast with clear errors

- **TASK-W3-DEP-003:** Verify error messages are clear and actionable
  - File: `tests/quality/test_dependency_validation.py`
  - Action: Test error message clarity
  - Verify: All messages include installation instructions

- **TASK-W3-DEP-004:** Test engines with all dependencies installed
  - File: `tests/quality/test_engine_integration.py`
  - Action: Verify engines work correctly when dependencies available
  - Verify: No fallbacks used when dependencies available

- **TASK-W3-DEP-005:** Create dependency installation verification script
  - File: `tools/verify_dependencies.py`
  - Action: Create script to verify all dependencies are installed
  - Output: Report of missing dependencies with installation commands

#### Phase 2: Documentation (5 tasks)

- **TASK-W3-DEP-006:** Update installation guide with all dependencies
  - File: `docs/user/GETTING_STARTED.md`
  - Action: Add comprehensive dependency list
  - Include: All required dependencies with versions

- **TASK-W3-DEP-007:** Create dependency troubleshooting guide
  - File: `docs/user/TROUBLESHOOTING.md`
  - Action: Add section on dependency issues
  - Include: Common problems and solutions

- **TASK-W3-DEP-008:** Document which engines need which dependencies
  - File: `docs/developer/ENGINE_DEPENDENCIES.md` (new file)
  - Action: Create comprehensive engine dependency matrix
  - Include: Required vs optional dependencies for each engine

- **TASK-W3-DEP-009:** Verify all dependencies in requirements_engines.txt
  - File: `requirements_engines.txt`
  - Action: Audit and verify all dependencies are listed
  - Verify: All required dependencies are present with correct versions

- **TASK-W3-DEP-010:** Create dependency installation script
  - File: `scripts/install-dependencies.ps1` or `.sh`
  - Action: Create automated installation script
  - Features:
    - Check Python version
    - Install PyTorch (CUDA version)
    - Install all other dependencies
    - Verify installations
    - Report any failures

---

## 📋 Implementation Guidelines

### For All Workers

1. **Dependency Validation Pattern:**
   ```python
   # At initialization
   if not HAS_DEPENDENCY:
       error_msg = (
           "DependencyName is required for EngineName. "
           "Install with: pip install dependency-name>=version"
       )
       logger.error(error_msg)
       raise ImportError(error_msg)
   ```

2. **Error Handling:**
   - Always raise `ImportError` for missing dependencies
   - Never silently fall back for missing dependencies
   - Fallbacks only for exceptional runtime errors
   - Always include installation instructions

3. **Testing:**
   - Test with dependencies missing (should fail fast)
   - Test with dependencies installed (should work correctly)
   - Verify no fallbacks used when dependencies available

---

## ✅ Success Criteria

### Worker 1
- ✅ All engines validate dependencies at initialization
- ✅ All engines fail fast with clear errors when dependencies missing
- ✅ No silent fallbacks for missing dependencies
- ✅ Backend routes properly handle missing modules
- ✅ All error messages include installation instructions

### Worker 2
- ✅ UI displays dependency status
- ✅ Clear error messages with installation instructions
- ✅ Settings panel shows dependency status
- ✅ Users can easily see what dependencies are missing

### Worker 3
- ✅ Comprehensive dependency tests
- ✅ Complete dependency documentation
- ✅ Installation scripts created
- ✅ All dependencies verified in requirements file

---

## 📊 Task Summary

| Worker | Tasks | Focus Area |
|--------|-------|------------|
| **Worker 1** | 25 tasks | Engine/Backend dependency fixes |
| **Worker 2** | 5 tasks | UI dependency display |
| **Worker 3** | 10 tasks | Testing/Documentation |
| **Total** | **40 tasks** | Complete dependency fix |

---

## 🚀 Implementation Priority

### High Priority (Do First)
1. FOMM Engine dependencies (3 tasks)
2. SadTalker Engine dependencies (3 tasks)
3. Speaker Encoder dependencies (3 tasks)
4. Quality Metrics dependencies (3 tasks)

### Medium Priority
1. Bark Engine dependencies (2 tasks)
2. Enhanced Quality Metrics (3 tasks)
3. Backend quality routes (5 tasks)

### Lower Priority
1. UI dependency display (5 tasks)
2. Testing improvements (5 tasks)
3. Documentation updates (5 tasks)

---

## 📝 Notes

- **Fallbacks are kept** - They remain as protective layer for exceptional runtime errors
- **Dependencies should be required** - Engines should fail fast if dependencies missing
- **Clear error messages** - All errors must include installation instructions
- **All dependencies in requirements** - Verify all are in `requirements_engines.txt`

---

**Document Created:** 2025-01-28  
**Status:** Ready for Implementation  
**Total Tasks:** 40 (25 + 5 + 10)

