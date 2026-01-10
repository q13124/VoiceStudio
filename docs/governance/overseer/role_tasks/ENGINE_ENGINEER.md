eeeeeeeeeeeeeeeer — Next task list (voice cloning focused)

## Mission alignment

Advance **voice cloning quality + capability** while staying local-first and keeping engine dependencies compatible (per the architecture blueprint + dependency guide).

## Current model wiring (must remain consistent)

- **Model root**: `E:\VoiceStudio\models` (default via `backend/api/main.py`, overrideable via `VOICESTUDIO_MODELS_PATH`)
- **Primary TTS**: Coqui XTTS-v2 (`coqui/XTTS-v2`) — HF auto-download allowed
- **Lightweight TTS**: Piper `en_US-amy-medium` — model expected at `models\piper\en_US-amy-medium.onnx` (HF auto-download allowed)
- **Fallback TTS**: eSpeak-ng (no download)
- **Transcription**: whisper.cpp medium English — `models\whisper\whisper-medium.en.gguf` (HF auto-download allowed)
- **Voice conversion target**: So-VITS-SVC 4.0 checkpoints at `models\checkpoints\<project>\model.pth` + `config.json` (manual/pre-seeded)

## What you do next (ordered)

### 1) Pre-flight model checks (fail fast with actionable errors)

- [ ] Add a backend/engine “preflight” check for required assets:
  - XTTS availability + model download path
  - Piper onnx + json presence (or auto-download flow)
  - whisper.cpp gguf presence
  - So-VITS-SVC checkpoint/config presence under `models\checkpoints\...`
- **Success**: API returns clear “what file is missing + where to put it” errors (no cryptic stack traces).

### 2) Auto-download implementation (HF-backed models only)

- [ ] Ensure XTTS/Piper/Whisper downloads land under `E:\VoiceStudio\models` consistently (respect `HF_HOME`, `TTS_HOME`, etc.).
- [ ] Log download start/finish + disk paths for operator visibility.
- **Success**: first-run pulls the models; subsequent runs are offline.

### 3) Wire “real” engine defaults into routes (no placeholder responses)

- [ ] Confirm `/api/voice/*` routes use XTTS as primary and Piper as fallback (then eSpeak).
- [ ] Confirm `/api/transcribe` defaults to whisper_cpp and supports `model_path` override.
- **Success**: end-to-end voice workflow produces real audio/text artifacts using the configured defaults.

### 4) Voice conversion (So-VITS-SVC 4.0)

- [ ] If no So-VITS-SVC engine adapter exists yet: implement it under `app/core/engines/` using the checkpoint layout defined above.
- [ ] Expose it via the engine registry/config so it is selectable and testable.
- **Success**: conversion endpoint produces transformed audio given a valid checkpoint + config.

### 5) Quality metrics (real computation)

- [ ] Ensure PESQ/STOI + embedding similarity (resemblyzer/speechbrain) execute when deps are present.
- [ ] When deps are missing, return actionable guidance (“pip install …”, “model path …”) instead of silent defaults.
- **Success**: quality metrics pipeline never returns dummy values; it either computes or explicitly reports missing dependencies.

## Proof run expectation

- Provide a proof run that performs:
  - synthesize (XTTS) → transcribe (whisper.cpp) → (optional) convert (So-VITS) → export
  - include the exact engine config + model paths used
