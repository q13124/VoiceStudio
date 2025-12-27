# VoiceStudio — Engine Integration Addendum (Offline-First, Modular, Governor-Ready)

**Goal:** Extend the plan/roadmap to integrate all user-approved engines (audio, image, video, alignment, subtitles) into the same plugin/manifest system, driven by the Governor + learners and surfaced through the dense WinUI 3 UI you approved.

## 1) Guardrails (Overseer → Cursor)

- Do **not** simplify the UI. Preserve lattice density, panel hierarchy, meters, Command Palette, Theme/Density packs.

- **Offline first.** Online connectors (Jogg.ai, InVideo) exist but are **disabled by default**.

- Use **one manifest format** for all engines so runtime selection + ensembles are trivial.

- **Additive overlay only.** Never delete existing panels/features/state.

- **Ethics gate**: face-swap/talking-head features require consent toggle + (optional) watermark.

---

## 2) Universal Engine Manifest (used for every engine)

`engines/<domain>/<engineId>/engine.manifest.json`

```jsonc
{
  "id": "xtts_v2",
  "type": "audio_tts",        // audio_tts|audio_stt|audio_vc|align|subtitle|image_gen|video_gen|video_edit|avatar|face_swap|upscaler|utility
  "displayName": "Coqui XTTS v2",
  "entry": {
    "kind": "python",         // python|exe|http|node|cli
    "exe": "..\\..\\..\\.venv\\Scripts\\python.exe",
    "args": ["-m","TTS.bin.tts_server","--model_name","tts_models/multilingual/multi-dataset/xtts_v2"],
    "cwd": ".",
    "env": { "PYTHONIOENCODING": "utf-8" }
  },
  "health": { "kind": "http", "url": "http://127.0.0.1:8021/health" },  // or "process"/"file"
  "tasks": ["tts","clone_infer","embed_voice"],
  "resources": { "needs": ["cuda_optional"], "vram_gb": 4 },
  "models": { "paths": ["%PROGRAMDATA%/VoiceStudio/models/xtts_v2"] },
  "protocol": "v1"
}
```

---

## 3) Engines to Integrate (What/Why/How)

### Audio — TTS / VC / STT / Alignment

| Engine | Type | Purpose | Wrapper |
|--------|------|---------|---------|
| Coqui XTTS v2 | audio_tts | premium cloning + multilingual | Python HTTP (TTS.bin.tts_server) |
| Higgs Audio | audio_tts | high-fidelity, zero-shot (OSS) | Python module |
| Piper | audio_tts | fast, lightweight, many voices | CLI piper.exe (stdin/out) |
| F5-TTS | audio_tts | modern expressive neural TTS | Python module |
| MaryTTS | audio_tts | classic OSS TTS | local HTTP |
| Festival/Flite, eSpeak NG, RHVoice | audio_tts | legacy/accessibility | CLI |
| GPT-SoVITS, MockingBird | audio_vc | conversion/fine-tune | Python module/CLI |
| whisper.cpp | audio_stt | local STT; SRT/VTT | CLI binary |
| Aeneas | align/subtitle | audio-text alignment, subtitles | Python module (aeneas.tools.execute_task) |

### Image — Generation/Upscale

| Engine | Type | Purpose | Wrapper |
|--------|------|---------|---------|
| ComfyUI | image_gen/video_gen | node workflows; SDXL/SVD | local HTTP (8188) |
| AUTOMATIC1111, SD.Next, InvokeAI | image_gen | SD pipelines | HTTP/CLI |
| Real-ESRGAN | upscaler | image/video upscale | CLI/HTTP |

### Video — Gen/Avatar/Edit

| Engine | Type | Purpose | Wrapper |
|--------|------|---------|---------|
| Stable Video Diffusion (SVD) | video_gen | short clips from img/text | via ComfyUI or python |
| Deforum | video_gen | keyframed SD animations | webui/CLI |
| First Order Motion Model (FOMM) | avatar | motion transfer | python |
| SadTalker | avatar | talking head, lip-sync | python |
| DeepFaceLab | face_swap | face replacement | python toolchain (gated) |
| MoviePy | video_edit | programmable editing | python |
| FFmpeg | utility/video_edit | transcode/mux/filters | CLI |

**Online connectors (OFF by default):** Jogg.ai, InVideo → manifests `kind:http` with OAuth placeholders.

**CPU-friendly fallbacks:** SD CPU forks, FastSD CPU (reduced quality/speed) as extra `image_gen` manifests.

---

## 4) Installers (PowerShell Notes)

### FFmpeg
```powershell
choco install ffmpeg -y
```

### Python Dependencies (inside `E:\VoiceStudio\.venv`)
```powershell
E:\VoiceStudio\.venv\Scripts\python.exe -m pip install --upgrade pip wheel
pip install TTS moviepy aeneas real-esrgan  # plus your pinned set
```

### whisper.cpp
Drop binaries under `tools\whispercpp\`.

### ComfyUI
Clone to `external\ComfyUI`, run `run_nvidia_gpu.bat`, manifest health at `http://127.0.0.1:8188`.

### Cursor Rule
Create manifests first, then EngineRunner wrappers (C#) and minimal FastAPI adapters where needed.

---

## 5) UI Wiring (Panels → Engines)

- **Voice Profile/Studio** → XTTS/Piper/Higgs/F5-TTS (router drop-down in header).

- **Transcribe** → whisper.cpp.

- **Alignment/Subtitles/ADR** → Aeneas (+ Whisper).

- **Image Gen** → ComfyUI/A1111/SD.Next (panel selector).

- **Video Gen** → SVD/Deforum (Comfy workflow ids).

- **Avatar** → SadTalker/FOMM.

- **Face Swap** → DeepFaceLab (consent/watermark).

- **Upscale** → Real-ESRGAN.

- **Video Edit** → MoviePy + FFmpeg nodes.

- **Pipeline/Node Graph** composes all; Governor orchestrates A/B and ensembles.

### Command Palette Actions

- `engine:select <task>`
- `engine:toggle ensemble`
- `render:image`
- `render:video`
- `subtitle:align`
- `avatar:talking_head`

---

## 6) Cursor Work Items (Overseer → 6 Workers)

### Phase A — Manifests & Runners

- Create folders in `engines/` and author `engine.manifest.json` for each engine above.
- Implement `EngineRunner` per `entry.kind` (python/exe/http).
- Health checks per engine (HTTP/process/file).
- Update `engine_router.json` defaults:
  ```json
  {"tts":"xtts_v2","image_gen":"comfyui","video_gen":"svd"}
  ```

### Phase B — Backend Adapters (FastAPI)

- Minimal routes for Aeneas, MoviePy, Real-ESRGAN, Avatar/FaceSwap wrappers.
- Standard response: `{status, progress, output_path}`.

### Phase C — UI Panels

- Add engine drop-downs in Image/Video/Avatar/Subtitle panels.
- Add "External Connector" panel grouping Jogg/InVideo (disabled).

### Phase D — Tests

- Smoke test per engine: start → health → trivial task → shutdown.
- Golden-set batch:
  - TTS (10 lines)
  - STT (3 clips)
  - Image (SDXL prompt)
  - Video (SVD 16–24 f)

### Phase E — Ethics & Safety

- Consent toggle required; optional watermark; audit log entries.

---

## 7) Sample Manifests (Drop-in)

### whisper.cpp (STT)

```json
{
  "id": "whisper_cpp",
  "type": "audio_stt",
  "displayName": "whisper.cpp",
  "entry": {
    "kind": "exe",
    "exe": "tools\\\\whispercpp\\\\whisper.exe",
    "args": []
  },
  "health": {
    "kind": "file",
    "path": "tools\\\\whispercpp\\\\whisper.exe"
  },
  "tasks": ["stt", "srt"]
}
```

### Aeneas (Alignment)

```json
{
  "id": "aeneas",
  "type": "align",
  "displayName": "Aeneas",
  "entry": {
    "kind": "python",
    "exe": ".venv\\\\Scripts\\\\python.exe",
    "args": ["-m", "aeneas.tools.execute_task"]
  },
  "health": {
    "kind": "process"
  },
  "tasks": ["align", "subtitle"]
}
```

### ComfyUI (Image/Video)

```json
{
  "id": "comfyui",
  "type": "image_gen",
  "displayName": "ComfyUI",
  "entry": {
    "kind": "exe",
    "exe": "external\\\\ComfyUI\\\\run_nvidia_gpu.bat",
    "args": []
  },
  "health": {
    "kind": "http",
    "url": "http://127.0.0.1:8188"
  },
  "tasks": ["img_gen", "svd_render"]
}
```

### SadTalker (Avatar)

```json
{
  "id": "sadtalker",
  "type": "avatar",
  "displayName": "SadTalker",
  "entry": {
    "kind": "python",
    "exe": ".venv\\\\Scripts\\\\python.exe",
    "args": ["-m", "sadtalker.cli"]
  },
  "health": {
    "kind": "process"
  },
  "tasks": ["talking_head"]
}
```

### DeepFaceLab (Face-Swap; Gated)

```json
{
  "id": "dfl",
  "type": "face_swap",
  "displayName": "DeepFaceLab (Gated)",
  "entry": {
    "kind": "python",
    "exe": ".venv\\\\Scripts\\\\python.exe",
    "args": ["-m", "dfl.pipeline"]
  },
  "health": {
    "kind": "process"
  },
  "tasks": ["extract", "train", "merge"],
  "policy": {
    "consent_required": true,
    "watermark_default": true
  }
}
```

---

## 8) Acceptance Checklist

- [ ] All manifests discovered by Engine Manager; start/stop works.
- [ ] Router switches per task; Governor records choices.
- [ ] Panels expose engine selectors; jobs succeed offline.
- [ ] End-to-end: TTS → Align → Subtitle → Video render passes.
- [ ] Palette commands work.
- [ ] Safety gates enabled for sensitive features.

---

## 9) Models & Storage

- Store all weights under `%PROGRAMDATA%/VoiceStudio/models/<engine>`.
- Provide "Model Manager" subpanel to fetch/update models (checksums).

---

## 10) Handoff to Cursor

Implement Phase A completely before UI edits. Then Phase B adapters, then selectors. Keep existing UI/panels; this addendum is an overlay.

---

**Note:** Ready-made engine manifests for your exact set and a `verify_env.py` health script are available on request.

