# Complete Dependency List
## VoiceStudio Quantum+ - All Missing Dependencies

**Date:** 2025-01-28  
**Status:** 📋 **AUDIT COMPLETE**  
**Purpose:** Complete list of all dependencies that need to be fixed

---

## 🎯 Summary

**Total Dependencies to Fix:** 8 critical dependencies  
**Total Tasks:** 40 tasks across 3 workers  
**Priority:** HIGH - Fix dependencies so engines work correctly

---

## 📋 Complete Dependency List

### 1. TensorFlow (`tensorflow>=2.8.0`) ✅ FIXED
- **Status:** ✅ Already fixed in DeepFaceLab engine
- **Used By:** DeepFaceLab Engine
- **Location:** `requirements_engines.txt` line 153
- **Action:** ✅ Already required and validated

### 2. SpeechBrain (`speechbrain>=0.5.0`)
- **Status:** ⚠️ Needs fixing
- **Used By:** 
  - Speaker Encoder Engine
  - Quality Metrics Module
- **Location:** `requirements_engines.txt` line 39
- **Action:** Mark as required, add validation
- **Tasks:** W1-DEP-007, W1-DEP-014

### 3. OpenCV (`opencv-python>=4.5.0`)
- **Status:** ✅ Mostly enforced
- **Used By:** 
  - DeepFaceLab Engine ✅
  - FOMM Engine ✅
  - SadTalker Engine ✅
  - Image/Video engines
- **Location:** `requirements_engines.txt` line 46
- **Action:** Already enforced in most engines

### 4. Face Alignment (`face-alignment>=1.3.0`)
- **Status:** ⚠️ Needs fixing
- **Used By:** 
  - FOMM Engine
  - SadTalker Engine
- **Location:** `requirements_engines.txt` line 147
- **Action:** Mark as required, add validation
- **Tasks:** W1-DEP-001, W1-DEP-004

### 5. Librosa (`librosa==0.11.0`)
- **Status:** ⚠️ Needs fixing
- **Used By:** 
  - Quality Metrics Module
  - Enhanced Quality Metrics
  - Multiple audio processing modules
  - Multiple engines
- **Location:** `requirements_engines.txt` line 32
- **Action:** Mark as required in quality/audio modules
- **Tasks:** W1-DEP-008, W1-DEP-013, W1-DEP-016

### 6. SoundFile (`soundfile==0.12.1`)
- **Status:** ⚠️ Needs fixing
- **Used By:** 
  - Bark Engine
  - Streaming Engine
  - Multiple engines for audio I/O
- **Location:** `requirements_engines.txt` line 34
- **Action:** Mark as required in engines that need it
- **Tasks:** W1-DEP-010, W1-DEP-012

### 7. PyLoudNorm (`pyloudnorm==0.1.1`)
- **Status:** ⚠️ Needs fixing
- **Used By:** 
  - Enhanced Quality Metrics
  - LUFS Meter
  - Audio processing modules
- **Location:** `requirements_engines.txt` line 36
- **Action:** Mark as required in quality/audio modules
- **Tasks:** W1-DEP-017

### 8. PyTorch (`torch>=2.0.0`)
- **Status:** ✅ Mostly enforced
- **Used By:** 
  - Most ML engines
  - Quality Metrics
- **Location:** `requirements_engines.txt` line 16
- **Action:** Already enforced in most engines, verify quality metrics
- **Tasks:** W1-DEP-015

### 9. Backend Quality Modules (Internal)
- **Status:** ⚠️ Needs fixing
- **Used By:** 
  - Backend quality routes
- **Location:** Internal modules
- **Action:** Fix imports, ensure modules are available
- **Tasks:** W1-DEP-021, W1-DEP-022, W1-DEP-023

---

## 📊 Dependency by Engine/Module

### Engines Requiring Fixes

#### FOMM Engine
- **Face Alignment:** ⚠️ Should be required
- **OpenCV:** ✅ Already required
- **PyTorch:** ✅ Already required

#### SadTalker Engine
- **Face Alignment:** ⚠️ Should be required
- **OpenCV:** ✅ Already required
- **PyTorch:** ✅ Already required

#### Speaker Encoder Engine
- **SpeechBrain or Resemblyzer:** ⚠️ At least one should be required
- **Librosa:** ⚠️ Should be required for preprocessing

#### Bark Engine
- **SoundFile:** ⚠️ Should be required
- **PyTorch:** ✅ Already required
- **NumPy:** ✅ Already required

#### Streaming Engine
- **SoundFile:** ⚠️ Verify if needed

#### DeepFaceLab Engine
- **TensorFlow:** ✅ Already fixed
- **OpenCV:** ✅ Already required

### Modules Requiring Fixes

#### Quality Metrics Module
- **Librosa:** ⚠️ Should be required
- **SpeechBrain:** ⚠️ Should be required
- **PyTorch:** ⚠️ Should be required

#### Enhanced Quality Metrics
- **Librosa:** ⚠️ Should be required
- **PyLoudNorm:** ⚠️ Should be required

#### Backend Quality Routes
- **Quality Optimization:** ⚠️ Fix import
- **Quality Presets:** ⚠️ Fix import
- **Quality Comparison:** ⚠️ Fix import

---

## 📋 Task Breakdown by Worker

### Worker 1: 25 Tasks

**Engine Fixes (15 tasks):**
- FOMM Engine: 3 tasks
- SadTalker Engine: 3 tasks
- Speaker Encoder: 3 tasks
- Bark Engine: 2 tasks
- Streaming Engine: 1 task
- Quality Metrics: 3 tasks

**Audio Module Fixes (5 tasks):**
- Enhanced Quality Metrics: 3 tasks
- Enhanced Ensemble Router: 2 tasks

**Backend Fixes (5 tasks):**
- Quality Routes: 5 tasks

### Worker 2: 5 Tasks

**UI Improvements:**
- Dependency status display: 2 tasks
- Error messages: 2 tasks
- Settings panel: 1 task

### Worker 3: 10 Tasks

**Testing:**
- Dependency validation tests: 5 tasks

**Documentation:**
- Installation guide: 1 task
- Troubleshooting guide: 1 task
- Engine dependencies doc: 1 task
- Requirements verification: 1 task
- Installation script: 1 task

---

## 🔧 Implementation Pattern

### Standard Pattern for All Fixes:

```python
# At engine initialization
def initialize(self) -> bool:
    # Check required dependencies
    if not HAS_DEPENDENCY:
        error_msg = (
            "DependencyName is required for EngineName. "
            "Install with: pip install dependency-name>=version"
        )
        logger.error(error_msg)
        raise ImportError(error_msg)
    
    # Continue with initialization...
```

### Error Handling Pattern:

```python
# In methods that use dependencies
def some_method(self):
    if not HAS_DEPENDENCY:
        raise ImportError(
            "DependencyName is required. "
            "Install with: pip install dependency-name>=version"
        )
    
    # Use dependency...
    # Fallback only for exceptional runtime errors, not missing dependencies
```

---

## ✅ Verification Checklist

### After Implementation:
- [ ] All engines validate dependencies at initialization
- [ ] All engines fail fast with clear errors when dependencies missing
- [ ] No silent fallbacks for missing dependencies
- [ ] All error messages include installation instructions
- [ ] All dependencies verified in requirements_engines.txt
- [ ] Tests verify dependency validation works
- [ ] Documentation updated with dependency information

---

## 📝 Installation Commands

### All Dependencies (from requirements_engines.txt):
```bash
pip install -r requirements_engines.txt
```

### Individual Dependencies:
```bash
# TensorFlow
pip install tensorflow>=2.8.0

# SpeechBrain
pip install speechbrain>=0.5.0

# Face Alignment
pip install face-alignment>=1.3.0

# Librosa
pip install librosa==0.11.0

# SoundFile
pip install soundfile==0.12.1

# PyLoudNorm
pip install pyloudnorm==0.1.1

# OpenCV
pip install opencv-python>=4.5.0
```

---

**Document Created:** 2025-01-28  
**Status:** Ready for Implementation  
**See:** `DEPENDENCY_FIX_TASK_DISTRIBUTION_2025-01-28.md` for task assignments

