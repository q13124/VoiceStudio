# Engine Engineer — Next task list (voice cloning focused)

## Mission alignment

Advance **voice cloning quality + capability** while staying local-first and keeping engine dependencies compatible (per the architecture blueprint + dependency guide).

## Current model wiring (must remain consistent)

- **Model root**: `E:\VoiceStudio\models` (default via `backend/api/main.py`, overrideable via `VOICESTUDIO_MODELS_PATH`)
- **Primary TTS**: Coqui XTTS-v2 (`tts_models/multilingual/multi-dataset/xtts_v2`) — Coqui TTS manages auto-download (legacy alias `coqui/XTTS-v2` accepted)
- **Lightweight TTS**: Piper `en_US-amy-medium` — model expected at `models\piper\en_US-amy-medium.onnx` (HF auto-download allowed)
- **Fallback TTS**: eSpeak-ng (no download)
- **Transcription**: whisper.cpp medium English — `models\whisper\whisper-medium.en.gguf` (HF auto-download allowed)
- **Voice conversion target**: So-VITS-SVC 4.0 checkpoints at `models\checkpoints\<project>\model.pth` + `config.json` (manual/pre-seeded)

## What you do next (ordered)

### 0) Gate status sanity (do not drift)

- Gate C is **DONE** (boot + UI smoke stable).
- Gate H is **DONE** (VS-0003 lifecycle proof). Avoid large dependency upgrades unless tracked in the ledger with proof.

### 1) Unblock XTTS and rerun the baseline proof (quality + functions)

- [x] Install the pinned engine stack in the backend venv so XTTS loads:
  - `powershell -NoProfile -Command '& { $log=Join-Path ".\.buildlogs" ("engine-deps-install-" + (Get-Date -Format "yyyyMMdd-HHmmss") + "-" + $PID + ".log"); New-Item -ItemType Directory -Path (Split-Path $log -Parent) -Force | Out-Null; & .\scripts\install-engine-deps.ps1 -VenvDir venv -Profile xtts 2>&1 | Tee-Object -FilePath $log; Write-Host ("LOG_PATH=" + $log) }'`
- [x] Verify `/api/engines/list` shows `xtts_v2` available; rerun `scripts/baseline_voice_workflow_proof.py` and capture a proof run with non-null `audio_id` + metrics.
- **Success**: proof run produces audio and metrics; artifacts recorded in `proof_runs/...`.
  - **PASS evidence (baseline)**: `proof_runs\\baseline_workflow_20260114-052929\\` (audio + transcription + metrics + config)
  - **PASS evidence (prosody)**: `proof_runs\\baseline_workflow_20260116-091722_prosody\\` (audio + transcription + metrics + config)

### 2) Auto-download implementation (HF-backed models only)

- [x] Ensure XTTS/Piper/Whisper downloads land under `E:\VoiceStudio\models` consistently (respect `HF_HOME`, `TTS_HOME`, etc.)
- [x] Log download start/finish + disk paths for operator visibility
- **Status**: Model preflight service supports auto-download
- **Next**: Verify auto-download works end-to-end and logs are visible

### 3) Wire "real" engine defaults into routes (no placeholder responses)

- [x] Confirm `/api/voice/*` routes use XTTS as primary and Piper as fallback (then eSpeak)
- [x] Confirm `/api/transcribe` defaults to whisper_cpp and supports `model_path` override
- **Success**: end-to-end voice workflow produces real audio/text artifacts using the configured defaults

### 4) Voice conversion (So-VITS-SVC 4.0)

- [ ] If no So-VITS-SVC engine adapter exists yet: implement it under `app/core/engines/` using the checkpoint layout defined above
- [ ] Expose it via the engine registry/config so it is selectable and testable
- **Success**: conversion endpoint produces transformed audio given a valid checkpoint + config

### 5) Quality metrics (real computation)

- [x] Ensure PESQ/STOI + embedding similarity (resemblyzer/speechbrain) execute when deps are present (VS-0002, VS-0007, VS-0009 - DONE)

**Code Quality Note:** Roslynator is integrated and configured as warnings (non-blocking). Fix warnings incrementally as you work to maintain clean, high-quality engine code.

- [x] ML quality prediction integrated into engine metrics (VS-0007 - DONE)
- [x] Enabled in Chatterbox and Tortoise engines (VS-0009 - DONE)
- [x] Quality metrics pipeline does not emit static defaults when deps are missing; returns actionable guidance instead
- **Status**: `/api/voice/analyze` reports `missing_dependencies` and omits unavailable metrics (VS-0034 DONE)

## Completed Work (Reference)

### VS-0002: Replace placeholder ML quality prediction (DONE)

- Production-ready deterministic quality prediction implementation
- Weighted combination of quality metrics (MOS, SNR, Naturalness, Similarity, Artifact Score)
- All placeholder comments removed

### VS-0007: ML quality prediction integration (DONE)

- Integrated ML prediction into `calculate_all_metrics` function
- XTTS engine uses ML prediction for enhanced quality assessment
- Backward compatible, opt-in feature

### VS-0009: Enable ML prediction in Chatterbox and Tortoise (DONE)

- All three major voice cloning engines (XTTS, Chatterbox, Tortoise) now have ML-based quality assessment
- Consistent quality evaluation across engines

## Proof run expectation

- Provide a proof run that performs:
  - synthesize (XTTS) → transcribe (whisper.cpp) → (optional) convert (So-VITS) → export
  - include the exact engine config + model paths used
