# Phase 5: Voice Conversion Testing Evidence

**Date**: 2026-02-06
**Owner**: Engine Engineer (Role 5) + Core Platform (Role 4)
**Status**: STRUCTURE VERIFIED - AWAITING RUNTIME TESTING

---

## RVC Engine Verification

### Implementation Details

Source: `app/core/engines/rvc_engine.py` (2215 lines)

| Component | Description | Status |
|-----------|-------------|--------|
| Class | `RVCEngine` (line 283) | ✅ Verified |
| Protocol | Implements `EngineProtocol` | ✅ Verified |
| Convert Method | `convert_voice()` (line 454) | ✅ Verified |
| Real-time | `convert_realtime()` (line 617) | ✅ Verified |
| Caching | LRU model cache with eviction | ✅ Verified |

### Model Path Configuration

```python
# Default RVC model location
model_cache_dir = os.getenv("VOICESTUDIO_MODELS_PATH")
# Fallback: %PROGRAMDATA%\VoiceStudio\models\rvc
```

### RVC Model Requirements

| File | Required | Purpose |
|------|----------|---------|
| `<model>.pth` | ✅ Yes | Model weights |
| `<model>.index` | Optional | Retrieval index |
| `hubert/` | ✅ Yes | HuBERT feature extractor |

---

## So-VITS-SVC Engine Verification

### Implementation Details

Source: `app/core/engines/sovits_svc_engine.py` (690 lines)

| Component | Description | Status |
|-----------|-------------|--------|
| Class | `SoVitsSvcEngine` (line 97) | ✅ Verified |
| Protocol | Implements `EngineProtocol` | ✅ Verified |
| Initialize | Loads checkpoint and config | ✅ Verified |
| Device Support | CUDA/CPU auto-detection | ✅ Verified |

### Default Model Paths

```python
# Default paths (lines 140-153)
models_root = os.getenv("VOICESTUDIO_MODELS_PATH", r"E:\VoiceStudio\models")
checkpoint_path = models_root / "checkpoints" / "MyVoiceProj" / "model.pth"
config_path = checkpoint_path.parent / "config.json"
```

### So-VITS-SVC Model Requirements

| File | Required | Purpose |
|------|----------|---------|
| `model.pth` | ✅ Yes | Checkpoint weights |
| `config.json` | ✅ Yes | Model configuration |

---

## HTTP 424 Guard Behavior

### Implementation

Source: `backend/api/routes/rvc.py` lines 152-158

```python
if not inference_configured and not allow_passthrough:
    detail = (
        "So-VITS-SVC inference command not configured. "
        "Set SOVITS_SVC_INFER_COMMAND or configure "
        "infer_command in engine settings."
    )
    raise HTTPException(status_code=424, detail=detail)
```

### Guard Trigger Conditions

| Condition | Result |
|-----------|--------|
| `model.pth` missing | HTTP 424 (model not found) |
| `config.json` missing | HTTP 424 (config not found) |
| `SOVITS_SVC_INFER_COMMAND` not set | HTTP 424 (inference not configured) |
| All present | Conversion proceeds |

---

## So-VITS-SVC Conversion Proof Script

### Script Location

Source: `scripts/sovits_svc_conversion_proof.py` (435 lines)

### Script Usage

```powershell
python scripts/sovits_svc_conversion_proof.py `
  --checkpoint-path "models/checkpoints/MyVoiceProj/model.pth" `
  --config-path "models/checkpoints/MyVoiceProj/config.json"
```

### Proof Workflow

1. Validate checkpoint and config files exist
2. Check preflight status via `/api/rvc/preflight`
3. Perform conversion via `/api/rvc/convert`
4. Capture audio output and metrics
5. Generate proof artifact in `.buildlogs/`

---

## Test Execution Requirements

### Test 5.1: So-VITS-SVC Configuration

```powershell
# Verify model files exist
$modelPath = "e:\VoiceStudio\models\checkpoints\MyVoiceProj"
Test-Path "$modelPath\model.pth"   # REQUIRED
Test-Path "$modelPath\config.json" # REQUIRED

# Set environment variable (if using external inference)
$env:SOVITS_SVC_INFER_COMMAND = "path/to/infer.py"
```

### Test 5.2: So-VITS-SVC Conversion

| Step | Action | Expected Result |
|------|--------|-----------------|
| 5.2.1 | Run proof script | Script executes |
| 5.2.2 | Check conversion output | Audio file created |
| 5.2.3 | Listen to output | Audio intelligible |
| 5.2.4 | HTTP 424 guard test | 424 returned when model missing |

### Test 5.3: RVC Conversion

| Step | Action | Expected Result |
|------|--------|-----------------|
| 5.3.1 | Verify RVC model exists | Model present |
| 5.3.2 | Navigate to RVC panel | Panel loads |
| 5.3.3 | Select source audio | Audio selected |
| 5.3.4 | Select target model | Model selected |
| 5.3.5 | Execute conversion | Conversion completes |
| 5.3.6 | Listen to output | Quality acceptable |
| 5.3.7 | Check VRAM usage | < 8GB |

---

## Backend API Endpoints

### RVC Routes

Source: `backend/api/routes/rvc.py`

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/rvc/convert` | POST | Convert audio using RVC/So-VITS |
| `/api/rvc/preflight` | GET | Check engine readiness |
| `/api/rvc/models` | GET | List available models |
| `/api/rvc/models/upload` | POST | Upload new model |

---

## Model Directory Status

### Current State (2026-02-06)

| Directory | Status | Contents |
|-----------|--------|----------|
| `models/checkpoints/MyVoiceProj/` | ✅ Created | `config.json` (placeholder) |
| `models/checkpoints/Lain_SVC4/` | ✅ Exists | `config.json` |

**Note**: Actual `model.pth` files must be provided by tester. These are large binary files not included in the repository.

---

## Evidence Files

| File | Purpose | Status |
|------|---------|--------|
| rvc_engine.py | RVC implementation | ✅ Analyzed |
| sovits_svc_engine.py | So-VITS-SVC implementation | ✅ Analyzed |
| rvc.py | Backend routes | ✅ Analyzed |
| sovits_svc_conversion_proof.py | E2E proof script | ✅ Analyzed |

---

## Phase 5 Code Analysis: PASS

- ✅ RVC engine with convert_voice() implemented
- ✅ So-VITS-SVC engine with checkpoint loading
- ✅ HTTP 424 guard implemented for missing inference
- ✅ Default model paths configured
- ✅ Proof script available for automated testing
- ✅ Model directory structure created
- ⏳ Runtime testing requires actual model.pth files
