# Engine Engineer — Start Prompt

**Date:** 2025-01-28  
**Role:** Engine Engineer (TTS / cloning / audio)  
**Gate Focus:** Advance voice cloning quality + capability (Gate E)  
**Status:** Ready to start

---

## 🎯 Your Mission

Advance **voice cloning quality + capability** while staying local-first and keeping engine dependencies compatible (per the architecture blueprint + dependency guide).

**Priority:** All work must move voice cloning quality forward. No placeholder implementations.

---

## ✅ Work Completed (Reference)

**VS-0002 (DONE):** Replace placeholder ML quality prediction with production implementation  
**VS-0007 (DONE):** ML quality prediction integration into engine metrics  
**VS-0009 (DONE):** Enable ML prediction in Chatterbox and Tortoise voice cloning engines

**Current Status:**
- ✅ Quality metrics framework exists (`app/core/engines/quality_metrics.py`)
- ✅ Model preflight service exists (`backend/services/model_preflight.py`)
- ✅ XTTS, Chatterbox, Tortoise engines have ML prediction enabled
- ✅ Default engine selection logic added to voice routes (XTTS -> Piper -> eSpeak fallback)

---

## 🚀 Next Tasks (Ordered Priority)

### Task 1: Wire "real" engine defaults into routes (NO placeholder responses)

**Status:** ⚠️ PARTIALLY DONE (default selection added, but need to verify full integration)

**What to do:**
1. Verify `/api/voice/*` routes use XTTS as primary default (✅ DONE - default selection logic added)
2. Verify fallback chain works: XTTS → Piper → eSpeak (✅ DONE - fallback logic added)
3. Test that `/api/voice/synthesize` endpoint works end-to-end with default engine
4. Verify `/api/transcribe` defaults to `whisper_cpp` and supports `model_path` override (✅ Already defaulted)

**Success Criteria:**
- `/api/voice/synthesize` with no `engine` parameter defaults to XTTS
- If XTTS unavailable, falls back to Piper
- If Piper unavailable, falls back to eSpeak-ng
- `/api/transcribe` defaults to `whisper_cpp` (✅ Already configured)
- End-to-end voice workflow produces real audio/text artifacts

**Files to verify:**
- `backend/api/routes/voice.py` - Default engine selection (✅ Updated)
- `backend/api/routes/transcribe.py` - Default whisper_cpp (✅ Already defaulted)
- `backend/services/model_preflight.py` - Preflight checks (✅ Exists)
- `backend/services/EngineConfigService.py` - Default engine config (✅ Exists)

**Proof Run:**
```bash
# Test default engine selection
curl -X POST http://localhost:8000/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"profile_id": "test", "text": "Hello world", "language": "en"}'
# Should use XTTS by default (or fallback chain if unavailable)

# Test transcribe default
curl -X POST http://localhost:8000/api/transcribe \
  -H "Content-Type: application/json" \
  -d '{"audio_path": "test.wav", "language": "en"}'
# Should use whisper_cpp by default
```

---

### Task 2: Voice conversion (So-VITS-SVC 4.0)

**Status:** 🔄 PENDING

**What to do:**
1. Check if So-VITS-SVC engine adapter exists under `app/core/engines/`
2. If not, implement it using checkpoint layout: `models\checkpoints\<project>\model.pth` + `config.json`
3. Implement voice conversion methods (`convert_voice`, `convert_realtime`)
4. Expose via engine registry/config so it's selectable and testable
5. Integrate with `/api/rvc` route if separate route exists

**Success Criteria:**
- So-VITS-SVC engine exists in `app/core/engines/`
- Engine registered in `app/core/engines/__init__.py`
- Engine manifest exists in `engines/audio/sovits/engine.manifest.json`
- `/api/rvc` or voice conversion endpoint produces transformed audio given valid checkpoint + config
- Preflight checks verify checkpoint/config existence before conversion

**Files to check/create:**
- `app/core/engines/sovits_engine.py` or `rvc_engine.py` (check if exists)
- `engines/audio/sovits/engine.manifest.json` (or similar)
- `backend/api/routes/rvc.py` (verify integration)
- `backend/services/model_preflight.py` (verify So-VITS preflight exists)

**Reference:**
- Model root: `E:\VoiceStudio\models`
- Checkpoint path: `models\checkpoints\<project>\model.pth` + `config.json`
- Related: RVC engine exists (`app/core/engines/rvc_engine.py`)

---

### Task 3: Quality metrics error handling (real computation with actionable guidance)

**Status:** ⚠️ NEEDS VERIFICATION

**What to do:**
1. Verify quality metrics pipeline never returns dummy values when deps are missing
2. Ensure missing dependencies return actionable guidance ("pip install ...", "model path ...")
3. Check that PESQ/STOI + embedding similarity (resemblyzer/speechbrain) execute when deps are present
4. Test error messages are user-friendly and actionable

**Success Criteria:**
- Quality metrics either compute OR explicitly report missing dependencies
- Error messages include installation instructions ("pip install pesq")
- Error messages include model path instructions when applicable
- No silent failures or placeholder values returned

**Files to verify:**
- `app/core/engines/quality_metrics.py` - Error handling for missing deps
- All engines using quality metrics - Error handling consistency

**Proof Run:**
```python
# Test with missing dependencies
from app.core.engines.quality_metrics import calculate_all_metrics
import numpy as np

audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 22050)).astype(np.float32)
metrics = calculate_all_metrics(audio, sample_rate=22050)

# Should either compute metrics OR return actionable error message
# No placeholder values or silent failures
```

---

## 📋 Current Model Wiring (MUST REMAIN CONSISTENT)

- **Model root**: `E:\VoiceStudio\models` (default via `backend/api/main.py`, overrideable via `VOICESTUDIO_MODELS_PATH`)
- **Primary TTS**: Coqui XTTS-v2 (`tts_models/multilingual/multi-dataset/xtts_v2`) — Coqui TTS manages auto-download (legacy alias `coqui/XTTS-v2` accepted)
- **Lightweight TTS**: Piper `en_US-amy-medium` — model expected at `models\piper\en_US-amy-medium.onnx` (HF auto-download allowed)
- **Fallback TTS**: eSpeak-ng (no download)
- **Transcription**: whisper.cpp medium English — `models\whisper\whisper-medium.en.gguf` (HF auto-download allowed)
- **Voice conversion target**: So-VITS-SVC 4.0 checkpoints at `models\checkpoints\<project>\model.pth` + `config.json` (manual/pre-seeded)

---

## 🔧 Implementation Guidelines

### Allowed Changes
- Model loading, caching, and lifecycle hardening
- Quality improvements in synthesis and conversion paths
- Deterministic configuration where feasible (seed/config capture)
- Clear fault mapping: internal faults → user-readable errors
- Default engine selection logic
- Preflight checks and auto-download flows

### Out of Scope
- UI layout and WinUI wiring under `src/VoiceStudio.App/` (UI role owns)
- Storage schema changes under `app/core/storage/` without Core Platform sign-off
- Build/tooling configuration (Build & Tooling Engineer owns)

### Handoff Requirements
- Add one handoff record file: `docs/governance/overseer/handoffs/VS-<ledgerId>.md`
- Use `docs/governance/overseer/CHANGESET_HANDOFF_TEMPLATE.md` as format
- Include proof run commands and results

### Evidence Standard
- Provide proof run that performs end-to-end voice workflow (import → synthesize/convert → export)
- Provide baseline audio outputs and exact engine configuration used
- Include quality metrics in proof runs
- Show preflight checks passing before operations

---

## 🎯 Immediate Action Items

1. **Verify default engine selection works:**
   - Test `/api/voice/synthesize` without `engine` parameter → should default to XTTS
   - Test fallback chain: XTTS unavailable → Piper → eSpeak
   - Test `/api/transcribe` defaults to `whisper_cpp`

2. **Check So-VITS-SVC engine status:**
   - Look for existing So-VITS engine in `app/core/engines/`
   - Check `backend/api/routes/rvc.py` for voice conversion endpoints
   - Verify preflight checks for So-VITS checkpoints

3. **Verify quality metrics error handling:**
   - Test with missing dependencies (pesq, pystoi, resemblyzer)
   - Verify actionable error messages
   - Ensure no placeholder values returned

---

## 📚 Reference Files

**Task List:** `docs/governance/overseer/role_tasks/ENGINE_ENGINEER.md`  
**Role Prompt:** `docs/governance/overseer/roles/ENGINE_ENGINEER.md`  
**Handoff Template:** `docs/governance/overseer/CHANGESET_HANDOFF_TEMPLATE.md`  
**Quality Ledger:** `Recovery Plan/QUALITY_LEDGER.md`

**Completed Handoffs:**
- `docs/governance/overseer/handoffs/VS-0002.md` - ML quality prediction
- `docs/governance/overseer/handoffs/VS-0007.md` - ML prediction integration
- `docs/governance/overseer/handoffs/VS-0009.md` - Chatterbox/Tortoise ML prediction

---

## 🚦 Start Here

1. Read your task list: `docs/governance/overseer/role_tasks/ENGINE_ENGINEER.md`
2. Verify default engine selection works (Task 1 above)
3. Check So-VITS-SVC engine status (Task 2 above)
4. Verify quality metrics error handling (Task 3 above)
5. Create handoff documents for any work completed
6. Update ledger entries when work is done

**Remember:** All work must advance voice cloning quality. No placeholders. Real implementations only.
